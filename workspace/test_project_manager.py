import unittest

from services.project_manager import ProjectManager


class ProjectManagerContractTests(unittest.TestCase):
    def test_current_constructor_and_missing_project_contract(self):
        manager = ProjectManager()
        result = manager.exists("__missing_project_for_contract_test__")
        self.assertTrue(result.success)
        self.assertFalse(result.data)


if __name__ == "__main__":
    unittest.main()
