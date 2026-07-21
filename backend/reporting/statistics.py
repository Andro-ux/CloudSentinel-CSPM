from collections import Counter


class Statistics:

    def generate(self, result):

        findings = result.findings
        assets = result.assets

        severity = Counter()

        category = Counter()

        service = Counter()

        for finding in findings:

            severity[
                finding["severity"].lower()
            ] += 1

            category[
                finding["category"]
            ] += 1

            service[
                finding["service"]
            ] += 1

        return {

            "asset_count": sum(
                assets.values()
            ),

            "finding_count": len(
                findings
            ),

            "severity": dict(
                severity
            ),

            "categories": dict(
                category
            ),

            "services": dict(
                service
            ),

            "resources": assets

        }