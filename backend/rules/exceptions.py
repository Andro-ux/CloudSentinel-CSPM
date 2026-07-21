

class RuleEngineError(Exception):

    pass


class RuleExecutionError(RuleEngineError):

    def __init__(self, rule_id: str, original_error: Exception):

        self.rule_id = rule_id

        self.original_error = original_error

        super().__init__(
            f"Rule '{rule_id}' failed: {original_error}"
        )


class FindingNotFound(RuleEngineError):

    def __init__(self, finding_id: str):

        self.finding_id = finding_id

        super().__init__(f"Finding not found: {finding_id}")
