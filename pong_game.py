import math
import random
import sys

import pygame

# ------------------------------------------------------------
# Constants
# ------------------------------------------------------------
WIDTH, HEIGHT = 960, 540
FPS = 60
WINNING_SCORE = 7

WHITE = (255, 255, 255)
BLACK = (10, 10, 18)
DARK = (22, 22, 32)
ACCENT = (102, 214, 255)

PADDLE_WIDTH = 16
PADDLE_HEIGHT = 110
BALL_SIZE = 14

# ------------------------------------------------------------
# Pygame setup
# ------------------------------------------------------------
pygame.init()
pygame.display.set_caption("Pong")
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.Font(None, 72)
small_font = pygame.font.Font(None, 36)
tiny_font = pygame.font.Font(None, 24)


class Paddle:
    def __init__(self, x, y, color):
        self.rect = pygame.Rect(x, y, PADDLE_WIDTH, PADDLE_HEIGHT)
        self.color = color
        self.speed = 520

    def move(self, direction, dt):
        self.rect.y += direction * self.speed * dt

    def clamp(self):
        self.rect.y = max(0, min(self.rect.y, HEIGHT - self.rect.height))

    def draw(self):
        pygame.draw.rect(screen, self.color, self.rect)


class Ball:
    def __init__(self):
        self.size = BALL_SIZE
        self.rect = pygame.Rect(WIDTH // 2 - self.size // 2, HEIGHT // 2 - self.size // 2, self.size, self.size)
        self.speed = 430
        self.velocity = [self.speed, self.speed * 0.4]

    def reset(self, direction):
        self.rect.center = (WIDTH // 2, HEIGHT // 2)
        angle = random.uniform(-0.8, 0.8)
        self.velocity = [direction * self.speed, math.sin(angle) * self.speed]

    def update(self, dt, left_paddle, right_paddle, game):
        self.rect.x += self.velocity[0] * dt
        self.rect.y += self.velocity[1] * dt

        # Top and bottom wall collisions
        if self.rect.top <= 0:
            self.rect.top = 0
            self.velocity[1] *= -1
        elif self.rect.bottom >= HEIGHT:
            self.rect.bottom = HEIGHT
            self.velocity[1] *= -1

        # Paddle collisions
        if self.rect.colliderect(left_paddle.rect):
            self.rect.left = left_paddle.rect.right
            self._bounce(left_paddle, 1)

        elif self.rect.colliderect(right_paddle.rect):
            self.rect.right = right_paddle.rect.left
            self._bounce(right_paddle, -1)

        # Scoring
        if self.rect.left <= 0:
            game.right_score += 1
            game.handle_score()
        elif self.rect.right >= WIDTH:
            game.left_score += 1
            game.handle_score()

    def _bounce(self, paddle, direction):
        speed = max(abs(self.velocity[0]), 430) + 30
        offset = (self.rect.centery - paddle.rect.centery) / (paddle.rect.height / 2)
        self.velocity[0] = direction * speed
        self.velocity[1] = offset * 360

        length = math.hypot(self.velocity[0], self.velocity[1]) or 1
        self.velocity[0] = (self.velocity[0] / length) * speed
        self.velocity[1] = (self.velocity[1] / length) * speed

    def draw(self):
        pygame.draw.ellipse(screen, WHITE, self.rect)


class PongGame:
    def __init__(self):
        self.state = "menu"
        self.mode = None
        self.left_score = 0
        self.right_score = 0
        self.winner = None

        self.left_paddle = Paddle(24, HEIGHT // 2 - PADDLE_HEIGHT // 2, WHITE)
        self.right_paddle = Paddle(WIDTH - 24 - PADDLE_WIDTH, HEIGHT // 2 - PADDLE_HEIGHT // 2, WHITE)
        self.ball = Ball()

    def start_game(self, mode):
        self.mode = mode
        self.state = "playing"
        self.left_score = 0
        self.right_score = 0
        self.winner = None

        self.left_paddle.rect.y = HEIGHT // 2 - PADDLE_HEIGHT // 2
        self.right_paddle.rect.y = HEIGHT // 2 - PADDLE_HEIGHT // 2
        self.ball.reset(random.choice([-1, 1]))

    def handle_score(self):
        # Serve toward the side that just lost the point
        if self.left_score >= WINNING_SCORE or self.right_score >= WINNING_SCORE:
            self.state = "game_over"
            if self.mode == "single":
                self.winner = "Player 1" if self.left_score > self.right_score else "CPU"
            else:
                self.winner = "Player 1" if self.left_score > self.right_score else "Player 2"
            return

        if self.left_score > self.right_score:
            self.ball.reset(1)
        else:
            self.ball.reset(-1)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == "playing":
                        self.state = "menu"
                        self.mode = None
                    elif self.state == "game_over":
                        self.state = "menu"
                        self.mode = None
                    elif self.state == "menu":
                        return False

                if self.state == "menu":
                    if event.key == pygame.K_1:
                        self.start_game("single")
                    elif event.key == pygame.K_2:
                        self.start_game("two_player")
                    elif event.key == pygame.K_q:
                        return False

                elif self.state == "game_over":
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self.state = "menu"
                    elif event.key == pygame.K_1:
                        self.start_game("single")
                    elif event.key == pygame.K_2:
                        self.start_game("two_player")

        return True

    def update(self, dt):
        if self.state != "playing":
            return

        keys = pygame.key.get_pressed()

        left_direction = 0
        if keys[pygame.K_w]:
            left_direction -= 1
        if keys[pygame.K_s]:
            left_direction += 1
        self.left_paddle.move(left_direction, dt)
        self.left_paddle.clamp()

        if self.mode == "single":
            self.update_cpu(dt)
        elif self.mode == "two_player":
            right_direction = 0
            if keys[pygame.K_UP]:
                right_direction -= 1
            if keys[pygame.K_DOWN]:
                right_direction += 1
            self.right_paddle.move(right_direction, dt)
            self.right_paddle.clamp()

        self.ball.update(dt, self.left_paddle, self.right_paddle, self)

    def update_cpu(self, dt):
        target_y = self.ball.rect.centery - self.right_paddle.rect.height / 2
        if self.ball.rect.x > WIDTH * 0.35:
            if self.right_paddle.rect.centery < target_y:
                self.right_paddle.move(1, dt)
            elif self.right_paddle.rect.centery > target_y:
                self.right_paddle.move(-1, dt)
        self.right_paddle.clamp()

    def draw(self):
        screen.fill(BLACK)

        for y in range(0, HEIGHT, 20):
            pygame.draw.rect(screen, DARK, (WIDTH // 2 - 2, y, 4, 12))

        self.left_paddle.draw()
        self.right_paddle.draw()
        self.ball.draw()

        left_text = font.render(str(self.left_score), True, WHITE)
        right_text = font.render(str(self.right_score), True, WHITE)

        screen.blit(left_text, (WIDTH // 2 - 90, 18))
        screen.blit(right_text, (WIDTH // 2 + 50, 18))

        if self.state == "menu":
            self.draw_menu()
        elif self.state == "game_over":
            self.draw_game_over()

    def draw_menu(self):
        title = font.render("PONG", True, WHITE)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 110))

        option1 = small_font.render("Press 1 for 1 Player (vs CPU)", True, ACCENT)
        option2 = small_font.render("Press 2 for 2 Players (same keyboard)", True, ACCENT)
        prompt = small_font.render("Esc to quit", True, WHITE)

        screen.blit(option1, (WIDTH // 2 - option1.get_width() // 2, HEIGHT // 2 - 10))
        screen.blit(option2, (WIDTH // 2 - option2.get_width() // 2, HEIGHT // 2 + 40))
        screen.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, HEIGHT // 2 + 90))

    def draw_game_over(self):
        if self.mode == "single":
            if self.winner == "CPU":
                msg = "CPU WINS"
            else:
                msg = "YOU WIN"
        else:
            msg = f"{self.winner} WINS"

        winner_text = font.render(msg, True, WHITE)
        screen.blit(winner_text, (WIDTH // 2 - winner_text.get_width() // 2, HEIGHT // 2 - 60))

        prompt = small_font.render("Press Enter or Space to return to menu", True, ACCENT)
        screen.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, HEIGHT // 2 + 30))

        controls = tiny_font.render("1 = 1 Player, 2 = 2 Players", True, WHITE)
        screen.blit(controls, (WIDTH // 2 - controls.get_width() // 2, HEIGHT // 2 + 75))


def main():
    game = PongGame()

    while True:
        dt = clock.tick(FPS) / 1000.0

        running = game.handle_events()
        if not running:
            pygame.quit()
            sys.exit()

        game.update(dt)
        game.draw()
        pygame.display.flip()


if __name__ == "__main__":
    main()
