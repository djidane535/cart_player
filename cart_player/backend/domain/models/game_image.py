import base64
import struct
from io import BytesIO

from PIL import Image

IMAGE_HEADER = bytes([0x20, 0x49, 0x50, 0x41])


class GameImage:
    """Game image.

    Args:
        data: Raw bytes.

    Attributes:
        data: Raw bytes.
    """

    def __init__(self, data: bytes = None):
        self.data = data

    @staticmethod
    def convert_to_analogue_pocket_library(data: bytes) -> bytes:
        """
        Convert imaged data to Analogue Library format
        """
        # Load data into image
        image = Image.open(BytesIO(base64.b64decode(data)))

        # Rotate 90 degrees per Analogue spec
        image = image.rotate(90)

        # Determine aspect ratio for scaling
        # Only need height ratio as target canvas is landscape oriented
        scale = 165 / image.height

        # Scale image
        image = image.resize((round(image.width * scale), round(image.height * scale)))

        # Create new bitmap from rotated bitmap using BGRA32 pixel format
        image = image.convert("RGBA")

        # Open output stream. We will write the transformed image data along with the
        # Analogue header here.
        with BytesIO() as out:
            out.write(IMAGE_HEADER)

            # Dimensions as bytes, reverse order for little endian
            h_bytes = struct.pack("<H", image.height)
            w_bytes = struct.pack("<H", image.width)

            # Write image dimensions in bytes
            out.write(h_bytes)
            out.write(w_bytes)

            # Create pixel buffer
            pixels = image.tobytes("raw", "BGRA")

            # Write image data
            out.write(pixels)

            # Return
            out.seek(0)
            return out.read()
