---
description: Tasks and items for the release.
---

# TODO

- Setup CD
  - Check quality before release: `"isort . && black . && flake8 . && mypy ."`
  - Config changelog (add unreleased section, update version in title)
  - Config GitHub release name and notes

- [ ] Look for TODO comments

## 0.1.0-0 - Core Gameplay Implementation

* **Core gameplay implemented:** Player can move left/right, jump, and interact with a generated map.
* **ECS architecture established:** Game uses an Entity-Component-System design with components for data (e.g., `Position`, `Velocity`) and systems for logic (e.g., `GravitySystem`, `CollisionSystem`).
* **Player controls:** Player entity responds to keyboard input for movement (`A/D`, left/right arrows) and jumping (`Space`).
* **Physics engine:** Basic physics is implemented, including gravity and collision detection with the game world and its boundaries.
* **Animations and sprites:** Player sprite changes based on actions (standing, walking, jumping), with support for horizontal flipping to match direction.
* **Level generation:** A simple, static map with grass and dirt platforms is procedurally created at game startup.

Out of scope:

- No Survival Elements: No health or mobs
- No sound
- No music

## 0.1.0-1 - Enemy System

- [ ] While the `R` key is held down, the player should instantly respawn every frame at a new random X position within the world boundaries (but never inside a platform tile). This continues until the "R" key is released.
- [ ] Press `G` to spawn a "prancing Wibblo."
    
- Enemy System
  - [ ] Basic enemy AI (chase player)
  - [ ] Enemy spawning system
  - [ ] Enemy movement patterns
  - [ ] Enemy collision detection

- Combat System
  - [ ] Jump on enemies to kill them
  - [ ] Enemy death animations
  - [ ] Score system for kills
