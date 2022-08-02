from pymongo import MongoClient
from config import DB_USER, DB_PASSWORD
from console import console, Progress
from time import sleep


def connect_to_db():
    console.print("Підключення до бази даних... ", end="")
    try:
        client = MongoClient("130.61.64.244", username=DB_USER, password=DB_PASSWORD, authSource='admin', authMechanism='SCRAM-SHA-256', tls=True, tlsAllowInvalidCertificates=True)
        console.print(f"[black on green]УСПІШНО[/]")
    except:
        console.print(f"[black on red]ПОМИЛКА[/]")
    return client


def use_vst(client):
    console.print("Пошук бази... ", end="")
    try:
        vst = client["vst"]
        console.print(f"[black on green]УСПІШНО[/]")
    except:
        console.print(f"[black on red]ПОМИЛКА[/]")
    return vst


def get_collection(vst, collection):
    console.print(f"Пошук колекції {collection}... ", end="")
    try:
        col = vst[collection]
        console.print(f"[black on green]УСПІШНО[/]")
    except:
        console.print(f"[black on red]ПОМИЛКА[/]")
    return col


def update_specs(vst, spec_list):
    def _insert():
        with Progress() as prog:
            task = prog.add_task("[light_sea_green]Оновлення...", total=len(spec_list)+3)
            sl = []
            for spec in spec_list:
                spe = {"code": spec[0], "name": spec[1]}
                sl += [spe]
                # specs.insert_one(spe)
                sleep(0.002)
                prog.update(task, advance=1)
            specs.insert_many(sl)
            prog.update(task, advance=3)
    console.print("Оновлення списку спеціальностей... ", end="")
    if "specs" in vst.list_collection_names():
        vst["specs"].drop()
        specs = vst["specs"]
    else:
        specs = vst["specs"]
    console.print(f"[black on blue]ПЕРЕДАНО[/]")
    _insert()
