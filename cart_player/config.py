import logging
import shutil
from pathlib import Path

import cart_player.backend.services as backend_services
import cart_player.core.services as core_services
import cart_player.frontend.services as frontend_services
from cart_player.backend.adapters.cart_flasher.gbx_flasher import GBXFlasher
from cart_player.backend.adapters.game_library import (
    CartMetadataLibrary,
    LaunchboxMetadataLibrary,
    LibretroImageLibrary,
    LibretroMetadataLibrary,
)
from cart_player.backend.adapters.memory import DummyMemory, LocalMemory
from cart_player.backend.domain.models import CartInfo
from cart_player.backend.domain.ports import GameLibrary
from cart_player.backend.resources.mock import (
    mock_gb_boxart_filepath,
    mock_gb_gbc_boxart_filepath,
    mock_gb_gbc_metadata,
    mock_gb_metadata,
    mock_gba_boxart_filepath,
    mock_gba_metadata,
    mock_gbc_boxart_filepath,
    mock_gbc_metadata,
)
from cart_player.backend.tests.mocks import (
    MockCartFlasher,
    MockGameData,
    MockGameImageLibrary,
    MockGameMetadataLibrary,
    MockMemory,
)
from cart_player.backend.utils.models import GameRegion, GameSupport
from cart_player.core import Broker, Channel
from cart_player.frontend.adapters.sg import SgApp
from cart_player.frontend.domain.events import WindowReadNoWindowEvent, WindowReadTimeoutEvent
from cart_player.frontend.domain.ports import LocalMemoryConfigurable

from .logging_handlers import logging_handlers
from .settings import (
    APP_NAME,
    SETTINGS_MEMORY_PATH,
    SETTINGS_NO_MEMORY,
    SETTINGS_RESET_MEMORY,
    SETTINGS_USE_CART_FLASHER_MOCK,
    SETTINGS_USE_IMAGE_LIBRARIES_MOCK,
    SETTINGS_USE_MEMORY_MOCK,
    SETTINGS_USE_METADATA_LIBRARIES_MOCK,
    cli_settings,
    settings,
)

# Logger and its handlers
logging.root.setLevel(logging.DEBUG)
[logging.root.addHandler(handler) for handler in logging_handlers]

# App
app = SgApp(APP_NAME, settings.get(SETTINGS_MEMORY_PATH))
channel = Channel()

# CartFlasher
if not cli_settings.get(SETTINGS_USE_CART_FLASHER_MOCK):
    cart_flasher = GBXFlasher()
else:
    carts = [
        CartInfo(
            "ZLA", "01", GameSupport.GAMEBOY, GameRegion.EUROPE, "Legend of Zelda, The - Link's Awakening (France)"
        ),
        CartInfo(
            "PKTCG",
            "02",
            GameSupport.GAMEBOY_OR_GAMEBOY_COLOR,
            GameRegion.EUROPE,
            "Pokemon Trading Card Game (Europe) (En,Fr,De) (SGB Enhanced) (GB Compatible)",
        ),
        CartInfo("MT", "03", GameSupport.GAMEBOY_COLOR, GameRegion.EUROPE, "Mario Tennis (Europe)"),
        CartInfo(
            "FFTA",
            "04",
            GameSupport.GAMEBOY_ADVANCE,
            GameRegion.EUROPE,
            "Final Fantasy Tactics Advance (Europe) (En,Fr,De,Es,It)",
        ),
        None,
    ]
    cart_flasher = MockCartFlasher(carts)

# Memory
if cli_settings.get(SETTINGS_NO_MEMORY):
    memory = DummyMemory()
elif cli_settings.get(SETTINGS_USE_MEMORY_MOCK):
    memory = MockMemory(
        app.memory_path,
        entries=[
            MockGameData(cart_info=cart_info, game_installed=i % 2 == 0, n_saves=i)
            for i, cart_info in enumerate(carts)
            if cart_info
        ],
    )
else:
    memory = LocalMemory(app.memory_path)
    if cli_settings.get(SETTINGS_RESET_MEMORY):
        shutil.rmtree(memory.root_path, ignore_errors=True)
    memory.configure()

# GameLibrary
metadata_libraries = []
if not cli_settings.get(SETTINGS_USE_METADATA_LIBRARIES_MOCK):
    metadata_libraries.append(CartMetadataLibrary())
    metadata_libraries.append(LaunchboxMetadataLibrary())
    metadata_libraries.append(LibretroMetadataLibrary())
else:
    metadata_library = MockGameMetadataLibrary()
    metadata_library.add_info(carts[0].id, mock_gb_metadata)
    metadata_library.add_info(carts[1].id, mock_gb_gbc_metadata)
    metadata_library.add_info(carts[2].id, mock_gbc_metadata)
    metadata_library.add_info(carts[3].id, mock_gba_metadata)
    metadata_libraries.append(metadata_library)

image_libraries = []
if not cli_settings.get(SETTINGS_USE_IMAGE_LIBRARIES_MOCK):
    image_libraries.append(LibretroImageLibrary())
