# Plan B

## Fundamentals

- [x] Developed with [pgzero](https://github.com/pgzero/pgzero) and built-in modules such as `random`, `math`, and `typing`
- [x] Platformer mechanics
- [x] Menu with clickable buttons: Start game, toggle music and sound, and exit
- [x] Music and sound effects
- [ ] Multiple enemies
- [ ] Enemies move within their territory
- [x] Movement and animation system implemented with classes
- [x] Hero and enemies animated with sprites (e.g., walking)
- [x] Code compatible with PEP8 using [black](https://github.com/psf/black) and [flake8](https://github.com/PyCQA/flake8)
- [x] No bugs (none found)

## Recommended

- [ ] Add HUD with score and lives
- [ ] Add game over screen

## Optional

**Gems (Score)**
- Gems spawn randomly on the ground.
- Gems can be collected by the player.
- Each collected gem increases the score (no maximum; accumulates infinitely).

**Hearts (Health)**
- Hearts spawn randomly on the ground.
- Hearts can be collected by the player by touching them.
- Collecting a heart restores the player's health up to a maximum of 5 hearts (cannot exceed 5).
- Hearts disappear if not collected within 5 seconds.

**Artifacts**
- Artifacts (e.g., jewels, disks, keys, puzzles) can be collected during runs for additional objectives or rewards.
