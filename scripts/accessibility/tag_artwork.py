#!/usr/bin/env python3
"""Tag a reviewed, single-page PDF illustration without changing its artwork.

Only for an image asset whose complete alternative is supplied by the caller.
Run veraPDF on the candidate before replacing a source file.
"""
import argparse
import pikepdf
from pikepdf import Array, Dictionary, Name

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--input', required=True)
parser.add_argument('--output', required=True)
parser.add_argument('--title', required=True)
parser.add_argument('--alt', required=True)
args = parser.parse_args()
pdf = pikepdf.open(args.input)
if len(pdf.pages) != 1 or '/StructTreeRoot' in pdf.Root:
    raise ValueError('Expected an untagged one-page illustration')
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
