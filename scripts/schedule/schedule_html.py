#!/usr/bin/env python3
"""Render the public schedule snapshot as screen and compact print HTML."""
import html
import json
import pathlib
import re

from schedule_build import BODY_MARK, _group, assert_room_free, detect_semester


def plain(value):
    value = value.replace(r'\tbd', 'To be announced').replace(r'\&', '&')
    value = value.replace('---', '—').replace('--', '–').replace('~', ' ')
    if '\\' in value or '{' in value or '}' in value:
        raise ValueError(f'Unsupported TeX in public schedule field: {value!r}')
    return html.escape(value)


def _groups(text, pos, count):
    values = []
    for _ in range(count):
        while pos < len(text) and text[pos].isspace():
            pos += 1
        group = _group(text, pos)
        if group is None:
            raise ValueError('Cannot parse schedule macro arguments')
        value, pos = group
        values.append(value)
    return values, pos


def prose(value):
    """Convert the small, explicit TeX vocabulary used by notes and the grid.

    Unknown commands fail closed so a future source change cannot quietly omit text.
    """
    value = re.sub(r'(?<!\\)%[^\n]*', '', value)
    result, pos = [], 0
    while pos < len(value):
        if value[pos] != '\\':
            end = value.find('\\', pos)
            if end < 0:
                end = len(value)
            result.append(plain(value[pos:end]))
            pos = end
            continue
        command = re.match(r'\\([A-Za-z]+|.)', value[pos:], re.S)
        if not command:
            raise ValueError('Incomplete TeX escape in schedule prose')
        name = command.group(1)
        pos += command.end()
        if name in ('textbf', 'textit'):
            args, pos = _groups(value, pos, 1)
            tag = 'strong' if name == 'textbf' else 'em'
            result.append(f'<{tag}>{prose(args[0])}</{tag}>')
        elif name == 'GridRoom':
            args, pos = _groups(value, pos, 1)
            if args[0].strip():
                raise ValueError('Room data in weekly grid')
        elif name == 'GridRoomNote':
            result.append('rooms omitted; ')
        elif name == 'tbd':
            result.append('To be announced')
        elif name == '&':
            result.append('&amp;')
        elif name.isspace():
            result.append(' ')
        else:
            raise ValueError(f'Unsupported TeX command in schedule prose: {name}')
    return re.sub(r'\s+', ' ', ''.join(result)).strip()


def parse(tex, path):
    assert_room_free(tex, path)
    semester = detect_semester(tex)
    stamp = re.search(r'\\newcommand\{\\SnapshotStamp\}\{([^}]+)\}', tex)
    if not stamp:
        raise ValueError('Missing schedule snapshot timestamp')
    document = tex.split(BODY_MARK, 1)[1]
    dates = re.search(r'\\hfill\s*(.*?)\\quad\\textbullet', document, re.S)
    if not dates:
        raise ValueError('Missing semester date range')
    body = document.split(r'\begin{multicols}{2}', 1)[1].split(r'\end{multicols}', 1)[0]
    starts = list(re.finditer(r'\\Ch\s*(?=\{)', body))
    courses = []
    for i, match in enumerate(starts):
        fields, pos = _groups(body, match.end(), 3)
        content = body[pos:starts[i + 1].start() if i + 1 < len(starts) else len(body)]
        course = {'heading': fields, 'rows': [], 'notes': []}
        cursor = 0
        for row in re.finditer(r'\\(Sx|Dx)\s*(?=\{)', content):
            if content[cursor:row.start()].strip():
                raise ValueError('Unexpected prose between schedule section rows')
            kind = row.group(1)
            args, cursor = _groups(content, row.end(), 6 if kind == 'Sx' else 5)
            course['rows'].append((kind, args))
        tail = content[cursor:].strip()
        if tail:
            course['notes'] = [prose(note) for note in tail.split(r'\par') if note.strip()]
        courses.append(course)
    if not courses:
        raise ValueError('Schedule contains no courses')
    # Preserve the hand-maintained graduate grid and its collision notes too.
    grid_match = re.search(r'\\begin\{tabular\}', document)
    if not grid_match:
        raise ValueError('Missing graduate weekly grid')
    _, grid_start = _groups(document, grid_match.end(), 1)
    grid_source = document[grid_start:].split(r'\end{tabular}', 1)[0].replace(r'\hline', '')
    grid = []
    for line in grid_source.split('\\\\'):
        if line.strip():
            cells = [prose(cell) for cell in re.split(r'(?<!\\)&', line)]
            if len(cells) != 6:
                raise ValueError(f'Weekly grid row has {len(cells)} cells, expected six')
            grid.append(cells)
    grid_note_match = re.search(r'\\textcolor\{lite\}\{\(5000-level', document)
    if not grid_note_match:
        raise ValueError('Missing graduate grid explanation')
    _, note_start = _groups(document, grid_note_match.start() + len(r'\textcolor'), 1)
    note, _ = _groups(document, note_start, 1)
    return {'semester': semester, 'stamp': plain(stamp.group(1)),
            'dates': plain(dates.group(1).strip()), 'courses': courses,
            'grid': grid, 'grid_note': prose(note[0])}


