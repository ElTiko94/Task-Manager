# Task-Manager

## Overview
The Task-Manager Application is a simple graphical user interface (GUI) application built using Python and Tkinter. It allows users to manage tasks and subtasks in a hierarchical manner.  A modern theme is applied using **ttkbootstrap** when the library is available, and key buttons adopt colorful *bootstyles* for a polished look.

## Features
- Create, edit, and delete tasks
- View subtasks
- Add subtasks to a task
- Save tasks to a JSON file for later retrieval
- Import and export tasks in CSV, JSON, or ICS formats from the File menu
- Optional due dates and priority levels for tasks
- Mark tasks as completed
- Switch themes from the View menu

## Color Coding
The task list uses colors to highlight different states and priorities:

- **Gray**: completed tasks
- **Red**: tasks past their due date
- **Orange**: priority `1` tasks
- **Yellow**: priority `2` tasks

## Requirements
- Python 3.7
- Tkinter (should be included with Python installation; on some Linux
  systems you may need the `python3-tk` package)
- Additional Python dependencies are listed in `requirements.txt`
  (`tkcalendar` for calendar pop-ups and `ttkbootstrap` for optional
  modern themes)

## Installation
1. Clone or download the repository to your local machine.
2. Ensure you have Python installed on your system.
3. Install the required Python packages with `pip install -r requirements.txt`.
   This installs the optional `tkcalendar` and `ttkbootstrap` packages
   for calendar pop-ups and additional themes.
4. Run `Start.bat` on Windows or `./Start.sh` on Linux/macOS to start the application.
   If you haven't used the shell script before, give it execute permission with `chmod +x Start.sh`.

## Usage
1. **Adding a Task**: Click on the "Add Task" button and enter the name of the task in the text field. Click "Confirm" to add the task.

2. **Editing a Task**: Select a task from the list and click the "Edit" button. Modify the task name in the text field and click "Confirm" to save changes.

3. **Deleting a Task**: Select a task from the list and click the "Delete" button to remove the task.

4. **Viewing Subtasks**: Select a task from the list and click the "View Subtasks" button to see its immediate subtasks.

5. **Saving Changes**: The application prompts you to save changes when you close the window. Click "Yes" to save changes or "No" to discard them.

6. **Filtering Tasks**: Use the controls below the task list to filter. You can
   search by name, hide completed tasks, show only tasks due before or after a
   specific date, and display tasks with priority above or below a chosen
   threshold. Click "Apply Filter" to update the list.
7. **Changing Themes**: Open the "View" menu and select a theme. When
   `ttkbootstrap` is installed, additional modern themes become available.
8. **Import/Export**: Use the "File" menu to export tasks to CSV or ICS or to
   import tasks from existing CSV/ICS files.

## File Structure
- `orga.py`: Main entry point of the application.
- `task.py`: Defines the `Task` class representing a single task.
- `controller.py`: Defines the `TaskController` class for managing tasks.
- `window.py`: Defines the `Window` class for creating the main GUI window.
- `tasks.json`: JSON file to store tasks.
- `Start.bat`: Windows script to launch the application.
- `Start.sh`: Shell script to launch the application on Unix systems.
## Running Tests
Run `pytest` from the repository root to execute the test suite.

## Contributions
Contributions to this project are welcome. If you find any bugs or have suggestions for improvements, please open an issue or submit a pull request on GitHub.

## Authors
- ElTiko_94 - Original author and maintainer
