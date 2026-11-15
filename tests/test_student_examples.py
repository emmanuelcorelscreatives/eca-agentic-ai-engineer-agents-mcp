from pathlib import Path
import subprocess
import sys
import unittest


class StudentExampleEntryTests(unittest.TestCase):
    def test_browser_mcp_help_needs_no_optional_sdk_or_browser(self):
        root = Path(__file__).resolve().parents[1]
        result = subprocess.run(
            [sys.executable, '-m', 'examples.s19.mcp_client_demo', '--help'],
            cwd=root, capture_output=True, text=True, timeout=10,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('owned synthetic browser fixture', result.stdout)
        self.assertNotIn('Traceback', result.stderr)


if __name__ == '__main__':
    unittest.main()
