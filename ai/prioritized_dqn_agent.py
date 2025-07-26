import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import numpy as np
import random
from ai.prioritized_replay_buffer import PrioritizedReplayBuffer

class DQNNetwork(nn.Module):
    """
    Deep Q Network
    """
    def __init__(self, state_size, action_size, hidden_size=256):
        super(DQNNetwork, self).__init__()
        self.fc1 = nn.Linear(state_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        self.fc3 = nn.Linear(hidden_size, hidden_size)
        self.fc4 = nn.Linear(hidden_size, action_size)
        self.dropout = nn.Dropout(0.2)
        
    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = F.relu(self.fc2(x))
        x = self.dropout(x)
        x = F.relu(self.fc3(x))
        x = self.fc4(x)
        return x

class PrioritizedDQNAgent:
    """
    DQN Agent based on Prioritized Experience Replay
    """
    def __init__(self, state_size, action_size, lr=0.0001, gamma=0.99, epsilon=1.0, 
                 epsilon_min=0.01, epsilon_decay=0.995, buffer_size=100000, 
                 batch_size=64, update_freq=4, target_update_freq=1000):
        """
        Args:
            state_size: State space dimension
            action_size: Action space dimension (special handling for MultiBinary)
            lr: Learning rate
            gamma: Discount factor
            epsilon: Exploration rate
            epsilon_min: Minimum exploration rate
            epsilon_decay: Exploration rate decay
            buffer_size: Experience replay buffer size
            batch_size: Batch size
            update_freq: Network update frequency
            target_update_freq: Target network update frequency
        """
        self.state_size = state_size
        if hasattr(action_size, 'n'):
            self.action_size = action_size.n  # Dimension count of MultiBinary space
        else:
            self.action_size = action_size
            
        self.lr = lr
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.batch_size = batch_size
        self.update_freq = update_freq
        self.target_update_freq = target_update_freq
        
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Using device: {self.device}")
        
        self.discrete_action_size = 2 ** self.action_size
        
        # Neural networks
        self.q_network = DQNNetwork(state_size, self.discrete_action_size).to(self.device)
        self.target_network = DQNNetwork(state_size, self.discrete_action_size).to(self.device)
        self.optimizer = optim.Adam(self.q_network.parameters(), lr=lr)
        
        # Initialize target network
        self.target_network.load_state_dict(self.q_network.state_dict())
        
        # Experience replay buffer
        self.memory = PrioritizedReplayBuffer(buffer_size)
        
        # Counters
        self.step_count = 0
        self.update_count = 0
        
    def multibinary_to_discrete(self, multibinary_action):
        """Convert MultiBinary action to discrete action index"""
        return int(''.join(map(str, multibinary_action)), 2)
    
    def discrete_to_multibinary(self, discrete_action):
        """Convert discrete action index to MultiBinary action"""
        binary_str = format(discrete_action, f'0{self.action_size}b')
        return np.array([int(bit) for bit in binary_str])
    
    def act(self, state, training=True):
        """Select action"""
        if training and np.random.random() <= self.epsilon:
            # Random action
            discrete_action = np.random.randint(0, self.discrete_action_size)
        else:
            # Greedy action
            state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
            with torch.no_grad():
                q_values = self.q_network(state_tensor)
                discrete_action = q_values.argmax().item()
        
        # Convert to MultiBinary format
        multibinary_action = self.discrete_to_multibinary(discrete_action)
        return multibinary_action
    
    def remember(self, state, action, reward, next_state, done):
        """Store experience"""
        # Convert MultiBinary action to discrete action
        discrete_action = self.multibinary_to_discrete(action)
        self.memory.add(state, discrete_action, reward, next_state, done)
    
    def replay(self):
        """Experience replay learning"""
        if len(self.memory) < self.batch_size:
            return
        
        # Sample from prioritized buffer
        batch, idxs, is_weights = self.memory.sample(self.batch_size)
        if batch is None:
            return
        
        # Prepare batch data
        states = torch.FloatTensor([e.state for e in batch]).to(self.device)
        actions = torch.LongTensor([e.action for e in batch]).to(self.device)
        rewards = torch.FloatTensor([e.reward for e in batch]).to(self.device)
        next_states = torch.FloatTensor([e.next_state for e in batch]).to(self.device)
        dones = torch.BoolTensor([e.done for e in batch]).to(self.device)
        is_weights = torch.FloatTensor(is_weights).to(self.device)
        
        # Current Q values
        current_q_values = self.q_network(states).gather(1, actions.unsqueeze(1)).squeeze(1)
        
        # Next state Q values (using target network)
        with torch.no_grad():
            next_q_values = self.target_network(next_states).max(1)[0]
            target_q_values = rewards + (self.gamma * next_q_values * ~dones)
        
        # TD errors
        td_errors = target_q_values - current_q_values
        
        # Weighted loss
        loss = (is_weights * F.mse_loss(current_q_values, target_q_values, reduction='none')).mean()
        
        # Backpropagation
        self.optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(self.q_network.parameters(), 1.0)
        self.optimizer.step()
        
        # Update priorities
        priorities = torch.abs(td_errors).detach().cpu().numpy() + 1e-6
        self.memory.update_priorities(idxs, priorities)
        
        # Update counter
        self.update_count += 1
        
        return loss.item()
    
    def step(self, state, action, reward, next_state, done):
        """Execute one learning step"""
        self.step_count += 1
        
        # Store experience
        self.remember(state, action, reward, next_state, done)
        
        # Learn periodically
        if self.step_count % self.update_freq == 0:
            loss = self.replay()
            
            # Update target network
            if self.step_count % self.target_update_freq == 0:
                self.target_network.load_state_dict(self.q_network.state_dict())
                print(f"Target network updated at step {self.step_count}")
            
            return loss
        
        return None
    
    def update_epsilon(self):
        """Update exploration rate"""
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
    
    def save(self, filepath):
        """Save model"""
        torch.save({
            'q_network_state_dict': self.q_network.state_dict(),
            'target_network_state_dict': self.target_network.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'epsilon': self.epsilon,
            'step_count': self.step_count,
            'update_count': self.update_count
        }, filepath)
        print(f"Model saved to {filepath}")
    
    def load(self, filepath):
        """Load model"""
        checkpoint = torch.load(filepath, map_location=self.device)
        self.q_network.load_state_dict(checkpoint['q_network_state_dict'])
        self.target_network.load_state_dict(checkpoint['target_network_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.epsilon = checkpoint['epsilon']
        self.step_count = checkpoint['step_count']
        self.update_count = checkpoint['update_count']
        print(f"Model loaded from {filepath}")
    
    def get_stats(self):
        """Get training statistics"""
        return {
            'epsilon': self.epsilon,
            'step_count': self.step_count,
            'update_count': self.update_count,
            'memory_size': len(self.memory),
            'beta': self.memory.beta
        } 