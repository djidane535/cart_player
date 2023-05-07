class BaseException(Exception):
    def __init__(self, message: str):
        self.message = message

    def __str__(self) -> str:
        return f"{self.__class__.__name__}: {self.message}"


class GameImageNotFoundException(BaseException):
    """Exception raised whenever game image cannot be found in game image library."""

    def __init__(self):
        super().__init__(
            message=("Unable to retrieve any game image from game image library."),
        )


class GameMetadataNotFoundException(BaseException):
    """Exception raised whenever game metadata cannot be found in game metadata library."""

    def __init__(self):
        super().__init__(
            message=("Unable to retrieve any game metadata from game metadata library."),
        )


class NoCartInCartFlasherException(BaseException):
    """Exception raised whenever we try to use cart flasher and no cart is inserted."""

    def __init__(self):
        super().__init__(message="No cart in cart flasher.")
