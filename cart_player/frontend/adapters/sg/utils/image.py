import base64
from io import BytesIO

from PIL import Image, ImageOps, UnidentifiedImageError


def invert_colors(data: bytes) -> bytes:
    """Invert the colors of an image.

    Args:
        data: Base64-encoded data representing the image.

    Returns:
        Base64-encoded data representing the inverted image.
    """
    image = Image.open(BytesIO(base64.b64decode(data)))

    r, g, b, a = image.split()
    r = ImageOps.invert(r)
    g = ImageOps.invert(g)
    b = ImageOps.invert(b)
    inverted_image = Image.merge("RGBA", (r, g, b, a))  # do not modify alpha channel

    buffered = BytesIO()
    inverted_image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue())


def put_image_into_square(data: bytes, square_size: int, real_ratio: float = None) -> bytes:
    """
    Put image into a square.

    Args:
        data: Base64 data representing an image.
        square_size: Size of the square.
        real_ratio: If provided, overrides image ratio.

    Returns:
        Base64 data representing the squared image.
    """
    # Open the image as RGBA
    try:
        image = Image.open(BytesIO(base64.b64decode(data)))
    except UnidentifiedImageError:
        image = Image.open(BytesIO(data))

    # Compute correction scales to reach real ratio
    hscale, vscale = compute_correction_scales(image, real_ratio)

    # Compute new size of image to maximise it in a <square_size> x <square_size> box
    # (taking into account correction scales)
    old_size = image.size
    new_size = compute_new_size(old_size, square_size, hscale, vscale)

    # Resize image
    resized_image = image.resize(new_size, Image.LANCZOS)

    # Compute padding and create a new image with appropriate (transparent) borders
    padding = compute_padding(square_size, new_size)
    resized_image.putalpha(255)  # pad w/ transparent color instead of black
    padded_image = ImageOps.expand(resized_image, padding)

    # Encode new image
    buffered = BytesIO()
    padded_image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue())


def compute_correction_scales(image, real_ratio):
    """
    Compute correction scales to reach real ratio.

    Args:
        image: The original image.
        real_ratio: The ratio that the image should have after correction.

    Returns:
        A tuple containing the horizontal and vertical correction scales.
    """
    if real_ratio is None:
        return 1.0, 1.0

    ratio = image.size[0] / image.size[1]

    ratio_scale = real_ratio / ratio
    hscale = ratio_scale if ratio_scale >= 1 else 1.0
    vscale = (1.0 / ratio_scale) if ratio_scale < 1 else 1.0

    return hscale, vscale


def compute_new_size(old_size, square_size, hscale, vscale):
    """
    Compute new size of image to maximize it in a <square_size> x <square_size> box
    (taking into account correction scales).

    Args:
        old_size: A tuple of two integers representing the old width and height of the image.
        square_size: An integer representing the size of the square.
        hscale: A float representing the horizontal correction scale.
        vscale: A float representing the vertical correction scale.

    Returns:
        A tuple of two integers representing the new width and height of the image.
    """
    ratio = float(square_size) / max([old_size[0] * hscale, old_size[1] * vscale])
    new_size = (
        round(old_size[0] * ratio * hscale),
        round(old_size[1] * ratio * vscale),
    )

    return new_size


def compute_padding(square_size, new_size):
    """
    Compute the padding required to place the resized image in the center of a square with the given size.

    Args:
        square_size: The size of the square in which to place the image.
        new_size: The size of the resized image.

    Returns:
        A tuple containing the padding values for the left, top, right, and bottom of the image.
    """
    delta_w = square_size - new_size[0]
    delta_h = square_size - new_size[1]
    padding = (
        delta_w // 2,
        delta_h // 2,
        delta_w - (delta_w // 2),
        delta_h - (delta_h // 2),
    )

    return padding
