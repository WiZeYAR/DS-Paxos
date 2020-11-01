

class ColoredString:
    END_COLOR = "\033[0m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    GREEN = "\033[92m"

    @staticmethod
    def color_string(string: str, color: str):
        return color + string + ColoredString.END_COLOR