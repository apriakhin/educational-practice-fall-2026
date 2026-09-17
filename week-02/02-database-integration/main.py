from pprint import pprint

from app.database import get_partners


if __name__ == "__main__":
    pprint(get_partners(), sort_dicts=False)
