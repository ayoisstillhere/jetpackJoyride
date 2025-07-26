import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from collections import deque
import time
from ai.jetpack_env import JetpackEnv
from ai.prioritized_dqn_agent import PrioritizedDQNAgent

class Logger:
    def __init__(self, log_file):
        self.terminal = sys.stdout
        self.log = open(log_file, "a", encoding='utf-8')

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        self.terminal.flush()
        self.log.flush()

def train_prioritized_dqn(start_episode=1, end_episode=4000, checkpoint_path=None):
    # Create directories
    os.makedirs("logs", exist_ok=True)
    os.makedirs("ai/models", exist_ok=True)
    os.makedirs("ai/plots", exist_ok=True)
    
    # Setup logging
    log_file = f"logs/prioritized_dqn_train_{start_episode}_to_{end_episode}.log"
    sys.stdout = Logger(log_file)
    
    print("="*60)
    if start_episode > 1:
        print(f"Continue Prioritized DQN Jetpack Training ({start_episode} -> {end_episode})")
    else:
        print("Prioritized DQN Jetpack Training Started")
    print("="*60)
    
    # Environment parameters
    env = JetpackEnv(render=False, debug=False)
    state_size = env.observation_space.shape[0]
    action_size = env.action_space  
    
    print(f"State size: {state_size}")
    print(f"Action space: {action_size}")
    print(f"Action space type: {type(action_size)}")
    
    # Agent parameters
    agent = PrioritizedDQNAgent(
        state_size=state_size,
        action_size=action_size,
        lr=0.0001,
        gamma=0.99,
        epsilon=1.0,
        epsilon_min=0.01,
        epsilon_decay=0.9995,
        buffer_size=100000,
        batch_size=64,
        update_freq=4,
        target_update_freq=1000
    )
    
    # If checkpoint is specified or start_episode > 1, try to load checkpoint
    if checkpoint_path or start_episode > 1:
        if not checkpoint_path:
            checkpoint_path = f"ai/models/prioritized_dqn_checkpoint_{start_episode - 1}.pth"
        
        if os.path.exists(checkpoint_path):
            print(f"Loading checkpoint from {checkpoint_path}")
            agent.load(checkpoint_path)
            print(f"Loaded! Current epsilon: {agent.epsilon:.4f}")
        else:
            print(f"Warning: Checkpoint {checkpoint_path} not found!")
            if start_episode > 1:
                print("Starting from episode 1 instead")
                start_episode = 1
    
    # Training parameters
    n_episodes = end_episode
    max_steps_per_episode = 5000
    solve_score = 200  # Target score
    
    # Statistics
    scores = deque(maxlen=100)
    episode_rewards = []
    losses = []
    distances = []
    coins_collected = []
    
    # Training loop
    start_time = time.time()
    
    print(f"Training from episode {start_episode} to {end_episode}")
    
    for episode in range(start_episode, n_episodes + 1):
        state = env.reset()
        total_reward = 0
        steps = 0
        episode_losses = []
        
        for step in range(max_steps_per_episode):
            # Select action
            action = agent.act(state, training=True)
            
            # Execute action
            next_state, reward, done, info = env.step(action)
            
            # Learn
            loss = agent.step(state, action, reward, next_state, done)
            if loss is not None:
                episode_losses.append(loss)
            
            # Update state
            state = next_state
            total_reward += reward
            steps += 1
            
            if done:
                break
        
        # Update exploration rate
        agent.update_epsilon()
        
        # Record statistics
        scores.append(total_reward)
        episode_rewards.append(total_reward)
        distances.append(env.game.state.distance)
        coins_collected.append(env.game.state.coin_count)
        
        if episode_losses:
            avg_loss = np.mean(episode_losses)
            losses.append(avg_loss)
        else:
            losses.append(0)
        
        # Print progress
        mean_score = np.mean(scores)
        if episode % 10 == 0:
            stats = agent.get_stats()
            elapsed_time = time.time() - start_time
            print(f"Episode {episode:4d} | "
                  f"Score: {total_reward:6.1f} | "
                  f"Mean Score: {mean_score:6.1f} | "
                  f"Distance: {env.game.state.distance:6.1f} | "
                  f"Coins: {env.game.state.coin_count:3d} | "
                  f"Steps: {steps:4d} | "
                  f"Epsilon: {stats['epsilon']:.3f} | "
                  f"Beta: {stats['beta']:.3f} | "
                  f"Memory: {stats['memory_size']:5d} | "
                  f"Loss: {losses[-1]:.4f} | "
                  f"Time: {elapsed_time/60:.1f}m")
        
        # Save checkpoint
        if episode % 100 == 0:
            agent.save(f"ai/models/prioritized_dqn_checkpoint_{episode}.pth")
            
        # Save best model
        if mean_score >= solve_score:
            print(f"\n🎉 Environment solved in {episode} episodes!")
            print(f"Average score: {mean_score:.2f}")
            agent.save("ai/models/prioritized_dqn_best.pth")
            break
    
    # Save final model
    final_model_name = f"prioritized_dqn_final_{end_episode}.pth" if end_episode != 4000 else "prioritized_dqn_final.pth"
    agent.save(f"ai/models/{final_model_name}")
    
    # Plot training curves
    plot_training_results(episode_rewards, losses, distances, coins_collected, start_episode, end_episode)
    
    # Final statistics
    total_time = time.time() - start_time
    print(f"\n{'='*60}")
    print(f"Training completed!")
    print(f"Episodes trained: {start_episode} to {episode}")
    print(f"Total time: {total_time/60:.1f} minutes")
    print(f"Average score (last 100 episodes): {np.mean(scores):.2f}")
    print(f"Best score: {max(episode_rewards):.2f}")
    print(f"Final epsilon: {agent.epsilon:.3f}")
    print(f"Memory size: {len(agent.memory)}")
    print(f"{'='*60}")

