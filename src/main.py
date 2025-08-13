import random
from typing import List, Literal, Tuple

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
CURSOR_SIZE = 32
BUTTON_WIDTH = 192
BUTTON_HEIGHT = 64

PLAYER_WIDTH = 70
PLAYER_HEIGHT = 94
BACKGROUND_WIDTH = 640
BACKGROUND_HEIGHT = 480
GRAVITY = 1200.0
JUMP_FORCE = -500.0
MOVE_SPEED = 300.0

# Enemy constants
ENEMY_WIDTH = 64
ENEMY_HEIGHT = 64
ENEMY_BASE_SPEED = 140.0
ENEMY_SPAWN_INTERVAL = 3.0

# Will be set in _create_map()
GROUND_TOP_Y = 0

# Audio toggles
MUSIC_ENABLED = True
SFX_ENABLED = True

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
        mirror_offset_on_flip: bool = True,
    ):
        self.texture = texture
        self.width = width
        self.height = height
        self.layer = layer
        self.offset = offset
        self.anchor = anchor
        self.mirror_offset_on_flip = mirror_offset_on_flip


class Animation(Component):
    def __init__(
        self,
        frames: List[str],
        fps: float = 10,
        frame_index: int = 0,
        frame_sizes: List[Tuple[int, int]] | None = None,
    ):
        self.frames = frames
        self.fps = fps
        self.frame_index = frame_index
        self.timer = 0
        self.frame_sizes = frame_sizes or []


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
        self.was_on_ground = True
        self.landed = False


class Lives(Component):
    def __init__(self, hearts: int = 5):
        self.hearts = hearts
        self.damage_timer = 0.0


class Enemy(Component):
    def __init__(self, speed: float = ENEMY_BASE_SPEED):
        self.base_speed = speed


class Blinky(Component):
    pass


class CollisionTarget(Component):
    def __init__(self, width: float, height: float):
        self.width = width
        self.height = height
        self.colliding = False


class Impactor(Component):
    def __init__(self):
        self.colliding = False
        self.colliding_with_enemy = False
        self.colliding_with_enemy_side = False
        self.colliding_with_enemy_top = False


class Controls(Component):
    def __init__(self):
        self.left = False
        self.right = False
        self.jump = False


class Footsteps(Component):
    def __init__(
        self,
        sound_names: List[str],
        sps: int = 6,  # sound per second
    ):
        self.sound_names = sound_names
        self.sps = sps
        self.timer = 0.0
        self.sound_index = -1
        self.last_index = -1
        self.was_walking = False
        # Dedicated RNG to avoid interference from global seeding elsewhere
        self.rng = random.Random()


class Cursor(Component):
    def __init__(self, cursor_type: Literal["default", "pointer"] = "default"):
        self.cursor_type = cursor_type


class Difficulty(Component):
    def __init__(self):
        self.elapsed = 0.0
        self.speed_multiplier = 1.0


class DeathTimer(Component):
    def __init__(self, time_remaining: float = 1.2):
        self.time_remaining = time_remaining


class Dead(Component):
    pass


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


class CollisionResolutionSystem(System):
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
            imp_comp = self.world.get_component(entity, Impactor)
            enemy_self = self.world.get_component(entity, Enemy)

            if not (pos and col and vel and imp_comp):
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

            # Only resolve against targets if flagged colliding
            if not imp_comp.colliding:
                if player is not None:
                    try:
                        if (not player.was_on_ground) and on_ground:
                            player.landed = True
                        player.was_on_ground = on_ground
                    except AttributeError:
                        player.was_on_ground = on_ground
                        player.landed = False
                    player.on_ground = on_ground
                continue

            # Collide with other targets (tiles, etc.)
            for target in targets:
                if target is entity:
                    continue

                tpos = self.world.get_component(target, Position)
                tcol = self.world.get_component(target, CollisionTarget)
                if not (tpos and tcol):
                    continue

                # Completely skip resolution between player and enemy
                if (player is not None and self.world.get_component(target, Enemy)) or (
                    enemy_self is not None and self.world.get_component(target, Player)
                ):
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
                    # Preserve walking when colliding with enemy as player
                    if (
                        player is not None
                        and self.world.get_component(target, Enemy) is not None
                    ):
                        pass
                    else:
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
                # Detect landing (transition from air to ground)
                try:
                    if (not player.was_on_ground) and on_ground:
                        player.landed = True
                    player.was_on_ground = on_ground
                except AttributeError:
                    # Backward compatibility if fields are missing
                    player.was_on_ground = on_ground
                    player.landed = False
                player.on_ground = on_ground


