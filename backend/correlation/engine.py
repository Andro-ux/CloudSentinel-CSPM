from backend.correlation.graph_builder import GraphBuilder
from backend.correlation.relationship_mapper import RelationshipMapper
from backend.correlation.attack_paths import AttackPathEngine
from backend.correlation.models import CorrelationResult


class CorrelationEngine:

    def __init__(self):

        self.graph_builder = GraphBuilder()

        self.attack_engine = AttackPathEngine()

    def correlate(self, assets):

        self.graph_builder.add_assets(
            assets
        )

        asset_index = self.graph_builder.build()

        mapper = RelationshipMapper(
            asset_index
        )

        relationships = mapper.build()

        attack_paths = self.attack_engine.discover(

            asset_index,

            relationships

        )

        result = CorrelationResult()

        result.relationships = relationships

        result.attack_paths = attack_paths

        return result