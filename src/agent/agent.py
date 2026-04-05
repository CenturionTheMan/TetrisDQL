import random
from collections import deque
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim


class QNetwork(nn.Module):
    
    def __init__(self, state_size: int):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(state_size, 64),
            nn.ReLU(),
            nn.Linear(64, 64),
            nn.ReLU(),
            nn.Linear(64, 1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x).squeeze(-1) 


class ReplayBuffer:

    def __init__(self, capacity: int):
        self.buffer: deque = deque(maxlen=capacity)

    def push(self, state: np.ndarray, reward: float, next_states: list, done: bool) -> None:
        self.buffer.append((state, reward, next_states, done))

    def sample(self, batch_size: int) -> list:
        return random.sample(self.buffer, batch_size)

    def __len__(self) -> int:
        return len(self.buffer)


class DQLAgent:

    def __init__(
        self,
        state_size: int,
        lr: float = 1e-3,
        gamma: float = 0.99,
        epsilon_start: float = 1.0,
        epsilon_end: float = 0.01,
        epsilon_decay: float = 0.995,
        batch_size: int = 512,
        target_update_freq: int = 50,
        buffer_capacity: int = 50_000,
    ):
        self.state_size = state_size 
        self.gamma = gamma
        self.epsilon = epsilon_start
        self.epsilon_end = epsilon_end
        self.epsilon_decay = epsilon_decay
        self.batch_size = batch_size
        self.target_update_freq = target_update_freq

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        self.policy_net = QNetwork(state_size).to(self.device) # sieć uczona
        self.target_net = QNetwork(state_size).to(self.device) # sieć zamrożona
        self.target_net.load_state_dict(self.policy_net.state_dict())
        self.target_net.eval() # ustawiamy target net żeby tylko ewaluował

        self.optimizer = optim.Adam(self.policy_net.parameters(), lr=lr)
        self.memory = ReplayBuffer(buffer_capacity)
        self.episodes_done = 0

    def select_action(self, placements: list) -> int: # placement to lista możliwych ruchów

        if not placements: # jeśli nie ma to zwracamy zero
            return 0
        if random.random() < self.epsilon: # jeśli wylosowało mniej niż epsilon to wybiera losowo 
            return random.randrange(len(placements))

        features = np.array([p[2] for p in placements], dtype=np.float32) # cechy planszy
        features_t = torch.tensor(features, device=self.device)
        with torch.no_grad():
            q_values = self.policy_net(features_t) # wartość Q dla każdego ruchu
        return int(q_values.argmax().item())

    def store(self, state: np.ndarray, reward: float, next_placements: list, done: bool) -> None:
        next_feats = [p[2] for p in next_placements] if next_placements else []
        self.memory.push(state, reward, next_feats, done)

    def learn(self) -> float | None:
        if len(self.memory) < self.batch_size:
            return None # jeśli za mało stanów w pamięci to zwracamy None

        batch = self.memory.sample(self.batch_size) # bierzemy losowo stany z pamięci
        states, rewards, next_states_list, dones = zip(*batch)

        states_t = torch.tensor(np.array(states), dtype=torch.float32, device=self.device)
        q_values = self.policy_net(states_t)  # wartości Q dla stanów z bufora

        targets = []
        for reward, next_states, done in zip(rewards, next_states_list, dones):
            if done or not next_states:
                targets.append(float(reward))
            else: 
                ns_t = torch.tensor(np.array(next_states), dtype=torch.float32, device=self.device) # tensor wszystkich możliwych ruchów w następnym stanie
                with torch.no_grad():
                    best_next_q = self.target_net(ns_t).max().item() # wartość Q najlepszego możliwego ruchu w następnym stanie
                targets.append(float(reward) + self.gamma * best_next_q)

        targets_t = torch.tensor(targets, dtype=torch.float32, device=self.device)

        loss = F.mse_loss(q_values, targets_t)
        self.optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(self.policy_net.parameters(), max_norm=1.0)
        self.optimizer.step()

        return loss.item()

    def update_target(self) -> None:
        self.target_net.load_state_dict(self.policy_net.state_dict())

    def decay_epsilon(self) -> None:
        self.epsilon = max(self.epsilon_end, self.epsilon * self.epsilon_decay)
        self.episodes_done += 1

    def save(self, path: str) -> None:
        torch.save({
            "policy_net": self.policy_net.state_dict(),
            "target_net": self.target_net.state_dict(),
            "optimizer": self.optimizer.state_dict(),
            "epsilon": self.epsilon,
            "episodes_done": self.episodes_done,
        }, path)

    def load(self, path: str) -> None:
        checkpoint = torch.load(path, map_location=self.device, weights_only=False)
        self.policy_net.load_state_dict(checkpoint["policy_net"])
        self.target_net.load_state_dict(checkpoint["target_net"])
        self.optimizer.load_state_dict(checkpoint["optimizer"])
        self.epsilon = checkpoint.get("epsilon", self.epsilon_end)
        self.episodes_done = checkpoint.get("episodes_done", 0)
