import numpy as np
import random
from collections import namedtuple, deque

Experience = namedtuple('Experience', ['state', 'action', 'reward', 'next_state', 'done'])

class SumTree:
    """
    SumTree data structure for efficient priority sampling
    """
    def __init__(self, capacity):
        self.capacity = capacity
        self.tree = np.zeros(2 * capacity - 1)
        self.data = np.zeros(capacity, dtype=object)
        self.write = 0
        self.n_entries = 0

    def _propagate(self, idx, change):
        """Propagate changes up to parent nodes"""
        parent = (idx - 1) // 2
        self.tree[parent] += change
        if parent != 0:
            self._propagate(parent, change)

    def _retrieve(self, idx, s):
        """Retrieve sample index"""
        left = 2 * idx + 1
        right = left + 1

        if left >= len(self.tree):
            return idx

        if s <= self.tree[left]:
            return self._retrieve(left, s)
        else:
            return self._retrieve(right, s - self.tree[left])

    def total(self):
        """Return the sum of the root node"""
        return self.tree[0]

    def add(self, p, data):
        """Add new experience"""
        idx = self.write + self.capacity - 1

        self.data[self.write] = data
        self.update(idx, p)

        self.write += 1
        if self.write >= self.capacity:
            self.write = 0

        if self.n_entries < self.capacity:
            self.n_entries += 1

    def update(self, idx, p):
        """Update priority"""
        change = p - self.tree[idx]
        self.tree[idx] = p
        self._propagate(idx, change)

    def get(self, s):
        """Get experience based on priority"""
        idx = self._retrieve(0, s)
        dataIdx = idx - self.capacity + 1
        return (idx, self.tree[idx], self.data[dataIdx])

class PrioritizedReplayBuffer:
    """
    Prioritized Experience Replay Buffer
    """
    def __init__(self, capacity, alpha=0.6, beta=0.4, beta_increment=0.001):
        """
        Args:
            capacity: Buffer capacity
            alpha: Priority exponent, controls the influence of priorities
            beta: Importance sampling exponent, initial value
            beta_increment: Beta growth rate
        """
        self.capacity = capacity
        self.alpha = alpha
        self.beta = beta
        self.beta_increment = beta_increment
        self.max_beta = 1.0
        
        self.tree = SumTree(capacity)
        self.max_priority = 1.0
        self.min_priority = 0.01

    def add(self, state, action, reward, next_state, done):
        """Add experience to buffer"""
        experience = Experience(state, action, reward, next_state, done)
        priority = self.max_priority ** self.alpha
        self.tree.add(priority, experience)

    def sample(self, batch_size):
        """Sample a batch of experiences"""
        if self.tree.n_entries < batch_size:
            return None, None, None

        batch = []
        idxs = []
        segment = self.tree.total() / batch_size
        priorities = []

        # Increase beta until reaching maximum value
        self.beta = min(self.max_beta, self.beta + self.beta_increment)

        for i in range(batch_size):
            a = segment * i
            b = segment * (i + 1)
            s = random.uniform(a, b)
            idx, priority, experience = self.tree.get(s)
            
            batch.append(experience)
            idxs.append(idx)
            priorities.append(priority)

        # Calculate importance sampling weights
        sampling_probabilities = np.array(priorities) / self.tree.total()
        is_weights = np.power(self.tree.n_entries * sampling_probabilities, -self.beta)
        is_weights /= is_weights.max()

        return batch, idxs, is_weights

    def update_priorities(self, idxs, priorities):
        """Update experience priorities"""
        for idx, priority in zip(idxs, priorities):
            # Limit priority range
            priority = max(self.min_priority, abs(priority))
            self.max_priority = max(self.max_priority, priority)
            self.tree.update(idx, priority ** self.alpha)

    def __len__(self):
        return self.tree.n_entries

    def is_full(self):
        return self.tree.n_entries >= self.capacity 