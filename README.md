# Jetpack Joyride (AI version)

A custom Jetpack Joyride-like game where an AI agent (trained with Stable-Baselines3) can play automatically.
You can also run it manually without any model.

---

## 1. Requirements

- Python >= 3.12
- Dependencies: pygame, gym, stable-baselines3, huggingface-hub, numpy, tensorboard

Install dependencies in the ```pyproject.toml``` with your favorite package manager.

## 2. Running the game

```python main.py```

By default:

- The game will automatically download the SAC pretrained model from the Hugging Face Hub [yanka9/jetpack-sb3sac-models](https://huggingface.co/yanka9/jetpack-sb3sac-models/tree/main) if not already cached.
- The AI will then control the player. If you want to run with a specific model file stored in the Hugging Face Hub repository, pass filename flag:

```python main.py --filename [YOUR MODEL].zip```

## 3. Manual play

You can control the game manually:

- Space: start the game.
- Key T: toggle on the manual control
- Keys W,A,D: move up, left, right
- Left mouse button: shoot

Now collect coins and avoid obstacles.

## 4. Notes
- The game runs fine on CPU for inference.
- No Hugging Face account or login is required for downloading public models.
- The first time you run it with a new filename, the file will be downloaded and cached by huggingface_hub.