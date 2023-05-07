import PySimpleGUI as sg


class InBuilder:
    @staticmethod
    def build(default: str, key: str) -> sg.In:
        """Build a folder browse button."""
        return In(default=default, key=key)


class In(sg.In):
    def __init__(self, default: str, key: str):
        self._in = sg.In(
            default,
            expand_x=True,
            readonly=True,
            enable_events=True,
            disabled_readonly_background_color='lemon chiffon',  # enforce color over night mode
            disabled_readonly_text_color='black',  # enforce color over night mode
            key=key,
        )

    def __getattr__(self, attr):
        return getattr(self._in, attr)
