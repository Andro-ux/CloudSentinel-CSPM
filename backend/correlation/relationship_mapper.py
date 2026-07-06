from backend.correlation.models import Relationship

from backend.correlation.mappers.compute_mapper import ComputeMapper


class RelationshipMapper:

    def __init__(self, asset_index):

        self.asset_index = asset_index

        self.relationships = []

        self.mappers = [

            ComputeMapper(),

        ]

    def build(self):

        for mapper in self.mappers:

            self.relationships.extend(

                mapper.map(self.asset_index)

            )

        return self.relationships