# reuniclusVGC
Bots to play VGC; random and DQN player created; this project is abandoned for Elite Furret AI. Here are my initial notes from readings:

### Rules of Pokemon that make it hard:
1. You and opponent make turns simultaneously
    1. Your opponents moves affect the effects of your moves (e.g. if you’re KO’ed)
2. Large aspect of luck / randomness:
    1. Damage Rolls
    2. Move success (accuracy, multiple protects, OHKOs)
    3. Secondary Move effects
    4. Luck-based abilities (Super Luck, Effect Spore)
    5. Critical Hits
3. Moves made now can affect outlook through next couple of turns (e.g. tailwind, reflect, protect)
4. Imperfect knowledge
    1. Abilities
    2. Items
    3. Moves
    4. EV spreads
    5. IV spreads
    6. Pokemon brought
5. Why VGC will be more computationally difficult
    1. Action Space; Singles Action Space is 13 and Doubles Action Space is 418.
    2. Turn Action Space; Singles is 169 while Doubles is 174,724 (ignoring probabilities which exacerbates this because the probabilities compound)
    3. More emphasis on teampreview (since there's an extra element of picking 4 out of 6). However, whie this is certainly another type of problem, it will be comparatively trivial to solve.

### ML basics:
- We need to learn a “policy”; given the game state, and thus a set of possible actions, ML will choose the most optimal action
- Because of terms like “reverse sweeping” (e.g. going down 4 to 1 so that you can win with your last mon), it’s hard to have heuristics of whether a game was totally or just lost — the best way to approach this would be to reward the ML with +1 with a win and a -1 with a loss. We can add more heuristics to speed up training though
- Input:
    - State: All knowable information of the current battle, your pokemon and the opponent's team
    - Possible Actions:
        - Singles: 4 actions * tera + 5 switches = 13
        - Doubles: (4 actions * 3 targets * tera + 2 switches)^2 = 676 options
            - In reality, there are more limited options (530 total, detailed below), but we can stick w/ 676 for simplicity
                - if two switches: 2
                - if one switch: 2 (cuz either mon could switch) *
                    - switch mon: 2 possible switches *
                    - non-switch mon: 4 moves * 3 targets * tera
                    - = 96
                - if no mon switches:
                    - if one teras: 2 possible teras * (4 moves * 3 targets) * (4 moves * 3 targets)
                    - if none teras: (4 moves * 3 targets)*(4 moves * 3 targets)
                    - = 432
- Output:
    - Best action (or output of our policy given the battle's state)
        - There is no such thing as a “best action” because a perfectly predictable strategy is exploitable. An understanding of how good each action is ideal

### Shortcuts I will take to simplify modeling:
- Primarily, ignore the existence of Zoroark and Ditto :)

### Ways Players Think
- Pokemon is a game of wincons
    - Goal is to eliminate all other pokemon that are threats to your wincon and outspeed/KO the rest
    - The ability to set yourself up and “look ahead” will be key
- Trainers think about HP not in the number, but in a way that matters: “survive two hits from kartana”
- Players dont bank on unlikely secondary effects unless absolutely necessary
- If we can eliminate pokemon each turn regardless of what the other player does, we win
- They work backwards:
    - In what situations will I win and how can I set up those situations?
        - Is it possible to identify 2+ x2 (where the opponent only has 2 mons left) situations in which we win and work backwards from there? As in, what HP/conditions will I need to beat the last two mons?
    - In what situations will I lose and how can I avoid those situations?
        - Is it possible to look at the situations in which I only have 2 mons left and I lose?
- In winning positions, they start making decisions according to probabilities: how can you minimize P(loss)?

### Type of Problem VGC is
- Markov Property; previous states don't matter given the current battle state. However, two caveats here:
    - This is certainly not true in a competitive format where certain players have tendencies (e.g .play more or less aggressively). Whether or not players currently play optimally enough for us to need to maximize rewards based on another player's likelihood to make a move is stil an unknown.
    - Cardinality of battle states is for all intents-and-purposes infinite (e.g. PP, HP values, timer)
- Stochastic Game (players make moves simultaneously in decision-making scenarios; the joint actions results in a transition to a different game state)
- Multi-Agent (two player)
- Zero Sum (aka constant sum; there is no mutually beneficial reward)
- Partially Observable (each player has imperfect information)

### Potential ML approaches:
- Reinforcement Learning because:
    - You dont know the probability of getting to the next state (due to opponent decision)
    - You don’t immediately know which states lead you to the reward
- Second Choice: Monte Carlo Tree Searching?
    - This would only really be applicable in Singles since in Doubles, this would be really expensive
    - We could create heuristics to limit your search space (e.g. not attacking your own pokemon unless healing or weakness policy)
    - “Backwards Induction” (implemented as Alpha-Beta pruning) can help prune gamestates
    - Intelligent prioritization of branches to search

### Useful Links:
1. Twitter Discussion: https://twitter.com/TBFUnreality/status/1059894045177200645
2. Simulator Github: https://github.com/smogon/pokemon-showdown
3. Paper on Poker ML using Imperfect Information: http://modelai.gettysburg.edu/2013/cfr/cfr.pdf
4. Someone creating DeepLearning for 1:1 battle: https://towardsdatascience.com/poke-agent-pokemon-battling-reinforcement-learning-27ef10885c5c
5. Create a showdown bot to operate easily: https://github.com/dramamine/leftovers-again
    1. ^ It will make a request and pass a gamestate, which we will return with a move
    2. Working Pokemon AI: https://github.com/vasumv/pokemon_ai/ (windows only)
6. Minimax AI: http://doublewise.net/pokemon/ (named Technical Machine)
    1. Code: https://bitbucket.org/davidstone/technical-machine/src/master/
7. Someone doing simple deep learning: https://web.stanford.edu/class/aa228/reports/2018/final151.pdf
8. Schoolwork: https://docplayer.net/63514819-Artificial-intelligence-for-pokemon-showdown.html
9. Schoolwork: https://nyuscholars.nyu.edu/en/publications/showdown-ai-competition
10. http://julian.togelius.com/Lee2017Showdown.pdf
    1. Includes primers on how to model AI using showdown API
    2. Also a bunch of fairly simple starter algorithms and their performance
11. https://papers.nips.cc/paper/2012/file/3df1d4b96d8976ff5986393e8767f5b2-Paper.pdf
    1. https://github.com/samhippie/shallow-red
12. Lit review on MARL: https://arxiv.org/pdf/2011.00583.pdf
    1. Zero sum games can always be reformulated to Linear Problems (Dantzig, 1951)
    2. Training against itself? (AlphaZero/AlphaGo approach)
    3. “Portfolio Optimization” would be a team builder algorithm, and is unsolved
    4. Minimax Q?
13. Create DeepLearning stuff using poke-env: https://poke-env.readthedocs.io/en/stable/getting_started.html
    1. **This is what I go with**
14. Implemented Bot: https://github.com/pmariglia/showdown
15. https://github.com/pkmn/EPOke
16. https://www.yuzeh.com/assets/CoG-2019-Pkmn.pdf

### How I got this up and running
1. [Forked Hsahovic's PokeEnv](https://github.com/hsahovic/poke-env/blob/master/src/poke_env/)
2. [Added more Doubles Support](https://github.com/caymansimpson/poke-env)
3. Install Node and requirements for PokeEnv (e.g. python3.6, tensorflow, orljson, keras-rl2==1.0.3)
4. [Set up Bash Profile](https://stackoverflow.com/questions/16904658/node-version-manager-install-nvm-command-not-found)

To run an example where we simulate random battles, from home directory:
`source ~/.bash_profile`,
`node Pokemon-Showdown/pokemon-showdown`
then `python3.8 simulators/simulate_random_doubles.py`
