import pgzrun

# Window settings
WIDTH = 800
HEIGHT = 600
TITLE = "Hello World - Pygame Zero"

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 100, 255)


def draw():
    """Draw function - called every frame to render the screen"""
    # Clear the screen with a dark blue background
    screen.fill(BLUE)

    # Draw "Hello World" text in the center of the screen
    screen.draw.text(
        "Hello World!", center=(WIDTH // 2, HEIGHT // 2), fontsize=60, color=WHITE
    )

    # Draw a subtitle
    screen.draw.text(
        "Welcome to Pygame Zero!",
        center=(WIDTH // 2, HEIGHT // 2 + 80),
        fontsize=30,
        color=WHITE,
    )


def update(dt):
    """Update function - called every frame to update game logic"""
    # This function is called every frame with the time delta
    # For a simple hello world, we don't need any updates
    pass


def on_key_down(key):
    """Handle key press events"""
    if key == keys.ESCAPE:
        # Exit the game when ESC is pressed
        exit()
    elif key == keys.SPACE:
        # Print a message to the console when space is pressed
        print("Space key pressed!")


pgzrun.go()
