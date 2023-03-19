import math
from random import randint

import pygame
from pygame import draw
from pygame import Rect, Vector2, Vector3, Color


class Pysnakexia:
    FPS = 30
    SCREEN_SIZE = Vector2(318, 212)
    FIELD_RECT = Rect(19, 16, 280, 180)

    BTN_RESUME, BTN_QUIT = True, False
    AXIS_X, AXIS_Y = True, False
    DIR_UP, DIR_LEFT, DIR_DOWN, DIR_RIGHT = 0, 1, 2, 3

    # Menu layout
    MENU_BG_RECT = Rect(74, 66, 170, 110)
    MENU_TITLE_POS = Vector2(159, 46)
    BTN_RECT = {BTN_RESUME: Rect(136, 76, 100, 40),
                BTN_QUIT: Rect(136, 126, 100, 40)}
    BTN_TEXT = {BTN_RESUME: {True: "Resume", False: "Start"},  # "in_game"
                BTN_QUIT: {True: "Quit", False: "Quit"}}
    BTN_TEXT_POS = {BTN_RESUME: Vector2(186, 96),
                    BTN_QUIT: Vector2(186, 146)}
    SCORE_TEXT_POS = Vector2(104, 121)

    GRID_RECT = Rect(0, 0, 14, 9)
    SQUARE_SIZE = 20
    SNAKE_RADIUS = 8
    SNAKE_SPEED = 1
    APPLE_RADIUS = 7

    COLOR = {"bg": Color(40, 100, 10),
             "field": Color(50, 200, 20),
             "menu_bg": Color(40, 30, 160),
             "menu_fg": Color(200, 200, 255),
             "btn": Color(40, 80, 180),
             "snake": Color(60, 100, 230),
             "apple": Color(200, 100, 20)}

    class SnakeBend:
        def __init__(self, d, a):
            self.d = d  # direction heading down to the tail
            self.a = a  # amount of steps to reach next bending point

        def __iter__(self):
            return iter((self.d, self.a))

    def __init__(self):
        pygame.init()
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 21)

        self.screen = None
        self.tick_cycle = self.FPS / self.SNAKE_SPEED

        self.main_loop = True
        self.in_game = False
        self.game_paused = True
        self.score = 0

        self.menu_selected_btn = self.BTN_RESUME

        # following variables are initialized in self.reset_game()
        self.game_ticks = None
        self.snake_head = None  # Vector2
        self.snake = None  # list of SnakeBends
        self.snake_end = None  # Vector2
        self.next_turn = None
        self.apple_pos = None  # Vector2
        self.eating_apple = None

    def __call__(self):
        self.run()

    def run(self):
        self.main_loop = True

        self.screen = pygame.display.set_mode(self.SCREEN_SIZE)
        pygame.display.set_caption("pysnakexia8")

        pygame.event.set_blocked(None)  # for some reason None is everything
        pygame.event.set_allowed(pygame.QUIT)
        pygame.event.set_allowed(pygame.KEYDOWN)

        background = pygame.Surface(self.SCREEN_SIZE).convert()
        background.fill(self.COLOR["bg"])
        self.screen.blit(background, (0, 0))
        self.draw_field()
        self.screen_refresh()

        while self.main_loop:
            self.clock.tick(self.FPS)

            keys = []
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE and self.in_game:
                        self.toggle_pause()
                    elif event.key in (pygame.K_TAB, pygame.K_RETURN,
                                       pygame.K_UP, pygame.K_LEFT,
                                       pygame.K_DOWN, pygame.K_RIGHT):
                        keys.append(event.key)

            if self.game_paused:
                self.pause_tick(keys)
            else:
                self.game_tick(keys)

            pygame.display.flip()

        self.screen = None

    def quit(self):
        if self.in_game:
            print("Game paused. Resume by calling run()")
        print("Score:", self.score)
        self.main_loop = False

    def toggle_pause(self):
        if self.game_paused:
            self.game_paused = False
            if not self.in_game:
                self.reset_game()
                self.in_game = True
            self.screen_refresh()
        else:
            self.screen_refresh()
            self.game_paused = True
            self.screen_refresh()

    def pause_tick(self, keys=()):
        for key in keys:
            if key in (pygame.K_TAB, pygame.K_UP, pygame.K_DOWN):
                self.menu_selected_btn = not self.menu_selected_btn
                self.screen_refresh()
            elif key == pygame.K_RETURN:
                if self.menu_selected_btn == self.BTN_RESUME:
                    self.toggle_pause()
                else:
                    self.quit()

    def game_tick(self, keys=()):
        for key in keys:
            if key in (pygame.K_UP, pygame.K_LEFT,
                       pygame.K_DOWN, pygame.K_RIGHT):
                d = self.get_dir(key)
                if not self.get_axis(self.snake[0].d) == self.get_axis(d):
                    self.next_turn = d

        if self.game_ticks % self.tick_cycle == 0:
            if self.eating_apple:
                self.eating_apple = False
                self.score += 1
                self.spawn_apple()

            if self.next_turn is not None:
                self.snake.insert(0, self.SnakeBend(
                    self.turn_round(self.next_turn), 0
                ))
                self.next_turn = None

            snake_head = self.move(self.snake_head,
                                   self.turn_round(self.snake[0].d), 1)
            # collision detection
            if (self.snake_occupied(snake_head)
                    or not self.GRID_RECT.collidepoint(snake_head)):
                self.game_over()
                return

            self.snake_head = snake_head
            self.snake[0].a += 1

            end = self.snake[len(self.snake) - 1]

            if self.apple_pos == self.snake_head:
                self.eating_apple = True
            else:
                end.a -= 1

            if end.a <= 0:
                if self.eating_apple or end.a < 0:
                    self.snake.remove(end)
                if end.a < 0:
                    self.snake[len(self.snake) - 1].a -= 1

            self.snake_end = self.calc_snake_end()

        # Animate end
        d = self.turn_round(self.snake[len(self.snake) - 1].d)
        v = self.get_dir_vect(d)

        offset = v * self.SQUARE_SIZE * self.clock.get_time() / 1000
        if not self.eating_apple:
            offset *= self.game_ticks % self.tick_cycle
            offset -= v * self.SQUARE_SIZE
        else:
            fact = (self.game_ticks % self.tick_cycle)
            fact /= self.tick_cycle
            fact = (-math.cos(fact * math.tau) * 0.5 + 0.5) * 0.5
            fact *= self.tick_cycle
            offset *= fact

        self.draw_snake_end(offset)

        if self.snake[len(self.snake) - 1].a == 0:
            draw.line(self.screen, self.COLOR["snake"],
                      self.get_screen_pos(self.snake_end, subtract_1=True),
                      self.get_screen_pos(
                          self.move(self.snake_end,
                                    self.snake[len(self.snake) - 2].d, -1),
                          subtract_1=True
                      ),
                      width=self.SNAKE_RADIUS * 2)

        # Animate head
        d = self.turn_round(self.snake[0].d)
        v = self.get_dir_vect(d)
        offset = v * self.SQUARE_SIZE * self.clock.get_time() / 1000
        offset *= self.game_ticks % self.tick_cycle
        offset -= v * self.SQUARE_SIZE
        draw.circle(self.screen, self.COLOR["snake"],
                    self.get_screen_pos(self.snake_head) + offset,
                    self.SNAKE_RADIUS)

        self.game_ticks += 1

    def draw_snake_end(self, offset):
        d = self.turn_round(self.snake[len(self.snake) - 1].d)
        v = self.get_dir_vect(d)

        pos = self.get_screen_pos(self.snake_end) + offset
        pos -= Vector2(self.SQUARE_SIZE // 2)
        pos += Vector2(abs(v.x), abs(v.y)) * self.SQUARE_SIZE // 2
        size = Vector2(1, 1) - Vector2(abs(v.x), abs(v.y))
        size -= v * 0.52
        size *= self.SQUARE_SIZE
        rect = Rect(pos, size)
        rect.normalize()
        self.draw_field(rect)

        # if self.eating_apple:
        #     draw.circle(self.screen, (255, 0, 0),
        #                 self.get_screen_pos(self.snake_end) + offset,
        #                 self.SNAKE_RADIUS)
        #     return

        draw.circle(self.screen, self.COLOR["snake"],
                    self.get_screen_pos(self.snake_end) + offset,
                    self.SNAKE_RADIUS)
        if not self.eating_apple:
            draw.line(self.screen, self.COLOR["snake"],
                      self.get_screen_pos(self.snake_end, subtract_1=True)
                      + offset,
                      self.get_screen_pos(self.snake_end, subtract_1=True),
                      width=self.SNAKE_RADIUS * 2)

    def screen_refresh(self):
        if self.game_paused:
            self.draw_text("Pysnakexia",
                           self.COLOR["menu_bg"], self.MENU_TITLE_POS)
            draw.rect(self.screen, self.COLOR["menu_bg"], self.MENU_BG_RECT)
            self.draw_btn(self.BTN_RESUME)
            self.draw_btn(self.BTN_QUIT)
            pos = self.SCORE_TEXT_POS.copy()
            pos.x -= self.APPLE_RADIUS * 2
            self.draw_apple(pos)
            pos.x += self.APPLE_RADIUS * 2 + 8
            self.draw_text(self.score, self.COLOR["menu_fg"], pos)

        else:
            self.draw_field()

            self.draw_apple(self.get_screen_pos(self.apple_pos))

            pos = self.snake_head.copy()
            draw.circle(self.screen, self.COLOR["snake"],
                        self.get_screen_pos(pos), self.SNAKE_RADIUS)
            for bend in self.snake:
                prev_pos = pos.copy()
                pos = self.move(pos, bend.d, bend.a)
                draw.circle(self.screen, self.COLOR["snake"],
                            self.get_screen_pos(pos), self.SNAKE_RADIUS)
                draw.line(self.screen, self.COLOR["snake"],
                          self.get_screen_pos(prev_pos, subtract_1=True),
                          self.get_screen_pos(pos, subtract_1=True),
                          width=self.SNAKE_RADIUS * 2)

    def reset_game(self):
        self.game_ticks = 0
        self.score = 0
        self.snake_head = Vector2(7, 4)
        self.snake = [self.SnakeBend(self.DIR_LEFT, 3)]
        self.snake_end = self.calc_snake_end()
        self.next_turn = None
        self.eating_apple = False
        self.spawn_apple()

    def game_over(self):
        self.in_game = False
        self.toggle_pause()

    def spawn_apple(self):
        apple_pos = Vector2(randint(0, self.GRID_RECT.w-1),
                            randint(0, self.GRID_RECT.h-1))
        while apple_pos == self.snake_head or self.snake_occupied(apple_pos):
            apple_pos = Vector2(randint(0, self.GRID_RECT.w-1),
                                randint(0, self.GRID_RECT.h-1))
        self.apple_pos = apple_pos

        self.draw_apple(self.get_screen_pos(self.apple_pos))

    @classmethod
    def get_screen_pos(cls, grid_pos, subtract_1=False):
        pos = Vector2(cls.FIELD_RECT.topleft)
        pos += grid_pos * cls.SQUARE_SIZE
        pos += Vector2(cls.SQUARE_SIZE) // 2
        if subtract_1:
            pos -= Vector2(1, 1)
        return pos

    @staticmethod
    def get_axis(d):
        return d % 2 == 0

    @classmethod
    def get_dir_vect(cls, d):
        return {
            cls.DIR_UP: Vector2(0, -1),
            cls.DIR_LEFT: Vector2(-1, 0),
            cls.DIR_DOWN: Vector2(0, 1),
            cls.DIR_RIGHT: Vector2(1, 0)
        }[d]

    @classmethod
    def get_dir(cls, key):
        return {
            pygame.K_UP: cls.DIR_UP, pygame.K_LEFT: cls.DIR_LEFT,
            pygame.K_DOWN: cls.DIR_DOWN, pygame.K_RIGHT: cls.DIR_RIGHT
        }[key]

    @staticmethod
    def turn(d, a):
        return (d + a) % 4

    @classmethod
    def turn_round(cls, d):
        return cls.turn(d, 2)

    @classmethod
    def move(cls, pos, d, a):
        pos = pos.copy()
        if d == cls.DIR_UP:
            pos.y -= a
        elif d == cls.DIR_LEFT:
            pos.x -= a
        elif d == cls.DIR_DOWN:
            pos.y += a
        elif d == cls.DIR_RIGHT:
            pos.x += a
        return pos

    def calc_snake_end(self):
        pos = self.snake_head.copy()
        for bend in self.snake:
            pos = self.move(pos, bend.d, bend.a)
        return pos

    def snake_occupied(self, grid_pos):
        pos = self.snake_head
        for sb in self.snake:
            for _ in range(sb.a):
                pos = self.move(pos, sb.d, 1)
                if pos == grid_pos:
                    return True
        return False

    def draw_text(self, text, color, pos):
        pos = pos.copy()
        label = self.font.render(str(text), True, color)
        pos -= Vector2(label.get_size()) // 2
        self.screen.blit(label, pos)

    def draw_btn(self, btn):
        color = self.COLOR["btn"]
        if btn == self.menu_selected_btn:
            x, y, w, h = self.BTN_RECT[btn]
            x, y, w, h = x - 2, y - 2, w + 4, h + 4
            draw.rect(self.screen, self.COLOR["menu_fg"], (x, y, w, h))
        else:
            r, g, b, _ = color
            color = tuple(Vector3(r, g, b) * 0.85)
        draw.rect(self.screen, color, self.BTN_RECT[btn])
        self.draw_text(self.BTN_TEXT[btn][self.in_game],
                       self.COLOR["menu_fg"],
                       self.BTN_TEXT_POS[btn])

    def draw_apple(self, pos):
        draw.circle(self.screen, self.COLOR["apple"], pos, self.APPLE_RADIUS)

    def draw_field(self, rect=None):
        if not rect:
            rect = self.FIELD_RECT
        draw.rect(self.screen, self.COLOR["field"], rect)

        # for x in range(self.GRID_RECT.w):
        #     for y in range(self.GRID_RECT.h):
        #         pos = self.get_screen_pos(Vector2(x, y))
        #         draw.circle(self.screen, (0, 0, 0), pos, 1)


run = Pysnakexia()
run()
