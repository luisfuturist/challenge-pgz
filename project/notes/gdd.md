# **Wibblo: Game Design Document**

### 1. Game Overview

* **Concept**: A fast-paced 2D platformer survival game where players use time-bending powers to outsmart relentless enemies in a single-screen, fixed-layout world.  
* **Genre**: 2D platformer, survival, action.  
* **Target Audience**: Players who enjoy challenging, strategic action games with a strong narrative and a unique mechanic.  
* **Unique Selling Points (USPs)**
  * **Time as a Weapon**: The ability to pause, rewind, fast-forward, and slow time to manipulate enemy behavior and gain a strategic advantage.  
  * **"Living Paradox" Lore**: A narrative centered on defying a time-enforcing cosmic entity, creating a meta-narrative where the player's actions are the ultimate anomaly.  
  * **Open-Ended Survival**: A focus on high-score chasing rather than a traditional win condition, encouraging mastery of the time-bending mechanics.

### 2. Gameplay Mechanics

* **Core Loop**: Survive \-\> Rewind to correct mistakes or plan \-\> Fast-forward to re-engage \-\> Repeat, with difficulty increasing over time.  
* **Player Actions**
  * **Movement**: Walk, run, jump between platforms.  
  * **Combat**: Jump and step on top of enemies to kill them.
  * **Time Control**
    * **Enter**: Pause and enter **Time Travel Mode**; Exit Time Travel Mode, committing to the current timeline and erasing all future possibilities from the rewound point.  
    * **Backspace/Left**: **Rewind** to a previous state.  
    * **Right**: **Fast-forward** to the present from a rewound state.  
    * **E**: **Slow time**.  
    * **Esc**: **Revert to present** without changing the timeline.  
* **Enemies**
  * Relentless, AI-driven enemies that chase the player.  
  * Spawn "out of nowhere" as the game progresses.  
  * Lethal on contact but not from the top.
  * Is killed by jumping and stepping on top of them.
  * Behavior is reset during rewind but resumes chase upon fast-forward/time restart.  
* **Win/Lose Conditions**
  * **Win**: No traditional victory; the goal is to achieve the highest possible score.  
  * **Lose**: Player is touched by an enemy.  
  * **Score**: Calculated based on survival time.  
* **Difficulty Scaling**
  * Difficulty increases gradually over time.  
  * More enemies spawn at regular intervals.  
  * Existing enemies become faster and more aggressive.

### 3. Story & Narrative (Lore)

* **World**: The universe is governed by the **Cosmic Neatness Rule**, enforced by the robotic **Enforcers** of the Time Supreme Court. This rule is a paradox, as interventions create more paradoxes.  
* **Protagonist**: **Wibblo**, an alien of a specieis that has an innate, time-bending ability. He is a living paradox who defies the Court and becomes an existential threat.  
* **Narrative Arc**: Wibblo's journey from grief-stricken fugitive to master of temporal glitches, culminating in a final confrontation with the Time Supreme Court's AI. The game's narrative is a reflection of its mechanics: the player is constantly defying and manipulating the rules to survive. The player's journey is Wibblo's journey to mastering time.

### 4. Game Endings

* **End Game 1 - Sacrifice**: You die and the main menu is shown.
* **End Game 2 - Destruction**: The destruction protocol is activated and you can see the world being destroyed with glitches. After that, the main menu is shown.
* **End Game 3 - Transcendence**: (Unlocked after completing End Games 1 and 2) You witness yourself merging with the system, visualized as code streaming down the screen like Matrix rain, until the main menu gradually reappears from within the code. The elixir is not implemented (not part of this game scope).

### 5. Art & Sound

* **Art Direction**: A simple, clean 2D tile-based aesthetic with a focus on clear visual communication.  
  * A **"red shimmer"** effect for Enforcers to visually represent their temporal anomaly.  
  * A distinct visual cue for when the player enters Time Travel Mode (e.g., a desaturated color palette or a static overlay).  
* **Audio**:
  * Atmospheric, minimalist soundtrack that shifts and changes with the state of time (slowed, rewinding, fast-forwarding).
  * Distinct sound effects for enemy spawns, player attacks, and time manipulation. Those sounds also change with the state of time.

### 6. Technical

* **Platform**: Desktop (cross-platform).
* **Technology Stack**: Pygame Zero.
* **Monetization**:
  * Potentially free-to-play with a leaderboard, with options for ad-based monetization or a one-time purchase to remove ads and unlock cosmetic features.

### 7. Project Plan

* **Team**: [Luis](https://github.com/luisfuturist) as the core developer, with a potential for open source contributors.  
* **Timeline**: Start with a minimal viable game focused on the core survival loop and time-rewind mechanic. Add other time controls and difficulty scaling in subsequent iterations.  
* **Risks**: Balancing the time-rewind mechanic so it's powerful but not "cheating" and ensuring enemies remain a threat despite the player's abilities.
