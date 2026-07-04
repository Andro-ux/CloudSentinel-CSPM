from typing import List
from backend.models.asset import Asset


class InventoryService:

    def __init__(self):
        self.assets = []

    def ingest(self, assets: List[Asset]):

        self.assets.extend(assets)

    def get_all(self):

        return self.assets

    def count(self):

        return len(self.assets)

    def clear(self):

        self.assets.clear()


inventory_service = InventoryService()