def plot_training_results(rewards, losses, distances, coins, start_episode=1, end_episode=None):
    """Plot training results"""
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    # Create episode list
    episodes = list(range(start_episode, start_episode + len(rewards)))
    if end_episode is None:
        end_episode = start_episode + len(rewards) - 1
    
    # Reward curve
    axes[0, 0].plot(episodes, rewards)
    title_suffix = f" (Episodes {start_episode}-{end_episode})" if start_episode > 1 else ""
    axes[0, 0].set_title(f'Episode Rewards{title_suffix}')
    axes[0, 0].set_xlabel('Episode')
    axes[0, 0].set_ylabel('Total Reward')
    axes[0, 0].grid(True)
    
    # Add moving average
    if len(rewards) > 10:
        window = min(50, len(rewards) // 10)
        moving_avg = np.convolve(rewards, np.ones(window)/window, mode='valid')
        axes[0, 0].plot(range(episodes[window-1], episodes[-1]+1), moving_avg, 'r-', linewidth=2, label=f'Moving Average ({window})')
        axes[0, 0].legend()
    
    # Loss curve
    axes[0, 1].plot(episodes, losses)
    axes[0, 1].set_title('Training Loss')
    axes[0, 1].set_xlabel('Episode')
    axes[0, 1].set_ylabel('Loss')
    axes[0, 1].grid(True)
    
    # Distance curve
    axes[1, 0].plot(episodes, distances)
    axes[1, 0].set_title('Distance Traveled')
    axes[1, 0].set_xlabel('Episode')
    axes[1, 0].set_ylabel('Distance')
    axes[1, 0].grid(True)
    
    # Coin collection curve
    axes[1, 1].plot(episodes, coins)
    axes[1, 1].set_title('Coins Collected')
    axes[1, 1].set_xlabel('Episode')
    axes[1, 1].set_ylabel('Coins')
    axes[1, 1].grid(True)
    
    plt.tight_layout()
    plot_filename = f'prioritized_dqn_training_results_{start_episode}_to_{end_episode}.png'
    plt.savefig(f'ai/plots/{plot_filename}', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Training plots saved to ai/plots/{plot_filename}")

if __name__ == '__main__':
    # control training by modifying these parameters
    # Continue training from 4000 to 6000:
    # train_prioritized_dqn(start_episode=4001, end_episode=6000)
    
    # Train from scratch to 4000 (default):
    train_prioritized_dqn()
    