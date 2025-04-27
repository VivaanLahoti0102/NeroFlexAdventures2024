import cv2
import mediapipe as mp
import pygame
import random
import time                                                                                          

# Initialize pygame
pygame.init()

# Game settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PLAYER_WIDTH = 50
PLAYER_HEIGHT = 80  # Character height
OBSTACLE_WIDTH = 50  # Taco width
OBSTACLE_HEIGHT = 30  # Taco height
BASE_OBSTACLE_SPEED = 5  # Taco speed
FPS = 30
GROUND_COLOR = (80, 80, 80)

# Border settings
BORDER_WIDTH = 10
BORDER_COLOR = (0, 0, 0)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
TACO_COLOR = (255, 215, 0)

# Set up the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Taco Eating Game")

# Initialize clock
clock = pygame.time.Clock()

# Load MediaPipe for wrist tracking
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()

# Camera capture
cap = cv2.VideoCapture(0)

# Game variables
player_x = SCREEN_WIDTH // 2 - PLAYER_WIDTH // 2
player_y = SCREEN_HEIGHT - PLAYER_HEIGHT - 50
player_speed = 5  # Default speed

# Obstacles (Tacos)
obstacles = []
obstacle_spawn_time = 0

# Score, tacos eaten, and game over state
score = 0
tacos_eaten = 0
game_over = False

# Game state control
game_started = False

def create_obstacle():
    x = random.randint(50, SCREEN_WIDTH - 50 - OBSTACLE_WIDTH)
    y = -OBSTACLE_HEIGHT
    return {'rect': pygame.Rect(x, y, OBSTACLE_WIDTH, OBSTACLE_HEIGHT)}

def draw_player():
    pygame.draw.rect(screen, GREEN, (player_x, player_y, PLAYER_WIDTH, PLAYER_HEIGHT))
    head_radius = 15
    pygame.draw.circle(screen, (0, 0, 0), (player_x + PLAYER_WIDTH // 2, player_y - head_radius), head_radius)
    pygame.draw.rect(screen, RED, (player_x + PLAYER_WIDTH // 2 - 10, player_y - head_radius // 2, 20, 10))

def draw_obstacles():
    for obstacle in obstacles:
        pygame.draw.polygon(screen, TACO_COLOR, [(obstacle['rect'].x, obstacle['rect'].y + OBSTACLE_HEIGHT),
                                                 (obstacle['rect'].x + OBSTACLE_WIDTH // 2, obstacle['rect'].y),
                                                 (obstacle['rect'].x + OBSTACLE_WIDTH, obstacle['rect'].y + OBSTACLE_HEIGHT)])

def move_obstacles():
    for obstacle in obstacles:
        obstacle['rect'].y += BASE_OBSTACLE_SPEED
        if obstacle['rect'].y > SCREEN_HEIGHT:
            obstacles.remove(obstacle)

def check_collision():
    global tacos_eaten, score
    mouth_rect = pygame.Rect(player_x + PLAYER_WIDTH // 2 - 10, player_y - 15, 20, 10)
    for obstacle in obstacles:
        if mouth_rect.colliderect(obstacle['rect']):
            obstacles.remove(obstacle)
            tacos_eaten += 1
            if tacos_eaten % 5 == 0:
                score += 1

def process_wrist_movement(results):
    global player_x
    if results.multi_hand_landmarks:
        hand_landmarks = results.multi_hand_landmarks[0]
        wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
        index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
        movement = index_tip.y - wrist.y

        if movement > 0.05:
            player_x += 5
        elif movement < -0.05:
            player_x -= 5

        player_x = max(BORDER_WIDTH, min(SCREEN_WIDTH - PLAYER_WIDTH - BORDER_WIDTH, player_x))

def start_screen():
    screen.fill(WHITE)
    font = pygame.font.Font(None, 74)
    text = font.render("Taco Eating Game", True, BLUE)
    screen.blit(text, (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 200))

    button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50, 200, 100)
    pygame.draw.rect(screen, GREEN, button_rect)
    font = pygame.font.Font(None, 50)
    button_text = font.render("Start", True, BLACK)
    screen.blit(button_text, (SCREEN_WIDTH // 2 - 40, SCREEN_HEIGHT // 2 - 20))

    pygame.display.flip()
    return button_rect

running = True
while running:
    if not game_started:
        button_rect = start_screen()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos):
                    game_started = True
        continue

    success, image = cap.read()
    if not success:
        print("Ignoring empty camera frame.")
        continue

    image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
    results = hands.process(image)

    cv2.imshow("Hand Tracking", cv2.cvtColor(image, cv2.COLOR_RGB2BGR))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    process_wrist_movement(results)
    move_obstacles()
    check_collision()

    if time.time() - obstacle_spawn_time > 1:
        obstacles.append(create_obstacle())
        obstacle_spawn_time = time.time()

    screen.fill(WHITE)
    pygame.draw.rect(screen, GROUND_COLOR, (0, SCREEN_HEIGHT - 50, SCREEN_WIDTH, 50))
    draw_player()
    draw_obstacles()
    
    font = pygame.font.Font(None, 36)
    score_text = font.render(f"Score: {score}", True, BLACK)
    screen.blit(score_text, (10, 10))

    pygame.display.flip()
    clock.tick(FPS)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
pygame.quit()
