import random
from typing import List, Tuple

import pgzrun
import pygame

from ems import Component, System, World

# region Constants

# Window settings
WIDTH = 800
HEIGHT = 600
TITLE = "Wibblo"

# Constants
TILE_SIZE = 64
PLAYER_WIDTH = 70
PLAYER_HEIGHT = 94
BACKGROUND_WIDTH = 640
BACKGROUND_HEIGHT = 480
GRAVITY = 1200.0
JUMP_FORCE = -500.0
MOVE_SPEED = 300.0

# endregion

# region Components


class Position(Component):
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y


class Velocity(Component):
    def __init__(self, vx: float = 0, vy: float = 0):
        self.vx = vx
        self.vy = vy


class Gravity(Component):
    """Component for entities affected by gravity"""

    def __init__(self, g: float = 9.8):
        self.g = g


class Sprite(Component):
    def __init__(
        self,
        texture: str,
        width: int,
        height: int,
        layer: int = 0,
        offset: Tuple[int, int] = (0, 0),
        anchor: Tuple[str, str] = ("left", "top"),
    ):
        self.texture = texture
        self.width = width
        self.height = height
        self.layer = layer
        self.offset = offset
        self.anchor = anchor


class Animation(Component):
    def __init__(
        self,
        frames: List[str],
        fps: float = 10,
        frame_index: int = 0,
    ):
        self.frames = frames
        self.fps = fps
        self.frame_index = frame_index
        self.timer = 0


class WalkingAnimation(Animation):
    pass


class FlipX(Component):
    def __init__(self, flip: bool = False):
        self.flip = flip


class Player(Component):
    def __init__(self):
        self.on_ground = True
        self.at_boundary = False
        self.walking = False


class CollisionTarget(Component):
    def __init__(self, width: float, height: float):
        self.width = width
        self.height = height


class Impactor(Component):
    pass


class Controls(Component):
    def __init__(self):
        self.left = False
        self.right = False
        self.jump = False


# endregion


# region Systems


class GravitySystem(System):
    def update(self, dt: float):
        affected_entities = self.world.get_matching_entities({Velocity, Gravity})

        for entity in affected_entities:
            velocity = self.world.get_component(entity, Velocity)
            gravity = self.world.get_component(entity, Gravity)

            if not velocity or not gravity:
                continue

            velocity.vy += gravity.g * dt


class MovementSystem(System):
    def update(self, dt: float):
        movable_entities = self.world.get_matching_entities({Position, Velocity})

        for entity in movable_entities:
            position = self.world.get_component(entity, Position)
            velocity = self.world.get_component(entity, Velocity)

            if not (position and velocity):
                continue

            position.x += velocity.vx * dt
            position.y += velocity.vy * dt


class CollisionSystem(System):
    def update(self, dt: float):
        # Entities that can move and collide
        impactors = self.world.get_matching_entities(
            {Impactor, Position, CollisionTarget, Velocity}
        )
        # All collision targets (including ground tiles and possibly the player)
        targets = self.world.get_matching_entities({Position, CollisionTarget})

        for entity in impactors:
            pos = self.world.get_component(entity, Position)
            col = self.world.get_component(entity, CollisionTarget)
            vel = self.world.get_component(entity, Velocity)
            player = self.world.get_component(entity, Player)

            if not (pos and col and vel):
                continue

            on_ground = False

            # World boundary collisions (left/right)
            if pos.x < 0:
                pos.x = 0
                vel.vx = 0
            elif pos.x + col.width > WIDTH:
                pos.x = WIDTH - col.width
                vel.vx = 0

            # World boundary collisions (top/bottom)
            if pos.y < 0:
                pos.y = 0
                vel.vy = 0
            elif pos.y + col.height > HEIGHT:
                pos.y = HEIGHT - col.height
                vel.vy = 0
                on_ground = True

            # Collide with other targets (tiles, etc.)
            for target in targets:
                if target is entity:
                    continue

                tpos = self.world.get_component(target, Position)
                tcol = self.world.get_component(target, CollisionTarget)
                if not (tpos and tcol):
                    continue

                # AABB overlap test using center/half-size method
                cx_a = pos.x + col.width / 2
                cy_a = pos.y + col.height / 2
                cx_b = tpos.x + tcol.width / 2
                cy_b = tpos.y + tcol.height / 2

                dx = cx_a - cx_b
                px = (col.width / 2 + tcol.width / 2) - abs(dx)
                if px <= 0:
                    continue

                dy = cy_a - cy_b
                py = (col.height / 2 + tcol.height / 2) - abs(dy)
                if py <= 0:
                    continue

                # Resolve on the axis with the least penetration
                if px < py:
                    # Horizontal resolution
                    if dx > 0:
                        pos.x += px
                    else:
                        pos.x -= px
                    vel.vx = 0
                else:
                    # Vertical resolution
                    if dy > 0:
                        # Impactor is below target
                        pos.y += py
                        vel.vy = 0
                    else:
                        # Impactor is above target -> land on it
                        pos.y -= py
                        vel.vy = 0
                        on_ground = True

            if player is not None:
                player.on_ground = on_ground


