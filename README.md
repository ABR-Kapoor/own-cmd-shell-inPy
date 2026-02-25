# 🐚 Own Command Shell in Python

A minimal custom command-line shell built in Python.  
This project is part of the **Build Your Own Shell** challenge and demonstrates how a basic Unix-like shell works under the hood.

---

## 🚀 Overview

This repository contains a simple shell implementation written in Python that:

- Reads user input in a loop (REPL)
- Parses commands and arguments
- Executes built-in commands
- Runs external system commands
- Interacts with the operating system via Python

The goal of this project is to understand how real shells (like `bash` or `zsh`) function internally.

---

## 📁 Project Structure


.
├── app/
│ └── main.py # Main shell implementation
├── your_program.sh # Runner script
├── codecrafters.yml # Challenge configuration
├── .gitignore
└── README.md


---

## 🛠️ Requirements

- Python 3.10+ (recommended 3.11+)
- Unix-like environment (Linux/macOS preferred)

---

````markdown
## ▶️ How to Run

### 1. Clone the Repository

```bash
git clone https://github.com/ABR-Kapoor/own-cmd-shell-inPy.git
cd own-cmd-shell-inPy
````

### 2. Run the Shell

**Option 1 (recommended):**

```bash
./your_program.sh
```

**Option 2:**

```bash
python3 app/main.py
```

---

## 💡 Example Commands

Once running, you can try:

```bash
pwd
echo Hello World
ls
cd ..
```

---

## ⚙️ How It Works

The shell follows a basic REPL model:

1. **Read** user input
2. **Parse** command and arguments
3. **Evaluate**

   * If built-in → execute internally
   * Otherwise → use `subprocess` to run system command
4. **Print** output

This mirrors how traditional POSIX shells operate at a high level.

---

## 🎯 Learning Goals

* Understand shell architecture
* Practice parsing and command dispatching
* Work with Python’s `subprocess` module
* Learn OS-level command execution
* Build systems-level programming intuition

---

## 🚧 Future Improvements

You can extend this shell by adding:

* Command history
* Auto-completion
* Piping (`|`)
* Output redirection (`>`, `>>`)
* Input redirection (`<`)
* Background execution (`&`)
* Environment variable support
* Signal handling (Ctrl+C, Ctrl+Z)

---

## 🤝 Contributing

Feel free to fork the project and submit pull requests to enhance functionality or improve structure.

```
```
