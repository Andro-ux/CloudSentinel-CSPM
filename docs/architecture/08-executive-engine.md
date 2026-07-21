# Executive Intelligence Engine

## Purpose

The Executive Intelligence Engine is the final backend intelligence layer in the CloudSentinel pipeline. It consumes outputs from the Knowledge Engine, Fact Engine, Rule Engine, and Risk Engine, and synthesizes them into executive-ready security intelligence.

It does **not** perform cloud scanning, graph construction, fact extraction, rule evaluation, or risk scoring.

## Architecture

```
Knowledge Engine
       ↓
Fact Engine
       ↓
Rule Engine
       ↓
Risk Engine
       ↓
Executive Intelligence Engine
```

The Executive Engine receives:
- `KnowledgeEngine` instance
- `FactSet`
- `FindingSet`
- `RiskSet`
- `assets`

And produces:
- `ExecutiveDashboard`

## Package Structure

```
backend/executive/
├── __init__.py
├── engine.py
├── interfaces.py
├── exceptions.py
├── models.py
├── builders.py
├── insights.py
├── recommendations.py
├── narrative.py
├── metrics.py
└── strategies/
    ├── __init__.py
    ├── weighted_score.py
    └── narrative.py
```

## Builders

Each builder creates exactly one domain object (Single Responsibility Principle).

### DashboardBuilder
Produces `ExecutiveDashboard` from summary, score, dimensions, breakdown, metrics, risks, recommendations, insights, and narrative.

### MetricsBuilder
Produces `ExecutiveMetrics` from assets, findings, risks, facts, and attack paths.

### InsightBuilder
Produces `List[Insight]` from risks, findings, and facts.

### RecommendationBuilder
Produces `List[Recommendation]` from risks, findings, and facts. Recommendations are ranked by expected score improvement.

### NarrativeBuilder
Produces `ExecutiveNarrative` from `ExecutiveDashboard` or `ExecutiveSummary` using a strategy.

## Security Score

Security score generation is implemented as a **strategy** (`IScoreStrategy`). The default implementation is `WeightedScoreStrategy`.

### Score Dimensions
- Network
- Identity
- Storage
- Logging
- Compute
- Overall

Each dimension scores independently from 0–100. The overall score is derived from dimension averages.

### Score Breakdown
The breakdown represents deductions explicitly:

| Component | Value |
|-----------|-------|
| Base Score | 100 |
| Internet Exposure | -14 |
| Identity | -8 |
| Storage | -6 |
| Logging | -3 |
| Compute | -2 |
| **Final** | **67** |

## Dashboard Model

`ExecutiveDashboard` contains:

| Field | Type | Description |
|-------|------|-------------|
| `summary` | `ExecutiveSummary` | Aggregate scan summary |
| `security_score` | `SecurityScore` | Overall score with grade |
| `security_dimensions` | `SecurityDimensions` | Per-dimension scores |
| `score_breakdown` | `ScoreBreakdown` | Deduction details |
| `metrics` | `ExecutiveMetrics` | Business metrics |
| `top_risks` | `List[Risk]` | Top 5 risks |
| `recommendations` | `List[Recommendation]` | Prioritized recommendations |
| `insights` | `List[Insight]` | Executive insights |
| `executive_narrative` | `ExecutiveNarrative` | Deterministic narrative |
| `generated_at` | `datetime` | Generation timestamp |
| `metadata` | `Dict` | Additional metadata |

## Metrics

`ExecutiveMetrics` includes:

- `total_assets`
- `assets_by_provider`
- `assets_by_type`
- `facts_by_category`
- `findings_by_severity`
- `risks_by_priority`
- `average_risk`
- `highest_risk`
- `internet_exposed_assets`
- `identity_risks`
- `storage_risks`
- `network_risks`
- `logging_risks`
- `compute_risks`

## Insights

`Insight` objects contain:

- `id`
- `title`
- `description`
- `severity`
- `category`
- `business_impact`
- `recommendation`
- `related_risks`

Insights are generated **only** from RiskEngine outputs. The engine never inspects cloud resources directly.

## Recommendations

`Recommendation` objects contain:

- `title`
- `priority`
- `description`
- `affected_assets`
- `expected_score_improvement`
- `related_risks`

Recommendations are **ranked by expected impact** (descending score improvement).

## Narrative Generation

The `DefaultNarrativeStrategy` generates a deterministic executive summary without AI:

> CloudSentinel analyzed 42 cloud assets and identified 18 findings, resulting in 11 prioritized risks. The environment currently has a Security Score of 81 (Grade B). Public exposure and storage configuration issues are the largest contributors to organizational risk. Addressing the top three recommendations is estimated to improve the security posture by approximately 14 points.

Custom strategies can be injected via `INarrativeStrategy`.

## Widget Models

The dashboard provides widget-ready domain models:

- `SecurityScoreWidget` — `security_score.to_dict()`
- `DimensionWidget` — `security_dimensions.to_dict()`
- `RiskDistributionWidget` — `metrics.risks_by_priority`
- `TopRiskWidget` — `top_risks` list
- `RecommendationWidget` — `recommendations` list

Frontend must only render these models. No frontend calculations.

## Strategy Pattern

Security score generation uses the strategy pattern:

```python
class IScoreStrategy(ABC):
    @abstractmethod
    def calculate_score(self, findings, risks, facts, assets) -> SecurityScore:
        pass
```

Custom strategies can be injected without modifying the engine.

## Extension Guide

### Adding a New Dashboard Section

Create a new builder implementing the appropriate interface:

```python
class ComplianceBuilder(IMetricsBuilder):
    def build(self, assets, findings, risks, facts, attack_paths):
        # Return new domain object
        pass
```

Inject it into `ExecutiveEngine`:

```python
engine = ExecutiveEngine(metrics_builder=ComplianceBuilder())
```

### Adding a New Score Dimension

Extend `SecurityDimensions` and update the scoring strategy:

```python
class CustomScoreStrategy(IScoreStrategy):
    def calculate_score(self, findings, risks, facts, assets):
        # Add new dimension calculation
        pass
```

## Testing

The test suite (`tests/test_executive_engine.py`) contains 67 tests covering:

- Dashboard generation
- Empty scans
- Large scans (100+ assets)
- Metrics calculation
- Score calculation
- Dimension calculation
- Recommendation ordering
- Insight generation
- Narrative generation
- Serialization
- Immutability
- Strategy replacement
- Builder correctness
- Integration with Risk Engine

## Code Quality

- Full type hints
- Clear module boundaries
- No circular imports
- No duplicated business logic
- No mutable global state
- Immutable domain models (`@dataclass(frozen=True)`)
- Comprehensive docstrings for public APIs
