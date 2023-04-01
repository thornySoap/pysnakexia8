'''This module serves as a "bridge" allowing \
Pysnakexia to run on TI-Nspire's Python platform.
This very likely cannot be used for other \
projects, since only needed features are implemented.'''
from ti_system import get_key
from ti_draw import fill_rect, fill_circle,  draw_text
from ti_draw import set_window, set_color, use_buffer, paint_buffer
from time import ticks_ms, sleep

QUIT = 0
KEYDOWN = 1
K_ESCAPE = 10
K_TAB = 11
K_RETURN = 12
K_UP = 13
K_LEFT = 14
K_DOWN = 15
K_RIGHT = 16

window = None


def init():
    pass


class display:
    @staticmethod
    def set_mode(*size):
        global window
        window = Vector2(*size)
        set_window(0, window.x, 0, window.y)
        use_buffer()
        return display

    @staticmethod
    def set_caption(caption):
        pass

    @staticmethod
    def flip():
        paint_buffer()

    @staticmethod
    def blit(obj, pos):
        obj.draw(pos)


class draw:
    @staticmethod
    def rect(display, color, rect):
        color.set()
        rect = Rect(rect).flip_y()
        fill_rect(rect.x, rect.y, rect.w, rect.h)

    @staticmethod
    def circle(display, color, pos, radius):
        color.set()
        pos = Vector2(pos).flip_y()
        fill_circle(pos.x, pos.y, radius)

    @staticmethod
    def line(display, color, start_pos, end_pos, width=1):
        color.set()
        start_pos = Vector2(start_pos).flip_y()
        end_pos = Vector2(end_pos).flip_y()
        rect = Rect(start_pos, end_pos - start_pos).normalize()
        if rect.w == 0:
            rect.x -= width // 2 - 1
            rect.w = width
        elif rect.h == 0:
            rect.y -= width // 2 + 1
            rect.h = width
        fill_rect(rect.x, rect.y, rect.w, rect.h)


class event:
    def __init__(self, key):
        self.type = KEYDOWN
        try:
            self.key = {
                "esc": K_ESCAPE,
                "enter": K_RETURN,
                "up": K_UP,
                "left": K_LEFT,
                "down": K_DOWN,
                "right": K_RIGHT
            }[key]
        except KeyError:
            self.type = "Invalid"

    @staticmethod
    def set_blocked(*args):
        pass

    @staticmethod
    def set_allowed(*args):
        pass

    @staticmethod
    def get():
        k = get_key()
        if k == "":
            return []
        return [event(k)]


class time:
    class Clock:
        def __init__(self):
            self.tick_start = None
            self.frame_times = []

        def tick(self, fps):
            if self.tick_start:
                tick_duration = ticks_ms() - self.tick_start
                target_time = 1000 // fps

                sleep_time = target_time - tick_duration
                if sleep_time < 0:
                    sleep_time = 0

                self.frame_times.append(tick_duration + sleep_time)

                if len(self.frame_times) > fps:
                    del self.frame_times[0]

                sleep(sleep_time / 1000)

            self.tick_start = ticks_ms()

        def get_time(self):
            return sum(self.frame_times) // len(self.frame_times)


class font:
    class Font:
        def __init__(self, family, size):
            self.text = None
            self.color = None

        def render(self, text, antialias, color):
            f = type(self)(None, None)
            f.text = text
            f.color = color
            return f

        def draw(self, pos):
            self.color.set()
            pos = Vector2(pos).flip_y()
            draw_text(pos.x, pos.y, self.text)

        def get_size(self):
            return Vector2(len(self.text) *  7, -12)


class Vector2:
    def __init__(self, *args):
        if len(args) == 0:
            self.x, self.y = 0, 0
        elif len(args) == 1:
            try:
                iter(args[0])
            except TypeError:
                self.x, self.y = args[0], args[0]
            else:
                self.x, self.y = args[0]
        else:
            self.x, self.y = args

    def flip_y(self):
        self.y = window.y - self.y
        return self

    def copy(self):
        return Vector2(self.x, self.y)

    def length(self):
        return (self.x ** 2 + self.y ** 2) ** 0.5

    def normalize(self):
        return self / self.length()

    def __iter__(self):
        return iter((self.x, self.y))

#    def __str__(self):
#        return f"Vector2<{self.x}, {self.y}>"

    def __eq__(self, other):
        return (self.x == other.x and self.y == other.y)

    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector2(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar):
        return Vector2(self.x * scalar, self.y * scalar)

    def __truediv__(self, scalar):
        return Vector2(self.x / scalar, self.y / scalar)

    def __floordiv__(self, scalar):
        return Vector2(self.x // scalar, self.y // scalar)


class Vector3:
    def __init__(self, *args):
        if len(args) == 0:
            self.x, self.y, self.z = 0, 0, 0
        elif len(args) == 1:
            self.x, self.y, self.z = args[0]
        else:
            self.x, self.y, self.z = args

    def __iter__(self):
        return iter((self.x, self.y, self.z))

    def __mul__(self, scalar):
        return Vector3(int(self.x * scalar), int(self.y * scalar), int(self.z * scalar))


class Rect:
    def __init__(self, *args):
        if len(args) == 1:
            self.x, self.y, self.w, self.h = args[0]
        elif len(args) == 2:
            self.x, self.y = args[0]
            self.w, self.h = args[1]
        else:
            self.x, self.y, self.w, self.h = args

    def copy(self):
        return Rect(self.x, self.y, self.w, self.h)

    def __getattr__(self, name):
        if name == "topleft":
            return Vector2(self.x, self.y)
        if name == "right":
            return self.x + self.w
        if name == "bottom":
            return self.y + self.h
        elif name == "size":
            return Vector2(self.w, self.h)

    def __iter__(self):
        return iter((self.x, self.y, self.w, self.h))

#    def __str__(self):
#        return (f"Rect<{self.x}, {self.y}, "
#                f"{self.w}, {self.h}>")

    def flip_y(self):
        self.y = window.y - self.y - self.h
        return self

    def normalize(self):
        if self.w < 0:
            self.w *= -1
            self.x -= self.w
        elif self.h < 0:
            self.h *= -1
            self.y -= self.h
        return self

    def collidepoint(self, point):
        return (self.x <= point.x < self.x + self.w
                and self.y <= point.y < self.y + self.h)


class Surface:
    def __init__(self, *size):
        self.size = Vector2(*size)
        self.color = Color(0, 0, 0)

    def fill(self, color):
        self.color = color

    def draw(self, pos):
        self.color.set()
        rect = Rect(pos, self.size).flip_y()
        fill_rect(rect.x, rect.y, rect.w, rect.h)

    def get_size(self):
        return self.size.copy()

    def convert(self):
        return self


class Color:
    def __init__(self, r, g, b):
        self.r, self.g, self.b = r, g, b

    def __iter__(self):
        return iter((self.r, self.g, self.b, 255))

    def set(self):
        set_color(self.r, self.g, self.b)