class CombatSystem(System):
    def update(self, dt: float):
        # Handle player-enemy combat based on flags (no physical resolution)
        players = self.world.get_matching_entities(
            {Player, Impactor, Position, Velocity, CollisionTarget}
        )
        if not players:
            return
        p = players[0]
        ppos = self.world.get_component(p, Position)
        pvel = self.world.get_component(p, Velocity)
        pcol = self.world.get_component(p, CollisionTarget)
        pimp = self.world.get_component(p, Impactor)
        if not (ppos and pvel and pcol and pimp):
            return

        # Stomp kill: player damaging enemy from top only when falling with overlap depth
        if pimp.colliding_with_enemy_top and pvel.vy > 0:
            enemies = self.world.get_matching_entities(
                {Enemy, Position, CollisionTarget}
            )
            for e in enemies:
                epos = self.world.get_component(e, Position)
                ecol = self.world.get_component(e, CollisionTarget)
                if not (epos and ecol):
                    continue
                ax1, ay1 = ppos.x, ppos.y
                ax2, ay2 = ppos.x + pcol.width, ppos.y + pcol.height
                bx1, by1 = epos.x, epos.y
                bx2, by2 = epos.x + ecol.width, epos.y + ecol.height
                if ax1 < bx2 and ax2 > bx1 and ay1 < by2 and ay2 > by1:
                    # Ensure sufficient vertical overlap to count as stomp
                    overlap_y = min(ay2, by2) - max(ay1, by1)
                    min_overlap = min(pcol.height, ecol.height) * 0.1
                    if overlap_y <= min_overlap:
                        continue
                    # Bounce player
                    pvel.vy = JUMP_FORCE * 0.5
                    # Kill enemy and let it fall off-screen
                    tsprite = self.world.get_component(e, Sprite)
                    if tsprite:
                        tsprite.texture = "blinky_dead"
                    self.world.remove_component(e, Enemy)
                    self.world.remove_component(e, WalkingAnimation)
                    self.world.remove_component(e, Impactor)
                    self.world.remove_component(e, CollisionTarget)
                    tvel = self.world.get_component(e, Velocity)
                    if tvel:
                        tvel.vx = 0
                        tvel.vy = 0
                    self.world.add_component(e, Dead())
                    break


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


class FootstepSystem(System):
    def update(self, dt: float):
        entities = self.world.get_matching_entities({Player, Velocity, Footsteps})

        for entity in entities:
            player = self.world.get_component(entity, Player)
            velocity = self.world.get_component(entity, Velocity)
            footsteps = self.world.get_component(entity, Footsteps)

            if not (player and velocity and footsteps):
                continue

            if player.on_ground and player.walking:
                frame_time = 1.0 / max(footsteps.sps, 0.0001)
                footsteps.timer += dt
                # On walking start, play immediately and skip scheduled play this frame
                if not footsteps.was_walking:
                    footsteps.was_walking = True
                    play_footstep_sound(footsteps)
                    footsteps.timer = 0.0
                    continue

                while footsteps.timer >= frame_time:
                    footsteps.timer -= frame_time
                    play_footstep_sound(footsteps)
            else:
                footsteps.timer = 0.0
                footsteps.was_walking = False


class DifficultySystem(System):
    def update(self, dt: float):
        entities = self.world.get_matching_entities({Difficulty})

        if not entities:
            return

        difficulty = entities[0]
        d = self.world.get_component(difficulty, Difficulty)
        d.elapsed += dt
        # Increase speed multiplier slowly over time
        d.speed_multiplier = 1.0 + 0.02 * d.elapsed


