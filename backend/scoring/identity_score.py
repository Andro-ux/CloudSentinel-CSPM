class IdentityScore:

    def calculate(self, findings):

        score = 100

        for finding in findings:

            category = finding.get("category", "").lower()

            if category not in ("identity", "iam"):
                continue

            severity = finding["severity"].upper()

            if severity == "CRITICAL":
                score -= 30

            elif severity == "HIGH":
                score -= 20

            elif severity == "MEDIUM":
                score -= 10

            elif severity == "LOW":
                score -= 5

        return max(score, 0)