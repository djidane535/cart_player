import os
import time
from datetime import datetime, timedelta
from typing import Callable, List

from cart_player.backend.domain.models import CartInfo
from cart_player.backend.domain.ports import CartFlasher


class MockCartFlasher(CartFlasher):
    def __init__(self, carts: List[CartInfo] = []):
        super().__init__()
        self._t = datetime.now()
        self._index = 0
        self._carts = carts

    @property
    def cart_inserted(self) -> bool:
        return self._cart

    @property
    def _cart(self) -> CartInfo:
        if not self._carts:
            return None

        dt = datetime.now() - self._t
        delta_index = int(dt / timedelta(seconds=15))
        self._index = delta_index % len(self._carts)
        return self._carts[self._index]

    def _read_cart_info(self) -> CartInfo:
        return self._cart

    def _read_game(self, cart_info: CartInfo, report_progress_callback: Callable[[float], None]) -> bytes:
        for i in range(0, 26, 5):
            report_progress_callback(i / 100.0)
            time.sleep(0.1)
        time.sleep(3)
        for i in range(30, 101, 5):
            report_progress_callback(i / 100.0)
            time.sleep(0.05)

        return os.urandom(2_000)

    def _read_save(self, cart_info: CartInfo, report_progress_callback: Callable[[float], None]) -> bytes:
        for i in range(0, 81, 5):
            report_progress_callback(i / 100.0)
            time.sleep(0.05)
        time.sleep(0.25)
        for i in range(85, 101, 5):
            report_progress_callback(i / 100.0)
            time.sleep(0.01)

        return os.urandom(512)

    def _write_save(self, cart_info: CartInfo, data: bytes, report_progress_callback: Callable[[float], None]) -> bytes:
        for i in range(0, 40, 3):
            report_progress_callback(i / 100.0)
            time.sleep(0.05)
        time.sleep(0.25)
        for i in range(43, 101, 5):
            report_progress_callback(i / 100.0)
            time.sleep(0.01)

        return os.urandom(512)

    def erase_save(self, cart_info: CartInfo, report_progress_callback: Callable[[float], None]):
        raise NotImplementedError