class EnemySpawnSystem(System):
    def __init__(self, world):
        super().__init__(world)
        self.timer = 0.0

    def update(self, dt: float):
        self.timer += dt
        if self.timer < ENEMY_SPAWN_INTERVAL:
            return
        self.timer = 0.0

        self._spawn_blinky()

    def _spawn_blinky(self):
        # Spawn one Blinky from either left or right, just outside screen
        side = -1 if random.random() < 0.5 else 1
        if side < 0:
            x = -TILE_SIZE
        else:
            x = WIDTH + TILE_SIZE
        y = max(GROUND_TOP_Y - ENEMY_HEIGHT, 0)

        e = self.world.create_entity()
        self.world.add_component(e, Enemy(ENEMY_BASE_SPEED))
        self.world.add_component(e, Blinky())
        self.world.add_component(e, Position(x, y))
        self.world.add_component(e, Velocity(0, 0))
        self.world.add_component(e, Gravity(GRAVITY))
        self.world.add_component(e, Impactor())
        self.world.add_component(e, CollisionTarget(ENEMY_WIDTH, ENEMY_HEIGHT))
        self.world.add_component(e, FlipX())
        self.world.add_component(
            e,
            Sprite(
                "blinky_walk01",
                ENEMY_WIDTH,
                ENEMY_HEIGHT,
                anchor=("left", "top"),
                offset=(0, 0),
                layer=900,
                mirror_offset_on_flip=False,
            ),
        )
        self.world.add_component(
            e,
            WalkingAnimation(
                [
                    "blinky_walk01",
                    "blinky_walk02",
                    "blinky_walk03",
                ],
                fps=10,
                # Optionally pass explicit frame sizes here if desired
                # frame_sizes=[(32, 44), (32, 42), (49, 38)],
            ),
        )


class EnemyAIChase(System):
    def update(self, dt: float):
        # Find player position
        players = self.world.get_matching_entities({Player, Position})
        if not players:
            return
        player_entity = players[0]
        player_pos = self.world.get_component(player_entity, Position)
        player_col = self.world.get_component(player_entity, CollisionTarget)

        # Difficulty
        mult = 1.0
        diff_ents = self.world.get_matching_entities({Difficulty})
        if diff_ents:
            diff = self.world.get_component(diff_ents[0], Difficulty)
            mult = diff.speed_multiplier

        enemies = self.world.get_matching_entities({Enemy, Position, Velocity, FlipX})
        for e in enemies:
            pos = self.world.get_component(e, Position)
            vel = self.world.get_component(e, Velocity)
            enemy = self.world.get_component(e, Enemy)
            flip = self.world.get_component(e, FlipX)
            ecol = self.world.get_component(e, CollisionTarget)
            if not (pos and vel and enemy):
                continue
            speed = enemy.base_speed * mult
            if pos.x + ENEMY_WIDTH / 2 < player_pos.x:
                vel.vx = speed
                if flip:
                    flip.flip = False
            else:
                vel.vx = -speed
                if flip:
                    flip.flip = True

            # If overlapping the player, stand still (no pushing)
            if ecol and player_col:
                ax1, ay1 = pos.x, pos.y
                ax2, ay2 = pos.x + ecol.width, pos.y + ecol.height
                bx1, by1 = player_pos.x, player_pos.y
                bx2, by2 = (
                    player_pos.x + player_col.width,
                    player_pos.y + player_col.height,
                )
                if ax1 < bx2 and ax2 > bx1 and ay1 < by2 and ay2 > by1:
                    vel.vx = 0


