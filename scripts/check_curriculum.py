"""Check the student curriculum, workbook navigation and supplied material files."""
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit


def require(condition, message):
    if not condition:
        raise ValueError(message)


def check_workbooks(root, lessons):
    entries = {}
    for workbook in sorted((root / 'curriculum/workbooks').glob('*.md')):
        for lesson_id, title in re.findall(r'^#{2,3} (s\d+-l\d+)\s*[:—–-]\s*(.+)$', workbook.read_text(), re.MULTILINE):
            require(lesson_id not in entries, 'Duplicate workbook lesson: ' + lesson_id)
            entries[lesson_id] = (title, workbook.relative_to(root).as_posix())
    require(set(entries) == {lesson['id'] for lesson in lessons}, 'Workbook lesson inventory differs from curriculum')
    for lesson in lessons:
        require(entries[lesson['id']][0] == lesson['title'], 'Workbook title differs: ' + lesson['id'])
    return entries


def check_materials(root, lessons, workbooks):
    index = json.loads((root / 'curriculum/materials.json').read_text())
    require(index['lessonCount'] == len(lessons), 'Material lesson count differs')
    require([row['id'] for row in index['lessons']] == [row['id'] for row in lessons], 'Material lesson ordering differs')
    for lesson, mapped in zip(lessons, index['lessons']):
        for field in ('title', 'objective'):
            require(mapped[field] == lesson[field], 'Material ' + field + ' differs: ' + lesson['id'])
        require(mapped['practicalWorkbook'] == workbooks[lesson['id']][1], 'Wrong workbook: ' + lesson['id'])
        require(bool(mapped['actualMaterials']), 'Missing materials: ' + lesson['id'])
        for item in mapped['actualMaterials']:
            path = root / item['path']
            require(not Path(item['path']).is_absolute() and path.resolve().is_relative_to(root.resolve()), 'Material escapes repository: ' + item['path'])
            require(path.is_file(), 'Missing material: ' + item['path'])
            content = path.read_bytes()
            require(hashlib.sha256(content).hexdigest() == item['sha256'], 'Stale material checksum: ' + item['path'])
            if 'sizeBytes' in item:
                require(len(content) == item['sizeBytes'], 'Stale material size: ' + item['path'])


def check_markdown_links(root):
    checked = 0
    for document in root.rglob('*.md'):
        if any(part in ('.venv', 'node_modules', '__pycache__', '.git') for part in document.parts):
            continue
        for target in re.findall(r'\]\(([^)]+)\)', document.read_text()):
            parsed = urlsplit(target)
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            path = document.parent / unquote(parsed.path)
            require(path.resolve().is_relative_to(root.resolve()), 'Link escapes repository: ' + str(document.relative_to(root)))
            require(path.exists(), 'Broken link in ' + str(document.relative_to(root)) + ': ' + target)
            checked += 1
    return checked


def check_curriculum(root):
    lessons = json.loads((root / 'curriculum/lessons.json').read_text())
    stages = json.loads((root / 'curriculum/stages.json').read_text())
    require(len(lessons) == 362 and len(stages) == 30, 'Expected 362 lessons in 30 stages')
    require(len({lesson['id'] for lesson in lessons}) == 362, 'Duplicate lesson IDs')
    require({lesson['project'] for lesson in lessons} == set(range(1, 9)), 'Expected eight projects')
    for stage in stages:
        rows = [lesson for lesson in lessons if lesson['stage'] == stage['stage']]
        require([lesson['lesson'] for lesson in rows] == list(range(1, stage['lessonCount'] + 1)), 'Lesson sequence differs in stage ' + str(stage['stage']))
    for lesson in lessons:
        require(bool(lesson['title']) and bool(lesson['objective']) and lesson['suggestedMinutes'] > 0, 'Incomplete lesson: ' + lesson['id'])
        require((root / lesson['practicalPath'] / 'README.md').is_file(), 'Missing project README: ' + lesson['id'])
    workbooks = check_workbooks(root, lessons)
    check_materials(root, lessons, workbooks)
    links = check_markdown_links(root)
    print('PASS: 362 lessons, 30 stages, 8 projects; exact workbook titles and current material paths/checksums')
    print('PASS: ' + str(links) + ' local Markdown links resolve')


if __name__ == '__main__':
    check_curriculum(Path(__file__).resolve().parents[1])
