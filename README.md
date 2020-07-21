# Snake AI

## Getting started

Install dependencies:
```bash
python3 -m virtualenv env
source env/bin/activate
pip install -r requirements.txt
```

Start game:
```
./game.py
```

## game.py

The main script takes options which change many aspects of the game. Use
```
./game.py --help
```
to see all the options.

The project consists of a core layer and different plugins that add functionalities. For example:

- Renderer plugins: they render the game state on the screen (e.g. `PgRenderer`). A renderer plugin is optional
and can be disabled, for example, as when an AI agent is training and no one is looking at the screen.
- Environment plugins: The core of the game logic. Typically, it would be the snake game logic, but it can be
replaced, for example, with a memory playback, in which the state progresses according to a previously saved
gameplay.
- Controller plugins: defines the control of the snake's actions. It can be either keyboard input handling,
or an AI agent that is setting the actions.
- Sound plugins: Enables sound.
- Auxiliary plugins: Add generic functionalities, such as recording a gameplay to a file.

Note that whichever controller plugin is chosen, there's always a basic keyboard input handling happening.
This is used to read events such as pressing Escape (which stops the game), or anything that is not
directly tied to the movement of the snake.

Examples:

Run the game without sound, updating the game state every 50ms and record the gameplay in a given file.
```
./game.py --sound off --speed 50 --record my_gameplay
```
This records the file *my_gameplay* in the *recordings/* directory. The recording can be played back with
```
./game.py --playback my_gameplay
```

