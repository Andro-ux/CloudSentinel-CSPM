from collections import defaultdict

from backend.correlation.models import AssetNode


class AssetIndex:

    def __init__(self):

        self.assets = {}

        self.by_service = defaultdict(list)

        self.by_type = defaultdict(list)

    def add(self, asset: AssetNode):

        self.assets[asset.id] = asset

        self.by_service[asset.service].append(asset)

        self.by_type[asset.resource_type].append(asset)

    def get(self, asset_id):

        return self.assets.get(asset_id)

    def get_by_service(self, service):

        return self.by_service.get(service, [])

    def get_by_type(self, resource_type):

        return self.by_type.get(resource_type, [])

    def all_assets(self):

        return list(self.assets.values())