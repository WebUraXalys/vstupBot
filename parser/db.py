from pymongo import MongoClient
from config import DB_USER, DB_PASSWORD
from console import console


def connect_to_db():
    console.print("\nПідключення до бази даних... ", end="")
    try:
        client = MongoClient("130.61.64.244", username=DB_USER, password=DB_PASSWORD, authSource='admin', authMechanism='SCRAM-SHA-256', tls=True, tlsAllowInvalidCertificates=True)
        console.print(f"[black on green]УСПІШНО[/]")
    except:
        console.print(f"[black on red]ПОМИЛКА[/]")
    return client
