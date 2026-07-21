# Rule Engine

The Rule Engine evaluates immutable security facts and produces immutable findings. It is the reasoning layer of CloudSentinel, sitting between the Fact Engine and downstream consumers.

## Architecture

```
Infrastructure
      ↓
Knowledge (Graph + Queries)
      ↓
Facts (Immutable Security Truths)
      ↓
Rules (Security Reasoning)
      ↓
Findings (Immutable Results)
      ↓
Risk / Executive Intelligence
```

## Responsibilities

- Receive a `FactSet`
- Execute registered rules
- Return an immutable `FindingSet`
- **Never** calculate risk
- **Never** generate reports
- **Never** modify facts

## Finding Model

Findings are immutable `@dataclass(frozen=True)` objects with the following fields:

| Field | Type | Description |
|-------|------|-------------|
| `id` | `str` | Unique finding identifier |
| `rule_id` | `str` | Stable rule identifier (e.g., `CS-RULE-001`) |
| `title` | `str` | Short finding title |
| `description` | `str` | Detailed description |
| `severity` | `Severity` | CRITICAL, HIGH, MEDIUM, LOW, INFO |
| `category` | `str` | Network, Compute, Storage, IAM, Logging |
| `asset_ids` | `List[str]` | Affected asset IDs |
| `facts` | `List[Fact]` | Supporting facts |
| `recommendation` | `str` | Remediation guidance |
| `references` | `List[str]` | External references |
| `evidence` | `Dict[str, Any]` | Structured evidence |
| `service` | `str` | Cloud service (for backward compatibility) |
| `resource_id` | `str` | Resource ID (for backward compatibility) |
| `risk_score` | `int` | Risk score (default 0, calculated by Risk Engine) |

### Severity Enum

```python
class Severity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"
```

### Rule Metadata

Every rule exposes metadata:

```python
@dataclass(frozen=True)
class RuleMetadata:
    rule_id: str      # e.g., "CS-RULE-001"
    name: str         # Human-readable name
    description: str  # What the rule detects
    version: str      # Semantic version
    author: str       # "CloudSentinel Core"
```

## FindingSet

`FindingSet` is a lightweight, read-only container with:

- Iteration over all findings
- `find_by_id(finding_id)` — O(1) lookup
- `find_by_severity(severity)` — O(1) lookup
- `find_by_asset(asset_id)` — O(1) lookup
- `find_by_rule(rule_id)` — O(1) lookup
- `statistics()` — counts by severity, rule, and asset
- `to_dicts()` — convert to list of dicts for JSON serialization
- `contains(finding)` — membership test

## Rule Registry

The `RuleRegistry` automatically discovers and executes rules:

1. **Registration** — Rules are registered with the registry
2. **Execution** — All rules run in sequence
3. **Merging** — Results are merged into a single list
4. **Duplicate prevention** — Findings with duplicate IDs are skipped
5. **Isolation** — One failing rule does not stop the pipeline; `RuleExecutionError` is raised

## Rules

Each rule implements `IRule`:

```python
class IRule(ABC):
    @property
    @abstractmethod
    def metadata(self) -> RuleMetadata:
        pass

    @abstractmethod
    def evaluate(self, fact_set: FactSet) -> List[Finding]:
        pass
```

### Production Rules

| Rule ID | Name | Severity | Condition |
|---------|------|----------|-----------|
| CS-RULE-001 | Public VM Detected | HIGH | `PUBLIC_VM` |
| CS-RULE-002 | Public Unencrypted Bucket | CRITICAL | `PUBLIC_BUCKET` + `UNENCRYPTED_BUCKET` |
| CS-RULE-003 | Open Firewall Detected | HIGH | `OPEN_FIREWALL` |
| CS-RULE-004 | Shielded VM Disabled | MEDIUM | `SHIELDED_VM_DISABLED` |
| CS-RULE-005 | Metadata Service Access Enabled | MEDIUM | `METADATA_SERVICE_ENABLED` |
| CS-RULE-006 | Admin Service Account Detected | HIGH | `ADMIN_SERVICE_ACCOUNT` |
| CS-RULE-007 | Unused Service Account | LOW | `UNUSED_SERVICE_ACCOUNT` |
| CS-RULE-008 | VPC Flow Logs Disabled | MEDIUM | `FLOW_LOGS_DISABLED` |
| CS-RULE-009 | Audit Logging Disabled | HIGH | `AUDIT_LOGGING_DISABLED` |

