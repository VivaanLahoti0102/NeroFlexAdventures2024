import cv2
import mediapipe as mp
import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Game screen settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Asteroids Therapy Game")

# Colors
BACKGROUND_COLOR = (0, 0, 0)
PLAYER_COLOR = (255, 255, 255)
BULLET_COLOR = (255, 0, 0)
ASTEROID_COLOR = (255, 255, 0)
TEXT_COLOR = (255, 255, 255)
HEALTH_COLOR = (0, 255, 0)
BUTTON_COLOR = (0, 0, 255)
BUTTON_HOVER_COLOR = (0, 128, 255)

# Fonts
font = pygame.font.Font(None, 50)
button_font = pygame.font.Font(None, 36)

# Game states
game_started = False
game_over = False

# Player settings
player_pos = [SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100]
player_speed = 5
player_width = 50
player_height = 50
bullets = []
bullet_speed = 10

# Scoring
score = 0

# Asteroid settings
asteroids = []
asteroid_spawn_rate = 30
asteroid_size = 30
asteroid_health = 3

# Health settings
player_health = 5

# Level settings
level = 1
damage_per_bullet = 1

# Hand tracking settings
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=2,
                       min_detection_confidence=0.7, min_tracking_confidence=0.7)
cap = cv2.VideoCapture(0)

# Function to create an asteroid
def create_asteroid():
    x_pos = random.randint(0, SCREEN_WIDTH - asteroid_size)
    return [x_pos, 0, asteroid_size, asteroid_health]

# Function to create bullets
def create_bullet():
    bullet_x = player_pos[0] + player_width // 2
    bullet_y = player_pos[1]
    bullets.append([bullet_x, bullet_y])

# Function to move bullets
def move_bullets():
    global score
    for bullet in bullets:
        bullet[1] -= bullet_speed
        if bullet[1] < 0:
            bullets.remove(bullet)

# Function to move asteroids
def move_asteroids():
    global score, player_health
    for asteroid in asteroids:
        asteroid[1] += 5
        if asteroid[1] > SCREEN_HEIGHT:
            asteroids.remove(asteroid)
        if (player_pos[0] < asteroid[0] < player_pos[0] + player_width and
            player_pos[1] < asteroid[1] < player_pos[1] + player_height):
            player_health -= 1
            asteroids.remove(asteroid)
            if player_health <= 0:
                return True
        for bullet in bullets:
            if (bullet[0] > asteroid[0] and bullet[0] < asteroid[0] + asteroid[2] and
                bullet[1] > asteroid[1] and bullet[1] < asteroid[1] + asteroid[2]):
                bullets.remove(bullet)
                asteroid[3] -= damage_per_bullet
                damage = max(1, asteroid[3] // 2)
                asteroid[3] -= damage
                if asteroid[3] <= 0:
                    asteroids.remove(asteroid)
                    score += 1
                break
    return False

# Function to draw the player
def draw_player():
    pygame.draw.rect(screen, PLAYER_COLOR, (*player_pos, player_width, player_height))

# Function to draw bullets
def draw_bullets():
    for bullet in bullets:
        pygame.draw.rect(screen, BULLET_COLOR, (bullet[0], bullet[1], 5, 10))

# Function to draw asteroids
def draw_asteroids():
    for asteroid in asteroids:
        pygame.draw.circle(screen, ASTEROID_COLOR, (asteroid[0], asteroid[1]), asteroid[2])

# Function to draw score and health
def draw_score_health():
    score_text = font.render(f"Score: {score}", True, TEXT_COLOR)
    health_text = font.render(f"Health: {player_health}", True, TEXT_COLOR)
    screen.blit(score_text, (10, 10))
    screen.blit(health_text, (10, 50))

# Function to reset the game state
def reset_game():
    global game_over, player_pos, bullets, score, asteroids, player_health, level, damage_per_bullet
    game_over = False
    player_pos[0] = SCREEN_WIDTH // 2
    player_pos[1] = SCREEN_HEIGHT - 100
    bullets.clear()
    score = 0
    asteroids.clear()
    player_health = 5
    level = 1
    damage_per_bullet = 1

# Function to draw the game over screen
def draw_game_over_screen():
    game_over_text = font.render("Game Over!", True, TEXT_COLOR)
    screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))

# Function to detect thumb movement
def detect_thumb_movement(results):
    global player_pos

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
            thumb_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_MCP]
            thumb_distance = thumb_tip.x - thumb_mcp.x
            if thumb_distance > 0.01:
                player_pos[0] += player_speed
            elif thumb_distance < -0.01:
                player_pos[0] -= player_speed
            player_pos[0] = max(0, min(SCREEN_WIDTH - player_width, player_pos[0]))

# Game loop
clock = pygame.time.Clock()
frame_count = 0
shoot_timer = 0
shoot_delay = 10

while True:
    success, image = cap.read()
    if not success:
        print("Error: Could not read from camera.")
        break

    image = cv2.flip(image, 1)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands.process(image_rgb)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            cap.release()
            cv2.destroyAllWindows()
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN and game_over:
            if event.button == 1:
                reset_game()

    if not game_over:
        screen.fill(BACKGROUND_COLOR)
        detect_thumb_movement(results)
        if frame_count % asteroid_spawn_rate == 0:
            asteroids.append(create_asteroid())
        if shoot_timer >= shoot_delay:
            create_bullet()
            shoot_timer = 0
        else:
            shoot_timer += 1
        if move_asteroids():
            game_over = True
        move_bullets()
        draw_player()
        draw_bullets()
        draw_asteroids()
        draw_score_health()
    else:
        draw_game_over_screen()

    pygame.display.flip()
    cv2.imshow('Hand Tracking', image)
    frame_count += 1

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
pygame.quit()
