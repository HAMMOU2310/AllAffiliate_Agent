import tempfile
import unittest
from pathlib import Path

from services.code_writer import CodeWriter


class CodeWriterContractTests(unittest.TestCase):
    def test_current_constructor_and_file_contract(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "example.py"
            writer = CodeWriter()
            created = writer.create_file(str(path), "print('ok')\n")
            self.assertTrue(created.success)
            self.assertEqual(path.read_text(encoding="utf-8"), "print('ok')\n")


if __name__ == "__main__":
    unittest.main()
