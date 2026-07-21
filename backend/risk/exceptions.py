

class RiskEngineError(Exception):

    pass


class InvalidFindingError(RiskEngineError):

    def __init__(self, finding_id: str):

        self.finding_id = finding_id

        super().__init__(f"Invalid finding: {finding_id}")


class StrategyError(RiskEngineError):

    def __init__(self, strategy_name: str, original_error: Exception):

        self.strategy_name = strategy_name

        self.original_error = original_error

        super().__init__(
            f"Strategy '{strategy_name}' failed: {original_error}"
        )
