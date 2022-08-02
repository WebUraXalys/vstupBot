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
    req = requests.get(url, headers=HEADERS)
    if req.ok:
        return req.text
    else:
        raise Not200Exception(req.status_code)
