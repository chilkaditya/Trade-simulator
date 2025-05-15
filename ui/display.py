# ui/display.py

from rich.console import Console
from rich.table import Table

def display_output(results: dict):
    console = Console()
    table = Table(title="Trade Simulation Output")

    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")

    for k, v in results.items():
        table.add_row(k, f"{v:.6f}")

    console.clear()
    console.print(table)
