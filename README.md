# TetrisDQL

A classic Tetris implementation with a modified scoring system and a Deep Q-Learning (DQL) agent trained to play the game.

## Overview

The **TetrisDQL** project aims to achieve two primary goals:

1. Implement a playable Tetris game with a modified scoring system.

2. Develop and train an AI agent capable of playing the game using Deep Q-Learning (DQL).

The main difference between the classic Tetris and this implementation lies in the scoring mechanism. In this version, each block is assigned a distinct score value. When a row is cleared, the player receives a reward equal to the sum of the squared values of the blocks in that row.

This modification encourages more strategic gameplay. Instead of clearing rows as quickly as possible, it may be advantageous to delay clearing and build higher structures in order to accumulate more valuable blocks within a single row, resulting in a higher score.

## Schedule

### Milestones

- 28.04.2026 – Game implementation (logic + GUI)
- 09.06.2026 – DQL agent: architecture, training, testing, and presentation

### Features

- ✅ Core Tetris game logic
- ✅ Console user interface
- 🔄 Graphical user interface (in progress)
- 🔄 DQL agent integration (in progress)

## Usage

### Prerequisites

- Python 3.x
- pip package manager

### Installation

1. Clone the repository:

```bash
git clone https://github.com/CenturionTheMan/TetrisDQL.git
cd TetrisDQL
```

2. Install required dependencies:

```bash
pip install -r requirements.txt
```
