from console import console, Style
from reqs import get_offer_page
from db import connect_to_db


db = connect_to_db()
get_offer_page()


if __name__ == "__main__":
    pass
