import unittest

from tools.python_tools import PythonTools


class PythonRunnerContractTests(unittest.TestCase):
    def test_current_constructor_and_missing_file_failure(self):
        result = PythonTools().run_script("workspace/__missing_file__.py")
        self.assertFalse(result.success)


if __name__ == "__main__":
    unittest.main()
