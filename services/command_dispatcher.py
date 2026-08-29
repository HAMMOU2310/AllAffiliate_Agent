from core.result import Result


class CommandDispatcher:

    def __init__(self, services):

        self.code_writer = services.get("code_writer")
        self.python_runner = services.get("python_runner")
        self.file_tools = services.get("file_tools")
        self.text_editor = services.get("text_editor")
        self.project_manager = services.get("project_manager")

    # -----------------------------
    # Create File
    # -----------------------------

    def create(self, filename):

        return self.code_writer.create_file(
            f"workspace/{filename}",
            "",
        )

    # -----------------------------
    # Run File
    # -----------------------------

    def run(self, filename):

        return self.python_runner.run_file(
            f"workspace/{filename}",
        )

    # -----------------------------
    # Read File
    # -----------------------------

    def read(self, filename):

        return self.file_tools.read_file(
            f"workspace/{filename}",
        )

    # -----------------------------
    # Delete File
    # -----------------------------

    def delete(self, filename):

        return self.file_tools.delete_file(
            f"workspace/{filename}",
        )

    # -----------------------------
    # List Files
    # -----------------------------

    def list(self):

        return self.file_tools.list_files()

    # -----------------------------
    # Write File
    # -----------------------------

    def write(self, filename, content):

        return self.text_editor.write(
            f"workspace/{filename}",
            content,
        )

    # -----------------------------
    # Append File
    # -----------------------------

    def append(self, filename, content):

        return self.text_editor.append(
            f"workspace/{filename}",
            content,
        )

    # -----------------------------
    # Create Project
    # -----------------------------

    def create_project(self, project_name):

        return self.project_manager.create_project(
            project_name,
        )

    # -----------------------------
    # List Projects
    # -----------------------------

    def list_projects(self):

        return self.project_manager.list_projects()