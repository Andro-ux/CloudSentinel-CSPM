from backend.correlation.models import AttackPath
from backend.correlation.detectors.base_detector import BaseDetector


class PublicVMDetector(BaseDetector):

    def detect(
        self,
        asset_index,
        relationships
    ):

        attack_paths = []

        compute_assets = asset_index.get_by_service(
            "Compute"
        )

        for vm in compute_assets:

            security = vm.properties.get(
                "security",
                {}
            )

            if not security.get(
                "public_ip",
                False
            ):
                continue

            attack_paths.append(

                AttackPath(

                    nodes=[

                        vm.id

                    ],

                    title="Public Compute Instance",

                    severity="HIGH",

                    risk_score=75,

                    description=(
                        f"Virtual machine "
                        f"'{vm.name}' "
                        "has a public IP address "
                        "and may be directly "
                        "reachable from the Internet."
                    )

                )

            )

        return attack_paths