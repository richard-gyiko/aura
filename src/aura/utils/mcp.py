from typing import List
from autogen_ext_mcp.tools import MCPToolAdapter
from rich.console import Console


def print_tools(tools: List[MCPToolAdapter]) -> None:
    console = Console()
    console.print("\n[bold blue]📦 Loaded MCP Tools:[/bold blue]")

    for tool in tools:
        console.print(f"\n[bold green]🔧 {tool.schema['name']}[/bold green]")
        if "description" in tool.schema:
            console.print(f"[italic]{tool.schema['description']}[/italic]")

        if "parameters" in tool.schema:
            console.print("\n[yellow]Parameters:[/yellow]")
            params = tool.schema["parameters"]
            if "properties" in params:
                for prop_name, prop_details in params["properties"].items():
                    required = prop_name in params.get("required", [])
                    required_mark = "[red]*[/red]" if required else ""
                    console.print(
                        f"  • [cyan]{prop_name}{required_mark}[/cyan]: {prop_details.get('type', 'any')}"
                    )
                    if "description" in prop_details:
                        console.print(f"    [dim]{prop_details['description']}[/dim]")

        console.print("─" * 50)