class ControlsSystem(System):
    def update(self, dt: float):
        player = self.world.get_matching_entities(
            {
                Player,
                Position,
                Velocity,
                CollisionTarget,
                FlipX,
                WalkingAnimation,
                Controls,
                Sprite,
            }
        )[0]

        if not player:
            return

        player_comp = self.world.get_component(player, Player)
        pos = self.world.get_component(player, Position)
        vel = self.world.get_component(player, Velocity)
        collision_target = self.world.get_component(player, CollisionTarget)
        flip_comp = self.world.get_component(player, FlipX)
        controls = self.world.get_component(player, Controls)

        # Update input state

        controls.left = keyboard.left or keyboard.a
        controls.right = keyboard.right or keyboard.d
        controls.jump = keyboard.space or keyboard.w

        # Handle movement

        vel.vx = 0

        if controls.left:
            vel.vx = -MOVE_SPEED
            flip_comp.flip = True
        elif controls.right:
            vel.vx = MOVE_SPEED
            flip_comp.flip = False

        player_comp.walking = vel.vx != 0
        player_comp.at_boundary = pos.x == 0 or pos.x + collision_target.width == WIDTH

        # Handle jump

        if controls.jump and player_comp.on_ground:
            vel.vy = JUMP_FORCE
            player_comp.on_ground = False

        # Update sprite

        sprite = self.world.get_component(player, Sprite)
        walking_anim = self.world.get_component(player, WalkingAnimation)

        if not player_comp.on_ground:
            sprite.texture = "p2_jump"
        elif player_comp.at_boundary or not player_comp.walking:
            sprite.texture = "p2_stand"
        else:
            sprite.texture = f"p2_walk{walking_anim.frame_index + 1:02d}"


class WalkingAnimationSystem(System):
    def update(self, dt: float):
        animated = self.world.get_matching_entities({WalkingAnimation})

        for entity in animated:
            anim = self.world.get_component(entity, WalkingAnimation)

            if not anim.frames:
                continue

            frame_time = 1.0 / max(anim.fps, 0.0001)
            anim.timer += dt
            while anim.timer >= frame_time:
                anim.timer -= frame_time
                anim.frame_index = (anim.frame_index + 1) % (len(anim.frames) - 1)


class RenderSystem(System):
    def __init__(self, world):
        super().__init__(world)

    def draw(self):
        drawable_entities = self.world.get_matching_entities({Position, Sprite})
        sprites = []

        for entity in drawable_entities:
            sprite = self.world.get_component(entity, Sprite)
            position = self.world.get_component(entity, Position)
            flipx = self.world.get_component(entity, FlipX)
            sprites.append((sprite.layer, position, sprite, flipx))

        # Sort by layer
        sprites.sort(key=lambda item: item[0])

        for _, pos, sprite, flipx in sprites:
            texture = getattr(images, sprite.texture, None)

            if not texture:
                screen.draw.rect(
                    Rect(pos.x, pos.y, sprite.width, sprite.height),
                    (255, 0, 255),
                )
                continue

            if flipx and flipx.flip:
                texture = pygame.transform.flip(texture, True, False)

            offset_x = sprite.offset[0]
            offset_y = sprite.offset[1]

            if flipx and flipx.flip:
                offset_x = -offset_x

            screen.blit(texture, (pos.x + offset_x, pos.y + offset_y))


# endregion


# region Game


