from backend.correlation.engine import CorrelationEngine
from backend.providers.factory import get_provider
from backend.config import settings
from backend.database.session import SessionLocal
from backend.services.persistence import save_findings
from backend.services.history_service import save_scan_history
from backend.services.asset_service import save_assets
from backend.services.asset_risk_service import update_asset_risk_scores
from backend.services.finding_lifecycle_service import (
    mark_existing_findings_pending,
    resolve_missing_findings,
)


class ScanService:

    def run_scan(self):

        db = SessionLocal()

        try:

            provider = get_provider(settings.CLOUD_PROVIDER)

            mark_existing_findings_pending(db)

            result = provider.scan()

            assets = provider.get_assets()

            correlation = CorrelationEngine().correlate(
                assets
            )

            result.relationships = correlation.relationships

            result.attack_paths = correlation.attack_paths

            result.fact_set = correlation.fact_set

            if correlation.finding_set:

                result.findings = correlation.finding_set.to_dicts()

            result.risk_set = correlation.risk_set

            result.dashboard = correlation.dashboard

            save_findings(db, result.findings)

            resolve_missing_findings(db)

            save_assets(db,assets)

            update_asset_risk_scores(db)

            save_scan_history(db, result)

            return result

        finally:

            db.close()
