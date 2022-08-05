from console import console, Style, Confirm
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


if __name__ == "__main__":
    main()