EXPLANATIONS = ('Meeting abbreviations: Mo = Monday, Tu = Tuesday, We = Wednesday, '
                'Th = Thursday, Fr = Friday; MWF = Monday, Wednesday, Friday. '
                'Times use the timetable’s 12-hour notation. '
                'Enrollment is enrolled/capacity; parentheses give combined cross-listed enrollment. '
                'D = discussion section; — = no value listed; TBA = to be announced. '
                'This public reference has rooms omitted.')


def _grid(data):
    out = ['<section class="weekly-grid">', '<h2>Graduate courses and seminars — weekly grid</h2>',
           f'<p>{data["grid_note"]}</p>', '<table>',
           '<caption>Graduate meetings by time and weekday (5000-level and above)</caption>',
           '<thead><tr><th scope="col">Time</th>']
    out.extend(f'<th scope="col">{cell}</th>' for cell in data['grid'][0][1:])
    out.append('</tr></thead><tbody>')
    for row in data['grid'][1:]:
        out.append(f'<tr><th scope="row">{row[0]}</th>')
        out.extend(f'<td>{cell or "—"}</td>' for cell in row[1:])
        out.append('</tr>')
    return '\n'.join(out + ['</tbody></table></section>'])


def render(tex, path):
    data = parse(tex, path)
    semester = data['semester']
    out = ['---', 'layout: static_page_no_right_menu',
           'title: ' + json.dumps(semester + ' Mathematics class schedule'),
           'permalink: /schedule/', '---', '',
           f'<h1>{semester} Mathematics class schedule</h1>',
           f'<p>Semester dates: {data["dates"]}. Snapshot: {data["stamp"]}. Enrollment may have changed since this snapshot.</p>',
           '<p>For current enrollment and registration, use <a href="https://sisuva.admin.virginia.edu/ihprd/signon.html">SIS</a>. A <a href="{{ site.url }}/schedule.pdf">printable PDF of this snapshot</a> is also available.</p>',
           f'<p>{EXPLANATIONS}</p>']
    for course in data['courses']:
        code, title, units = course['heading']
        out += [f'<h2>{plain(code)}' + (f': {plain(title)}' if title else '') + '</h2>']
        if units:
            out.append(f'<p>{plain(units)}</p>')
        # A group headed by something other than a course code (the Seminars group)
        # lists course numbers in the section field and "Topic (Instructor)" cells.
        seminar_group = not re.fullmatch(r'MATH \d{4}', code.strip())
        if course['rows']:
            out.append('<ul class="schedule-sections">')
            for macro, fields in course['rows']:
                section, number, meeting, room = fields[:4]
                instructor = fields[-1]
                kind = 'Discussion section' if macro == 'Dx' else 'Section'
                heading, label = f'{kind} {plain(section)}', 'Instructor'
                if seminar_group:
                    topic = re.fullmatch(r'(.+?)\s*\(([^()]+)\)\s*', instructor)
                    heading = f'MATH {plain(section)}'
                    if topic:
                        heading += f': {plain(topic.group(1))}'
                        instructor = topic.group(2)
                    else:
                        label = 'Topic and instructor'
                out += [f'<li><h3>{heading}</h3>', '<dl>',
                        f'<dt>Class number</dt><dd>{plain(number)}</dd>',
                        f'<dt>Meetings</dt><dd>{plain(meeting)}</dd>',
                        f'<dt>{label}</dt><dd>{plain(instructor)}</dd>']
                if macro == 'Sx':
                    out.append(f'<dt>Enrollment / capacity</dt><dd>{plain(fields[4])}</dd>')
                out += ['</dl></li>']
            out.append('</ul>')
        out.extend(f'<p>{note}</p>' for note in course['notes'])
    out += ['<div class="table-responsive" role="region" aria-label="Graduate weekly schedule" tabindex="0">',
            _grid(data), '</div>']
    return '\n'.join(out) + '\n'


