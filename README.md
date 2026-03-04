# Advanced Python Calculator (Midterm Project)

## Project Overview

This project implements an advanced command-line calculator built in Python. The application supports multiple mathematical operations, maintains calculation history, and demonstrates professional software engineering practices including configuration management, logging, serialization with pandas, automated testing, and continuous integration.

The calculator allows users to perform operations interactively through a REPL (Read-Evaluate-Print Loop) interface and persist calculation history between sessions using CSV files.

---

# Features

- Command Line REPL Calculator
- Multiple mathematical operations
- Persistent calculation history
- Undo and redo functionality
- Configurable environment settings
- Automatic logging
- Serialization and deserialization using pandas
- Robust error handling
- Comprehensive unit testing with pytest
- Code coverage enforcement (≥90%)
- Continuous Integration using GitHub Actions
- Advanced Design Patterns (Command, Decorator, Observer, Memento, Facade, Factory)
- Color-coded terminal outputs for improved UX
- Dynamic auto-generated help menu

---

# Supported Operations

The calculator supports the following operations:

| Operation | Command Aliases | Example |
|-----------|----------------|---------|
| Addition | `add`, `+` | `add 2 3` |
| Subtraction | `sub`, `subtract`, `-` | `sub 10 4` |
| Multiplication | `mul`, `multiply`, `*` | `mul 3 5` |
| Division | `div`, `divide`, `/` | `div 10 2` |
| Power | `pow`, `power`, `**` | `pow 2 3` |
| Root | `root` | `root 16 2` |
| Modulus | `mod`, `modulus`, `%` | `mod 10 3` |
| Integer Division | `int_divide`, `//` | `int_divide 7 2` |
| Percentage | `percent`, `pct` | `percent 1 4` |
| Absolute Difference | `abs_diff`, `absdiff` | `abs_diff 10 14` |

---

# Project Structure
```text
app/
calculation.py
calculator_config.py
calculator_memento.py
calculator_repl.py
colors.py
commands.py
exceptions.py
history.py
input_validators.py
logger.py
observers.py
operations.py
tests/


```

Unit tests using pytest

.github/workflows/
GitHub Actions CI workflow


---

# Installation

### 1. Clone the repository


git clone <your-repository-url>
cd Midterm_Project


### 2. Create virtual environment


python -m venv .venv


Activate the environment:

Windows


.venv\Scripts\activate


Mac/Linux


source .venv/bin/activate


### 3. Install dependencies


pip install -r requirements.txt


---

# Environment Configuration

The application supports configuration using environment variables or a `.env` file.

Example `.env` file:


CALCULATOR_LOG_DIR=data/logs
CALCULATOR_HISTORY_DIR=data/history
CALCULATOR_HISTORY_FILE=data/history/history.csv
CALCULATOR_AUTO_SAVE=true
CALCULATOR_PRECISION=4
CALCULATOR_MAX_HISTORY_SIZE=100
CALCULATOR_MAX_INPUT_VALUE=1000000
CALCULATOR_DEFAULT_ENCODING=utf-8


---

# Running the Calculator

Start the REPL interface:


python -m app.calculator_repl


Example session:


add 2 3
Result: 5

mul 4 6
Result: 24

history
timestamp operation a b result

undo
redo
save
exit


---

# Calculation History Persistence

Calculation history is stored using **pandas** and serialized to a CSV file.

Saved columns include:

- timestamp
- operation
- operand a
- operand b
- result

History can be saved and loaded using commands:


save
load


The CSV file location is configured using:


CALCULATOR_HISTORY_FILE


---

# Logging

The calculator uses Python's logging system to track operations and errors.

Logs are written to the directory specified by:


CALCULATOR_LOG_DIR


Default location:


data/logs/calculator.log


---

# Running Tests

The project includes extensive unit tests using **pytest**.

Run tests:


pytest


---

# Code Coverage

To run tests with coverage:


pytest --cov=app --cov-report=term-missing


The project enforces **minimum 90% coverage**.

---

# Continuous Integration (CI)

The project uses **GitHub Actions** to automatically run tests and enforce coverage requirements.

The CI pipeline performs the following steps:

1. Checkout repository
2. Setup Python environment
3. Install dependencies
4. Run pytest with coverage
5. Fail build if coverage drops below 90%

Workflow file:


.github/workflows/python-app.yml


---

# Error Handling

Custom exceptions are used throughout the application:

- `OperationError`
- `InvalidInputError`
- `ValidationError`
- `PersistenceError`
- `ConfigError`

This ensures clear and consistent error reporting.

---

# Development Practices

This project demonstrates several software engineering best practices:

- Modular architecture
- Clean separation of concerns
- Unit testing
- Configuration management
- Logging
- Serialization and persistence
- Continuous integration
- Code coverage enforcement
- Design Patterns Application (Command, Decorator, Observer, Memento, Facade, Factory)

---

# Author

Isha Jagtap \
Master's in Computer Science  
NJIT
