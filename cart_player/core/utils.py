import multiprocessing
import os
from multiprocessing import Lock
from pathlib import Path
from typing import Callable, Type

# avoid restarts when using pyinstaller build
if os.name == 'nt':  # for Windows
    multiprocessing.set_start_method("spawn")  
elif os.name == 'posix':  # for macOS and Linux
    multiprocessing.set_start_method("fork")


def lockedclass(cls: Type) -> Type:
    """Decorator that locks a class.

    The decorator adds a `Lock` object to the class as an attribute, which can be used to synchronize access
    to the class.

    Args:
        cls: The class to be locked.

    Returns:
        The decorated class.
    """

    class Wrapper(cls):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            setattr(self, "__lock", Lock())

    return Wrapper


def lockedmethod(func: Callable) -> Callable:
    """Decorator that locks a method.

    The decorator acquires and releases the lock around the method call to prevent multiple threads from accessing
    the method at the same time.

    Args:
        func: The method to be locked.

    Returns:
        The decorated method.
    """

    def wrapper(self, *args, **kwargs):
        self.__lock.acquire()
        try:
            result = func(self, *args, **kwargs)
        except Exception as e:
            self.__lock.release()
            raise e
        else:
            self.__lock.release()
            return result

    return wrapper


def open_folder(path: Path):
    # Open folder
    if os.name == 'nt':  # for Windows
        os.startfile(path)
    elif os.name == 'posix':  # for macOS and Linux
        os.system('open "{}"'.format(path))
    else:
        raise RuntimeError("Unsupported operating system")
