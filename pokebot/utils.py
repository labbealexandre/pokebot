from numpy import zeros, ones, array
import cv2


def memoryview_to_img(buffer: memoryview, height, width):
    return array(buffer).reshape(height, width, 4)[:, :, :3] / 255.0


def resize_img(img, resize_factor):
    (height, width, _) = img.shape
    return cv2.resize(
        img,
        (width * resize_factor, height * resize_factor),
        interpolation=cv2.INTER_AREA,
    )


def add_red_border(img, border_size):
    (width, height, _) = img.shape

    # Top border
    img[:border_size, :, :] = zeros((border_size, height, 3))
    img[:border_size, :, 2:] = 255 * ones((border_size, height, 1))

    # Bottom border
    img[-border_size:, :, :] = zeros((border_size, height, 3))
    img[-border_size:, :, 2:] = 255 * ones((border_size, height, 1))

    # Left border
    img[:, :border_size, :] = zeros((width, border_size, 3))
    img[:, :border_size, 2:] = 255 * ones((width, border_size, 1))

    # Right border
    img[:, -border_size:, :] = zeros((width, border_size, 3))
    img[:, -border_size:, 2:] = 255 * ones((width, border_size, 1))

    return img


def put_text(img, org, text):
    cv2.putText(
        img=img,
        text=text,
        org=org,
        color=(255, 255, 255),
        fontFace=cv2.FONT_HERSHEY_DUPLEX,
        fontScale=1,
        lineType=cv2.LINE_AA,
        thickness=6,
    )
    cv2.putText(
        img=img,
        text=text,
        org=org,
        color=(0, 0, 255),
        fontFace=cv2.FONT_HERSHEY_DUPLEX,
        fontScale=1,
        lineType=cv2.LINE_AA,
        thickness=2,
    )
