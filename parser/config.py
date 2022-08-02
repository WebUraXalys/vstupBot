import os
from dotenv import load_dotenv

load_dotenv()

BASE_SITE = "https://vstup.edbo.gov.ua/"
OFFERS_URL = "offers/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:103.0) Gecko/20100101 Firefox/103.0",
    "Accept": "*/*"
}
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
