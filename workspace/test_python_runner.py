import unittest

from services.python_runner import PythonRunner


class PythonRunnerContractTests(unittest.TestCase):
    def test_current_constructor_and_missing_file_failure(self):
        result = PythonRunner().run_file("workspace/__missing_file__.py")
        self.assertFalse(result.success)


if __name__ == "__main__":
    unittest.main()
