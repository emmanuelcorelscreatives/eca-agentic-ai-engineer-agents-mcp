import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from scripts.check_curriculum import check_markdown_links, check_materials, check_workbooks


class StudentNavigationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.workbook = self.root / 'curriculum/workbooks/first.md'
        self.workbook.parent.mkdir(parents=True)
        self.workbook.write_text('### s01-l01: First practical\n')
        self.material = self.root / 'exercise.md'
        self.material.write_text('Try the exercise.\n')
        self.lessons = [{'id': 's01-l01', 'title': 'First practical', 'objective': 'Run an exercise.'}]
        self.index = {'lessonCount': 1, 'lessons': [{
            **self.lessons[0], 'practicalWorkbook': 'curriculum/workbooks/first.md',
            'actualMaterials': [{'path': 'exercise.md', 'sha256': hashlib.sha256(self.material.read_bytes()).hexdigest(),
                                 'sizeBytes': self.material.stat().st_size}],
        }]}
        self.save_index()

    def save_index(self):
        (self.root / 'curriculum/materials.json').write_text(json.dumps(self.index))

    def test_matching_workbook_and_materials(self):
        workbooks = check_workbooks(self.root, self.lessons)
        check_materials(self.root, self.lessons, workbooks)

    def test_stale_file_contents_are_rejected(self):
        self.material.write_text('Changed exercise.\n')
        with self.assertRaisesRegex(ValueError, 'Stale material checksum'):
            check_materials(self.root, self.lessons, check_workbooks(self.root, self.lessons))

    def test_wrong_workbook_is_rejected(self):
        self.index['lessons'][0]['practicalWorkbook'] = 'curriculum/workbooks/missing.md'
        self.save_index()
        with self.assertRaisesRegex(ValueError, 'Wrong workbook'):
            check_materials(self.root, self.lessons, check_workbooks(self.root, self.lessons))

    def test_workbook_title_must_match_the_curriculum(self):
        self.workbook.write_text('### s01-l01 — A different practical\n')
        with self.assertRaisesRegex(ValueError, 'Workbook title differs'):
            check_workbooks(self.root, self.lessons)

    def test_duplicate_lesson_is_rejected(self):
        self.workbook.write_text('### s01-l01: First practical\n### s01-l01: First practical\n')
        with self.assertRaisesRegex(ValueError, 'Duplicate workbook lesson'):
            check_workbooks(self.root, self.lessons)

    def test_material_path_cannot_escape_the_checkout(self):
        self.index['lessons'][0]['actualMaterials'][0]['path'] = '../private.md'
        self.save_index()
        with self.assertRaisesRegex(ValueError, 'Material escapes repository'):
            check_materials(self.root, self.lessons, check_workbooks(self.root, self.lessons))

    def test_material_size_is_verified(self):
        self.index['lessons'][0]['actualMaterials'][0]['sizeBytes'] += 1
        self.save_index()
        with self.assertRaisesRegex(ValueError, 'Stale material size'):
            check_materials(self.root, self.lessons, check_workbooks(self.root, self.lessons))

    def test_relative_markdown_links_are_checked(self):
        self.workbook.write_text('[Exercise](../../exercise.md)\n')
        self.assertEqual(check_markdown_links(self.root), 1)
        self.workbook.write_text('[Missing](../../missing.md)\n')
        with self.assertRaisesRegex(ValueError, 'Broken link'):
            check_markdown_links(self.root)


if __name__ == '__main__':
    unittest.main()