class CollisionDetectionSystem(System):
    def update(self, dt: float):
        # Reset flags
        impactors = self.world.get_matching_entities(
            {Impactor, Position, CollisionTarget}
        )
        targets = self.world.get_matching_entities({Position, CollisionTarget})
        for e in impactors:
            imp = self.world.get_component(e, Impactor)
            if imp:
                imp.colliding = False
                imp.colliding_with_enemy = False
                imp.colliding_with_enemy_side = False
                imp.colliding_with_enemy_top = False
        for t in targets:
            tcol = self.world.get_component(t, CollisionTarget)
            if tcol:
                tcol.colliding = False

        # Mark overlaps
        for e in impactors:
            pos_a = self.world.get_component(e, Position)
            col_a = self.world.get_component(e, CollisionTarget)
            if not (pos_a and col_a):
                continue
            enemy_a = self.world.get_component(e, Enemy)
            imp_a = self.world.get_component(e, Impactor)
            for t in targets:
                if t is e:
                    continue
                pos_b = self.world.get_component(t, Position)
                col_b = self.world.get_component(t, CollisionTarget)
                if not (pos_b and col_b):
                    continue
                ax1, ay1 = pos_a.x, pos_a.y
                ax2, ay2 = pos_a.x + col_a.width, pos_a.y + col_a.height
                bx1, by1 = pos_b.x, pos_b.y
                bx2, by2 = pos_b.x + col_b.width, pos_b.y + col_b.height
                if ax1 < bx2 and ax2 > bx1 and ay1 < by2 and ay2 > by1:
                    # Skip setting flags for enemy colliding with player
                    # to avoid enemy pull and pushing
                    if enemy_a is not None and self.world.get_component(t, Player):
                        continue
                    if imp_a:
                        imp_a.colliding = True
                        is_enemy_b = self.world.get_component(t, Enemy) is not None
                        if is_enemy_b:
                            imp_a.colliding_with_enemy = True
                            # Determine side vs top overlap via axis test
                            cx_a = pos_a.x + col_a.width / 2
                            cy_a = pos_a.y + col_a.height / 2
                            cx_b = pos_b.x + col_b.width / 2
                            cy_b = pos_b.y + col_b.height / 2
                            dx = cx_a - cx_b
                            px = (col_a.width / 2 + col_b.width / 2) - abs(dx)
                            dy = cy_a - cy_b
                            py = (col_a.height / 2 + col_b.height / 2) - abs(dy)
                            # Add small overlap threshold to avoid grazing registering as top
                            min_overlap = min(col_a.height, col_b.height) * 0.1
                            if py < px and dy < 0 and py > min_overlap:
                                imp_a.colliding_with_enemy_top = True
                            elif px < py and px > min_overlap:
                                imp_a.colliding_with_enemy_side = True
                    col_b.colliding = True


class EnemySpriteSystem(System):
    def update(self, dt: float):
        ents = self.world.get_matching_entities({WalkingAnimation, Sprite, Enemy})
        for e in ents:
            anim = self.world.get_component(e, WalkingAnimation)
            sprite = self.world.get_component(e, Sprite)
            col = self.world.get_component(e, CollisionTarget)
            if anim and sprite and anim.frames:
                idx = max(min(anim.frame_index, len(anim.frames) - 1), 0)
                frame_name = anim.frames[idx]
                sprite.texture = frame_name
                # Determine current frame size
                fw = fh = None
                if idx < len(anim.frame_sizes):
                    try:
                        fw, fh = anim.frame_sizes[idx]
                    except Exception:
                        fw = fh = None
                if fw is None or fh is None:
                    tex = getattr(images, frame_name, None)
                    try:
                        fw = tex.get_width()
                        fh = tex.get_height()
                    except Exception:
                        fw, fh = sprite.width, sprite.height
                # Update sprite width/height to match frame
                sprite.width = fw
                sprite.height = fh
                # Center horizontally in collision box; bottom align
                if col:
                    off_x = int((col.width - fw) / 2)
                    off_y = int(col.height - fh)
                    sprite.offset = (off_x, off_y)


class ContactDamageSystem(System):
    def update(self, dt: float):
        # Player damage based on flags with cooldown
        players = self.world.get_matching_entities({Player, Lives, Impactor})
        if not players:
            return
        p = players[0]
        lives = self.world.get_component(p, Lives)
        imp = self.world.get_component(p, Impactor)
        if not (lives and imp):
            return
        # cooldown countdown
        if lives.damage_timer > 0:
            lives.damage_timer = max(0.0, lives.damage_timer - dt)
        # apply damage only for side collisions with enemies
        if (
            imp.colliding_with_enemy
            and imp.colliding_with_enemy_side
            and not imp.colliding_with_enemy_top
            and lives.damage_timer <= 0.0
            and lives.hearts > 0
        ):
            lives.hearts -= 1
            lives.damage_timer = 1.0

        # Transition to game over when lives reach zero
        if lives.hearts <= 0:
            global MENU_STATE
            if MENU_STATE != "game_over":
                MENU_STATE = "game_over"
                _ensure_ui_world()
                reset_ui_for_state()
                apply_music_state()


class LandSoundSystem(System):
    def update(self, dt: float):
        entities = self.world.get_matching_entities({Player, Footsteps})
        for entity in entities:
            player = self.world.get_component(entity, Player)
            footsteps = self.world.get_component(entity, Footsteps)
            if not (player and footsteps):
                continue

            landed = player.landed
            if landed:
                play_footstep_sound(footsteps)
                player.landed = False


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

            if flipx and flipx.flip and sprite.mirror_offset_on_flip:
                offset_x = -offset_x

            screen.blit(texture, (pos.x + offset_x, pos.y + offset_y))


