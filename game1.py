import cv2  # Import OpenCV
import mediapipe as mp
import pygame
import math
import random
import time  # For adding a delay

# Initialize pygame
pygame.init()

# Set up the display
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pop the Lock - Hand Gesture")

# Define colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (100, 100, 100)

# Game settings
LOCK_RADIUS = 100
BAR_LENGTH = 150
BAR_WIDTH = 30 
bar_angle = 0
bar_speed = 0.05  # Adjusted speed of the rotating bar
target_angle = random.uniform(0, 2 * math.pi)
target_range = 0.3  # Increased width of the target zone
level = 1
score = 0
high_score = 0  # Initialize high score
game_over = False
game_started = False  # Game will start after clicking Start button

# Grace period settings
grace_period = 1.0  # Grace period in seconds
grace_timer = 0.0  # Timer for the grace period

# Button settings
BUTTON_WIDTH = 200
BUTTON_HEIGHT = 80

# Initialize Mediapipe
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

# Function to calculate the Euclidean distance between two points
def calculate_distance(landmark1, landmark2):
    return math.sqrt((landmark1.x - landmark2.x) ** 2 + (landmark1.y - landmark2.y) ** 2)

# Function to detect if the hand is making a fist
def is_fist(hand_landmarks):
    thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
    index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
    middle_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
    ring_tip = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP]
    pinky_tip = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP]
    
    index_base = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_MCP]
    middle_base = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP]
    ring_base = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_MCP]
    pinky_base = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_MCP]

    index_distance = calculate_distance(index_tip, index_base)
    middle_distance = calculate_distance(middle_tip, middle_base)
    ring_distance = calculate_distance(ring_tip, ring_base)
    pinky_distance = calculate_distance(pinky_tip, pinky_base)

    fist_threshold = 0.15
    return (index_distance < fist_threshold and
            middle_distance < fist_threshold and
            ring_distance < fist_threshold and
            pinky_distance < fist_threshold)

# Open the webcam
cap = cv2.VideoCapture(0)

# Mediapipe hand detection
hands = mp_hands.Hands()

# Function to check if the bar is in the target range
def in_target_range(bar_angle, target_angle, target_range):
    return abs(bar_angle - target_angle) < target_range or abs(bar_angle - target_angle) > 2 * math.pi - target_range

# Function to draw a button
def draw_button(text, x, y, width, height, color, text_color):
    pygame.draw.rect(screen, color, (x, y, width, height))
    font = pygame.font.Font(None, 36)
    button_text = font.render(text, True, text_color)
    screen.blit(button_text, (x + (width - button_text.get_width()) // 2, y + (height - button_text.get_height()) // 2))

# Function to reset the game
def reset_game():
    global bar_angle, bar_speed, target_angle, target_range, level, score, game_over, grace_timer
    bar_angle = 0
    bar_speed = 0.05
    target_angle = random.uniform(0, 2 * math.pi)
    target_range = 0.3
    level = 1
    score = 0
    game_over = False
    grace_timer = 0.0

# Main game loop
clock = pygame.time.Clock()  # To manage frame rate
running = True
while running:
    success, image = cap.read()
    if not success:
        print("Ignoring empty camera frame.")
        continue
    
    # Flip the image and process it with Mediapipe
    image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
    results = hands.process(image)

    # Clear the screen
    screen.fill(WHITE)

    if not game_started:
        # Display start button
        draw_button("Start", SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2, SCREEN_HEIGHT // 2 - BUTTON_HEIGHT // 2, BUTTON_WIDTH, BUTTON_HEIGHT, GREEN, WHITE)
        
        # Check for mouse click to start the game
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2 <= mouse_x <= SCREEN_WIDTH // 2 + BUTTON_WIDTH // 2 and SCREEN_HEIGHT // 2 - BUTTON_HEIGHT // 2 <= mouse_y <= SCREEN_HEIGHT // 2 + BUTTON_HEIGHT // 2:
                    game_started = True  # Start the game after clicking the button
            if event.type == pygame.QUIT:
                running = False

    elif not game_over:
        # Update the rotating bar
        bar_angle += bar_speed
        if bar_angle > 2 * math.pi:
            bar_angle -= 2 * math.pi

        # Draw the lock body (yellow circle)
        pygame.draw.circle(screen, YELLOW, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), LOCK_RADIUS)

        # Draw the lock shackle (gray rectangle to resemble a lock shackle)
        pygame.draw.rect(screen, GRAY, (SCREEN_WIDTH // 2 - 40, SCREEN_HEIGHT // 2 - LOCK_RADIUS - 30, 80, 30))

        # Draw the rotating bar (red line)
        bar_x = SCREEN_WIDTH // 2 + int(LOCK_RADIUS * math.cos(bar_angle))
        bar_y = SCREEN_HEIGHT // 2 + int(LOCK_RADIUS * math.sin(bar_angle))
        pygame.draw.line(screen, RED, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), (bar_x, bar_y), BAR_WIDTH)

        # Draw the target zone (wider for easier hits)
        target_x = SCREEN_WIDTH // 2 + int(LOCK_RADIUS * math.cos(target_angle))
        target_y = SCREEN_HEIGHT // 2 + int(LOCK_RADIUS * math.sin(target_angle))
        pygame.draw.line(screen, BLUE, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), (target_x, target_y), BAR_WIDTH)

        # Handle grace period
        if grace_timer > 0:
            grace_timer -= clock.get_time() / 1000  # Subtract the frame time in seconds
        else:
            # If hand landmarks are detected
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    # Draw hand landmarks on the image for visualization
                    mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                    # Check if the hand is making a fist
                    if is_fist(hand_landmarks):
                        # Check if the bar is in the target range
                        if in_target_range(bar_angle, target_angle, target_range):
                            score += 1
                            level += 1
                            target_angle = random.uniform(0, 2 * math.pi)  # Generate a new target zone
                            bar_speed += 0.005  # Increase the bar speed slowly
                            grace_timer = grace_period  # Reset grace timer
                        else:
                            game_over = True
                            # Update high score if current score is higher
                            if score > high_score:
                                high_score = score

    # Display game info
    font = pygame.font.Font(None, 36)
    score_text = font.render(f"Score: {score}", True, (0, 0, 0))  # (0, 0, 0) is black in RGB
    high_score_text = font.render(f"High Score: {high_score}", True, (0, 0, 0))
    screen.blit(score_text, (10, 10))
    screen.blit(high_score_text, (10, 40))
    
    if game_over:
        game_over_text = font.render("Game Over!", True, RED)
        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2))
        draw_button("Restart", SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2, SCREEN_HEIGHT // 2 + 40, BUTTON_WIDTH, BUTTON_HEIGHT, GREEN, WHITE)

        # Check for restart button click
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2 <= mouse_x <= SCREEN_WIDTH // 2 + BUTTON_WIDTH // 2 and SCREEN_HEIGHT // 2 + 40 <= mouse_y <= SCREEN_HEIGHT // 2 + 40 + BUTTON_HEIGHT:
                    reset_game()  # Reset the game
            if event.type == pygame.QUIT:
                running = False

    # Update the display
    pygame.display.flip()

    # Show hand tracking image in OpenCV window with landmarks
    cv2.imshow("Hand Tracking", image)

    # Event handling for quitting the game
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Limit frame rate to 30 FPS
    clock.tick(30)

# Release resources
cap.release()
cv2.destroyAllWindows()  # Close the OpenCV window
pygame.quit()
