import os
from dotenv import load_dotenv

load_dotenv()

BASE_SITE = "https://vstup.edbo.gov.ua/"
REGISTRY_SITE = "https://registry.edbo.gov.ua/"
OFFERS_URL = "offers/"
UNIV_API_URL = "api/universities/"
UNIV_DATA_API_URL = "api/university/"
OFFERS_UNIVS_URL = "offers-universities/"
OFFERS_LIST_URL = "offers-list/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:103.0) Gecko/20100101 Firefox/103.0",
    "Accept": "*/*",
    "Referer": "https://vstup.edbo.gov.ua/offers",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
}
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_IP_ADDR = os.getenv("DB_IP_ADDR")
DB_AUTH_SOURCE = os.getenv("DB_AUTH_SOURCE")
