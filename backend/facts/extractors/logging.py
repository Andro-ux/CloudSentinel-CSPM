from typing import List

from backend.facts.extractors.base import BaseExtractor
from backend.facts.models import Evidence, Fact, FactType
from backend.knowledge.interfaces import IKnowledgeEngine


class LoggingFactsExtractor(BaseExtractor):

    @property
    def fact_types(self) -> List[FactType]:

        return [

            FactType.AUDIT_LOGGING_DISABLED,

            FactType.FLOW_LOGS_DISABLED,

        ]

    def extract(self, knowledge: IKnowledgeEngine) -> List[Fact]:

        facts: List[Fact] = []

        audit_logging_enabled = False

        for asset in knowledge.find_assets():

            if asset.service.lower() in ("cloudtrail", "audit", "logging"):

                audit_logging_enabled = True

                break

        if not audit_logging_enabled:

            facts.append(

                Fact(

                    id="global-AUDIT_LOGGING_DISABLED-project",

                    asset_id="project-acme",

                    fact_type=FactType.AUDIT_LOGGING_DISABLED,

                    severity="MEDIUM",

                    provider="gcp",

                    category="Logging",

                    evidence=self._make_evidence(
                        provider="gcp",
                        source="knowledge_engine",
                        attribute="audit_logs",
                        value=False,
                    ),

                    description=(
                        "No audit logging configuration detected for the project. "
                        "Cloud Audit Logs should be enabled for all critical services."
                    ),

                )

            )

        for subnet in knowledge.find_assets(resource_type="Subnet"):

            flow_logs = subnet.properties.get("flow_logs", False)

            if not flow_logs:

                facts.append(

                    Fact(

                        id=self._fact_id(
                            subnet.properties.get("cloud", "unknown"),
                            FactType.FLOW_LOGS_DISABLED,
                            subnet.id,
                        ),

                        asset_id=subnet.id,

                        fact_type=FactType.FLOW_LOGS_DISABLED,

                        severity="MEDIUM",

                        provider=subnet.properties.get("cloud", "unknown"),

                        category="Logging",

                        evidence=self._make_evidence(
                            provider=subnet.properties.get("cloud", "unknown"),
                            source="asset.properties",
                            attribute="flow_logs",
                            value=False,
                        ),

                        description=(
                            f"Subnet '{subnet.name}' does not have VPC Flow "
                            f"Logs enabled, limiting network visibility and "
                            f"incident response capabilities."
                        ),

                    )

                )

        return facts
