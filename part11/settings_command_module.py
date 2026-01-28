class _SingleSettingsCommand:
    def __init__(self, command_name: str, allowed_values: list[str], usage_text: str, config_attribute: str):
        self.command_name = command_name
        self.allowed_values = [v.upper() for v in allowed_values]
        self.usage_text = usage_text
        self.config_attribute = config_attribute

    def try_handle(self, raw: str, config) -> bool:
        if not raw.startswith(self.command_name):
            return False

        parts = raw.split()
        if len(parts) != 2:
            print(self.usage_text)
            return True

        value = parts[1].upper()
        if value not in self.allowed_values:
            print(self.usage_text)
            return True

        if self.config_attribute == "highlight":
            config.highlight = (value == "ON")
            print(f"Highlighting {'ON' if config.highlight else 'OFF'}")

        elif self.config_attribute == "search_mode":
            config.search_mode = value
            print(f"Search mode set to {config.search_mode}")

        elif self.config_attribute == "hl_mode":
            config.hl_mode = value
            print(f"Highlight mode set to {config.hl_mode}")

        config.save()
        return True


class SettingsCommand:
    """
    De-duplicated settings handler (Part 11 ToDo 0):
    One object handles all settings commands.
    """
    def __init__(self, config):
        self.config = config
        self.commands = [
            _SingleSettingsCommand(":highlight", ["ON", "OFF"], "Usage: :highlight ON|OFF", "highlight"),
            _SingleSettingsCommand(":search-mode", ["AND", "OR"], "Usage: :search-mode AND|OR", "search_mode"),
            _SingleSettingsCommand(":hl-mode", ["DEFAULT", "GREEN"], "Usage: :hl-mode DEFAULT|GREEN", "hl_mode"),
        ]

    def execute(self, raw: str) -> None:
        for cmd in self.commands:
            if cmd.try_handle(raw, self.config):
                return
        print("Unknown command. Type :help for commands.")
