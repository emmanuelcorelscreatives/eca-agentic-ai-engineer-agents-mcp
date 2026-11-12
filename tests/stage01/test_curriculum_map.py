"""Check the authored map against the extracted curriculum, not production readiness."""
import csv
import json
import pathlib
import unittest
ROOT=pathlib.Path(__file__).resolve().parents[2]
class CurriculumMap(unittest.TestCase):
    def test_exact_ordered_lessons_and_titles(self):
        actual=json.loads((ROOT/'curriculum/course-map.json').read_text())
        source=json.loads((ROOT/'curriculum/lessons.json').read_text())
        self.assertEqual(actual['lessonCount'],362)
        self.assertEqual(len(actual['lessons']),362)
        self.assertEqual(len({x['id']for x in actual['lessons']}),362)
        self.assertEqual([(x['id'],x['stage'],x['number'],x['title'])for x in actual['lessons']],[(x['id'],x['stage'],x['lesson'],x['title'])for x in source])
        self.assertEqual(len(actual['modules']),6);self.assertEqual(len(actual['stages']),30)
        self.assertEqual([s for m in actual['modules']for s in m['stages']],list(range(1,31)))
        self.assertEqual([x for s in actual['stages']for x in s['lessonIds']],[x['id']for x in source])
    def test_eight_source_projects_and_real_directories(self):
        p=json.loads((ROOT/'curriculum/project-portfolio.json').read_text())['projects']
        self.assertEqual([x['stage']for x in p],[5,8,9,13,15,20,25,29])
        self.assertEqual([x['id']for x in p],[f'p{i:02}'for i in range(1,9)])
        stages=json.loads((ROOT/'curriculum/stages.json').read_text())
        for x in p:
            self.assertTrue((ROOT/x['directory']).is_dir())
            self.assertEqual(stages[x['stage']-1]['title'],f"Project {x['number']}: {x['title']}")
            self.assertTrue(x['humanApproval']);self.assertTrue(x['limitation']);self.assertTrue(x['requiredEvidence'])
    def test_stack_marks_absent_components_truthfully(self):
        rows=list(csv.DictReader((ROOT/'curriculum/development-stack.csv').read_text().splitlines()))
        by={r['component']:r for r in rows}
        self.assertEqual(by['MCP']['first_workflow_status'],'not used')
        self.assertEqual(by['memory']['first_workflow_status'],'not used')
        self.assertIn('not agent memory',by['memory']['control_note'])
    def test_all_six_student_and_answer_paths_exist(self):
        for i in range(1,7):
            self.assertTrue(any((ROOT/f'labs/s01-l{i:02}').iterdir()))
            self.assertTrue(any((ROOT/f'solutions/s01-l{i:02}').iterdir()))
if __name__=='__main__': unittest.main()
