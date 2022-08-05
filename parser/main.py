from console import console, Style, Confirm, Table
from parse import parse_for_spec_list
from db import connect_to_db, use_vst, update_specs, update_univs
from reqs import get_all_univ, get_full_univs_data
import json


def main():
    print("\n")

    db = connect_to_db()
    vst = use_vst(db)

    spec_list = parse_for_spec_list()
    if Confirm.ask("Завантажити новий [italic]Spec List[/] в базу даних?", default=False):
        update_specs(vst, spec_list)

    univs = get_all_univ()
    udata = get_full_univs_data(univs)
    update_univs(vst, udata)

    table = Table(title="Uploaded Universities Data")
    table.add_column("#", style="dark_cyan")
    table.add_column("Name", style="magenta")
    table.add_column("Qty. of specs", style="cyan")
    for index, univ in enumerate(udata):
        table.add_row("#"+index, univ["name"], str(len(univ["specs"])))
    console.print(table)


if __name__ == "__main__":
    main()
