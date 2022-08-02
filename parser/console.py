from rich.console import Console
from rich.style import Style
from rich.theme import Theme
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.live import Live
from rich.progress import Progress

success = Style.parse("black on green")

console = Console(theme=Theme({"repr.number": ""}))
