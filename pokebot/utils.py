from numpy import zeros, ones, array, ubyte, empty
import cv2  # type: ignore

from pokebot.type import Screen


def memoryview_to_screen(
    buffer: memoryview,
    height: int,
    width: int,
) -> Screen:
    return array(buffer).reshape(height, width, 4)[:, :, :3]


def generate_white_screen(
    width: int,
    height: int,
) -> Screen:
    screen = empty((width, height, 3), dtype=ubyte)
    screen[:] = 255

    return screen


def resize_screen(
    screen: Screen,
    resize_factor: int,
) -> Screen:
    return screen.repeat(resize_factor, axis=0).repeat(resize_factor, axis=1)


def add_red_border(
    screen: Screen,
    border_size: int,
) -> Screen:
    (width, height, _) = screen.shape

    # Top border
    screen[:border_size, :, :] = zeros((border_size, height, 3), dtype=ubyte)
    screen[:border_size, :, 2:] = 255 * ones((border_size, height, 1), dtype=ubyte)

    # Bottom border
    screen[-border_size:, :, :] = zeros((border_size, height, 3), dtype=ubyte)
    screen[-border_size:, :, 2:] = 255 * ones((border_size, height, 1), dtype=ubyte)

    # Left border
    screen[:, :border_size, :] = zeros((width, border_size, 3), dtype=ubyte)
    screen[:, :border_size, 2:] = 255 * ones((width, border_size, 1), dtype=ubyte)

    # Right border
    screen[:, -border_size:, :] = zeros((width, border_size, 3), dtype=ubyte)
    screen[:, -border_size:, 2:] = 255 * ones((width, border_size, 1), dtype=ubyte)

    return screen


def put_text(
    screen: Screen,
    x: int,
    y: int,
    text: str,
) -> None:
    cv2.putText(  # type: ignore
        img=screen,
        text=text,
        org=(x, y),
        color=(255, 255, 255),
        fontFace=cv2.FONT_HERSHEY_DUPLEX,
        fontScale=1,
        lineType=cv2.LINE_AA,
        thickness=6,
    )
    cv2.putText(  # type: ignore
        img=screen,
        text=text,
        org=(x, y),
        color=(0, 0, 255),
        fontFace=cv2.FONT_HERSHEY_DUPLEX,
        fontScale=1,
        lineType=cv2.LINE_AA,
        thickness=2,
    )
