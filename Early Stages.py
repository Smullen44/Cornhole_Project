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
    #Represents the cornhole board and hole.

   # - Store board geometry
   # - Draw board and hole
   # - Determine score for a landed bag


    def __init__(self, rect, hole_center, hole_radius):
        self.rect = rect
        self.hole_center = hole_center
        self.hole_radius = hole_radius

    def draw(self, surface):
        pygame.draw.rect(surface, (160, 110, 60), self.rect, border_radius = 8)
        pygame.draw.circle(surface, (0, 0, 0), self.hole_center, self.hole_radius)

    def score_bag(self, bag_center, bag_radius):

        #Score based on where it lands
        #Returns (points, message)

        effective_radius = self.hole_radius - bag_radius // 2
        if distance_squared(bag_center, self.hole_center) <= effective_radius ** 2:
            return 3, "IN THE HOLE! (+3)"

        if self.rect.collidepoint(int(bag_center[0]), int(bag_center[1])):
            return 1, "ON THE BOARD (+1)"

        return 0, "MISS (+0)"


class Bag:

    #Bean bag

    #- Track position and velocity
    #- Apply gravity-based motion
    #- Reset after landing

    def __init__(self, start_pos, radius):
        self.start_pos = list(start_pos)
        self.radius = radius
        self.pos = self.start_pos[:]
        self.vel = [0.0, 0.0]
        self.in_flight = False

    def reset(self):
        self.pos = self.start_pos[:]
        self.vel = [0.0, 0.0]
        self.in_flight = False

    def launch(self, angle_deg, power):
        rad = math.radians(angle_deg)
        self.vel[0] = power * math.cos(rad)
        self.vel[1] = -power * math.sin(rad)
        self.in_flight = True

    def update(self, gravity):
        if not self.in_flight:
            return
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        self.vel[1] += gravity

    def draw(self, surface):
        pygame.draw.circle(
            surface,
            (220, 50, 50),
            (int(self.pos[0]), int(self.pos[1])),
            self.radius,
        )



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

        board_rect = pygame.Rect(650, 260, 180, 200)
        hole_center = (board_rect.centerx, board_rect.y + 50)
        self.board = Board(board_rect, hole_center, 22)

        self.bag = Bag((120, self.ground_y - 10), 10)

        self.angle = 45
        self.power = 0.0
        self.charging = False
        self.score = 0
        self.last_result = ""
        self.hole_forgiveness = 20

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
                if event.key == pygame.K_SPACE and not self.bag.in_flight:
                    self.charging = True

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE and self.charging:
                    self.charging = False
                    self.bag.launch(self.angle, self.power)

        return True

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if not self.bag.in_flight:
            if keys[pygame.K_UP]:
                self.angle = clamp(self.angle + 1, 10, 80)
            if keys[pygame.K_DOWN]:
                self.angle = clamp(self.angle - 1, 10, 80)
            if self.charging:
                self.power = clamp(self.power + 0.25, 0, 18)

    def update(self):
        self.bag.update(self.gravity)

        #check for bag going in hole while in the air
        if self.bag.in_flight and self.board.rect.collidepoint(int(self.bag.pos[0]), int(self.bag.pos[1])):
            effective = self.board.hole_radius + self.hole_forgiveness
            if distance_squared(self.bag.pos, self.board.hole_center) <= effective * effective:
                self.score += 3
                self.last_result = "IN THE HOLE! (+3)"
                self.bag.reset()
                self.power = 0
                return
            
        if self.bag.in_flight and self.bag.pos[1] >= self.ground_y - self.bag.radius:
            self.bag.pos[1] = self.ground_y - self.bag.radius
            self.bag.in_flight = False

            pts, msg = self.board.score_bag(self.bag.pos, self.bag.radius)
            self.score += pts
            self.last_result = msg

            self.bag.reset()
            self.power = 0

    def draw(self):
        self.screen.fill((255, 255, 255))

        pygame.draw.line(
            self.screen, (0, 0, 0), (0, self.ground_y), (self.W, self.ground_y), 2
        )

        self.board.draw(self.screen)
        self.bag.draw(self.screen)

        if not self.bag.in_flight:
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
