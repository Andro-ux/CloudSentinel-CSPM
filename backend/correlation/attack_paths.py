from backend.correlation.detectors.public_vm_detector import (
    PublicVMDetector,
)


class AttackPathEngine:

    def __init__(self):

        self.detectors = [

            PublicVMDetector(),

        ]

    def discover(

        self,

        asset_index,

        relationships

    ):

        attack_paths = []

        for detector in self.detectors:

            attack_paths.extend(

                detector.detect(

                    asset_index,

                    relationships

                )

            )

        return attack_paths