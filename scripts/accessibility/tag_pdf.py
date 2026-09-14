#!/usr/bin/env python3
"""Repair known Chromium PDF structure omissions, without changing visible content.

Input must come from export_pdf.cjs: mathematical figures carry unique markers,
all meaningful images already have alternatives, and document chrome is removed.
The caller must run veraPDF after this step; repair alone is not certification.
"""
import argparse
from collections import Counter
import json
from pathlib import Path
import re
from urllib.parse import urlsplit, urlunsplit

import pikepdf
from pikepdf import Array, ContentStreamInstruction, Dictionary, Name, Operator


def children(element):
    value = element.get('/K', [])
    return list(value) if isinstance(value, Array) else [value]


def has_described_figure_child(element):
    return any(
        isinstance(child, Dictionary)
        and ((child.get('/S') == Name.Figure and bool(child.get('/Alt')))
             or has_described_figure_child(child))
        for child in children(element)
    )


def public_url(value, public_base):
    parsed = urlsplit(value)
    base = urlsplit(public_base)
    if parsed.hostname in ('localhost', '127.0.0.1', '::1', base.hostname):
        return urlunsplit((base.scheme, base.netloc, parsed.path, parsed.query, parsed.fragment))
    return value


def repair(source, destination, metadata):
    pdf = pikepdf.open(source)
    stats = {'formulas': 0, 'figures': 0, 'lists': 0, 'artifactRuns': 0, 'links': 0, 'figureGroups': 0}
    expected_math = {formula['id']: formula['speech'] for formula in metadata['formulas']}
    found_math = Counter()
    expected_images = Counter(figure['alt'] for figure in metadata['figures'] if figure['alt'])
    found_images = Counter()
    link_labels = {link['url']: link['text'] for link in metadata['links']}

    for element in list(pdf.objects):
        if not isinstance(element, Dictionary):
            continue
        if element.get('/Type') == Name.StructElem:
            alternative = str(element.get('/Alt', ''))
            match = re.match(r'^(UVA_FORMULA_\d+) (.+)$', alternative, re.S)
            if match:
                marker, speech = match.groups()
                if expected_math.get(marker) != speech:
                    raise ValueError(f'Unexpected mathematical alternative: {marker}')
                element.S = Name.Formula
                element.Alt = speech
                found_math[marker] += 1
                stats['formulas'] += 1
            elif element.get('/S') == Name.Figure and alternative:
                found_images[alternative] += 1
                stats['figures'] += 1
            elif element.get('/S') == Name.Figure and has_described_figure_child(element):
                # Chromium tags both HTML <figure> and its described <img> as
                # Figure. The outer container includes the caption; it is a
                # group, while the nested image retains its own alternative.
                element.S = Name.Div
                stats['figureGroups'] += 1
            if element.get('/S') == Name.LI:
                kids = children(element)
                if any(not isinstance(child, Dictionary) or child.get('/S') not in (Name.Lbl, Name.LBody) for child in kids):
                    if any(not isinstance(child, Dictionary) or child.get('/Type') != Name.StructElem for child in kids):
                        raise ValueError('Direct marked content in list item requires a separate parent-tree repair')
                    body = pdf.make_indirect(Dictionary(Type=Name.StructElem, S=Name.LBody, P=element, K=Array(kids)))
                    for child in kids:
                        child.P = body
                    element.K = body
                    stats['lists'] += 1
        if element.get('/Subtype') == Name.Link:
            action = element.get('/A', {})
            if '/URI' in action:
                uri = public_url(str(action['/URI']), metadata['publicBase'])
                action['/URI'] = uri
                element.Contents = link_labels.get(uri, uri)
            elif not element.get('/Contents'):
                element.Contents = 'Link within this document'
            stats['links'] += 1

    if found_math != Counter({marker: 1 for marker in expected_math}):
        raise ValueError(f'Formula tag count mismatch: expected {len(expected_math)}, found {dict(found_math)}')
    missing_images = expected_images - found_images
    if missing_images:
        raise ValueError(f'Image descriptions missing from PDF: {dict(missing_images)}')

    for page in pdf.pages:
        instructions = []
        marked_depth = 0
        artifact_open = False
        for instruction in pikepdf.parse_content_stream(page):
            operator = str(instruction.operator)
            if operator in ('BMC', 'BDC'):
                if artifact_open:
                    instructions.append(ContentStreamInstruction([], Operator('EMC')))
                    artifact_open = False
                instructions.append(instruction)
                marked_depth += 1
            elif operator == 'EMC':
                instructions.append(instruction)
                marked_depth -= 1
                if marked_depth < 0:
                    raise ValueError('Unbalanced marked-content sequence')
            else:
                if marked_depth == 0 and not artifact_open:
                    # The exporter checked every equation and meaningful image;
                    # Chromium leaves page backgrounds, rules and list markers
                    # outside the marked content. Preserve their drawing while
                    # marking those runs as presentation artifacts.
                    instructions.append(ContentStreamInstruction([Name.Artifact], Operator('BMC')))
                    artifact_open = True
                    stats['artifactRuns'] += 1
                instructions.append(instruction)
        if artifact_open:
            instructions.append(ContentStreamInstruction([], Operator('EMC')))
        if marked_depth:
            raise ValueError('Unbalanced marked-content sequence')
        page.Contents = pdf.make_stream(pikepdf.unparse_content_stream(instructions))

    pdf.Root.Lang = 'en'
    preferences = pdf.Root.get('/ViewerPreferences', Dictionary())
    preferences.DisplayDocTitle = True
    pdf.Root.ViewerPreferences = preferences
    roles = pdf.Root.StructTreeRoot.get('/RoleMap', Dictionary())
    roles.Strong = Name.Span
    roles.Em = Name.Span
    pdf.Root.StructTreeRoot.RoleMap = roles
    pdf.docinfo.Title = metadata['title']
    with pdf.open_metadata(set_pikepdf_as_editor=False) as xmp:
        xmp.register_xml_namespace('http://www.aiim.org/pdfua/ns/id/', 'pdfuaid')
        xmp['pdfuaid:part'] = '1'
        xmp['dc:title'] = metadata['title']
    pdf.save(destination, force_version='1.7')
    return stats


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--metadata', required=True)
    arguments = parser.parse_args()
    print(json.dumps(repair(arguments.input, arguments.output, json.loads(Path(arguments.metadata).read_text()))))
