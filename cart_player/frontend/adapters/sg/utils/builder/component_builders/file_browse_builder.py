import FreeSimpleGUI as sg


class FileBrowseBuilder:
    @staticmethod
    def build(initial_folder: str, target: str, key: str, file_types: list[str] = None) -> sg.Button:
        """Build a file browse button."""
        return FileBrowse(initial_folder=initial_folder, target=target, key=key, file_types=file_types)


class FileBrowse(sg.Button):
    def __init__(self, initial_folder: str, target: str, key: str, file_types: list[str] = None):
        self._file_browse = sg.FileBrowse(
            initial_folder=initial_folder,
            target=target,
            key=key,
            file_types=file_types or sg.FILE_TYPES_ALL_FILES,
        )

    def __getattr__(self, attr):
        return getattr(self._file_browse, attr)
