from backend.correlation.graph_builder import GraphBuilder
from backend.correlation.relationship_mapper import RelationshipMapper
from backend.correlation.attack_paths import AttackPathEngine
from backend.executive.engine import ExecutiveEngine
from backend.facts.engine import FactEngine
from backend.facts.extractors.compute import ComputeFactsExtractor
from backend.facts.extractors.iam import IAMFactsExtractor
from backend.facts.extractors.logging import LoggingFactsExtractor
from backend.facts.extractors.network import NetworkFactsExtractor
from backend.facts.extractors.storage import StorageFactsExtractor
from backend.facts.registry import FactRegistry
from backend.knowledge.engine import KnowledgeEngine
from backend.risk.engine import RiskEngine
from backend.rules.engine import RuleEngine
from backend.rules.rules.admin_service_account import AdminServiceAccountRule
from backend.rules.rules.audit_logs import AuditLoggingRule
from backend.rules.rules.flow_logs import FlowLogsRule
from backend.rules.rules.metadata_service import MetadataServiceRule
from backend.rules.rules.open_firewall import OpenFirewallRule
from backend.rules.rules.public_bucket import PublicBucketRule
from backend.rules.rules.public_vm import PublicVMRule
from backend.rules.rules.shielded_vm import ShieldedVMRule
from backend.rules.rules.unused_service_account import UnusedServiceAccountRule
from backend.rules.registry import RuleRegistry
from backend.correlation.models import CorrelationResult


class CorrelationEngine:

    def __init__(self):

        self.graph_builder = GraphBuilder()

        self.attack_engine = AttackPathEngine()

        self.executive_engine = ExecutiveEngine()

    def correlate(self, assets):

        self.graph_builder.add_assets(
            assets
        )

        relationships = RelationshipMapper().map(
            self.graph_builder.index
        )

        graph = self.graph_builder.build(
            relationships
        )

        knowledge = KnowledgeEngine(graph)

        fact_registry = FactRegistry()

        fact_registry.register(NetworkFactsExtractor())

        fact_registry.register(ComputeFactsExtractor())

        fact_registry.register(StorageFactsExtractor())

        fact_registry.register(IAMFactsExtractor())

        fact_registry.register(LoggingFactsExtractor())

        fact_engine = FactEngine(knowledge, fact_registry)

        fact_set = fact_engine.extract()

        rule_registry = RuleRegistry()

        rule_registry.register(PublicVMRule())

        rule_registry.register(PublicBucketRule())

        rule_registry.register(OpenFirewallRule())

        rule_registry.register(ShieldedVMRule())

        rule_registry.register(MetadataServiceRule())

        rule_registry.register(AdminServiceAccountRule())

        rule_registry.register(UnusedServiceAccountRule())

        rule_registry.register(FlowLogsRule())

        rule_registry.register(AuditLoggingRule())

        rule_engine = RuleEngine(rule_registry)

        finding_set = rule_engine.evaluate(fact_set)

        attack_paths = self.attack_engine.discover(
            knowledge
        )

        public_assets = knowledge.find_public_assets()

        context = {

            "attack_paths": attack_paths,

            "public_assets": public_assets,

        }

        risk_engine = RiskEngine()

        risk_set = risk_engine.evaluate(
            finding_set,
            context=context,
        )

        dashboard = self.executive_engine.build_dashboard(
            knowledge=knowledge,
            fact_set=fact_set,
            finding_set=finding_set,
            risk_set=risk_set,
            assets=assets,
        )

        result = CorrelationResult()

        result.relationships = graph.edges

        result.attack_paths = attack_paths

        result.fact_set = fact_set

        result.finding_set = finding_set

        result.risk_set = risk_set

        result.dashboard = dashboard

        return result
