class PluginError(Exception):

    pass


class PluginRegistrationError(PluginError):

    def __init__(self, plugin_name: str, reason: str):

        self.plugin_name = plugin_name

        self.reason = reason

        super().__init__(f"Failed to register plugin '{plugin_name}': {reason}")


class PluginNotFoundError(PluginError):

    def __init__(self, plugin_name: str):

        self.plugin_name = plugin_name

        super().__init__(f"Plugin '{plugin_name}' not found")


class InvalidPluginError(PluginError):

    def __init__(self, plugin_name: str, reason: str):

        self.plugin_name = plugin_name

        self.reason = reason

        super().__init__(f"Invalid plugin '{plugin_name}': {reason}")


class PluginLifecycleError(PluginError):

    def __init__(self, plugin_name: str, action: str, reason: str):

        self.plugin_name = plugin_name

        self.action = action

        self.reason = reason

        super().__init__(
            f"Plugin '{plugin_name}' failed during {action}: {reason}"
        )


class DuplicatePluginError(PluginError):

    def __init__(self, plugin_name: str):

        self.plugin_name = plugin_name

        super().__init__(f"Plugin '{plugin_name}' is already registered")