else:
    image_library = MockGameImageLibrary()
    image_library.add_image(carts[0].id, Path(mock_gb_boxart_filepath))
    image_library.add_image(carts[1].id, Path(mock_gb_gbc_boxart_filepath))
    image_library.add_image(carts[2].id, Path(mock_gbc_boxart_filepath))
    image_library.add_image(carts[3].id, Path(mock_gba_boxart_filepath))
    image_libraries.append(image_library)

game_library = GameLibrary(metadata_libraries, image_libraries)

# running in main thread, used for messages that have to be handled in main thread
main_broker = Broker(channel=channel)

# running in child threads, used for all other messages
broker = Broker(channel=channel)

# Core - event handlers
broker.register(core_services.LocalMemoryConfigurationUpdatedEventHandler(main_broker))
broker.register(core_services.UnexpectedWarningEventHandler(main_broker))
broker.register(core_services.UnexpectedErrorEventHandler(main_broker))

# Frontend - ignored events
channel.ignore(WindowReadNoWindowEvent)
channel.ignore(WindowReadTimeoutEvent)

# Frontend - handlers
main_broker.register(frontend_services.OpenDataWindowHandler(main_broker, app))
main_broker.register(frontend_services.OpenPlayWindowHandler(main_broker, app))
main_broker.register(frontend_services.OpenPopUpWarningWindowHandler(main_broker, app))
main_broker.register(frontend_services.OpenPopUpErrorWindowHandler(main_broker, app))
main_broker.register(frontend_services.OpenSettingsWindowHandler(main_broker, app))
main_broker.register(frontend_services.RestorePreviousWindowHandler(main_broker, app))
main_broker.register(frontend_services.StopAppHandler(main_broker, app))

broker.register(frontend_services.BeginProgressBarHandler(broker, app))
broker.register(frontend_services.EndProgressBarHandler(broker, app))
broker.register(frontend_services.UpdateProgressBarHandler(broker, app))
broker.register(frontend_services.UpdateETAHandler(broker, app))

# Frontend - event handlers
main_broker.register(frontend_services.DataSelectorButtonPressedEventHandler(main_broker))
main_broker.register(frontend_services.PlaySelectorButtonPressedEventHandler(main_broker))
main_broker.register(frontend_services.PopUpWindowIsClosingEventHandler(main_broker))
main_broker.register(frontend_services.SettingsSelectorButtonPressedEventHandler(main_broker))
main_broker.register(frontend_services.WindowCloseAttemptedEventHandler(main_broker))

broker.register(frontend_services.BackupButtonPressedEventHandler(broker))
broker.register(frontend_services.BackupCartSaveProgressEventHandler(broker))
broker.register(frontend_services.CartGameInstalledEventHandler(broker))
broker.register(frontend_services.CartDataReadEventHandler(broker, app))
broker.register(frontend_services.CartSaveBackupEventHandler(broker))
broker.register(frontend_services.CartSaveErasedEventHandler(broker))
broker.register(frontend_services.CartSaveWrittenEventHandler(broker))
broker.register(frontend_services.EndSessionButtonPressedEventHandler(broker, app))
broker.register(frontend_services.EraseButtonPressedEventHandler(broker))
broker.register(frontend_services.EraseCartSaveProgressEventHandler(broker))
broker.register(frontend_services.InputMemoryFolderButtonPressedEventHandler(broker))
broker.register(frontend_services.InstallButtonPressedEventHandler(broker))
broker.register(frontend_services.InstallCartGameProgressEventHandler(broker))
broker.register(frontend_services.LaunchButtonPressedEventHandler(broker, app))
broker.register(frontend_services.OpenMemoryButtonPressedEventHandler(main_broker))
broker.register(frontend_services.RefreshButtonPressedEventHandler(broker, app))
broker.register(frontend_services.UploadButtonPressedEventHandler(broker))
broker.register(frontend_services.WriteCartSaveProgressEventHandler(broker))
if isinstance(memory, LocalMemory) and isinstance(app, LocalMemoryConfigurable):
    broker.register(frontend_services.LocalMemoryConfigurationUpdatedEventHandler(broker, app))

# Backend - handlers
broker.register(backend_services.BackupCartSaveHandler(broker, memory, cart_flasher))
broker.register(backend_services.BackupSaveFileAfterPlayingHandler(broker, memory))
broker.register(backend_services.EraseCartSaveHandler(broker, memory, cart_flasher))
broker.register(backend_services.ExportToAnaloguePocketLibraryHandler(broker, memory))
broker.register(backend_services.InstallCartGameHandler(broker, memory, cart_flasher))
broker.register(backend_services.ReadCartDataHandler(broker, memory, cart_flasher, game_library))
broker.register(backend_services.SetupGameFileAndSaveFileForPlayingHandler(broker, memory))
broker.register(backend_services.WriteCartSaveHandler(broker, memory, cart_flasher))
if isinstance(memory, LocalMemory):
    broker.register(backend_services.UpdateLocalMemoryConfigurationHandler(broker, memory))

# Save current memory path if none was found in settings
if not settings.get(SETTINGS_MEMORY_PATH):
    from cart_player.backend.api.events import LocalMemoryConfigurationUpdatedEvent
    from cart_player.backend.domain.dtos import LocalMemoryConfiguration

    broker.publish(
        LocalMemoryConfigurationUpdatedEvent(
            new_memory_configuration=LocalMemoryConfiguration(root_path=app.memory_path)
        )
    )