class Game:
    def __init__(self):
        self.world = World()
        self.player = None
        self.input = Controls()

        # Add systems
        self.world.add_system(ControlsSystem(self.world))
        self.world.add_system(GravitySystem(self.world))
        self.world.add_system(MovementSystem(self.world))
        self.world.add_system(CollisionSystem(self.world))
        self.world.add_system(WalkingAnimationSystem(self.world))
        self.world.add_system(RenderSystem(self.world))

        self._create_background()
        self._create_map()
        self._create_player()

    def update(self, dt):
        self.world.update(dt)

    def draw(self):
        self.world.draw()

    def _get_random_dirt_texture(self):
        roll = random.random()
        if roll < 0.09:
            return "tile_green_08"
        elif roll < 0.2:
            return "tile_green_17"
        return "tile_green_03"

    def _create_background(self):
        """
        Repeat background, hills, and tiles to fill the screen
        """
        width = BACKGROUND_WIDTH
        height = BACKGROUND_HEIGHT
        cols = WIDTH // width + 1
        rows = HEIGHT // height + 1

        for r in range(rows):
            for c in range(cols):
                x = c * width
                y = r * height

                bg = self.world.create_entity()
                self.world.add_component(bg, Position(x, y))
                self.world.add_component(
                    bg, Sprite("set2_background", width, height, layer=-30)
                )

                hills = self.world.create_entity()
                self.world.add_component(hills, Position(x, y))
                self.world.add_component(
                    hills, Sprite("set2_hills", width, height, layer=-20)
                )

                tiles = self.world.create_entity()
                self.world.add_component(tiles, Position(x, y))
                self.world.add_component(
                    tiles, Sprite("set2_tiles", width, height, layer=-10)
                )

    def _create_map(self):
        """
        Create a platform of grass starting a little below the middle (1 tile on top),
        and fill all rows below with dirt (with rare variations).
        """
        random.seed(42)

        cols = WIDTH // TILE_SIZE + 1
        grass_row = (HEIGHT // TILE_SIZE) - 3  # 3 rows above the bottom

        # Create the grass row
        for c in range(cols):
            x = c * TILE_SIZE
            grass = self.world.create_entity()
            self.world.add_component(grass, Position(x, grass_row * TILE_SIZE))
            self.world.add_component(grass, CollisionTarget(TILE_SIZE, TILE_SIZE))
            self.world.add_component(
                grass, Sprite("tile_green_05", TILE_SIZE, TILE_SIZE)
            )

        # Fill the dirt rows below the grass to the bottom of the screen
        for r in range(grass_row + 1, HEIGHT // TILE_SIZE + 1):
            for c in range(cols):
                x = c * TILE_SIZE
                y = r * TILE_SIZE
                dirt = self.world.create_entity()
                self.world.add_component(dirt, Position(x, y))
                self.world.add_component(dirt, CollisionTarget(TILE_SIZE, TILE_SIZE))
                tex = self._get_random_dirt_texture()
                self.world.add_component(dirt, Sprite(tex, TILE_SIZE, TILE_SIZE))

        # Spawn the player on top of the grass, in the middle of the screen
        spawn_x = WIDTH // 2
        spawn_y = grass_row * TILE_SIZE - (PLAYER_HEIGHT // 2) - 1
        self.player_spawn = (spawn_x, spawn_y)

    def _create_player(self):
        self.player = self.world.create_entity()
        spawn_x, spawn_y = getattr(self, "player_spawn")
        self.world.add_component(self.player, Position(spawn_x, spawn_y))
        self.world.add_component(self.player, Velocity(0, 0))
        self.world.add_component(self.player, Gravity(GRAVITY))
        self.world.add_component(self.player, Impactor())
        self.world.add_component(
            self.player, CollisionTarget(PLAYER_WIDTH, PLAYER_HEIGHT)
        )
        self.world.add_component(
            self.player,
            Sprite(
                "p2_stand",
                PLAYER_WIDTH,
                PLAYER_HEIGHT,
                anchor=("center", "bottom"),
                offset=(0, 3),
                layer=1000,
            ),
        )
        self.world.add_component(self.player, Player())
        self.world.add_component(self.player, self.input)
        self.world.add_component(self.player, FlipX())
        self.world.add_component(
            self.player,
            WalkingAnimation(
                [
                    "p2_stand",
                    "p2_walk01",
                    "p2_walk02",
                    "p2_walk03",
                    "p2_walk04",
                    "p2_walk05",
                    "p2_walk06",
                    "p2_walk07",
                    "p2_walk08",
                    "p2_walk09",
                    "p2_walk10",
                    "p2_walk11",
                ],
                fps=24,
            ),
        )


game = Game()


def draw():
    game.draw()


def update(dt):
    game.update(dt)


def on_key_down(key):
    if key == keys.ESCAPE:
        quit()


pgzrun.go()

# endregion
