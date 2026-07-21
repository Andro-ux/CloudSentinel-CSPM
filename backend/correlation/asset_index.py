from collections import defaultdict

from backend.correlation.models import AssetNode


class AssetIndex:

    def __init__(self):

        self.assets = {}

        self.by_service = defaultdict(list)

        self.by_type = defaultdict(list)

        self.by_name = {}

        self.by_service_and_name = {}

        self.by_type_and_name = {}

    def add(self, asset: AssetNode):

        if asset.id in self.assets:
            return

        self.assets[asset.id] = asset

        self.by_service[asset.service].append(asset)

        self.by_type[asset.resource_type].append(asset)

        self.by_name[asset.name.lower()] = asset

        self.by_service_and_name[
            (
                asset.service.lower(),
                asset.name.lower(),
            )
        ] = asset

        self.by_type_and_name[
            (
                asset.resource_type.lower(),
                asset.name.lower(),
            )
        ] = asset

    def get(self, asset_id: str):

        return self.assets.get(asset_id)

    def get_by_service(self, service: str):

        return list(
            self.by_service.get(service, [])
        )

    def get_by_type(self, resource_type: str):

        return list(
            self.by_type.get(resource_type, [])
        )

    def find_by_name(self, name: str):

        return self.by_name.get(
            name.lower()
        )

    def find_by_service_and_name(
        self,
        service: str,
        name: str,
    ):

        return self.by_service_and_name.get(
            (
                service.lower(),
                name.lower(),
            )
        )

    def find_by_type_and_name(
        self,
        resource_type: str,
        name: str,
    ):

        return self.by_type_and_name.get(
            (
                resource_type.lower(),
                name.lower(),
            )
        )

    def exists(self, asset_id: str):

        return asset_id in self.assets

    def find_by_type(self, resource_type: str):
        return self.get_by_type(resource_type)

    def find_by_service(self, service: str):
        return self.get_by_service(service)

    def find_by_resource_id(self, asset_id: str):
        return self.get(asset_id)

    def get_neighbors(self, asset_id: str, relationships: list) -> list:
        neighbors = []
        for rel in relationships:
            if rel.source == asset_id:
                neighbor = self.get(rel.target)
                if neighbor:
                    neighbors.append(neighbor)
            elif rel.target == asset_id:
                neighbor = self.get(rel.source)
                if neighbor:
                    neighbors.append(neighbor)
        return neighbors


    def all_assets(self):

        return list(
            self.assets.values()
        )

    def __iter__(self):

        return iter(
            self.assets.values()
        )

    def __len__(self):

        return len(
            self.assets
        )