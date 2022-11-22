from desmume.emulator import DeSmuME, SCREEN_PIXEL_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT
from desmume.controls import Keys, keymask
import cv2
from multiprocessing import Queue
from time import time
from numpy import concatenate

from pokebot.default import RESIZE_FACTOR, SPEED, BORDER_SIZE, SAVE_FILE
from pokebot.utils import memoryview_to_img, resize_img, add_red_border, put_text

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

KEYS_DESCRIPTIONS = [
    "esc: Quit",
    "F1: Pause",
    "F2: Slow down",
    "F3: Speed up",
    "F4: Load state",
    "F5: Save state",
    "F6: Take a screenshot",
    "F7: Decrease screen size",
    "F8: Increase screen size",
    "F9: Hide this help",
]


class Simulation:
    def __init__(self, rom: str, queue: Queue) -> None:
        self.upper_img = None
        self.lower_img = None
        self.img = None
        self.emu = DeSmuME()
        self.emu.open(rom)
        self.stop = False
        self.pause = False
        self.speed = SPEED
        self.resize_factor = RESIZE_FACTOR
        self.hide_help = False
        self.queue = queue

        self.run()

    def add_red_border(self):
        return

    def get_key(self):
        input_key = cv2.waitKey(1)
        if input_key in [ord(key) for key in KEYS_DICT]:
            self.queue.put(keymask(KEYS_DICT[chr(input_key)]))
        elif input_key == 27:
            self.stop = True
        elif input_key == 190:  # F1
            self.pause = not self.pause
            if self.pause:
                self.img = add_red_border(self.img, BORDER_SIZE)
        elif input_key == 191:  # F2
            self.speed = max(1, self.speed - 1)
        elif input_key == 192:  # F3
            self.speed += 1
        elif input_key == 193:  # F4
            self.emu.savestate.load_file(SAVE_FILE)
        elif input_key == 194:  # F5
            self.emu.savestate.save_file(SAVE_FILE)
        elif input_key == 195:  # F6
            t0 = int(time() * 1000)
            cv2.imwrite(f"pictures/upper_{t0}.jpg", self.upper_img * 255)
            cv2.imwrite(f"pictures/lower_{t0}.jpg", self.lower_img * 255)
            print(f"Screenshot saved, date: {t0}")
        elif input_key == 196:  # F7
            self.resize_factor = max(1, self.resize_factor - 1)
        elif input_key == 197:  # F8
            self.resize_factor += 1
        elif input_key == 198:  # F9
            self.hide_help = not self.hide_help
        elif input_key != -1:
            print(input_key)

    def compute_img(self):
        gpu_framebuffer = self.emu.display_buffer_as_rgbx()
        self.upper_img = memoryview_to_img(
            gpu_framebuffer[: SCREEN_PIXEL_SIZE * 4], SCREEN_HEIGHT, SCREEN_WIDTH
        )
        self.lower_img = memoryview_to_img(
            gpu_framebuffer[SCREEN_PIXEL_SIZE * 4 :], SCREEN_HEIGHT, SCREEN_WIDTH
        )

        self.img = concatenate((self.upper_img, self.lower_img), axis=0)
        self.img = resize_img(self.img, self.resize_factor)

        if self.hide_help:
            return

        text = f"Speed: x{self.speed}, Size: x{self.resize_factor}"
        put_text(self.img, (15, 35), text)

        for i, line in enumerate(KEYS_DESCRIPTIONS):
            x, y = 15, 10 + 2 * self.resize_factor * SCREEN_HEIGHT - 35 * (
                len(KEYS_DESCRIPTIONS) - i
            )
            put_text(self.img, (x, y), line)

    def destroy(self):
        cv2.destroyAllWindows()

    def ticks(self, n):
        for i in range(n):
            self.emu.cycle(with_joystick=False)

    def run(self):
        while True:
            self.get_key()

            if self.stop:
                self.destroy()
                break

            if self.pause:
                cv2.imshow("image", self.img)
                continue

            self.ticks(self.speed)

            try:
                key = self.queue.get(False)
                self.emu.input.keypad_add_key(key)
                self.ticks(2)
                self.emu.input.keypad_rm_key(key)
            except:
                pass

            self.compute_img()
            cv2.imshow("image", self.img)
