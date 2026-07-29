from rich.console import Console

console = Console()


class Logger:

    @staticmethod
    def info(message):

        console.print(f"[cyan]{message}[/cyan]")


    @staticmethod
    def success(message):

        console.print(f"[green]{message}[/green]")


    @staticmethod
    def warning(message):

        console.print(f"[yellow]{message}[/yellow]")


    @staticmethod
    def error(message):

        console.print(f"[red]{message}[/red]")