PRINT_CSS = '''
@page { size: Letter landscape; margin: .32in; }
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; color: #000; background: #fff; }
body { font-family: Arial, Helvetica, sans-serif; font-size: 8pt; line-height: 1.12; }
h1 { font-size: 13pt; line-height: 1.15; margin: 0 0 3pt; }
h2 { font-size: 8pt; line-height: 1.1; margin: 0 0 1pt; }
p { margin: 0 0 3pt; }
a { color: #000; }
.schedule-intro { margin-bottom: 4pt; border-bottom: 1pt solid #000; padding-bottom: 3pt; }
.schedule-intro p { font-size: 7pt; line-height: 1.1; }
.schedule-columns { column-count: 2; column-gap: .22in; column-fill: balance; }
.course { break-inside: avoid; margin: 0 0 3pt; }
.course h2 { border-top: .5pt solid #777; padding-top: 2pt; }
.course h2 .units { font-weight: normal; }
table { width: 100%; border-collapse: collapse; table-layout: fixed; }
th, td { vertical-align: top; text-align: left; padding: .35pt 1.2pt; overflow-wrap: anywhere; }
thead th { font-size: 6.8pt; font-weight: normal; border-bottom: .35pt solid #999; }
.course tbody th { font-weight: normal; }
.course col:nth-child(1) { width: 7%; }
.course col:nth-child(2) { width: 9%; }
.course col:nth-child(3) { width: 25%; }
.course col:nth-child(4) { width: 17%; }
.course col:nth-child(5) { width: 42%; }
.course td:nth-child(2), .course td:nth-child(3) { white-space: nowrap; }
.course.notes { font-size: 7.4pt; }
.course.notes p { margin-bottom: 1.8pt; }
.weekly-grid { margin-top: 5pt; break-inside: avoid; }
.weekly-grid h2 { font-size: 9pt; }
.weekly-grid p { font-size: 7pt; }
.weekly-grid table { font-size: 7pt; line-height: 1.08; }
.weekly-grid th, .weekly-grid td { border: .35pt solid #999; padding: 2pt; }
.weekly-grid caption { font-size: 7pt; text-align: left; margin-bottom: 2pt; }
@media screen { body { max-width: 11in; margin: 1rem auto; padding: .32in; } }
'''


def render_print(tex, path):
    """Return a standalone, semantic, compact landscape print document."""
    data = parse(tex, path)
    title = data['semester'] + ' Mathematics class schedule'
    out = ['<!DOCTYPE html>', '<html lang="en"><head><meta charset="utf-8">',
           '<meta name="viewport" content="width=device-width, initial-scale=1">',
           f'<title>{html.escape(title)}</title>', f'<style>{PRINT_CSS}</style>',
           '</head><body><main>', '<header class="schedule-intro">',
           f'<h1>UVA Mathematics — {data["semester"]}</h1>',
           f'<p><strong>{data["dates"]}</strong> · {data["stamp"]}. Enrollment may have changed since this snapshot.</p>',
           f'<p>{EXPLANATIONS}</p>',
           '<p>Readable snapshot: <a href="https://math.virginia.edu/schedule/">math.virginia.edu/schedule/</a>. '
           'Current enrollment and registration: <a href="https://sisuva.admin.virginia.edu/ihprd/signon.html">SIS</a>.</p>',
           '</header>', '<div class="schedule-columns">']
    for i, course in enumerate(data['courses'], 1):
        code, name, units = course['heading']
        heading = plain(code) + (': ' + plain(name) if name else '')
        if units:
            heading += f' <span class="units">({plain(units)})</span>'
        out += [f'<section class="course{" notes" if course["notes"] else ""}">',
                f'<h2 id="course-{i}">{heading}</h2>']
        if course['rows']:
            out += [f'<table aria-labelledby="course-{i}"><colgroup><col><col><col><col><col></colgroup>',
                    '<thead><tr><th scope="col">Section</th><th scope="col">Class #</th><th scope="col">Meetings</th><th scope="col">Enrolled/cap.</th><th scope="col">Instructor / seminar</th></tr></thead><tbody>']
            for kind, row in course['rows']:
                section = ('D ' if kind == 'Dx' else '') + plain(row[0])
                enrollment = plain(row[4]) if kind == 'Sx' else '—'
                cells = [plain(row[1]), plain(row[2]), enrollment, plain(row[-1])]
                cells = [cell.replace('To be announced', 'TBA') for cell in cells]
                out += [f'<tr><th scope="row">{section}</th>' + ''.join(f'<td>{cell}</td>' for cell in cells) + '</tr>']
            out.append('</tbody></table>')
        out.extend(f'<p>{note}</p>' for note in course['notes'])
        out.append('</section>')
    out += ['</div>', _grid(data), '</main></body></html>']
    return '\n'.join(out) + '\n'


def write_html(site):
    source = site / 'schedule.tex'
    target = site / 'schedule.html'
    target.write_text(render(source.read_text(), source))
    return target


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=pathlib.Path, default=pathlib.Path(__file__).resolve().parents[2] / 'schedule.tex')
    parser.add_argument('--print-output', type=pathlib.Path, help='write standalone compact print HTML instead of the screen snapshot')
    args = parser.parse_args()
    if args.print_output:
        args.print_output.write_text(render_print(args.source.read_text(), args.source))
        print(args.print_output)
    else:
        print(write_html(args.source.parent))
