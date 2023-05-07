import abc
from contextlib import contextmanager
from typing import Callable

from cart_player.backend.domain.models import CartInfo
from cart_player.core.exceptions import NoCartInCartFlasherException
from cart_player.core.utils import lockedclass, lockedmethod


@lockedclass
class CartFlasher(abc.ABC):
    """Cart flasher, allowing to interact with real carts.

    Properties:
        cart_inserted: True if a cart is inserted.
        is_busy: True if cart flasher is not available.
    """

    def __init__(self):
        self._busy = False

    @contextmanager
    def use_flasher(self):
        self._busy = True
        try:
            yield
        finally:
            self._busy = False

    @property
    @abc.abstractmethod
    def cart_inserted(self) -> bool:
        """True if a cart is inserted."""
        pass

    @property
    def is_busy(self) -> bool:
        """True if cart flasher is busy."""
        return self._busy

    @lockedmethod
    def read_cart_info(self) -> CartInfo:
        """Read the info from the cart connected to the cart flasher.

        Raises:
            NoCartInCartFlasherException: If no cart in cart flasher.
            RuntimeError: If cart flasher is busy.
            RuntimeError: If unexpected error occured.
        """
        if not self.cart_inserted:
            raise NoCartInCartFlasherException
        if self.is_busy:
            raise RuntimeError("Cannot read cart info when cart flasher is busy.")

        with self.use_flasher():
            cart_info = self._read_cart_info()
        return cart_info

    @abc.abstractmethod
    def _read_cart_info(self) -> CartInfo:
        """Read the info from the cart connected to the cart flasher.
        Perform the actual operations with the cart flasher.

        Raises:
            RuntimeError: If unexpected error occured.
        """
        pass

    @lockedmethod
    def read_game(self, cart_info: CartInfo, report_progress_callback: Callable[[float], None]) -> bytes:
        """Read game from the cart connected to the cart flasher.

        Args:
            cart_info: Cart info of the inserted cartridge.
            report_progress_callback: Method to be called to report current progress of the process (in [0; 1]).

        Raises:
            NoCartInCartFlasherException: If no cart in cart flasher.
            RuntimeError: If cart flasher is busy.
            RuntimeError: If unexpected error occured.

        Returns:
            Bytes read.
        """
        if not self.cart_inserted:
            raise NoCartInCartFlasherException
        if self.is_busy:
            raise RuntimeError("Cannot install a game when cart flasher is busy.")

        with self.use_flasher():
            file_content = self._read_game(cart_info, report_progress_callback)
        return file_content

    @abc.abstractmethod
    def _read_game(self, cart_info: CartInfo, report_progress_callback: Callable[[float], None]) -> bytes:
        """Read game from the cart connected to the cart flasher.
        Perform the actual operations with the cart flasher.

        Args:
            cart_info: Cart info of the inserted cartridge.
            report_progress_callback: Method to be called to report current progress of the process (in [0; 1]).

        Returns:
            Bytes read.

        Raises:
            RuntimeError: If unexpected error occured.
        """
        pass

    @lockedmethod
    def read_save(self, cart_info: CartInfo, report_progress_callback: Callable[[float], None]) -> bytes:
        """Read save from the cart connected to the cart flasher.

        Args:
            cart_info: Cart info of the inserted cartridge.
            report_progress_callback: Method to be called to report current progress of the process (in [0; 1]).

        Raises:
            NoCartInCartFlasherException: No cart in cart flasher.
            RuntimeError: Cart flasher is busy.

        Returns:
            Bytes read.

        Raises:
            NoCartInCartFlasherException: No cart in cart flasher.
            RuntimeError: If cart flasher is busy.
            RuntimeError: If unexpected error occured.
        """
        if not self.cart_inserted:
            raise NoCartInCartFlasherException
        if self.is_busy:
            raise RuntimeError("Cannot install a game when cart flasher is busy.")

        with self.use_flasher():
            file_content = self._read_save(cart_info, report_progress_callback)
        return file_content

    @abc.abstractmethod
    def _read_save(self, cart_info: CartInfo, report_progress_callback: Callable[[float], None]) -> bytes:
        """Read save from the cart connected to the cart flasher.
        Perform the actual operations with the cart flasher.

        Args:
            cart_info: Cart info of the inserted cartridge.
            report_progress_callback: Method to be called to report current progress of the process (in [0; 1]).

        Returns:
            Bytes read.

        Raises:
            RuntimeError: If unexpected error occured.
        """
        pass

    @lockedmethod
    def erase_save(self, cart_info: CartInfo, report_progress_callback: Callable[[float], None]):
        """Erase save from the cart connected to the cart flasher.

        Args:
            cart_info: Cart info of the inserted cartridge.
            report_progress_callback: Method to be called to report current progress of the process (in [0; 1]).

        Raises:
            NoCartInCartFlasherException: No cart in cart flasher.
            RuntimeError: Cart flasher is busy.

        Raises:
            NoCartInCartFlasherException: No cart in cart flasher.
            RuntimeError: If cart flasher is busy.
            RuntimeError: If unexpected error occured.
        """
        if not self.cart_inserted:
            raise NoCartInCartFlasherException
        if self.is_busy:
            raise RuntimeError("Cannot install a game when cart flasher is busy.")

        with self.use_flasher():
            file_content = self._erase_save(cart_info, report_progress_callback)
        return file_content

    @abc.abstractmethod
    def _erase_save(self, cart_info: CartInfo, report_progress_callback: Callable[[float], None]):
        """Erase save from the cart connected to the cart flasher.
        Perform the actual operations with the cart flasher.

        Args:
            cart_info: Cart info of the inserted cartridge.
            report_progress_callback: Method to be called to report current progress of the process (in [0; 1]).

        Raises:
            RuntimeError: If unexpected error occured.
        """
        pass

    @lockedmethod
    def write_save(self, cart_info: CartInfo, data: bytes, report_progress_callback: Callable[[float], None]):
        """Write save from the cart connected to the cart flasher.

        Args:
            cart_info: Cart info of the inserted cartridge.
            data: Data to be written.
            report_progress_callback: Method to be called to report current progress of the process (in [0; 1]).

        Raises:
            NoCartInCartFlasherException: No cart in cart flasher.
            RuntimeError: Cart flasher is busy.

        Raises:
            NoCartInCartFlasherException: No cart in cart flasher.
            RuntimeError: If cart flasher is busy.
            RuntimeError: If unexpected error occured.
        """
        if not self.cart_inserted:
            raise NoCartInCartFlasherException
        if self.is_busy:
            raise RuntimeError("Cannot write a save when cart flasher is busy.")

        with self.use_flasher():
            file_content = self._write_save(cart_info, data, report_progress_callback)
        return file_content

    @abc.abstractmethod
    def _write_save(self, cart_info: CartInfo, data: bytes, report_progress_callback: Callable[[float], None]):
        """Write save from the cart connected to the cart flasher.
        Perform the actual operations with the cart flasher.

        Args:
            cart_info: Cart info of the inserted cartridge.
            data: Data to be written.
            report_progress_callback: Method to be called to report current progress of the process (in [0; 1]).

        Raises:
            RuntimeError: If unexpected error occured.
        """
        pass
