"""Settings command handler for configuration management."""


class _SingleSettingsCommand:
    def __init__(self, command_name, allowed_values, usage_text, config_attribute):
        self.command_name = command_name
        self.allowed_values = allowed_values
        self.usage_text = usage_text
        self.config_attribute = config_attribute

    def try_handle(self, raw, config) -> bool:
        if not raw.startswith(self.command_name):
            return False

        parts = raw.split()
        if len(parts) != 2:
            print(self.usage_text)
            return True

        value = parts[1].upper()
        allowed_upper = [v.upper() for v in self.allowed_values]
        if value not in allowed_upper:
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
    Part 11 ToDo 0 style: one entry-point used by app.py
    - SettingsCommand(config).execute(raw)
    """
    def __init__(self, config):
        self.config = config
        self.commands = [
            _SingleSettingsCommand(
                ":highlight",
                ["ON", "OFF"],
                "Usage: :highlight ON|OFF",
                "highlight",
            ),
            _SingleSettingsCommand(
                ":search-mode",
                ["AND", "OR"],
                "Usage: :search-mode AND|OR",
                "search_mode",
            ),
            _SingleSettingsCommand(
                ":hl-mode",
                ["DEFAULT", "GREEN"],
                "Usage: :hl-mode DEFAULT|GREEN",
                "hl_mode",
            ),
        ]

    def execute(self, raw: str):
        handled_any = False
        for cmd in self.commands:
            if cmd.try_handle(raw, self.config):
                handled_any = True
                break

        if not handled_any:
            print("Unknown command. Type :help for help.")
