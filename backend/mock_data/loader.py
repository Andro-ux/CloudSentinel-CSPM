import json
from pathlib import Path


BASE_DIR = Path(__file__).parent


def load(name):

    path = BASE_DIR / f"{name}.json"

    with open(path, encoding="utf-8") as file:

        return json.load(file)