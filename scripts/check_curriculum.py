"""Check exact curriculum inventory and practical directory references."""
import json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
lessons=json.loads((root/'curriculum/lessons.json').read_text())
stages=json.loads((root/'curriculum/stages.json').read_text())
assert len(lessons)==362 and len(stages)==30
assert len({l['id'] for l in lessons})==362
assert {l['project'] for l in lessons}==set(range(1,9))
for s in stages:
 rows=[l for l in lessons if l['stage']==s['stage']]
 assert [l['lesson'] for l in rows]==list(range(1,s['lessonCount']+1))
for lesson in lessons:
 assert lesson['title'] and lesson['objective'] and lesson['suggestedMinutes']>0
 assert (root/lesson['practicalPath']/'README.md').is_file(),lesson['id']
print('PASS: 362 lessons, 30 stages, 8 practical project directories')
