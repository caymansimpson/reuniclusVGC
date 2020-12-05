class TeamRepository:
  teams = ["""
Tapu Fini @ Wiki Berry
Level: 50
Ability: Misty Surge
EVs: 236 HP / 0 Atk / 4 Def / 204 SpA / 12 SpD / 52 Spe
Modest Nature
IVs: 31 HP / 31 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe
-  Muddy Water
-  Moonblast
-  Protect
-  Calm Mind

Regieleki @ Light Clay
Level: 50
EVs: 0 HP / 0 Atk / 0 Def / 252 SpA / 4 SpD / 252 Spe
Timid Nature
IVs: 31 HP / 31 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe
-  Electroweb
-  Thunderbolt
-  Reflect
-  Light Screen

Incineroar @ Figy Berry
Level: 50
EVs: 244 HP / 20 Atk / 84 Def / 0 SpA / 148 SpD / 12 Spe
Careful Nature
IVs: 31 HP / 31 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe
-  Fake Out
-  Flare Blitz
-  Parting Shot
-  Snarl

Landorus-Therian @ Assault Vest
Level: 50
Ability: Intimidate
EVs: 4 HP / 252 Atk / 0 Def / 0 SpA / 0 SpD / 252 Spe
Jolly Nature
IVs: 31 HP / 31 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe
-  Earthquake
-  Rock Slide
-  Fly
-  Superpower

Metagross @ Weakness Policy
Level: 50
Ability: Clear Body
EVs: 252 HP / 252 Atk / 0 Def / 0 SpA / 4 SpD / 0 Spe
Adamant Nature
IVs: 31 HP / 31 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe
-  Protect
-  Iron Head
-  Stomping Tantrum
-  Ice Punch

Urshifu @ Focus Sash
Level: 50
EVs: 0 HP / 252 Atk / 0 Def / 0 SpA / 4 SpD / 252 Spe
Jolly Nature
IVs: 31 HP / 31 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe
-  Wicked Blow
-  Close Combat
-  Sucker Punch
-  Protect
""","""
Zapdos-Galar @ Choice Scarf
Level: 50
Ability: Defiant
EVs: 4 HP / 252 Atk / 0 Def / 0 SpA / 0 SpD / 252 Spe
Jolly Nature
IVs: 31 HP / 31 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe
-  Thunderous Kick
-  Brave Bird
-  Coaching
-  Stomping Tantrum

Dragapult @ Life Orb
Level: 50
Ability: Clear Body
EVs: 4 HP / 252 Atk / 0 Def / 0 SpA / 0 SpD / 252 Spe
Jolly Nature
IVs: 31 HP / 31 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe
-  Phantom Force
-  Dragon Darts
-  Fly
-  Protect

Swampert @ Assault Vest
Level: 50
Ability: Torrent
EVs: 252 HP / 228 Atk / 4 Def / 0 SpA / 4 SpD / 20 Spe
Adamant Nature
IVs: 31 HP / 31 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe
-  Liquidation
-  Ice Punch
-  High Horsepower
-  Hammer Arm

Clefairy @ Eviolite
Level: 50
Ability: Friend Guard
EVs: 252 HP / 0 Atk / 252 Def / 0 SpA / 4 SpD / 0 Spe
Bold Nature
IVs: 31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe
-  Follow Me
-  Helping Hand
-  Sing
-  Protect

Celesteela @ Weakness Policy
Level: 50
Ability: Beast Boost
EVs: 92 HP / 0 Atk / 4 Def / 252 SpA / 4 SpD / 156 Spe
Modest Nature
IVs: 31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe
-  Flash Cannon
-  Air Slash
-  Meteor Beam
-  Protect

Rotom-Heat @ Sitrus Berry
Level: 50
Ability: Levitate
EVs: 252 HP / 0 Atk / 44 Def / 36 SpA / 20 SpD / 156 Spe
Modest Nature
IVs: 31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe
-  Overheat
-  Thunderbolt
-  Nasty Plot
-  Protect
""","""
Raichu @ Focus Sash
Level: 50
Ability: Lightning Rod
EVs: 4 HP / 252 Atk / 0 Def / 0 SpA / 0 SpD / 252 Spe
Jolly Nature
IVs: 31 HP / 31 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe
-  Nuzzle
-  Reflect
-  Fake Out
-  Eerie Impulse

Tapu Fini @ Sitrus Berry
Level: 50
Ability: Misty Surge
EVs: 252 HP / 0 Atk / 68 Def / 116 SpA / 20 SpD / 52 Spe
Modest Nature
IVs: 31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe
-  Moonblast
-  Muddy Water
-  Calm Mind
-  Protect

Kartana @ Life Orb
Level: 50
Ability: Beast Boost
EVs: 4 HP / 252 Atk / 0 Def / 0 SpA / 0 SpD / 252 Spe
Jolly Nature
IVs: 31 HP / 31 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe
-  Leaf Blade
-  Sacred Sword
-  Smart Strike
-  Protect

Rotom-Heat @ Safety Goggles
Level: 50
Ability: Levitate
EVs: 252 HP / 0 Atk / 44 Def / 36 SpA / 20 SpD / 156 Spe
Modest Nature
IVs: 31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe
-  Overheat
-  Thunderbolt
-  Nasty Plot
-  Protect

Regirock @ Leftovers
Level: 50
Ability: Clear Body
EVs: 252 HP / 156 Atk / 0 Def / 0 SpA / 100 SpD / 0 Spe
Adamant Nature
IVs: 31 HP / 31 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe
-  Rock Slide
-  Body Press
-  Earthquake
-  Curse

Moltres-Galar @ Weakness Policy
Level: 50
Ability: Berserk
EVs: 204 HP / 0 Atk / 100 Def / 76 SpA / 28 SpD / 100 Spe
Modest Nature
IVs: 31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe
-  Fiery Wrath
-  Air Slash
-  Nasty Plot
-  Protect
""","""
Garchomp @ Weakness Policy
Ability: Rough Skin
Level: 50
EVs: 124 HP / 132 Atk / 4 Def / 4 SpD / 244 Spe
Jolly Nature
- Earthquake
- Rock Slide
- Swords Dance
- Protect

Regieleki @ Light Clay
Ability: Transistor
Level: 50
EVs: 92 HP / 180 Def / 36 SpA / 4 SpD / 196 Spe
Timid Nature
IVs: 0 Atk
- Electroweb
- Volt Switch
- Light Screen
- Reflect

Moltres @ Life Orb
Ability: Pressure
Level: 50
EVs: 4 HP / 252 SpA / 252 Spe
Timid Nature
IVs: 0 Atk
- Heat Wave
- Air Slash
- Scorching Sands
- Protect

Ferrothorn @ Leftovers
Ability: Iron Barbs
Level: 50
EVs: 252 HP / 204 Atk / 52 Def
Brave Nature
IVs: 0 Spe
- Power Whip
- Iron Head
- Knock Off
- Protect

Porygon2 @ Eviolite
Ability: Download
Level: 50
EVs: 244 HP / 76 Def / 4 SpA / 140 SpD / 44 Spe
Bold Nature
IVs: 0 Atk
- Shadow Ball
- Ice Beam
- Trick Room
- Recover

Tapu Fini @ Sitrus Berry
Ability: Misty Surge
Level: 50
EVs: 252 HP / 68 Def / 116 SpA / 20 SpD / 52 Spe
Modest Nature
IVs: 0 Atk
- Moonblast
- Muddy Water
- Calm Mind
- Protect
""","""
Thundurus (M) @ Life Orb
Ability: Defiant
Level: 50
EVs: 4 HP / 252 Atk / 252 Spe
Jolly Nature
- Wild Charge
- Fly
- Superpower
- Protect

Mamoswine @ Focus Sash
Ability: Oblivious
Level: 50
EVs: 4 HP / 252 Atk / 252 Spe
Jolly Nature
- Icicle Crash
- Earthquake
- Ice Shard
- Protect

Nihilego @ Power Herb
Ability: Beast Boost
Level: 50
EVs: 4 HP / 252 SpA / 252 Spe
Timid Nature
IVs: 0 Atk
- Meteor Beam
- Sludge Bomb
- Power Gem
- Protect

Chandelure @ Sitrus Berry
Ability: Flash Fire
Level: 50
EVs: 252 HP / 4 Def / 100 SpA / 4 SpD / 148 Spe
Modest Nature
IVs: 0 Atk
- Heat Wave
- Shadow Ball
- Trick Room
- Imprison

Tapu Fini @ Wiki Berry
Ability: Misty Surge
Level: 50
EVs: 252 HP / 116 Def / 12 SpA / 76 SpD / 52 Spe
Calm Nature
IVs: 0 Atk
- Muddy Water
- Moonblast
- Calm Mind
- Protect

Kartana @ Assault Vest
Ability: Beast Boost
Level: 50
EVs: 84 HP / 52 Atk / 4 Def / 116 SpD / 252 Spe
Jolly Nature
- Leaf Blade
- Smart Strike
- Sacred Sword
- Aerial Ace
""","""
Spectrier @ Grassy Seed
Ability: Grim Neigh
Level: 50
EVs: 140 HP / 92 Def / 36 SpA / 4 SpD / 236 Spe
Modest Nature
IVs: 0 Atk
- Shadow Ball
- Mud Shot
- Nasty Plot
- Protect

Rillaboom-Gmax @ Rose Incense
Ability: Grassy Surge
Level: 50
EVs: 252 HP / 116 Atk / 4 Def / 132 SpD / 4 Spe
Adamant Nature
- Wood Hammer
- Grassy Glide
- Fake Out
- Protect

Incineroar @ Sitrus Berry
Ability: Intimidate
Level: 50
EVs: 244 HP / 4 Atk / 156 Def / 4 SpA / 100 SpD
Relaxed Nature
IVs: 0 Spe
- Flare Blitz
- Burning Jealousy
- Parting Shot
- Fake Out

Milotic @ Expert Belt
Ability: Competitive
Level: 50
EVs: 132 HP / 12 Def / 204 SpA / 4 SpD / 156 Spe
Modest Nature
IVs: 0 Atk
- Muddy Water
- Ice Beam
- Mud Shot
- Protect

Togedemaru @ Focus Sash
Ability: Lightning Rod
Level: 50
EVs: 4 HP / 252 Atk / 252 Spe
Jolly Nature
- Fake Out
- Zing Zap
- Nuzzle
- Spiky Shield

Togekiss (M) @ Scope Lens
Ability: Super Luck
Level: 50
EVs: 236 HP / 100 Def / 12 SpA / 4 SpD / 156 Spe
Modest Nature
IVs: 0 Atk
- Air Slash
- Dazzling Gleam
- Follow Me
- Protect
""","""
Magikarp
Ability: Swift Swim
EVs: 8 HP
IVs: 0 Atk
- Splash

Eevee @ Choice Specs
Ability: Run Away
EVs: 20 HP
IVs: 0 Atk
- Detect

Machop @ Choice Band
Ability: Guts
EVs: 4 Atk
IVs: 0 Atk
- Encore

Blissey (F) @ Choice Scarf
Ability: Natural Cure
EVs: 8 SpA
IVs: 0 Atk
- Aromatherapy
"""
  ]
