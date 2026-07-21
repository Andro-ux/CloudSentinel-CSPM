from dataclasses import asdict


class FindingSerializer:

    @staticmethod
    def serialize(finding):

        return asdict(finding)