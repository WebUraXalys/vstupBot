from bs4 import BeautifulSoup
from reqs import get_offer_page
from exceptions import Not200Exception
from console import console, Table
import requests


def parse_for_spec_list():
    console.print("Пошук списку спеціальностей... ", end="")
    try:
        text = get_offer_page()
    except Not200Exception:
        console.print(f"[black on red]ПОМИЛКА[/]")
    soup = BeautifulSoup(text, "html.parser")
    select = soup.find("select", id="offers-search-speciality")
    options = select.find_all("option")
    spec_list = []
    table = Table(title="Spec List")
    table.add_column("#", style="dark_cyan")  # no_wrap=True
    table.add_column("Code", style="cyan")
    table.add_column("Name", style="magenta")
    for index, option in enumerate(options):
        code = option.get("value", None)
        name = option.text
        if code is not None:
            spec = [code, name]
            spec_list += [spec]
            table.add_row("#"+str(index), code, name)
    console.print(f"[black on green]УСПІШНО[/]")
    console.print(table)
    return spec_list
