from rich.console import Console

from core.app import App
from agents.master_agent import MasterAgent

console = Console()


def main():

    app = App()

    settings = app.get_settings()

    console.print()

    console.print(f"[bold cyan]{settings.get('project_name')}[/bold cyan]")

    console.print(f"الإصدار : v1.0")

    console.print(f"اللغة : {settings.get('language')}")

    console.print()

    master = MasterAgent()

    try:
        master.start()
    finally:
        master.shutdown()


if __name__ == "__main__":

    main()