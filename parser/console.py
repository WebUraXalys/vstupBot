from rich.console import Console
from rich.style import Style
from rich.theme import Theme

success = Style.parse("black on green")

console = Console(theme=Theme({"repr.number": ""}))
