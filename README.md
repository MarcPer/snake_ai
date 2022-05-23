# Snake AI

## Getting started

The older Python version 3.6 is required. This can be managed with [Anaconda](https://docs.conda.io/en/latest/miniconda.html).

Install python 3.6:
```bash
conda create -n py36 python=3.6.13
conda activate py36
```

Install OS dependencies (Debian/Ubuntu):
```bash
sudo apt-get install \
  libsdl1.2-dev \
  libsdl-image1.2-dev \
  libsdl-mixer1.2-dev \
  libsdl-ttf2.0-dev \
  libavformat-dev \
  libportmidi-dev
```


Install Python-specific dependencies:
```bash
pip install -r requirements.txt
```

Start game:
```
./game.py
```

## Game options

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

## Train AI model

To train an AI model using PPO2 from [stable baselines](https://github.com/hill-a/stable-baselines), run

```bash
./train.py
```

This will train the AI on a 4x4 grid and save the result in the `models` directory. Running `train.py` repeateadly further trains the model, if there is one saved already in the `models` directory.

To see the AI playing the game, start the game making sure the grid size is the same as what the model was trained for:
```bash
./game.py --controller sb:ppo2 ppo2_model1 --grid_size 4
```

To train multiple models in parallel with different hyperparameters, use


The reward and other metrics for each model can be seen in real time during training with tensorboard:
```
tensorboard --logdir logs/
```

This starts a server locally at http://127.0.0.1:6006/#scalars

## Recording gameplay

The `game.py` script can record a gameplay with the `--record <filename>` option and replay it with `--playback <filename>`. Only the file name needs to be given, not a complete path - recordings are stored in the `recordings` directory. Note that the `--speed` option also affects the playback.

