#!/usr/bin/env python3
"""Tag a reviewed, single-page PDF illustration without changing its artwork.

Only for an image asset whose complete alternative is supplied by the caller.
Run veraPDF on the candidate before replacing a source file.
"""
import argparse
import re
import pikepdf
from pikepdf import Array, Dictionary, Name


def repair_tex_unicode(pdf):
    """Repair reviewed TeX glyph encodings without changing any drawing data.

    The defense posters contain CMEX size variants absent from their ToUnicode
    maps and remapped CM ligatures/symbols with incorrect maps. Glyph names come
    from the embedded Type 1 encoding or the PDF's explicit Differences array.
    Only these known glyphs are handled; unknown encodings fail closed.
    """
    glyphs = {
        'ffi': 'ffi', 'arrowright': '\u2192', 'element': '\u2208',
        'angbracketleft': '\u27e8', 'angbracketright': '\u27e9',
        'similar': '\u223c', 'multiply': '\u00d7', 'asteriskmath': '\u2217',
        'minus': '\u2212', 'summationtext': '\u2211',
        'summationdisplay': '\u2211', 'producttext': '\u220f',
        'productdisplay': '\u220f',
    }
    for side, text in [('left', '('), ('right', ')')]:
        for size in ['big', 'Big', 'bigg', 'Bigg']:
            glyphs[f'paren{side}{size}'] = text
    repaired = 0
    for font in pdf.objects:
        if not isinstance(font, Dictionary) or font.get('/Subtype') != Name.Type1:
            continue
        family = str(font.get('/BaseFont', '')).split('+')[-1]
        encoding = font.get('/Encoding')
        pairs = []
        replace_map = False
        if family == 'CMEX10' and encoding is None:
            program = font.FontDescriptor.FontFile
            header = program.read_bytes()[:int(program.Length1)].decode('latin1')
            pairs = [(int(code), glyph) for code, glyph in
                     re.findall(r'dup\s+(\d+)\s+/([^\s]+)\s+put', header)]
        elif (family in ('CMSSBX10', 'CMTI10', 'CMSY10', 'CMSY8')
              and isinstance(encoding, Dictionary)):
            if '/BaseEncoding' in encoding:
                raise ValueError(f'Unsupported TeX base encoding: {family}')
            code = None
            for entry in encoding.get('/Differences', []):
                if isinstance(entry, int):
                    code = entry
                else:
                    if code is None:
                        raise ValueError('Glyph without a character code')
                    pairs.append((code, str(entry)[1:]))
                    code += 1
            expected = set(range(int(font.FirstChar), int(font.LastChar) + 1))
            if {code for code, _ in pairs} != expected:
                raise ValueError(f'Incomplete explicit TeX encoding: {family}')
            replace_map = True
        if not pairs:
            continue
        if any(glyph not in glyphs for _, glyph in pairs):
            raise ValueError(f'Unreviewed TeX glyph encoding: {family}: {pairs}')
        entries = '\n'.join(
            f'<{code:02X}> <{glyphs[glyph].encode("utf-16-be").hex().upper()}>'
            for code, glyph in pairs)
        block = f'{len(pairs)} beginbfchar\n{entries}\nendbfchar\n'
        if replace_map:
            cmap = ('/CIDInit /ProcSet findresource begin\n12 dict begin\n'
                    'begincmap\n/CIDSystemInfo << /Registry (Adobe) '
                    '/Ordering (UCS) /Supplement 0 >> def\n'
                    '/CMapName /ReviewedTeXUnicode def\n/CMapType 2 def\n'
                    '1 begincodespacerange\n<00> <FF>\nendcodespacerange\n'
                    + block + 'endcmap\nCMapName currentdict /CMap '
                    'defineresource pop\nend\nend\n')
        else:
            cmap = font.ToUnicode.read_bytes().decode('ascii')
            if cmap.count('endcmap') != 1:
                raise ValueError('Unexpected TeX ToUnicode CMap')
            cmap = cmap.replace('endcmap', block + 'endcmap')
        font.ToUnicode = pdf.make_stream(cmap.encode('ascii'))
        repaired += 1
    if not repaired:
        raise ValueError('No supported TeX Unicode maps found to repair')


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--input', required=True)
parser.add_argument('--output', required=True)
parser.add_argument('--title', required=True)
parser.add_argument('--alt', required=True)
parser.add_argument('--repair-tex-unicode', action='store_true',
    help='Repair reviewed CMEX and explicitly remapped CM glyph Unicode maps')
args = parser.parse_args()
pdf = pikepdf.open(args.input)
if len(pdf.pages) != 1 or '/StructTreeRoot' in pdf.Root:
    raise ValueError('Expected an untagged one-page illustration')
if args.repair_tex_unicode:
    repair_tex_unicode(pdf)
page = pdf.pages[0]
tree = pdf.make_indirect(Dictionary(Type=Name.StructTreeRoot))
document = pdf.make_indirect(Dictionary(Type=Name.StructElem, S=Name.Document, P=tree))
figure = pdf.make_indirect(Dictionary(Type=Name.StructElem, S=Name.Figure,
    P=document, Pg=page.obj, K=0, Alt=args.alt))
document.K = figure
tree.K = document
tree.ParentTree = pdf.make_indirect(Dictionary(Nums=Array([0, Array([figure])])))
tree.ParentTreeNextKey = 1
pdf.Root.StructTreeRoot = tree
pdf.Root.MarkInfo = Dictionary(Marked=True)
pdf.Root.Lang = 'en'
pdf.Root.ViewerPreferences = Dictionary(DisplayDocTitle=True)
page.StructParents = 0
page.Tabs = Name.S
contents = page.Contents
streams = list(contents) if isinstance(contents, Array) else [contents]
page.Contents = pdf.make_stream(b'/Figure <</MCID 0>> BDC\n' +
    b'\n'.join(stream.read_bytes() for stream in streams) + b'\nEMC\n')
pdf.docinfo.Title = args.title
with pdf.open_metadata(set_pikepdf_as_editor=False) as xmp:
    xmp.register_xml_namespace('http://www.aiim.org/pdfua/ns/id/', 'pdfuaid')
    xmp['pdfuaid:part'] = '1'
    xmp['dc:title'] = args.title
pdf.save(args.output, force_version='1.7')
