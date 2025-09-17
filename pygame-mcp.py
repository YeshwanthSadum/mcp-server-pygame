# pygame-mcp.py
import asyncio
import threading
import pygame
from mcp.server.fastmcp import FastMCP

# -------------------------
# Game state
# -------------------------
ball_pos = [300, 300]
ball_vel = [0, 0]
on_ground = True

# -------------------------
# MCP Server
# -------------------------
mcp = FastMCP("ball-server")

@mcp.tool()
async def move_left():
    """Move the ball to the left."""
    ball_vel[0] = -5
    return "Ball moving left"

@mcp.tool()
async def move_right():
    """Move the ball to the right."""
    ball_vel[0] = 5
    return "Ball moving right"

@mcp.tool()
async def jump():
    """Make the ball jump if it's on the ground."""
    global on_ground
    if on_ground:
        ball_vel[1] = -15
        on_ground = False
        return "Ball jumped"
    return "Ball already in air"

# -------------------------
# Pygame loop
# -------------------------
async def game_loop():
    global ball_pos, ball_vel, on_ground

    pygame.init()
    screen = pygame.display.set_mode((600, 400))
    pygame.display.set_caption("MCP Controlled Ball")
    clock = pygame.time.Clock()

    gravity = 1
    floor_y = 350
    ball_radius = 20

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Physics
        ball_pos[0] += ball_vel[0]
        ball_pos[1] += ball_vel[1]

        # Gravity
        ball_vel[1] += gravity

        # Ground collision
        if ball_pos[1] + ball_radius >= floor_y:
            ball_pos[1] = floor_y - ball_radius
            ball_vel[1] = 0
            on_ground = True

        # Friction on x-axis
        ball_vel[0] *= 0.9

        # Drawing
        screen.fill((30, 30, 30))
        pygame.draw.circle(screen, (200, 50, 50), ball_pos, ball_radius)
        pygame.display.flip()
        clock.tick(30)

        # Yield back to event loop
        await asyncio.sleep(0)

    pygame.quit()

# -------------------------
# Main entry
# -------------------------
def start_mcp():
    """Run MCP server in its own thread (blocking)."""
    mcp.run()

async def main():
    # Start MCP in background thread
    threading.Thread(target=start_mcp, daemon=True).start()

    # Run pygame game loop
    await game_loop()

# asyncio.run(main())

if __name__ == "__main__":
    asyncio.run(main())
