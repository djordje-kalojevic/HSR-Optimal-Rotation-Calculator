# HSR Optimal Rotation Calculator

The HSR Optimal Rotation Calculator is a powerful tool designed to optimize character rotations in Honkai: Star Rail, turn-based strategy game. It provides a range of features for calculating and refining rotations through an intuitive and user-friendly graphical user interface (GUI).

## Features

The HSR Optimal Rotation Calculator offers the following features:

- **Neutral Rotations:**\
Calculate the neutral rotation, i.e., a rotation that costs an average of 0 skill points per turn, where applicable.

- **Basic Attack Rotation and Energy Recharge (ER) breakpoints:**\
Calculate the optimal rotation composed only of basic attacks, along with the required ER to reach the next breakpoint.

- **Skill Rotation and ER breakpoints:**\
Calculate the optimal rotation composed only of skills, along with the required ER to reach the next breakpoint.

- **One-Skill Rotation for Buffers/Debuffers:**\
Calculate a one-skill rotation to see if it aligns with buff/debuff durations, such as Tingyun, Silver Wolf, etc.

- **Shortest, most efficient Rotation:**\
This mode prioritizes rotations with minimal skill point cost.

- **Specialized algorithms for certain characters:**\
These characters posses unique attacks or additional ways of generating energy.
These currently include: Argenti, Arlan, Blade, Dan Heng Imbibitor Lunae, Fu Xuan, Jingliu, Luka, Topaz, and Trailblazer (Preservation), i.e., Fire MC.

- **Detailed energy breakdown:**\
This option will list all the energy sources and the amount of energy they have generated. 

## Customization Options

The calculator supports a wide range of customization options, including:

- Character selection
- Their associated eidolons, traces, talents, and techniques
- Equipped Light Cones, support Light Cones, as well as relics, ornaments and energy recharge ropes
- Numbers of kills, hits taken, etc. assumed during the rotation
- Team buffs (e.g. Tingyun and HuoHuo Ultimate)

The results of these calculations are then presented via the terminal interface.

## Future Plans

Include:

- New characters and equipment as soon as they are released / fully revealed (in other words no leaks unless clearly specified)
- Incorporation of any missing options
- Further code and documentation improvements to support further development

## Accessing the Calculator

To access the HSR Optimal Rotation Calculator, you can:

1. **Install from GitHub:** Clone or download the repository to set up the calculator locally.

2. **Use the Executable:** Utilize the pre-compiled portable executable for local use found in the [GitHub releases](https://github.com/djordje-kalojevic/HSR-Optimal-Rotation-Calculator/releases). This approach does not have any dependencies.

## Feedback and Contribution

Your feedback, suggestions, and bug reports are very much appreciated! If you encounter any issues or have ideas for improvement, please don't hesitate to contribute by submitting issues or pull requests on [GitHub](https://github.com/djordje-kalojevic/HSR-Optimal-Rotation-Calculator/issues).

---

*Note: Version numbers will follow game release versions as much as possible, i.e., Calculator's v1.3 includes all new additions found in the game's 1.3 update.*

*Note: The calculator's calculations are powered by various Depth-First Search algorithms. For detailed information about these algorithms and their implementation, please refer to the calculator's source code available [here](https://github.com/djordje-kalojevic/HSR-Optimal-Rotation-Calculator/tree/master/calculation_scripts/character_algorithms).*
