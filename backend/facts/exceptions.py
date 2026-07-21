

class FactEngineError(Exception):

    pass


class ExtractorError(FactEngineError):

    def __init__(self, extractor_name: str, original_error: Exception):

        self.extractor_name = extractor_name

        self.original_error = original_error

        super().__init__(
            f"Extractor '{extractor_name}' failed: {original_error}"
        )


class FactNotFound(FactEngineError):

    def __init__(self, fact_id: str):

        self.fact_id = fact_id

        super().__init__(f"Fact not found: {fact_id}")


class InvalidFactType(FactEngineError):

    def __init__(self, fact_type: str):

        self.fact_type = fact_type

        super().__init__(f"Invalid fact type: {fact_type}")
