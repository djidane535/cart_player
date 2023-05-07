import math
import textwrap


def wrap_text(text: str, width: int, max_lines: int, with_ellipsis: bool = True) -> str:
    """Wrap text.

    Args:
        width: Max width of a line.
        max_lines: Maximum number of lines.
        with_ellipsis: If True, add "[...]" at the end of the last line.

    Returns:
        Wrapped text.
    """
    div = len(text) // width
    remainder = len(text) % width
    padding = (width - remainder + 1) - math.ceil(div)

    # Wrap text
    text = textwrap.fill(text, width=width)
    text = text + " " * padding  # useful when only 1 line

    # Truncate text if too long
    if len(text.split("\n")) > max_lines:
        text = "\n".join(text.split("\n")[:max_lines])
        if with_ellipsis:
            text = text[:-5] + "[...]"

    return text
