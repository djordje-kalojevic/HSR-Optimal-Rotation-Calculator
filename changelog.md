## v1.6

### **New characters:**
- Ruan Mei
- Dr. Ratio, note that 2 follow-ups (3 with E6), are included when the “Assume Ultimate Activation” is toggled
- Xueyi

### **Equipment:**
- Ruan Mei's Light Cone, “Past Self in Mirror”

### **Other Additions:**
- Added Himeko's missing +5 energy on Ultimate kills
- Added Welt's missing E2

### **Corrected Energy Recharge breakpoint accuracy:**
- Using a Binary Search Algorithm, a precise ER breakpoint is being pinpointed.
- Max ER checked is 200% to give some leeway for any future ER-related additions.
- Note that this feature is marked as being in “BETA”, this is purely due to the fact that there are so many combinations, and I am not able to check them all.

### **Other improvements:**
- Rewrote and sped up Jingliu's rotations by almost 10x
- added [changelog](https://github.com/djordje-kalojevic/HSR-Optimal-Rotation-Calculator/blob/master/changelog.md) for easier tracking of changes (use "ctrl + f" to search).
- Traces are now pre-selected
- removed Trace names from the character info banners, as they are getting ridiculously long (looking at you Ruan Mei!), now they will only display the ascension at which the trace unlocks, i.e., A2, A4 or A6

### **Fixes:**
- Removed the possibility of HuoHuo's Ultimate being affected by Energy Recharge
- fixed instances of Enhanced Attacks not showing in the Detailed Energy Breakdown, most notably with Blade
- fixed instances of single occurrences (i.e., a single Follow-up attack) not showing in the Detailed Energy Breakdown

### **Code Improvements:**
- simplified Calculate Turn Energy function significantly
- simplified and sped up the cache function of the UserInput class
- removed white theme, and simplified theme application
- other code and documentation improvements

### **Known issues/limitations:****
- For example, if you specify 6 follow-up attacks (1 per turn) but the rotation is, however, only 5 turns long, the Detailed Breakdown will still show 6 follow-up attacks.
- Missing E2 Tingyun team buff
- Missing E1 Bailu team buff

## v1.5.1

### **New Characters:**

- Introducing two new characters to the roster:
  - Argenti
  - Hanya

### **Improvements:**

**Optimized Rotation Duplicates Removal:**

- Implemented a [Bloom filter](https://en.wikipedia.org/wiki/Bloom_filter) ([KenanHanke's rbloom](https://github.com/KenanHanke/rbloom) implementation) to improve the process of rotation duplicates removal.
- The Rotation class is now instantiated only after confirming that the rotation is unique, i.e., not a permutation of another one.

#### _Characters with a high number of potential rotations (e.g., Dan Heng IL):_

- 2x speed increase
- Uses ~93% less memory for task execution and result storage.

#### _Characters with a fewer/average number of potential rotations (e.g., Asta):_

- 2-3x speed increase
- Uses ~93% less memory for task execution and result storage.

### **Package Optimization:**

- Trimmed down the requirements.txt by removing unnecessary packages.

### **Fixes:**

- Resolved instances of Detailed Breakdown not displaying information.
- Added missing tooltip texts for improved user guidance.

## v1.5

### New characters/equipment:

- Topaz
- Guinaifen
- HuoHuo and her signature Light Cone
- Added “Penacony, Land of the Dreams” ornament set (effectively the same as the existing the Sprightly Vonwacq set for the purposes of this calculator)

### New additions:

- Ability to apply certain events (kills, hits taken, talent triggers, Support Light Cones, etc.) multiple times per turn.  
      Looking into adding limits to various stacks, like Blade's and Fire MC's, since now multiple hits can be triggered per turn.
- Option to select HuoHuo's Ultimate bonus through the GUI
- Added talent and relic trigger energy generation, as well as HuoHuo's Ultimate Bonus to the detailed breakdown
- Small GUI redesign
- Integrated search functionality into comboboxes for character, Light Cone, and Support Light Cone selection. Note that you can still use them as regular comboboxes if you so prefer, by clicking on the dropdown button.
- Implemented a specific algorithm for Arlan, considering he does not spend skill points on his Skill attack. Looking into ways of combining and simplifying some of these algorithms that do not differ much from the default one (like Arlan's), aiming for the 1.6 or 1.7 release cycle.
- Added option to toggle on and off Luka's A4 trace (previously was always on)

### Code improvements:

- Optimized if-elif chains by replacing them with match-case statements or dictionary lookups
- Optimized certain checks, especially for turn energy calculations, to reduce call numbers
- Reduced overhead of initializing Rotation class instances by performing most of it only after proper filtering and removal of all turn permutations
- Completely rewrote the “Detailed Breakdown” module
- Simplified the process of printing out rotation information
- Modularized layouts into its respective module
- Updated requirements.txt

### Fixes:

- Fixed instances of incorrect Light Cone Superimposition levels being applied
- Fixed Echoes of the Coffin Light Cone not receiving the full benefit from Loucha's Ultimate (maxing out at 1 stack instead of 3)
- Fixed Blade's SP consumption by correcting his skill's duration (lasts for 4 Enhanced Basic Attacks instead of 3)
- Fixed Fu Xuan's Enhanced Skill generating Skill Points instead of consuming them
- Corrected weird top and bottom padding in rows where tooltips are present
- various other smaller fixes and improvements

## v1.4

### New Characters:

- Jingliu

### New Additions:

- Added input for enemy count. This allows the user to choose between single target scenarios and AoE ones. Currently, impactful to very few characters, notably:
  - Serval with Eidolon 2:
    - Basic Attack maxes out at 2 stacks of her talent (formula: enemy count / 2 rounded DOWN with a minimum of 1)
    - Skill maxes out at 3 stacks of her talent (formula: enemy count / 2 rounded UP)
    - Ultimate: maxes out at the number of enemies specified
  - Luocha with the Echoes of the Coffin Light Cone:
    - Basic Attack grants one stack of the EotC Light Cone
    - Ultimate maxes out at 3 stacks, or fewer if enemy count is less than 3
- Added Clara's Enhanced Follow-up attacks gained when allies get hit after Clara's ultimate. User's can specify this via the “Ally Hit” counter
  - At base, this can be triggered up to 2 times
  - one additional time with her Eidolon 6
- Added technique indicator to the character info header for easier calculation distinguishing.

### Calculation Fixes:

- Echoes of the Coffin Light Cone:
  - No longer applies to all characters' ultimates, only ones that are considered attacks
  - Additionally, added checks for applying this bonus to characters that have Skill that are considered attacks
- Dan Heng Imbibitor Lunae (DHIL):
  - fixed Energy Recharge applying twice to his Basic Attacks
- Fixed rare cases of Energy Recharge Threshold for the next breakpoint being negative
- Additionally, breakpoints will no longer show for rotations that are one turn long (extremely rare in game, but possible though the use of the calculator)

### General Fixes:

- fixed colours not showing in the console output of the compiled executable
- replaced the old “Quick and Dirty” way of refreshing the window with a proper one. The main benefit is that this no longer reopens the whole main window, secondary benefits include the window no longer returning to the middle of the screen when resetting.

### General improvements:

- removed all references to Character “abilities” and replaced them with proper terminology (“Character Traces”)
- many code improvements, especially to the GUI's code and DHIL's rotation calculations
- many documentation improvements
- updated requirements.txt file

## v1.3.2

### Additions:

- Added Fu Xuan and her signature Light Cone
- Added Lynx
- Added option to select how many times allies were hit  
  (currently only Lynx and Fu Xuan E4 can take advantage of this)

### Calculation improvements:

- Filter changes:
  - Basic Only Rotations: Now correctly takes into account all types of Skills
  - One Skill Rotations. Same as above
  - Skill Only Rotations: Now correctly takes into account all types of Basic Attacks

### GUI Improvements:

- small GUI redesign, more planned in the future as additional options need to be added

### Fixes:

- Corrected the energy gained from triggering Solitary Healing support Light Cone

### Known issues:

- Energy Recharge (ER) breakpoints are not 100% accurate
- Blade and Luka's ER breakpoints may show negative values under certain conditions

### Planned / still considered additions:

- Ability to select multiple support Light Cones
- Option to assume multiple kills/hits per turn
- Enemy count selection for simulating single target and AOE situations
- Look into creating more sophisticated filters that favour certain attacks, similarly to how DHIL's rotations take into account his DPS potential (i.e., they favour Enhanced Basic 3 > EB2 > EB1 > Basics).

## v1.3.1

- Added Solitary Healing Light Cone to support Light Cones

## v1.3

### Additions:

- Added neutral rotations to all characters if such rotations are found
- Added “energy generated” and “skill point generation per turn” to all rotations. This might lead to info overload, but I think it will be very useful to a lot of users.
- Added Dan Heng Imbibitor Lunae (DHIL) and his signature Light Cone  
  (_big thanks to @echoecho0 on discord for all the help and for keeping me company while coding til 6am!^^_)
- Fu Xuan and her signature Light Cone (completed but _not included_ due to them still not being officially released)
- Added / moved to support Light Cones:
  - Quid Pro Quo
  - Carve the Moon, Weave the Clouds
  - Shared Feelings
  - Fine Fruit
- Added Support Light Cones to the character info header (header that appears before calculations)

### Improvements:

- Reworked and simplified all rotation filters, which should result in slightly faster calculations while also giving a vastly more powerful framework for future, more sophisticated filters
- Changed the way rotations are calculated and stored which allows for keeping the track of how much energy they generate as well as their skill point cost. This has been incorporated into the filters for various rotation types, most notably DHIL's various skill point breakpoints.
- Kills and hits are no longer frontloaded
- Several calculation improvements
- Various code and documentation improvements
- Completely rewritten readme file

### Blade:

- Sped up Blade's calculations by focusing only on Enhanced Basics
- No longer frontloading stacks which could lead to extra follow-ups
- Calculations no longer assume skill use at the start. This does not change any of his current rotations, but it is done to ensure that it does not mess up any of his potential future rotations.

### GUI improvements:

- “Ultimate kills” option now shows only for characters who have ultimates that are considered attacks
- Added a tooltip to denote that hits taken generate 10 energy, while the actual range is 2-25 energy per hit
- Disabled many options for characters that cannot effectively use them

### Fixes:

- Fixed Before Tutorial and Meshing Cogs sometimes not applying to ultimates
- Corrected the misspelling of Arlan's name (he's just so forgettable lol)

### Known issues:

- Energy Recharge (ER) breakpoints are not 100% accurate
- Blade and Luka's ER breakpoints may show negative values under certain conditions

### Planned / still considered additions:

- Ability to select multiple support Light Cones
- Option to assume multiple kills/hits per turn
- Enemy count selection for simulating single target and AOE situations
- Look into creating more sophisticated filters that favour certain attacks, similarly to how DHIL's rotations take into account his DPS potential (i.e., they favour Enhanced Basic 3 > EB2 > EB1 > Basics).

## v1.2

### Additions:

- Kafka (currently missing trace energy generation)
- Luka
  - Added enemy weakness toggle for him, and any future characters
- Added +12 5\* Rope to the rope selection
- Added more info to the character info header (characters eidolon and selected ability)
- Added an option to display a detailed energy breakdown that lists energy sources

![breakdown example](https://github.com/djordje-kalojevic/HSR-Optimal-Rotation-Calculator/assets/112823059/c3767a60-0f9d-41ed-bdda-992fe8fb1628)

### Improvements:

- Now GUI displays only the relevant eidolons instead of all of them, i.e., selecting Asta will only show eidolons 1 and 4, instead of eidolons 1-6, as only 1 and 4 are relevant to the calculation of her rotations.
- Greatly improved the accuracy of the ER breakpoints. However, it is still WIP so use it more as a suggestion, and give more weight to the rotations, as they are a lot more accurate.
- Improved logic for determining certain types of rotations
- Several calculation improvements
- Various code and documentation improvements.

### Fixes:

- Fixed a crash when trying to find ER breakpoint for a rotation shorter than 1 turn, now correctly returns 0%
- Fixed a crash that would occur when trying to find the "one skill rotation" in a list of rotations where not are eligible

### Known issues:

- ER breakpoints are not 100% accurate
- Blade and Luka's ER breakpoints may show negative values

### Planned additions:

Support LC separate from regular LCs so that they can be "equipped" alongside one another. These would include:

- Quid Pro Quo
- Carve the Moon, Weave the Clouds
- Shared Feeling
- Fine Fruit
- any future support LCs

Enemy count selection for simulating single target and AOE situations

## v1.1.1

### Important calculation fixes:

- Fixed instances where the energy gained from ultimate's activation would apply twice.
- Removed energy rounding from calculations, as the game does not seem to round values at all.  
  _Thanks to @EdisonsMathsClub!_

### For example:

- Natasha using S3 Shared Feelings giving 3.00 Energy
- Luocha with a +1 3\* Rope giving 1.866% energy
- Luocha with a S1 Post-Op giving 8.00% ER

### Would result in:

- (5+20+20+20+20+3+3)\*(109.866%) = 99.978 energy

And this would **not** get rounded up to 100, thus Luocha would not be able to cast his ultimate.

## v1.1

### General:

- Support for follow-up attacks.

### Trailblazer Preservation (Fire MC):

- Improvements to their rotations by adding the logic for calculating and applying their enhanced basic attacks (30 base energy generation).

### Blade:

- Improvements to his rotations by adding logic for calculating and applying his follow-up attacks (10 base energy generation).
- Additionally removed the ability to specify the number of follow-ups via the GUI as this is no longer necessary.
- Added his Eidolon 6 as it reduces the number of stacks necessary for follow-ups.
- Added a toggle for his technique as it grants one said stack.

### Bug Fixes:

- fixed Meshing Cogs and Memories of the Past applying to all skills and ultimates. Now they correctly apply only to skills and ultimates that are considered "attacks". Also added this functionality to any future Light Cones with similar mechanics.
- greatly increased the accuracy of ER breakpoints, as well as fixed some bugs (like sometimes getting negative outputs). However, they can still be 1-2% off based on rounding values, so bear that in mind
- fixed a case where ER would not apply correctly

### Code Improvements:

- moved main algorithm to a separate function in order to more easily add other, more specialized, algorithms for future character (like there are for Fire MC and Blade)
- added function for removing turn permutations, which should speed up calculations
- removed some unnecessary variables
- slightly corrected when Quid Pro Quo Light Cone grants energy (note that it still has a 100% proc chance, will be changed in the future)

## v1.1-pre-3

- Fixes for Assume Ult and Assume Ult kills options (used 100x multiplier for ER instead of 1x, i.e., 100% base ER)  
  Thanks @WolfHeroEX on reddit for reporting it!
- Fixes for ER applying twice on hits and kills

## v1.1-pre-2

### Recommended update:

- Includes various bug-fixes and improvements
- Fixes to certain calculation steps
- Improved follow-up attacks (and the addition of Clara's counters)

## v1.1-pre-1

### Recommended update for all:

- Important bug-fixes and improvements
- Early support for follow-up attacks

## v1.0

Initial release.
