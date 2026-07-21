

class KnowledgeEngineError(Exception):

    pass


class AssetNotFound(KnowledgeEngineError):

    def __init__(self, asset_id: str):

        self.asset_id = asset_id

        super().__init__(
            f"Asset not found: {asset_id}"
        )


class GraphNotInitialized(KnowledgeEngineError):

    def __init__(self):

        super().__init__(
            "Knowledge Engine has not been initialized with a graph"
        )


class InvalidRelationship(KnowledgeEngineError):

    def __init__(self, source: str, target: str, relation: str):

        self.source = source

        self.target = target

        self.relation = relation

        super().__init__(
            f"Invalid relationship: {source} --({relation})--> {target}"
        )
