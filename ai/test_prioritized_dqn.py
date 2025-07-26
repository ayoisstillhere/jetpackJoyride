import os
import time
import numpy as np
from ai.jetpack_env import JetpackEnv
from ai.prioritized_dqn_agent import PrioritizedDQNAgent

def test_prioritized_dqn(model_path="ai/models/best.pth", n_episodes=5, render=True):
    """
    Test the trained prioritized DQN model
    """
    print("="*60)
    print("Testing Prioritized DQN Agent")
    print("="*60)
    
    # Create environment
    env = JetpackEnv(render=render, debug=False)
    state_size = env.observation_space.shape[0]
    action_size = env.action_space  # Pass the entire action space object
    
    # Create agent and load model
    agent = PrioritizedDQNAgent(
        state_size=state_size,
        action_size=action_size,
        epsilon=0.0  # No exploration during testing
    )
    
    try:
        agent.load(model_path)
        print(f"✅ Model loaded successfully from {model_path}")
    except FileNotFoundError:
        print(f"❌ Model file not found: {model_path}")
        print("Please train the model first using train_prioritized_dqn.py")
        return
    
    # Test multiple episodes
    results = []
    
    for episode in range(1, n_episodes + 1):
        print(f"\n🎮 Starting Episode {episode}/{n_episodes}")
        
        state = env.reset()
        total_reward = 0
        steps = 0
        done = False
        
        episode_start_time = time.time()
        
        while not done:
            # Select action (no exploration)
            action = agent.act(state, training=False)
            
            # Execute action
            next_state, reward, done, info = env.step(action)
            
            # Update state
            state = next_state
            total_reward += reward
            steps += 1
            
            # Frame rate control when rendering
            if render:
                time.sleep(1/60)  # 60 FPS
            
            # Prevent infinite loops
            if steps > 10000:
                print("⚠️  Episode too long, stopping...")
                break
        
        episode_time = time.time() - episode_start_time
        
        # Record results
        result = {
            'episode': episode,
            'total_reward': total_reward,
            'distance': env.game.state.distance,
            'coins': env.game.state.coin_count,
            'steps': steps,
            'time': episode_time
        }
        results.append(result)
        
        # Print episode results
        print(f"📊 Episode {episode} Results:")
        print(f"   Total Reward: {total_reward:.2f}")
        print(f"   Distance: {env.game.state.distance:.1f}m")
        print(f"   Coins Collected: {env.game.state.coin_count}")
        print(f"   Steps: {steps}")
        print(f"   Time: {episode_time:.1f}s")
    
    # Calculate overall statistics
    print(f"\n{'='*60}")
    print("📈 Overall Results:")
    print(f"{'='*60}")
    
    avg_reward = np.mean([r['total_reward'] for r in results])
    avg_distance = np.mean([r['distance'] for r in results])
    avg_coins = np.mean([r['coins'] for r in results])
    avg_steps = np.mean([r['steps'] for r in results])
    avg_time = np.mean([r['time'] for r in results])
    
    max_reward = max([r['total_reward'] for r in results])
    max_distance = max([r['distance'] for r in results])
    max_coins = max([r['coins'] for r in results])
    
    print(f"Average Reward: {avg_reward:.2f}")
    print(f"Average Distance: {avg_distance:.1f}m")
    print(f"Average Coins: {avg_coins:.1f}")
    print(f"Average Steps: {avg_steps:.1f}")
    print(f"Average Episode Time: {avg_time:.1f}s")
    print(f"")
    print(f"Best Reward: {max_reward:.2f}")
    print(f"Best Distance: {max_distance:.1f}m")
    print(f"Best Coins: {max_coins}")
    print(f"{'='*60}")
    
    env.close()
    return results

def compare_models():
    """
    Compare performance of different checkpoint models
    """
    print("🔍 Comparing model checkpoints...")
    
    model_files = [
        "ai/models/prioritized_dqn_best.pth",
        "ai/models/prioritized_dqn_final.pth",
        "ai/models/prioritized_dqn_checkpoint_100.pth",
        "ai/models/prioritized_dqn_checkpoint_200.pth"
    ]
    
    for model_file in model_files:
        if os.path.exists(model_file):
            print(f"\n📂 Testing {model_file}:")
            results = test_prioritized_dqn(model_file, n_episodes=3, render=False)
            if results:
                avg_reward = np.mean([r['total_reward'] for r in results])
                avg_distance = np.mean([r['distance'] for r in results])
                print(f"   Average Reward: {avg_reward:.2f}")
                print(f"   Average Distance: {avg_distance:.1f}m")
        else:
            print(f"❌ {model_file} not found")

if __name__ == '__main__':
    import sys
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "compare":
            compare_models()
        elif sys.argv[1] == "no-render":
            test_prioritized_dqn(render=False)
        else:
            # Specify model file
            test_prioritized_dqn(model_path=sys.argv[1])
    else:
        # Default test
        test_prioritized_dqn() 