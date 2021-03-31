# Faulty Technology Randomized Swaps Tool
A simple tool to assist in running a Faulty Technology challenge run of Pokémon. Inspired by [a thread](https://www.smogon.com/forums/threads/faulty-technology.3509964/) on Smogon's forums.


> A summary of the general rules of a Faulty Technology run:
> - Every time a Pokémon Center is used to heal, a randomized swap of party members with boxed Pokémon must be made, as follows:
>     1. Randomly pick 1 (or more) Pokémon from your party to be deposited into the PC
>         - Deposited Pokémon go into the first box in the PC with space
>     2. Replace the Pokémon you just deposited in step 1 with something from Box 1.
>         - You cannot withdraw something you just deposited in step 1.
>     3. Only 1 box may have empty spaces at a time. If you have Pokémon in Box 2 and space in Box 1, move Pokémon from Box 2 to Box 1 until it is full. Repeat this process for each box until only the last one has space.
>         - A Pokémon cannot move more than 1 box during this process. (i.e. no moving something from Box 7 down to Box 1 in a single swap)
> - A white-out counts as a Pokémon Center heal, which means you must perform a randomized swap.
> - You must catch all DISTINCT Pokemon you possibly can.
>     - You don't have to catch the first of a species you encounter, just so long as you don't intentionally avoid catching things entirely.
> - Play honorably. Don't try to game the rules by using or avoiding Pokemon Centers excessively!


## Features
- Customizable number of swaps
- Randomize swap-ins as well as swap-outs
- Randomize box shifts
- Uses a JSON file for reusing configurations between sessions


## Development
To run the source code, you need Python 3.6 or above as well as the `PySimpleGUI` package

```
pip install --upgrade PySimpleGUI
```


### To Do
In no particular order:

- In-app About information
- use PySimpleGUI's UserSettings rather than a manually managed JSON
- Full saved configuration management (delete)
- Text version of swap suggestions (see [this gist](https://gist.github.com/SpiredMoth/da6d71ec19b5ccd3c75227feccfa0a07) for my original CLI version of this tool)
- Session swap history log
