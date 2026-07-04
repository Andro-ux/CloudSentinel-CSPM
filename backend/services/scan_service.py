from backend.providers.factory import get_provider
from backend.config import settings
from backend.database.session import SessionLocal
from backend.services.persistence import save_findings
from backend.services.history_service import save_scan_history
from backend.services.asset_service import save_assets

class ScanService:

    def run_scan(self):

        db = SessionLocal()

        try:

            provider = get_provider(settings.CLOUD_PROVIDER)

            result = provider.scan()

            save_findings(db, result.findings)

            save_scan_history(db, result)

            save_assets(db, provider.get_assets())

            # We'll save data here in the next step

            return result

        finally:
            db.close()