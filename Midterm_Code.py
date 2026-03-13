#This program implements a 2D cornhole game.
#The game allows the user to aim, charge power, and throw a bean bag
#toward a cornhole board. The bag follows projectile motion with gravity.
#When the bag lands, the program scores the throw and resets for the next one.

#Controls:
#- UP / DOWN arrows: adjust throw angle
#- Hold SPACE: charge power
#- Release SPACE: throw bag
#- R: reset bag manually
#- ESC or close window: quit

#Required library:
#- pygame

from cmath import rect

import pygame
import math


# Helper functions

def clamp(value, min_val, max_val): #Clamp a value between min_val and max_val
    return max(min_val, min(value, max_val))


def distance_squared(a, b): #Return squared distance between points a and b
    dx = a[0] - b[0]
    dy = a[1] - b[1]
    return dx * dx + dy * dy



# Game object classes

class Board:
    """
    Tilted (perspective) cornhole board drawn as a trapezoid.
    Uses (u,v) board-space:
      u in [0..1] across width (left->right)
      v in [0..1] along length (near/front -> far/top)
    """

    def __init__(self, bl, br, tl, tr, hole_uv=(0.5, 0.25), hole_radius=22):
        # corners: bottom-left, bottom-right, top-left, top-right
        self.bl = bl
        self.br = br
        self.tl = tl
        self.tr = tr

        self.hole_uv = hole_uv
        self.hole_radius = hole_radius

        # convex quad polygon
        self.poly = [self.bl, self.br, self.tr, self.tl]

    def draw(self, surface):
        # board shape
        pygame.draw.polygon(surface, (160, 110, 60), self.poly)
        pygame.draw.polygon(surface, (60, 40, 20), self.poly, 3)

        # hole drawn as ellipse
        hole_center = self.uv_to_xy(*self.hole_uv)

        v = self.hole_uv[1]
        squash = self._lerp(0.85, 0.55, v)  # farther up = more squished
        rx = self.hole_radius
        ry = max(6, int(self.hole_radius * squash))

        hole_rect = pygame.Rect(0, 0, rx * 2, ry * 2)
        hole_rect.center = (int(hole_center[0]), int(hole_center[1]))
        pygame.draw.ellipse(surface, (0, 0, 0), hole_rect)

    def uv_to_xy(self, u, v):
        # interpolate along edges by v, then across by u?
        left = self._lerp_point(self.bl, self.tl, v)
        right = self._lerp_point(self.br, self.tr, v)
        return self._lerp_point(left, right, u)

    def hole_center_xy(self):
        return self.uv_to_xy(*self.hole_uv)

    def point_in_board(self, x, y):
        # point-in-convex-quad test
        p = (x, y)
        poly = self.poly

        def sign(o, a, b):
            return (o[0] - b[0]) * (a[1] - b[1]) - (a[0] - b[0]) * (o[1] - b[1])

        b1 = sign(p, poly[0], poly[1]) < 0.0
        b2 = sign(p, poly[1], poly[2]) < 0.0
        b3 = sign(p, poly[2], poly[3]) < 0.0
        b4 = sign(p, poly[3], poly[0]) < 0.0
        return (b1 == b2) and (b2 == b3) and (b3 == b4)

    # helpers kept inside Board to avoid clutter
    @staticmethod
    def _lerp(a, b, t):
        return a + (b - a) * t

    @classmethod
    def _lerp_point(cls, p, q, t):
        return (cls._lerp(p[0], q[0], t), cls._lerp(p[1], q[1], t))


class Bag:
    # Bean bag with 2 motion states:
    # - in_flight: projectile motion with gravity
    # - sliding: slides along the board axis with "friction" after landing on board

    def __init__(self, start_pos, radius):
        self.start_pos = list(start_pos)
        self.radius = radius
        self.pos = self.start_pos[:]
        self.vel = [0.0, 0.0]
        self.in_flight = False

        # sliding state
        self.sliding = False
        self.slide_dir = (0.0, -1.0)   # direction vector which the bag will slide
        self.slide_speed = 0.0         # pixels per frame
        self.slide_dist_left = 0.0     # remaining slide distance (pixels)

    def reset(self):
        self.pos = self.start_pos[:]
        self.vel = [0.0, 0.0]
        self.in_flight = False
        self.sliding = False
        self.slide_speed = 0.0
        self.slide_dist_left = 0.0

    def launch(self, angle_deg, power):
        rad = math.radians(angle_deg)
        self.vel[0] = power * math.cos(rad)
        self.vel[1] = -power * math.sin(rad)
        self.in_flight = True
        self.sliding = False

    def start_slide(self, slide_dir, initial_speed, max_distance):
        # slide_dir should already be normalized (or close)
        L = math.hypot(slide_dir[0], slide_dir[1])
        if L == 0:
            slide_dir = (0.0, -1.0)
        else:
            slide_dir = (slide_dir[0] / L, slide_dir[1] / L)

        self.in_flight = False
        self.sliding = True
        self.slide_dir = slide_dir
        self.slide_speed = max(0.0, initial_speed)
        self.slide_dist_left = max(0.0, max_distance)

    def update(self, gravity):
        if self.in_flight:
            self.pos[0] += self.vel[0]
            self.pos[1] += self.vel[1]
            self.vel[1] += gravity
            return

        if self.sliding:
            if self.slide_speed <= 0.05 or self.slide_dist_left <= 0.0:
                self.sliding = False
                self.slide_speed = 0.0
                return

            step = min(self.slide_speed, self.slide_dist_left)
            self.pos[0] += self.slide_dir[0] * step
            self.pos[1] += self.slide_dir[1] * step
            self.slide_dist_left -= step

            # friction: smaller drop = more slippery
            self.slide_speed *= 0.94

    def draw(self, surface):
        size = self.radius * 2

        rect = pygame.Rect(
            int(self.pos[0] - self.radius),
            int(self.pos[1] - self.radius),
            size,
            size
        )
        pygame.draw.rect(surface, (220, 50, 50), rect)