class HUDSystem(System):
    def __init__(self, world):
        super().__init__(world)

    def draw(self):
        players = self.world.get_matching_entities({Player, Lives})
        if not players:
            return
        lives = self.world.get_component(players[0], Lives)
        if not lives:
            return

        pad = 8
        gap = 6
        x = pad
        y = pad

        badge = getattr(images, "badge_p2", None)
        if badge:
            try:
                w = badge.get_width()
            except Exception:
                w = 24
            count = max(lives.hearts, 0)
            for i in range(count):
                screen.blit(badge, (x + i * (w + gap), y))
        else:
            # Fallback: draw simple rectangles if badge missing
            w = 18
            h = 18
            count = max(lives.hearts, 0)
            for i in range(count):
                screen.draw.filled_rect(
                    Rect(x + i * (w + gap), y, w, h),
                    (220, 60, 60),
                )


class DeathCleanupSystem(System):
    def update(self, dt: float):
        # Timer-based cleanup (backward compatible)
        ents_timer = self.world.get_matching_entities({DeathTimer})
        for e in ents_timer:
            timer = self.world.get_component(e, DeathTimer)
            if not timer:
                continue
            timer.time_remaining -= dt
            if timer.time_remaining <= 0:
                self.world.destroy_entity(e)

        # Off-screen cleanup for dead falling enemies
        ents_dead = self.world.get_matching_entities({Dead, Position})
        for e in ents_dead:
            pos = self.world.get_component(e, Position)
            if not pos:
                continue
            if pos.y > HEIGHT + ENEMY_HEIGHT:
                self.world.destroy_entity(e)


# endregion


# region Game


