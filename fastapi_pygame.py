import threading
import asyncio
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn
import pygame

app = FastAPI()

# -------------------------
# Game state
# -------------------------
ball_pos = [300, 300]
ball_vel = [0, 0]
on_ground = True

# Control commands
command_queue = []

# -------------------------
# Pygame loop
# -------------------------
def game_loop():
    global ball_pos, ball_vel, on_ground
    import random
    pygame.init()
    screen = pygame.display.set_mode((600, 400))
    pygame.display.set_caption("API Controlled Ball")
    clock = pygame.time.Clock()
    gravity = 1
    floor_y = 350
    ball_radius = 20
    # Generate moving stars (add speed)
    stars = [[random.randint(0, 600), random.randint(0, 200), random.uniform(0.5, 2.0)] for _ in range(10)]
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        # Handle commands
        while command_queue:
            cmd = command_queue.pop(0)
            if cmd == "move_left":
                ball_vel[0] = -5
            elif cmd == "move_right":
                ball_vel[0] = 5
            elif cmd == "jump":
                if on_ground:
                    ball_vel[1] = -15
                    on_ground = False
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
        # Draw vertical gradient background
        for y in range(400):
            color = (
                30 + int(40 * y / 400),
                30 + int(60 * y / 400),
                60 + int(80 * y / 400)
            )
            pygame.draw.line(screen, color, (0, y), (600, y))
        # Move and draw stars
        for star in stars:
            star[0] -= star[2]  # Move left by speed
            if star[0] < 0:
                star[0] = 600
                star[1] = random.randint(0, 200)
                star[2] = random.uniform(0.5, 2.0)
            pygame.draw.circle(screen, (255, 255, 200), (int(star[0]), int(star[1])), 2)
        # Draw ground
        pygame.draw.rect(screen, (60, 180, 75), (0, floor_y, 600, 400 - floor_y))
        # Draw ball
        pygame.draw.circle(screen, (200, 50, 50), ball_pos, ball_radius)
        pygame.display.flip()
        clock.tick(30)
    pygame.quit()

def start_game_loop():
    t = threading.Thread(target=game_loop, daemon=True)
    t.start()

# -------------------------
# FastAPI endpoints
# -------------------------
@app.on_event("startup")
def on_startup():
    start_game_loop()

@app.post("/move_left")
def move_left():
    command_queue.append("move_left")
    return JSONResponse({"status": "Ball moving left"})

@app.post("/move_right")
def move_right():
    command_queue.append("move_right")
    return JSONResponse({"status": "Ball moving right"})

@app.post("/jump")
def jump():
    command_queue.append("jump")
    return JSONResponse({"status": "Ball jumped (if on ground)"})

if __name__ == "__main__":
    uvicorn.run("fastapi_pygame:app", host="127.0.0.1", port=8000, reload=False)
