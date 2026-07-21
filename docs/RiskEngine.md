# Risk Engine

The Risk Engine consumes `FindingSet` objects and produces immutable `RiskSet` objects. It is the prioritization layer of CloudSentinel, sitting between the Rule Engine and Executive Intelligence.

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
Risk Engine (Prioritization)
      ↓
RiskSet (Immutable Risks)
      ↓
Executive Intelligence
```

## Responsibilities

- Receive a `FindingSet`
- Optionally query `KnowledgeEngine` and `AttackPathEngine` for context
- Apply scoring strategy
- Return an immutable `RiskSet`
- **Never** create findings or facts
- **Never** generate reports

## Risk Model

Risks are immutable `@dataclass(frozen=True)` objects with the following fields:

| Field | Type | Description |
|-------|------|-------------|
| `id` | `str` | Unique risk identifier |
| `finding_id` | `str` | Source finding ID |
| `asset_ids` | `List[str]` | Affected asset IDs |
| `score` | `int` | Risk score (0-100) |
| `priority` | `Priority` | CRITICAL, HIGH, MEDIUM, LOW |
| `category` | `str` | Finding category |
| `severity` | `str` | Original finding severity |
| `explanation` | `str` | Human-readable explanation |
| `contributing_factors` | `List[str]` | Structured factors contributing to score |
| `recommendation` | `str` | Remediation guidance |
| `metadata` | `Dict[str, Any]` | Additional context including weights used |

### Priority Enum

Priority is derived from score, not copied from severity:

```python
class Priority(str, Enum):
    CRITICAL = "CRITICAL"  # score >= 80
    HIGH = "HIGH"          # score >= 60
    MEDIUM = "MEDIUM"      # score >= 40
    LOW = "LOW"            # score < 40
```

## RiskSet

`RiskSet` is a lightweight, read-only container with:

- Iteration over all risks
- `find_by_id(risk_id)` — O(1) lookup
- `find_by_priority(priority)` — O(1) lookup
- `find_by_category(category)` — O(1) lookup
- `find_by_asset(asset_id)` — O(1) lookup
- `top_n(n)` — get top N risks by score
- `statistics()` — counts by priority, category, and asset
- `to_dicts()` — convert to list of dicts for JSON serialization
- `contains(risk)` — membership test

## Scoring Strategy

The Risk Engine uses a strategy pattern for scoring. The default strategy is `WeightedScoreStrategy`.

### WeightedScoreStrategy

Inputs:
- Finding severity
- Number of affected assets
- Number of supporting facts
- Attack path presence
- Public exposure
- Identity-related findings

Outputs:
- `score` (0-100)
- `explanation`
- `contributing_factors`

### Configurable Weights

Weights are defined in a `ScoreWeights` dataclass:

```python
@dataclass(frozen=True)
class ScoreWeights:
    severity_critical: int = 30
    severity_high: int = 20
    severity_medium: int = 10
    severity_low: int = 5
    multiple_assets: int = 10
    supporting_facts: int = 5
    attack_path_presence: int = 20
    public_exposure: int = 15
    identity_related: int = 10
```

Weights are configurable at initialization:

```python
from backend.risk.strategies.weighted import WeightedScoreStrategy, ScoreWeights

custom_weights = ScoreWeights(
    severity_critical=40,
    public_exposure=25,
)
strategy = WeightedScoreStrategy(custom_weights)
```

## Explainability

Every `Risk` carries structured contributing factors that can be rendered directly in the UI and reused by the AI Copilot:

```python
risk = risk_set.find_by_id("risk-CS-RULE-001-vm-frontend")
print(risk.explanation)
# "Finding 'Public VM Detected' received a risk score of 55/100 with priority MEDIUM. Contributing factors: High severity, Publicly exposed asset, Reachable via attack path."

print(risk.contributing_factors)
# ["High severity", "Publicly exposed asset", "Reachable via attack path"]
```

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
    ↓ input to risk engine
RiskEngine
    ↓ apply scoring strategy
RiskSet
    ↓ available to Executive Intelligence
```

## Usage

```python
from backend.risk.engine import RiskEngine
from backend.risk.strategies.weighted import WeightedScoreStrategy, ScoreWeights

strategy = WeightedScoreStrategy()
engine = RiskEngine(strategy)

context = {
    "attack_paths": attack_paths,
    "public_assets": public_assets,
}

risk_set = engine.evaluate(finding_set, context=context)

# Query risks
critical_risks = risk_set.find_by_priority(Priority.CRITICAL)
top5 = risk_set.top_n(5)
stats = risk_set.statistics()

# Convert to dicts for JSON
risk_dicts = risk_set.to_dicts()
```

## Extension Guide

### Adding a New Scoring Factor

1. Add a new weight field to `ScoreWeights` in `backend/risk/strategies/weighted.py`
2. Add scoring logic in `WeightedScoreStrategy.score()`
3. Add a contributing factor string
4. Update tests

### Adding a New Strategy

1. Implement `IScoreStrategy` in `backend/risk/strategies/`
2. Register the strategy in `CorrelationEngine` or pass to `RiskEngine`
3. Add tests

### Tuning Weights

Modify `ScoreWeights` defaults or create custom instances:

```python
conservative = ScoreWeights(
    severity_critical=40,
    public_exposure=25,
    attack_path_presence=25,
)
```

## Performance

- Risk scoring: O(F × C) where F is findings and C is context size
- Risk lookup by asset: O(1)
- Risk lookup by priority: O(1)
- Risk lookup by category: O(1)
- Top N: O(R log R) where R is risks

## Future Business Context Hooks

The `Risk.metadata` field reserves space for future business context:

```python
Risk(
    ...
    metadata={
        "rule_id": "CS-RULE-001",
        "finding_title": "Public VM Detected",
        "weights": {...},
        "business_criticality": "HIGH",  # Future
        "asset_tier": "production",      # Future
        "compliance_frameworks": ["PCI-DSS", "HIPAA"],  # Future
    },
)
```
