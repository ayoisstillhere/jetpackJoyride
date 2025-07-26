# Prioritized Experience Replay DQN Training

This project implements a DQN agent with Prioritized Experience Replay to train an AI for the Jetpack game.

## File Description

- `prioritized_replay_buffer.py`: Prioritized experience replay buffer implementation
- `prioritized_dqn_agent.py`: DQN agent based on prioritized experience replay
- `train_prioritized_dqn.py`: Training script
- `test_prioritized_dqn.py`: Testing script

## Advantages of Prioritized Experience Replay

1. **More Efficient Learning**: Prioritizes experiences with larger TD errors, improving learning efficiency
2. **Better Sample Utilization**: Important experiences are replayed more frequently
3. **Faster Convergence**: Usually achieves better performance faster compared to regular experience replay
4. **Importance Sampling**: Corrects sampling bias through IS weights

## Training the Model

```bash
python -m ai.train_prioritized_dqn
```

## Testing the Model

```bash
# Default test (with rendering)
python -m ai.test_prioritized_dqn

# Test without rendering
python -m ai.test_prioritized_dqn no-render

# Compare different checkpoints
python -m ai.test_prioritized_dqn compare

# Test specific model
python -m ai.test_prioritized_dqn ai/models/prioritized_dqn_checkpoint_100.pth
```

## Model Files

After training completion, the following model files will be generated:
- `ai/models/prioritized_dqn_best.pth`: Best performing model
- `ai/models/prioritized_dqn_final.pth`: Final trained model
- `ai/models/prioritized_dqn_checkpoint_X.pth`: Periodically saved checkpoints

## Training Curves

After training completion, training curve plots will be generated in the `ai/plots/` directory, including:
- Reward curves
- Loss curves
- Distance curves
- Coin collection curves

## Hyperparameter Tuning

You can adjust training by modifying parameters in `train_prioritized_dqn.py`:

```python
agent = PrioritizedDQNAgent(
    state_size=state_size,
    action_size=action_size,
    lr=0.0001,           # Learning rate
    gamma=0.99,          # Discount factor
    epsilon=1.0,         # Initial exploration rate
    epsilon_min=0.01,    # Minimum exploration rate
    epsilon_decay=0.9995,# Exploration rate decay
    buffer_size=100000,  # Buffer size
    batch_size=64,       # Batch size
    update_freq=4,       # Update frequency
    target_update_freq=1000 # Target network update frequency
)
```

Prioritized replay buffer parameters:
- `alpha=0.6`: Priority exponent, controls the influence of priorities
- `beta=0.4`: Initial importance sampling exponent value
- `beta_increment=0.001`: Beta growth rate