# Main controls

class Game:

    #Controls the main game loop, input handling, physics, scoring, and rendering.

    def __init__(self):
        pygame.init()
        self.W, self.H = 900, 500
        self.screen = pygame.display.set_mode((self.W, self.H))
        pygame.display.set_caption("Cornhole – Checkpoint 1")
        self.clock = pygame.time.Clock()

        self.font = pygame.font.SysFont(None, 28)

        self.ground_y = 460
        self.gravity = 0.35

        #Board is a trapezoid to look tilted
        bl = (620, self.ground_y)   # bottom-left
        br = (860, self.ground_y)   # bottom-right
        tl = (760, 280)             # top-left  
        tr = (880, 280)             # top-right

        self.board = Board(bl, br, tl, tr, hole_uv=(0.55, 0.80), hole_radius=22)


        self.bag = Bag((120, self.ground_y - 10), 10)

        self.angle = 45
        self.power = 0.0
        self.charging = False
        self.score = 0
        self.last_result = ""
        # how forgiving the hole is
        self.hole_forgiveness = 18  # try 12..30

        # sliding tuning
        self.max_slide_distance = 90         
        self.slide_speed_multiplier = 0.30     

        # board axis direction (front/bottom -> back/top)
        cb = self.board.uv_to_xy(0.5, 0.0)
        ct = self.board.uv_to_xy(0.5, 1.0)
        dx, dy = (ct[0] - cb[0], ct[1] - cb[1])
        L = math.hypot(dx, dy) or 1.0
        self.board_axis = (dx / L, dy / L)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if event.key == pygame.K_r:
                    self.bag.reset()
                    self.power = 0
                if event.key == pygame.K_SPACE and (not self.bag.in_flight) and (not self.bag.sliding):
                    self.charging = True

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE and self.charging:
                    self.charging = False
                    self.bag.launch(self.angle, self.power)

        return True

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if (not self.bag.in_flight) and (not self.bag.sliding):
            if keys[pygame.K_UP]:
                self.angle = clamp(self.angle + 1, 10, 80)
            if keys[pygame.K_DOWN]:
                self.angle = clamp(self.angle - 1, 10, 80)
            if self.charging:
                self.power = clamp(self.power + 0.25, 0, 18)

    def update(self):
        self.bag.update(self.gravity)
        bag_xy = (self.bag.pos[0], self.bag.pos[1])

        # Check for hole while in air or sliding
        if (self.bag.in_flight or self.bag.sliding) and self.board.point_in_board(bag_xy[0], bag_xy[1]):
            hc = self.board.hole_center_xy()
            effective = self.board.hole_radius + self.hole_forgiveness

            if distance_squared(bag_xy, hc) <= effective * effective:
                self.score += 3
                self.last_result = "IN THE HOLE! (+3)"
                self.bag.reset()
                self.power = 0
                self.angle = 45
                return

        # Landing logic
        if self.bag.in_flight and self.bag.pos[1] >= self.ground_y - self.bag.radius:

            self.bag.pos[1] = self.ground_y - self.bag.radius
            bag_xy = (self.bag.pos[0], self.bag.pos[1])

            if self.board.point_in_board(bag_xy[0], bag_xy[1]):

                impact_speed = math.hypot(self.bag.vel[0], self.bag.vel[1])
                slide_speed = impact_speed * self.slide_speed_multiplier

                self.bag.start_slide(self.board_axis, slide_speed, self.max_slide_distance)
                self.last_result = "SLIDING..."
                self.power = 0
                return

            else:
                self.last_result = "MISS (+0)"
                self.bag.reset()
                self.power = 0
                self.angle = 45
                return

        # Sliding finished
        if (not self.bag.in_flight) and (not self.bag.sliding) and (not self.charging) and (self.last_result != ""):

            bag_xy = (self.bag.pos[0], self.bag.pos[1])

            if self.board.point_in_board(bag_xy[0], bag_xy[1]):
                self.score += 1
                self.last_result = "ON THE BOARD (+1)"

                self.bag.reset()
                self.power = 0
                self.angle = 45

    def draw(self):
        self.screen.fill((255, 255, 255))

        pygame.draw.line(
            self.screen, (0, 0, 0), (0, self.ground_y), (self.W, self.ground_y), 2
        )

        self.board.draw(self.screen)
        self.bag.draw(self.screen)

        if (not self.bag.in_flight) and (not self.bag.sliding):
            rad = math.radians(self.angle)
            start = self.bag.start_pos
            end = (
                start[0] + 60 * math.cos(rad),
                start[1] - 60 * math.sin(rad),
            )
            pygame.draw.line(self.screen, (0, 0, 0), start, end, 2)

        self.screen.blit(self.font.render(f"Angle: {self.angle}", True, (0, 0, 0)), (20, 20))
        self.screen.blit(self.font.render(f"Power: {self.power:.1f}", True, (0, 0, 0)), (20, 50))
        self.screen.blit(self.font.render(f"Score: {self.score}", True, (0, 0, 0)), (20, 80))
        self.screen.blit(self.font.render(self.last_result, True, (0, 0, 0)), (20, 110))
        self.screen.blit(
            self.font.render("UP/DOWN aim | SPACE throw | R reset | ESC quit", True, (0, 0, 0)),
            (20, 150),
        )

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            self.clock.tick(60)
            running = self.handle_events()
            self.handle_input()
            self.update()
            self.draw()

        pygame.quit()


# Entry point

if __name__ == "__main__":
    Game().run()
