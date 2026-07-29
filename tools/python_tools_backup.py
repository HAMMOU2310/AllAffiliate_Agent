from pathlib import Path

from tools.terminal_tools import TerminalTools


class PythonTools:

    @staticmethod
    def run(script: str):

        script_path = Path(script)

        return TerminalTools.run(
            ["python", str(script_path)]
        )