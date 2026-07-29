from services.base_service import BaseService
from tools.file_tools import FileTools
from tools.python_tools import PythonTools
from tools.terminal_tools import TerminalTools


service = BaseService(
    file_tools=FileTools(),
    terminal_tools=TerminalTools(),
    python_tools=PythonTools(),
)

print(type(service.file_tools).__name__)
print(type(service.terminal_tools).__name__)
print(type(service.python_tools).__name__)