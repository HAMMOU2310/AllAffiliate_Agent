from rich.console import Console

from core.task_manager import TaskManager
from core.router import TaskRouter
from core.service_container import ServiceContainer

console = Console()


class MasterAgent:

    def __init__(self):

        self.services = ServiceContainer()
        self.task_manager = TaskManager()
        self.router = TaskRouter(self.services)

    def start(self):

        console.print("[bold green]تم تشغيل Master Agent[/bold green]")

        while True:

            command = input("\nأنت > ").strip()

            if command.lower() in ["exit", "quit"]:
                break

            if not command:
                continue

            task = self.task_manager.create_task(command)

            result = self.router.route(task)

            if result.success:
                console.print(f"[green]{result.message}[/green]")
            else:
                console.print(f"[red]{result.message}[/red]")