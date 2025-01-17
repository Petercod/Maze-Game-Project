import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
CELL_SIZE = 40  # Size of each maze cell
COLUMNS = WIDTH // CELL_SIZE
ROWS = HEIGHT // CELL_SIZE

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Maze Game with Maze Generator")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GOLD = (255, 215, 0)

# Clock for controlling the frame rate
clock = pygame.time.Clock()

# Player settings
player_size = CELL_SIZE // 2
player_pos = [CELL_SIZE // 4, CELL_SIZE // 4]
player_speed = 5

# Maze and walls
maze = []
walls = []
coins = []

# Directions for maze generation
DIRECTIONS = [(0, -1), (0, 1), (-1, 0), (1, 0)]

def generate_maze():
    """Generates a maze using recursive backtracking."""
    stack = []
    visited = [[False] * COLUMNS for _ in range(ROWS)]

    def is_valid(x, y):
        return 0 <= x < COLUMNS and 0 <= y < ROWS and not visited[y][x]

    def carve_passage(cx, cy):
        visited[cy][cx] = True
        stack.append((cx, cy))

        while stack:
            x, y = stack[-1]
            neighbors = [(x + dx, y + dy) for dx, dy in DIRECTIONS if is_valid(x + dx, y + dy)]

            if neighbors:
                nx, ny = random.choice(neighbors)
                visited[ny][nx] = True
                maze[y][x].remove_wall(nx - x, ny - y)
                maze[ny][nx].remove_wall(x - nx, y - ny)
                stack.append((nx, ny))
            else:
                stack.pop()

    # Initialize maze grid
    for row in range(ROWS):
        maze.append([Cell(x, row) for x in range(COLUMNS)])

    # Start generating maze
    carve_passage(0, 0)

def create_walls_from_maze():
    """Convert maze to walls."""
    global walls, coins
    walls = []
    coins = []
    for row in maze:
        for cell in row:
            if cell.top_wall:
                walls.append(pygame.Rect(cell.x * CELL_SIZE, cell.y * CELL_SIZE, CELL_SIZE, 2))
            if cell.left_wall:
                walls.append(pygame.Rect(cell.x * CELL_SIZE, cell.y * CELL_SIZE, 2, CELL_SIZE))

            # Randomly place coins in the open areas
            if random.random() < 0.1:  # 10% chance to place a coin
                coins.append(pygame.Rect(
                    cell.x * CELL_SIZE + CELL_SIZE // 4,
                    cell.y * CELL_SIZE + CELL_SIZE // 4,
                    CELL_SIZE // 2, CELL_SIZE // 2
                ))

class Cell:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.top_wall = True
        self.left_wall = True

    def remove_wall(self, dx, dy):
        """Remove a wall based on direction."""
        if dx == -1:
            self.left_wall = False
        elif dx == 1:
            maze[self.y][self.x + 1].left_wall = False
        elif dy == -1:
            self.top_wall = False
        elif dy == 1:
            maze[self.y + 1][self.x].top_wall = False

# Generate the maze
generate_maze()
create_walls_from_maze()

# Goal settings
goal = pygame.Rect(WIDTH - CELL_SIZE + CELL_SIZE // 4, HEIGHT - CELL_SIZE + CELL_SIZE // 4, CELL_SIZE // 2, CELL_SIZE // 2)
score = 0

def check_collision(player_rect, walls):
    for wall in walls:
        if player_rect.colliderect(wall):
            return True
    return False

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Player movement
    keys = pygame.key.get_pressed()
    new_player_pos = player_pos.copy()

    if keys[pygame.K_UP]:
        new_player_pos[1] -= player_speed
    if keys[pygame.K_DOWN]:
        new_player_pos[1] += player_speed
    if keys[pygame.K_LEFT]:
        new_player_pos[0] -= player_speed
    if keys[pygame.K_RIGHT]:
        new_player_pos[0] += player_speed

    # Create a temporary player rect to check for collisions
    temp_player_rect = pygame.Rect(new_player_pos[0], new_player_pos[1], player_size, player_size)

    # Move the player only if there is no collision
    if not check_collision(temp_player_rect, walls):
        player_pos = new_player_pos

    # Create player rect for drawing
    player_rect = pygame.Rect(player_pos[0], player_pos[1], player_size, player_size)

    # Check collision with coins
    for coin in coins[:]:
        if player_rect.colliderect(coin):
            coins.remove(coin)
            score += 1
            print(f"Score: {score}")

    # Check if player reaches the goal
    if player_rect.colliderect(goal):
        print("You Win!")
        print(f"Final Score: {score}")
        running = False

    # Draw everything
    screen.fill(WHITE)
    pygame.draw.rect(screen, RED, player_rect)  # Player
    for wall in walls:
        pygame.draw.rect(screen, BLACK, wall)  # Walls
    for coin in coins:
        pygame.draw.rect(screen, GOLD, coin)  # Coins
    pygame.draw.rect(screen, BLUE, goal)  # Goal

    # Display score
    font = pygame.font.SysFont(None, 36)
    score_text = font.render(f"Score: {score}", True, BLACK)
    screen.blit(score_text, (10, 10))

    pygame.display.flip()
    clock.tick(30)  # 30 FPS

pygame.quit()
sys.exit()
