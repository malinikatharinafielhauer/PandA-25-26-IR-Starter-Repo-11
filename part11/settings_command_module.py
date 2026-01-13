"""Settings command handler for configuration management."""


class SettingsCommand:
    def __init__(self, command_name, allowed_values, usage_text, config_attribute):
        self.command_name = command_name
        self.allowed_values = allowed_values
        self.usage_text = usage_text
        self.config_attribute = config_attribute

    def try_handle(self, raw, config):
        """Tries to handle the given input. Returns True if this command was responsible for it."""
        if not raw.startswith(self.command_name):
            return False

        parts = raw.split()

        if len(parts) != 2:
            print(self.usage_text)  # observes if we even have 2 words (analyzes the input)
            return True

        value = parts[1]
        value_upper = value.upper()  # ✅ #case sensitivity for upper and lower case

        if value_upper not in [v.upper() for v in self.allowed_values]:
            print(self.usage_text)  # if the second word (part[1]) is not in our "pool of possibilities", we print an error message.
            return True

        if self.config_attribute == "highlight":
            config.highlight = (value_upper == "ON")
            print(f"Highlighting {'ON' if config.highlight else 'OFF'}")

        elif self.config_attribute == "search_mode":
            config.search_mode = value_upper
            print(f"Search mode set to {config.search_mode}")

        elif self.config_attribute == "hl_mode":  # ✅ FIX 3: Changed from "highlight_mode" to "hl_mode"
            config.hl_mode = value_upper
            print(f"Highlight mode set to {config.hl_mode}")

        config.save()

        return True


# placeholder for submission