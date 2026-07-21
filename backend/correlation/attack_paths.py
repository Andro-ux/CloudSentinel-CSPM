from backend.correlation.path_finder import PathFinder
from backend.graph.blast_radius import BlastRadius
from backend.knowledge.interfaces import IKnowledgeEngine
from backend.correlation.models import AttackPath


class AttackPathEngine:

    def __init__(self):

        self.path_finder = PathFinder()

        self.blast = BlastRadius()

    def discover(
        self,
        knowledge: IKnowledgeEngine,
        entry_points=None
    ):

        if entry_points is None:

            entry_points = self._find_entry_points(
                knowledge
            )

        adjacency = knowledge.get_adjacency()

        paths = []

        for source in entry_points:

            paths.extend(

                self.path_finder.bfs(

                    adjacency,

                    source

                )

            )

        blast_radius = self.blast.calculate(

            paths

        )

        attack_paths = []

        seen = set()

        for path in paths:

            if len(path) < 2:

                continue

            key = tuple(path)

            if key in seen:

                continue

            seen.add(key)

            attack_path = self._classify_path(

                path,

                blast_radius,

                knowledge

            )

            if attack_path:

                attack_paths.append(

                    attack_path

                )

        return attack_paths

    def _find_entry_points(self, knowledge: IKnowledgeEngine):

        internet_assets = self._find_internet_assets(
            knowledge
        )

        public_subnets = self._find_public_subnets(
            knowledge
        )

        return list(

            dict.fromkeys(

                internet_assets + public_subnets

            )

        )

    def _find_internet_assets(self, knowledge: IKnowledgeEngine):

        return [

            asset.id

            for asset in knowledge.find_public_assets()

        ]

    def _find_public_subnets(self, knowledge: IKnowledgeEngine):

        public_subnets = []

        subnet_to_vms = {}

        for rel in knowledge.get_edges():

            if rel.relation == "IN_SUBNET":

                subnet_to_vms.setdefault(
                    rel.target,
                    []
                ).append(rel.source)

        for subnet in knowledge.find_assets(
            resource_type="Subnet"
        ):

            vm_ids = subnet_to_vms.get(
                subnet.id,
                []
            )

            for vm_id in vm_ids:

                vm = knowledge.find_asset(vm_id)

                security = vm.properties.get(
                    "security",
                    {}
                )

                if security.get(
                    "public_ip",
                    False
                ):

                    public_subnets.append(
                        subnet.id
                    )

                    break

        return public_subnets

    def _classify_path(
        self,
        path,
        blast_radius,
        knowledge: IKnowledgeEngine
    ):

        root = path[0]

        root_asset = knowledge.find_asset(root)

        rel_map = self._build_rel_map(
            knowledge.get_edges()
        )

        path_rels = []

        for i in range(len(path) - 1):

            path_rels.append(

                rel_map.get(
                    (
                        path[i],
                        path[i + 1]
                    ),
                    "CONNECTED_TO"
                )

            )

        attack_type = self._determine_attack_type(
            path,
            path_rels,
            root_asset
        )

        title = attack_type["title"]

        description = attack_type["description"]

        severity = attack_type.get(
            "severity",
            "HIGH"
        )

        techniques = attack_type.get(
            "techniques",
            ["T1190"]
        )

        mitigations = attack_type.get(
            "mitigations",
            [
                "Restrict internet-facing exposure",
                "Implement zero-trust network controls"
            ]
        )

        risk_score = min(
            100,
            blast_radius.get(
                root,
                1
            ) * 10
        )

        return AttackPath(
            nodes=path,
            title=title,
            severity=severity,
            risk_score=risk_score,
            description=description,
            graph_paths=[path],
            techniques=techniques,
            mitigations=mitigations
        )

    def _build_rel_map(self, relationships):

        rel_map = {}

        for rel in relationships:

            rel_map[
                (rel.source, rel.target)
            ] = rel.relation

        return rel_map

    def _determine_attack_type(
        self,
        path,
        path_rels,
        root_asset
    ):

        if root_asset.resource_type == "Subnet":

            return {

                "title": "Public Subnet Exposure",

                "description": (
                    f"Subnet '{root_asset.name}' hosts internet-accessible "
                    f"resources. An attacker can reach {len(path)-1} "
                    f"additional resources through this subnet."
                ),

                "severity": "HIGH",

                "techniques": [
                    "T1190",
                    "T1040",
                    "T1552"
                ],

                "mitigations": [
                    "Remove public IPs from resources in this subnet",
                    "Enable VPC Flow Logs for network monitoring",
                    "Restrict subnet CIDR ranges",
                    "Use Private Google Access where appropriate"
                ]

            }

        if root_asset.resource_type == "VPC":

            return {

                "title": "VPC Network Compromise",

                "description": (
                    f"An attacker can reach the VPC '{root_asset.name}' "
                    f"and laterally move to {len(path)-1} resources."
                ),

                "severity": "HIGH",

                "techniques": [
                    "T1190",
                    "T1566",
                    "T1210"
                ],

                "mitigations": [
                    "Harden firewall rules for VPC access",
                    "Implement network segmentation",
                    "Enable VPC Flow Logs"
                ]

            }

        if root_asset.resource_type == "VM":

            if path_rels and path_rels[0] == "IN_SUBNET":

                return {

                    "title": "Internet-to-Subnet Attack Path",

                    "description": (
                        f"An attacker reaching VM '{root_asset.name}' via "
                        f"its public IP can traverse through its subnet "
                        f"to reach {len(path)-1} additional resources."
                    ),

                    "severity": "HIGH",

                    "techniques": [
                        "T1190",
                        "T1552",
                        "T1078"
                    ],

                    "mitigations": [
                        "Remove public IP from the VM",
                        "Place VM behind a bastion host",
                        "Enable OS Login and disable metadata server access"
                    ]

                }

            return {

                "title": "Compromised VM Lateral Movement",

                "description": (
                    f"An attacker reaching VM '{root_asset.name}' can "
                    f"laterally move to {len(path)-1} resources."
                ),

                "severity": "HIGH",

                "techniques": [
                    "T1078",
                    "T1552",
                    "T1003"
                ],

                "mitigations": [
                    "Harden VM access controls",
                    "Enable Shielded VM",
                    "Rotate service account keys regularly"
                ]

            }

        return {

            "title": "Reachable Attack Path",

            "description": (
                f"An attacker reaching {root_asset.name} can laterally "
                f"reach {len(path)-1} additional resources."
            ),

            "severity": "HIGH",

            "techniques": ["T1190"],

            "mitigations": [
                "Review access controls for this resource",
                "Implement least-privilege permissions"
            ]

        }
