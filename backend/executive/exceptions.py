

class ExecutiveEngineError(Exception):

    pass


class InvalidScoreStrategy(ExecutiveEngineError):

    def __init__(self, strategy_name: str):

        self.strategy_name = strategy_name

        super().__init__(f"Invalid score strategy: {strategy_name}")


class DashboardBuildError(ExecutiveEngineError):

    def __init__(self, builder_name: str, original_error: Exception):

        self.builder_name = builder_name

        self.original_error = original_error

        super().__init__(
            f"Dashboard builder '{builder_name}' failed: {original_error}"
        )


class EmptyScanError(ExecutiveEngineError):

    def __init__(self):

        super().__init__("Cannot build executive dashboard from empty scan")
