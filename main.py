from desmume.emulator import DeSmuME, SCREEN_PIXEL_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT
from desmume.controls import Keys, keymask
from multiprocessing import Queue, Process
import numpy as np
import cv2
import time

RESIZE_FACTOR = 3
SAVE_FILE = "saves/save_0"
BORDER_SIZE = 10


def memoryview_to_img(buffer: memoryview, height, width):
    return np.array(buffer).reshape(height, width, 4)[:, :, :3] / 255.0


def resize_img(img):
    return cv2.resize(
        img,
        (SCREEN_WIDTH * RESIZE_FACTOR, SCREEN_HEIGHT * RESIZE_FACTOR),
        interpolation=cv2.INTER_AREA,
    )


def add_red_border(img, border_size=BORDER_SIZE):
    (width, height, _) = img.shape

    # Top border
    img[:BORDER_SIZE, :, :] = np.zeros((BORDER_SIZE, height, 3))
    img[:BORDER_SIZE, :, 2:] = 255 * np.ones((BORDER_SIZE, height, 1))

    # Bottom border
    img[-BORDER_SIZE:, :, :] = np.zeros((BORDER_SIZE, height, 3))
    img[-BORDER_SIZE:, :, 2:] = 255 * np.ones((BORDER_SIZE, height, 1))

    # Left border
    img[:, :BORDER_SIZE, :] = np.zeros((width, BORDER_SIZE, 3))
    img[:, :BORDER_SIZE, 2:] = 255 * np.ones((width, BORDER_SIZE, 1))

    # Right border
    img[:, -BORDER_SIZE:, :] = np.zeros((width, BORDER_SIZE, 3))
    img[:, -BORDER_SIZE:, 2:] = 255 * np.ones((width, BORDER_SIZE, 1))

    return img


KEYS_DICT = {
    "a": Keys.KEY_A,
    "b": Keys.KEY_B,
    "x": Keys.KEY_X,
    "y": Keys.KEY_Y,
    "l": Keys.KEY_L,
    "r": Keys.KEY_R,
    "z": Keys.KEY_UP,
    "s": Keys.KEY_DOWN,
    "q": Keys.KEY_LEFT,
    "d": Keys.KEY_RIGHT,
    "o": Keys.KEY_START,
    "p": Keys.KEY_SELECT,
}


def run_simulation(queue: Queue):
    emu = DeSmuME()
    emu.open("roms/heartgold.nds")

    img = None
    pause = False
    speed = 1
    print(f"Speed: x{speed}")

    while True:

        input_key = cv2.waitKey(1)
        if input_key in [ord(key) for key in KEYS_DICT]:
            queue.put(KEYS_DICT[chr(input_key)])

        elif input_key == 27:
            cv2.destroyAllWindows()
            break

        elif input_key == 190:
            pause = not pause
            if pause:
                img_with_pause = add_red_border(img)
                cv2.imshow("image", img_with_pause)

        elif input_key == 191:
            speed = max(1, speed - 1)
            print(f"Speed: x{speed}")

        elif input_key == 192:
            speed += 1
            print(f"Speed: x{speed}")

        elif input_key == 193:
            emu.savestate.load_file(SAVE_FILE)

        elif input_key == 194:
            emu.savestate.save_file(SAVE_FILE)

        elif input_key == 195:  # F2
            t0 = int(time.time() * 1000)
            cv2.imwrite(f"pictures/upper_{t0}.jpg", upper_img * 255)
            cv2.imwrite(f"pictures/lower_{t0}.jpg", lower_img * 255)
            print(f"Screenshot saved, date: {t0}")
            time.sleep(0.1)

        elif input_key != -1:
            print(input_key)

        if pause:
            add_red_border(img)
            continue

        for i in range(speed):
            emu.cycle(with_joystick=False)

        try:
            key = queue.get(False)
            mask = keymask(key)
            emu.input.keypad_add_key(mask)

            for i in range(2):
                emu.cycle(with_joystick=False)

            emu.input.keypad_rm_key(mask)
        except:
            pass

        gpu_framebuffer = emu.display_buffer_as_rgbx()
        upper_img = memoryview_to_img(
            gpu_framebuffer[: SCREEN_PIXEL_SIZE * 4], SCREEN_HEIGHT, SCREEN_WIDTH
        )
        lower_img = memoryview_to_img(
            gpu_framebuffer[SCREEN_PIXEL_SIZE * 4 :], SCREEN_HEIGHT, SCREEN_WIDTH
        )

        resized_upper_img = resize_img(upper_img)
        resized_lower_img = resize_img(lower_img)
        img = np.concatenate((resized_upper_img, resized_lower_img), axis=0)

        cv2.imshow("image", img)


def main():
    input_queue = Queue()
    emulator_job = Process(target=run_simulation, args=(input_queue,))
    emulator_job.start()
    emulator_job.join()


if __name__ == "__main__":
    main()
