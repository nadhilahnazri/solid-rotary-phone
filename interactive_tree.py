import pygame
import math
import random

# Recursive function to draw a realistic tree
def draw_realistic_tree(screen, x, y, angle, length, depth, thickness):
    if depth == 0:
        # Draw leaves at the end of branches
        leaf_color = (34, random.randint(100, 180), 34)  # Shades of green
        pygame.draw.circle(screen, leaf_color, (int(x), int(y)), random.randint(3, 6))
        return

    # Calculate the end point of the branch
    x2 = x + length * math.cos(math.radians(angle))
    y2 = y - length * math.sin(math.radians(angle))

    # Draw the branch
    branch_color = (139, 69, 19)  # Brown for the trunk
    pygame.draw.line(screen, branch_color, (x, y), (x2, y2), thickness)

    # Randomize angles and lengths for natural branching
    angle_variation = random.uniform(-10, 10)
    length_variation = random.uniform(-5, 5)

    # Recursive calls for left and right branches
    draw_realistic_tree(
        screen, x2, y2, angle - 20 + angle_variation, length * 0.7 + length_variation, depth - 1, max(1, thickness - 1)
    )
    draw_realistic_tree(
        screen, x2, y2, angle + 20 + angle_variation, length * 0.7 + length_variation, depth - 1, max(1, thickness - 1)
    )

# Pygame setup for tree rendering
def run_realistic_tree():
    pygame.init()

    # Set up display
    screen_width, screen_height = 800, 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Realistic 2D Tree")

    # Colors and clock
    background_color = (255, 255, 255)  # White background
    clock = pygame.time.Clock()

    # Tree state variables
    running = True
    depth = 5  # Default depth for the tree

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and depth < 15:  # Increase depth
                    depth += 1
                elif event.key == pygame.K_DOWN and depth > 1:  # Decrease depth
                    depth -= 1

        # Clear the screen
        screen.fill(background_color)

        # Draw the tree
        draw_realistic_tree(screen, screen_width // 2, screen_height - 50, -90, 100, depth, 10)

        # Display instructions
        font = pygame.font.Font(None, 30)
        text = font.render("Press UP to grow, DOWN to shrink, ESC to quit", True, (0, 0, 0))
        screen.blit(text, (10, 10))

        # Update the display
        pygame.display.flip()
        clock.tick(30)

    pygame.quit()

# Run the realistic tree rendering
run_realistic_tree()
