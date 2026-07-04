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

            save_findings(db, result.findings)

            resolve_missing_findings(db)

            save_assets(db, provider.get_assets())

            update_asset_risk_scores(db)

            save_scan_history(db, result)

            return result

        finally:
            db.close()