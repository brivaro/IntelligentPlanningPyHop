<div align="center">
<h1>🚚 Intelligent Planning with PyHop in Python</h1>
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg" height="100" alt="python logo" />
</div>

---

### 💡 Overview
This project implements an intelligent planning system using the PyHop planner in Python. The system models a transportation domain where drivers, trucks, and packages must be coordinated across multiple cities while respecting cost constraints. By employing Hierarchical Task Network (HTN) planning, the project decomposes complex transportation tasks into simpler, manageable actions using clearly defined operators and methods.

### 🗳 Features
- **HTN Planning with PyHop:**  
  Utilizes PyHop to break down high-level transportation goals into atomic operators and methods.
  
- **Dynamic Cost Management:**  
  Incorporates cost constraints via walking and bus travel (with different cost constants) to ensure the overall plan does not exceed a specified limit.
  
- **Modular Domain Modeling:**  
  Separates domain definitions (in `domain.py`) from the problem instance (in `problem.py`), making it easy to extend and modify the system.
  
- **Robust and Extensible Code:**  
  Provides a clear and scalable structure to model states, tasks, and planning operators, facilitating future enhancements.

- **Comprehensive Documentation:**  
  Comes with an in-depth report (`ValienteRodenasBrian_TRABAJO.pdf`) that details the problem, domain modeling, and plan execution strategies.

### 📌 Technologies Used
- **Python** – Core programming language.
- **PyHop** – Lightweight HTN planner for generating plans.
- **Markdown** – For creating project documentation.
- **Graphical Tools** – For visualizing planning models and cost constraints.

## 📖 Getting Started

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/brivaro/IntelligentPlanningPyHop

2. **Install Dependencies:** Ensure you have Python 3.6 or higher installed. Using the `pyhop.py` that it is already in the repo.

3. **Run the Planner:** Execute the problem instance to generate a plan.
   ```bash
   python problem.py
