import requests
from config import BASE_SITE, OFFERS_URL, HEADERS
from console import console
from exceptions import Not200Exception


def get_offer_page() -> str:
    """
    Завантажує сторінку конкурсних пропозицій, повертає текст сторінки в випадку успіху.
    Викликає Not200Exception якщо не вдалось получити доступ
    """
    url = BASE_SITE + OFFERS_URL
    console.print("Завантаження головної сторіник конкурсних пропозицій... ", end="")
    req = requests.get(url, headers=HEADERS)
    if req.ok:
        console.print(f"[black on green]УСПІШНО[/]")
        return req.text
    else:
        console.print(f"[black on red]НЕ 200[/] \n(Неможливо получити доступ до {url})")
        raise Not200Exception(req.status_code)