## Lifecycle

```
GraphBuilder
    ↓ build Graph
KnowledgeEngine
    ↓ initialize caches
FactRegistry
    ↓ execute extractors
FactEngine
    ↓ produce immutable facts
FactSet
    ↓ input to rules
RuleRegistry
    ↓ execute rules
RuleEngine
    ↓ produce immutable findings
FindingSet
    ↓ available to Risk Engine / Executive Intelligence
```

## Usage

```python
from backend.rules.engine import RuleEngine
from backend.rules.registry import RuleRegistry
from backend.rules.rules.public_vm import PublicVMRule
from backend.rules.rules.public_bucket import PublicBucketRule

registry = RuleRegistry()
registry.register(PublicVMRule())
registry.register(PublicBucketRule())

rule_engine = RuleEngine(registry)
finding_set = rule_engine.evaluate(fact_set)

# Query findings
high_findings = finding_set.find_by_severity(Severity.HIGH)
vm_findings = finding_set.find_by_asset("vm-frontend")
stats = finding_set.statistics()

# Convert to dicts for JSON
finding_dicts = finding_set.to_dicts()
```

## Rule Authoring Guide

To create a new rule:

1. Create a new file in `backend/rules/rules/`
2. Extend `BaseRule`
3. Provide `RuleMetadata` with a stable `rule_id` (e.g., `CS-RULE-010`)
4. Implement `evaluate(self, fact_set: FactSet) -> List[Finding]`
5. Use `self._make_finding()` helper for consistent creation
6. Register the rule in `CorrelationEngine.correlate()`
7. Add tests

### Example Rule

```python
from typing import List
from backend.facts.models import Fact, FactSet, FactType
from backend.rules.base import BaseRule
from backend.rules.models import Finding, RuleMetadata, Severity

class MyRule(BaseRule):
    def __init__(self):
        super().__init__(
            RuleMetadata(
                rule_id="CS-RULE-010",
                name="My New Rule",
                description="Detects something important.",
                version="1.0.0",
                author="CloudSentinel Core",
            )
        )

    def evaluate(self, fact_set: FactSet) -> List[Finding]:
        findings = []
        for fact in fact_set.find_by_type(FactType.MY_FACT_TYPE):
            findings.append(
                self._make_finding(
                    rule_id=self.metadata.rule_id,
                    title="My Finding",
                    description="Description here.",
                    severity=Severity.HIGH,
                    category="Network",
                    asset_ids=[fact.asset_id],
                    facts=[fact],
                    recommendation="Fix it.",
                    references=["https://example.com"],
                    evidence={"key": "value"},
                    service="Compute",
                    resource_id=fact.asset_id,
                )
            )
        return findings
```

## Performance

- Rule execution: O(R × F) where R is rules and F is facts
- Finding lookup by asset: O(1)
- Finding lookup by severity: O(1)
- Finding lookup by rule: O(1)
- Duplicate prevention: O(F) where F is total findings

## Extension Guide

| To Add | Action |
|--------|--------|
| New severity | Add to `Severity` enum |
| New rule | Create file in `backend/rules/rules/`, extend `BaseRule` |
| New rule ID | Use `CS-RULE-XXX` format, never reuse old IDs |
| New category | Add string constant, update rule |
| New fact type | Add to `FactType` in `backend/facts/models.py` first |