class Game:
    def __init__(self):
        self.world = World()
        self.player = None
        self.input = Controls()

        # Add global difficulty entity
        difficulty = self.world.create_entity()
        self.world.add_component(difficulty, Difficulty())

        # Add systems
        self.world.add_system(ControlsSystem(self.world))
        self.world.add_system(GravitySystem(self.world))
        self.world.add_system(MovementSystem(self.world))
        self.world.add_system(CollisionDetectionSystem(self.world))
        self.world.add_system(CombatSystem(self.world))
        self.world.add_system(CollisionResolutionSystem(self.world))
        self.world.add_system(LandSoundSystem(self.world))
        self.world.add_system(DifficultySystem(self.world))
        self.world.add_system(EnemySpawnSystem(self.world))
        self.world.add_system(EnemyAIChase(self.world))
        self.world.add_system(WalkingAnimationSystem(self.world))
        self.world.add_system(EnemySpriteSystem(self.world))
        self.world.add_system(ContactDamageSystem(self.world))
        self.world.add_system(FootstepSystem(self.world))
        self.world.add_system(DeathCleanupSystem(self.world))
        self.world.add_system(RenderSystem(self.world))
        self.world.add_system(CursorSystem(self.world))
        self.world.add_system(HUDSystem(self.world))

        self._create_background()
        self._create_map()
        self._create_player()
        # Cursor entity for in-game
        cur = self.world.create_entity()
        self.world.add_component(cur, Cursor("default"))

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
        Create a platform of grass starting a little below the middle
        (1 tile on top), and fill all rows below with dirt (with rare
        variations).
        """
        random.seed(42)

        cols = WIDTH // TILE_SIZE + 1
        grass_row = (HEIGHT // TILE_SIZE) - 3  # 3 rows above the bottom
        global GROUND_TOP_Y
        GROUND_TOP_Y = grass_row * TILE_SIZE

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
        self.world.add_component(self.player, Lives(5))
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
        self.world.add_component(
            self.player,
            Footsteps(
                [
                    "footstep_wood_000",
                    "footstep_wood_001",
                    "footstep_wood_002",
                    "footstep_wood_003",
                    "footstep_wood_004",
                ],
            ),
        )


# region Menu

MENU_STATE = "menu"  # "menu" | "game" | "game_over"

pygame.mouse.set_visible(False)


def play_click_sound():
    if not SFX_ENABLED:
        return

    sounds.click5.play()


def play_footstep_sound(footsteps):
    names = footsteps.sound_names
    if not names or not SFX_ENABLED:
        return
    count = len(names)
    if count == 1:
        idx = 0
    else:
        idx = footsteps.rng.randrange(count)
        if idx == footsteps.last_index:
            idx = (idx + 1) % count
    name = names[idx]
    sound_obj = getattr(sounds, name, None)
    if sound_obj:
        footsteps.sound_index = idx
        footsteps.last_index = idx
        sound_obj.play()


class UIRect(Component):
    def __init__(self, x: int, y: int, w: int, h: int):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def contains(self, pos: Tuple[int, int]) -> bool:
        px, py = pos
        return self.x <= px <= self.x + self.w and self.y <= py <= self.y + self.h


class UIButton(Component):
    def __init__(
        self,
        label: str,
        action: str,
        label_color: Tuple[int, int, int] = (0, 0, 0),
        texture_normal: str = "button_rectangle_normal",
        texture_pressed: str = "button_rectangle_pressed",
    ):
        self.label = label
        self.label_color = label_color
        self.action = action  # "start" | "toggle_music" | "toggle_sfx" | "exit"
        self.texture_normal = texture_normal
        self.texture_pressed = texture_pressed


class Hoverable(Component):
    def __init__(self):
        pass


class Pressable(Component):
    def __init__(self):
        self.is_pressed = False


class UIButtonLabelSystem(System):
    def update(self, dt: float):
        # Keep labels for toggle buttons in sync
        buttons = self.world.get_matching_entities({UIButton})
        for e in buttons:
            btn = self.world.get_component(e, UIButton)
            if not btn:
                continue
            if btn.action == "toggle_music":
                btn.label = f"Música {'ON' if MUSIC_ENABLED else 'OFF'}"
            elif btn.action == "toggle_sfx":
                btn.label = f"Sons: {'ON' if SFX_ENABLED else 'OFF'}"


class UIButtonInputSystem(System):
    def update(self, dt: float):
        # Consume queued clicks
        global MENU_STATE, MUSIC_ENABLED, SFX_ENABLED, _game
        downs = list(_ui_mouse_downs)
        ups = list(_ui_mouse_ups)
        _ui_mouse_downs.clear()
        _ui_mouse_ups.clear()

        # Prepare button list
        ents = self.world.get_matching_entities({UIRect, UIButton, Pressable})
        items = []
        for e in ents:
            rect = self.world.get_component(e, UIRect)
            btn = self.world.get_component(e, UIButton)
            prs = self.world.get_component(e, Pressable)
            if rect and btn and prs is not None:
                items.append((e, rect, btn, prs))

        # Mouse down: set pressed on the button under cursor
        for pos in downs:
            for _, rect, _, prs in items:
                prs.is_pressed = False
            for _, rect, _, prs in items:
                if rect.contains(pos):
                    prs.is_pressed = True
                    play_click_sound()
                    break

        # Mouse up: if releasing on the same pressed button, trigger action
        for pos in ups:
            target = None
            for e, rect, btn, prs in items:
                if prs.is_pressed and rect.contains(pos):
                    target = btn
                prs.is_pressed = False
            if target:
                if target.action == "start":
                    MENU_STATE = "game"
                    if _game is None:
                        _create_game()
                    apply_music_state()
                elif target.action == "toggle_music":
                    MUSIC_ENABLED = not MUSIC_ENABLED
                    apply_music_state()
                elif target.action == "toggle_sfx":
                    SFX_ENABLED = not SFX_ENABLED
                elif target.action == "exit":
                    quit()
                elif target.action == "restart":
                    MENU_STATE = "game"
                    _game = None
                    _create_game()
                    apply_music_state()
                elif target.action == "menu":
                    MENU_STATE = "menu"
                    _game = None
                    _ensure_ui_world()
                    reset_ui_for_state()
                    apply_music_state()


class UIDrawSystem(System):
    def __init__(self, world):
        super().__init__(world)
        self.background_tiles_normal = []
        self.background_tiles_game_over = []
        self.generate_background_tiles_normal()
        self.generate_background_tiles_game_over()

    def draw(self):
        screen.clear()
        GRAY = (120, 120, 120)
        screen.fill(GRAY)

        # Draw background tiles
        if MENU_STATE == "game_over":
            for tile in self.background_tiles_game_over:
                screen.blit(tile[2], (tile[0], tile[1]))
        else:
            for tile in self.background_tiles_normal:
                screen.blit(tile[2], (tile[0], tile[1]))

        # Title
        if MENU_STATE == "game_over":
            RED = (220, 60, 60)
            screen.draw.text(
                "Game Over",
                center=(WIDTH // 2, 140),
                fontname="kenney_future",
                fontsize=64,
                color=RED,
            )
        else:
            BLACK = (0, 0, 0)
            screen.draw.text(
                TITLE,
                center=(WIDTH // 2, 140),
                fontname="kenney_future",
                fontsize=64,
                color=BLACK,
            )

        # Buttons
        ents = self.world.get_matching_entities({UIRect, UIButton})
        for e in ents:
            rect = self.world.get_component(e, UIRect)
            button = self.world.get_component(e, UIButton)
            pressable = self.world.get_component(e, Pressable)
            if not (rect and button):
                continue
            r = Rect(rect.x, rect.y, rect.w, rect.h)

            # Texture
            texture_name = (
                button.texture_pressed
                if (pressable and pressable.is_pressed)
                else button.texture_normal
            )
            texture = getattr(images, texture_name, None)

            # Draw texture
            try:
                scaled = pygame.transform.smoothscale(texture, (r.w, r.h))
            except Exception:
                scaled = texture
            screen.blit(scaled, (r.x, r.y))

            # Label
            screen.draw.text(
                button.label,
                center=r.center,
                fontname="kenney_future",
                fontsize=24,
                color=button.label_color,
            )

    def generate_background_tiles_normal(self):
        if not self.background_tiles_normal:
            for x in range(0, WIDTH, TILE_SIZE):
                for y in range(0, HEIGHT, TILE_SIZE):
                    texture = self._get_random_dirt_texture()
                    texture = getattr(images, texture, None)
                    self.background_tiles_normal.append((x, y, texture))

    def generate_background_tiles_game_over(self):
        if not self.background_tiles_game_over:
            for x in range(0, WIDTH, TILE_SIZE):
                for y in range(0, HEIGHT, TILE_SIZE):
                    texture = self._get_random_game_over_texture()
                    texture = getattr(images, texture, None)
                    self.background_tiles_game_over.append((x, y, texture))

    def _get_random_dirt_texture(self):
        roll = random.random()
        if roll < 0.09:
            return "tile_green_08"
        elif roll < 0.2:
            return "tile_green_17"
        return "tile_green_03"

    def _get_random_game_over_texture(self):
        roll = random.random()
        if roll < 0.09:
            return "tile_brown_09"
        elif roll < 0.2:
            return "tile_brown_18"
        return "tile_brown_27"


class UIHoverSystem(System):
    def update(self, dt: float):
        # Only if app window focused and cursor inside
        if not pygame.mouse.get_focused():
            return
        mx, my = pygame.mouse.get_pos()
        if not (0 <= mx < WIDTH and 0 <= my < HEIGHT):
            return

        # Default to normal cursor
        cursor_entities = self.world.get_matching_entities({Cursor})
        if not cursor_entities:
            return
        cursor = self.world.get_component(cursor_entities[0], Cursor)
        if not cursor:
            return
        cursor.cursor_type = "default"

        # Set pointer when hovering any Hoverable
        ents = self.world.get_matching_entities({UIRect, Hoverable})
        for e in ents:
            rect = self.world.get_component(e, UIRect)
            hov = self.world.get_component(e, Hoverable)
            if rect and hov and rect.contains((mx, my)):
                cursor.cursor_type = "pointer"
                break


class CursorSystem(System):
    def __init__(self, world):
        super().__init__(world)
        self._hide_cursor()

    def draw(self):
        entities = self.world.get_matching_entities({Cursor})
        if not entities:
            return
        entity = entities[0]
        cursor = self.world.get_component(entity, Cursor)
        if not cursor:
            return

        if not pygame.mouse.get_focused():
            return

        image_name = (
            "cursor_pointer" if cursor.cursor_type == "pointer" else "cursor_default"
        )
        texture = getattr(images, image_name, None)
        mouse_x, mouse_y = pygame.mouse.get_pos()

        if texture:
            screen.blit(
                texture, (mouse_x - CURSOR_SIZE // 2, mouse_y - CURSOR_SIZE // 2)
            )
        else:
            screen.draw.filled_circle(
                (mouse_x - CURSOR_SIZE // 2, mouse_y - CURSOR_SIZE // 2),
                CURSOR_SIZE,
                (255, 255, 255),
            )

    def _hide_cursor(self):
        try:
            pygame.mouse.set_visible(False)
        except Exception:
            pass


# UI world and click queue
_ui_world: World | None = None
_ui_mouse_downs: List[Tuple[int, int]] = []
_ui_mouse_ups: List[Tuple[int, int]] = []


def _ensure_ui_world():
    global _ui_world

    if _ui_world is not None:
        return
    _ui_world = World()
    _ui_world.add_system(UIButtonLabelSystem(_ui_world))
    _ui_world.add_system(UIButtonInputSystem(_ui_world))
    _ui_world.add_system(UIDrawSystem(_ui_world))
    _ui_world.add_system(UIHoverSystem(_ui_world))
    _ui_world.add_system(CursorSystem(_ui_world))

    create_layout()

    # UI cursor entity (default type)
    cur = _ui_world.create_entity()
    _ui_world.add_component(cur, Cursor("default"))


def create_layout():
    global _ui_world
    if _ui_world is None:
        return
    # If buttons already exist, don't recreate
    if _ui_world.get_matching_entities({UIButton}):
        return

    BUTTONS_DIV_GAP = 8
    TITLE_MB = 32

    button_width = BUTTON_WIDTH * 1.5
    button_height = BUTTON_HEIGHT

    # Configure buttons for current UI state
    if MENU_STATE == "game_over":
        buttons_spec = [
            ("Reiniciar", "restart"),
            ("Menu", "menu"),
        ]
    else:
        buttons_spec = [
            ("Começar", "start"),
            ("Música", "toggle_music"),
            ("Sons", "toggle_sfx"),
            ("Sair", "exit"),
        ]

    num_buttons = len(buttons_spec)
    base_y = (
        HEIGHT - (button_height * num_buttons + BUTTONS_DIV_GAP * (num_buttons - 1))
    ) // 2 + TITLE_MB
    x = (WIDTH - button_width) // 2

    def add_button(y: int, label: str, action: str):
        e = _ui_world.create_entity()
        _ui_world.add_component(e, UIRect(x, y, button_width, button_height))
        _ui_world.add_component(
            e,
            UIButton(
                label,
                action,
                texture_normal="button_rectangle_depth",
                texture_pressed="button_rectangle_depth",
            ),
        )
        _ui_world.add_component(e, Hoverable())
        _ui_world.add_component(e, Pressable())

    for i, (label, action) in enumerate(buttons_spec):
        add_button(base_y + i * (button_height + BUTTONS_DIV_GAP), label, action)


def reset_ui_for_state():
    global _ui_world
    if _ui_world is None:
        return
    # Remove existing UI button entities
    ents = _ui_world.get_matching_entities({UIButton})
    for e in ents:
        _ui_world.destroy_entity(e)
    # Recreate the layout for the current state
    create_layout()


def apply_music_state():
    try:
        # Stop both first to avoid overlap
        sounds.music_space_cadet.stop()
        sounds.music_sad_descent.stop()
        sounds.music_game_over.stop()
    except Exception:
        pass

    if not MUSIC_ENABLED:
        return

    try:
        if MENU_STATE == "menu":
            sounds.music_space_cadet.play(-1)
        elif MENU_STATE == "game_over":
            sounds.music_game_over.play(-1)
        else:
            sounds.music_sad_descent.play(-1)
    except Exception:
        pass


# Apply initial music state
apply_music_state()

# endregion

# Global game instance created on demand
_game: Game | None = None


def _create_game():
    global _game
    _game = Game()


# Pygame Zero hooks


def draw():
    if MENU_STATE in ("menu", "game_over"):
        _ensure_ui_world()
        _ui_world.draw()
    else:
        if _game:
            _game.draw()


def update(dt):
    if MENU_STATE in ("menu", "game_over"):
        _ensure_ui_world()
        _ui_world.update(dt)
        return
    if _game:
        _game.update(dt)


def on_mouse_down(pos):
    global MENU_STATE, MUSIC_ENABLED, SFX_ENABLED, _game
    if MENU_STATE not in ("menu", "game_over"):
        return
    _ui_mouse_downs.append(pos)


def on_mouse_up(pos):
    global MENU_STATE
    if MENU_STATE not in ("menu", "game_over"):
        return
    _ui_mouse_ups.append(pos)


pgzrun.go()

# endregion
