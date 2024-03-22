# Task-Manager

## Overview
The Task-Manager Application is a simple graphical user interface (GUI) application built using Python and Tkinter. It allows users to manage tasks and subtasks in a hierarchical manner.

## Features
- Create, edit, and delete tasks
- View subtasks
- Add subtasks to a task
- Save tasks to a file for later retrieval

## Requirements
- Python 3.7
- Tkinter (should be included with Python installation)

## Installation
1. Clone or download the repository to your local machine.
2. Ensure you have Python installed on your system.
3. Run `Start.bat` to start the application.

## Usage
1. **Adding a Task**: Click on the "Add Task" button and enter the name of the task in the text field. Click "Confirm" to add the task.

2. **Editing a Task**: Select a task from the list and click the "Edit" button. Modify the task name in the text field and click "Confirm" to save changes.

3. **Deleting a Task**: Select a task from the list and click the "Delete" button to remove the task.

4. **Viewing Subtasks**: Select a task from the list and click the "View Subtasks" button to see its immediate subtasks.

5. **Saving Changes**: The application prompts you to save changes when you close the window. Click "Yes" to save changes or "No" to discard them.

## File Structure
- `main.py`: Main entry point of the application.
- `task.py`: Defines the `Task` class representing a single task.
- `controller.py`: Defines the `TaskController` class for managing tasks.
- `window.py`: Defines the `Window` class for creating the main GUI window.
- `object.pkl`: Pickle file to store tasks.

## Contributions
Contributions to this project are welcome. If you find any bugs or have suggestions for improvements, please open an issue or submit a pull request on GitHub.

## Authors
ElTiko_94