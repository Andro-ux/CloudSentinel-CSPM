from backend.correlation.builders.relationship_builder import RelationshipBuilder

from backend.correlation.mappers.compute_mapper import ComputeMapper
from backend.correlation.mappers.iam_mapper import IAMMapper
from backend.correlation.mappers.network_mapper import NetworkMapper
from backend.correlation.mappers.storage_mapper import StorageMapper


class RelationshipMapper:

    def map(self, asset_index):

        builder = RelationshipBuilder()

        ComputeMapper().map(
            asset_index,
            builder
        )

        IAMMapper().map(
            asset_index,
            builder
        )

        NetworkMapper().map(
            asset_index,
            builder
        )

        StorageMapper().map(
            asset_index,
            builder
        )

        return builder.build()