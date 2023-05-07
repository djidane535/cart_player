import PySimpleGUI as sg


class FolderBrowseBuilder:
    @staticmethod
    def build(initial_folder: str, target: str, key: str) -> sg.Button:
        """Build a folder browse button."""
        return FolderBrowse(initial_folder=initial_folder, target=target, key=key)


class FolderBrowse(sg.Button):
    def __init__(self, initial_folder: str, target: str, key: str):
        self._folder_browse = sg.FolderBrowse(
            initial_folder=initial_folder,
            target=target,
            key=key,
        )

    def __getattr__(self, attr):
        return getattr(self._folder_browse, attr)
