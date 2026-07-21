class FindingPrioritizer:

    SEVERITY_SCORE = {
        "critical": 100,
        "high": 75,
        "medium": 50,
        "low": 25
    }

    INTERNET_EXPOSURE = {
        "Network Exposure",
        "Public Access",
        "Firewall",
        "Internet Exposure"
    }

    IDENTITY = {
        "Identity",
        "IAM"
    }

    DATA = {
        "Storage",
        "Secrets",
        "Database"
    }

    def prioritize(self, findings):

        ranked = []

        for finding in findings:

            score = self.SEVERITY_SCORE.get(
                finding["severity"].lower(),
                0
            )

            category = finding.get(
                "category",
                ""
            )

            if category in self.INTERNET_EXPOSURE:
                score += 20

            if category in self.IDENTITY:
                score += 15

            if category in self.DATA:
                score += 15

            finding["priority_score"] = score

            ranked.append(
                finding
            )

        ranked.sort(
            key=lambda x: x["priority_score"],
            reverse=True
        )

        return ranked