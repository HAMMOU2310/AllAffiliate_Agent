from rich.console import Console

from core.app import App
from agents.master_agent import MasterAgent

console = Console()


def main():

    app = App()

    settings = app.get_settings()

    console.print()

    console.print(f"[bold cyan]{settings.get('project_name')}[/bold cyan]")

    console.print(f"الإصدار : 0.1")

    console.print(f"اللغة : {settings.get('language')}")

    console.print()

    master = MasterAgent()

    master.start()


if __name__ == "__main__":

    main()