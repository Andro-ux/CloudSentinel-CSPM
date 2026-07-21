from backend.correlation.models import Relationship


class RelationshipBuilder:

    def __init__(self):

        self.relationships = []
        self.index = set()

    def connect(
        self,
        source,
        target,
        relation,
        provider="",
        confidence=1.0,
        metadata=None,
        evidence=None,
    ):

        if not source or not target:

            return

        if source == target:

            return

        relation = relation.upper().strip()

        key = (
            source,
            target,
            relation
        )

        if key in self.index:

            return

        self.index.add(key)

        self.relationships.append(

            Relationship(

                source=source,

                target=target,

                relation=relation,

                provider=provider,

                confidence=confidence,

                metadata=metadata or {},

                evidence=evidence or {},

            )

        )

    def build(self):

        return self.relationships