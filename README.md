# Sophia Maze Project

## Getting Started

1. **Clone your repo**

   ```bash
   git clone https://github.com/Edwin-A-B-White/Python_Maze_Game.git
   cd Python_Maze_Game
   ```

2. **Create & activate a virtual environment**

   ```bash
   python3 -m venv venv
   source venv/bin/activate    # macOS/Linux
   venv\Scripts\activate       # Windows
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the maze game**

   ```bash
   python maze_game.py
   ```

## Continuous Integration

On each push, GitHub Actions will install your requirements and verify there are no syntax errors:

```yaml
name: Maze Project

on: [push]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.x'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Syntax check
        run: python -m py_compile maze_game.py
```
