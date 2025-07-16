import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from task import Task
from controller import TaskController
import window


class DummyRoot:
    def resizable(self, x, y):
        self.size = (x, y)


class DummyStringVar:
    def __init__(self):
        self.value = ''
    def set(self, v):
        self.value = v
    def get(self):
        return self.value


class DummyIntVar:
    def __init__(self):
        self.value = 0

    def set(self, v):
        self.value = int(v)

    def get(self):
        return self.value


class DummyWidget:
    def __init__(self, *args, **kwargs):
        self.command = kwargs.get('command')
    def pack(self):
        pass
    def destroy(self):
        pass
    def invoke(self):
        if self.command:
            self.command()


class DummyEntry(DummyWidget):
    def __init__(self, *args, textvariable=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.textvariable = textvariable
    def get(self):
        return self.textvariable.get() if self.textvariable else ''


class DummyCheckbutton(DummyWidget):
    def __init__(self, *args, variable=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.variable = variable


class DummyListbox(DummyWidget):
    END = 'end'
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.items = []
        self.selection = ()
        self.bindings = {}
    def delete(self, start, end):
        self.items = []
    def insert(self, index, item):
        self.items.append(item)
    def curselection(self):
        return self.selection
    def bind(self, event, func):
        self.bindings[event] = func


class DummyTkModule:
    END = 'end'
    Label = DummyWidget
    Button = DummyWidget
    Entry = DummyEntry
    Listbox = DummyListbox
    StringVar = DummyStringVar
    IntVar = DummyIntVar
    Checkbutton = DummyCheckbutton


def setup_window(monkeypatch):
    fake_tk = DummyTkModule()
    monkeypatch.setattr(window, 'tk', fake_tk)
    root = DummyRoot()
    controller = TaskController(Task('Main'))
    return window.Window(root, controller)


def test_window_initial_refresh(monkeypatch):
    win = setup_window(monkeypatch)
    assert win.listbox.items == []
    win.controller.add_task('Task1')
    win.refresh_window()
    assert win.listbox.items == ['Task1']


def test_create_task_button(monkeypatch):
    win = setup_window(monkeypatch)
    entry = DummyEntry(textvariable=DummyStringVar())
    due = DummyEntry(textvariable=DummyStringVar())
    prio = DummyEntry(textvariable=DummyStringVar())
    chk_var = DummyIntVar()
    chk = DummyCheckbutton(variable=chk_var)
    entry.textvariable.set('New')
    due.textvariable.set('2025-12-31')
    prio.textvariable.set('2')
    chk_var.set(1)
    btn = DummyWidget()
    win.create_task_button(entry, due, prio, chk_var, chk, btn)
    t = win.controller.get_sub_tasks()[0]
    assert t.name == 'New'
    assert t.due_date == '2025-12-31'
    assert t.priority == 2
    assert t.completed
    assert win.listbox.items == ['New (Completed) - Due: 2025-12-31 - Priority: 2']


def test_confirm_edit(monkeypatch):
    win = setup_window(monkeypatch)
    win.controller.add_task('Old')
    win.refresh_window()
    var = DummyStringVar()
    var.set('Updated')
    due_var = DummyStringVar()
    due_var.set('2026-01-01')
    prio_var = DummyStringVar()
    prio_var.set('3')
    chk_var = DummyIntVar()
    chk_var.set(1)
    win.listbox.selection = (0,)
    entry = DummyEntry(textvariable=var)
    due_entry = DummyEntry(textvariable=due_var)
    prio_entry = DummyEntry(textvariable=prio_var)
    chk = DummyCheckbutton(variable=chk_var)
    btn = DummyWidget()
    win.confirm_edit(entry, due_entry, prio_entry, chk_var, chk, (0,), btn)
    t = win.controller.get_sub_tasks()[0]
    assert t.name == 'Updated'
    assert t.due_date == '2026-01-01'
    assert t.priority == 3
    assert t.completed


def test_edit_task_prefills_fields(monkeypatch):
    entries = []

    class TrackedEntry(DummyEntry):
        def __init__(self, *args, textvariable=None, **kwargs):
            super().__init__(*args, textvariable=textvariable, **kwargs)
            entries.append(self)

    fake_tk = DummyTkModule()
    fake_tk.Entry = TrackedEntry
    monkeypatch.setattr(window, 'tk', fake_tk)
    root = DummyRoot()
    controller = TaskController(Task('Main'))
    controller.add_task('Existing', due_date='2024-12-31', priority=2)
    win = window.Window(root, controller)
    win.listbox.selection = (0,)
    win.edit_task()

    assert entries[0].get() == 'Existing'
    assert entries[1].get() == '2024-12-31'
    assert entries[2].get() == '2'


def test_edit_subtask_prefills_fields(monkeypatch):
    entries = []

    class TrackEntry(DummyEntry):
        def __init__(self, *args, textvariable=None, **kwargs):
            super().__init__(*args, textvariable=textvariable, **kwargs)
            entries.append(self)

    fake_tk = DummyTkModule()
    fake_tk.Entry = TrackEntry
    monkeypatch.setattr(window, 'tk', fake_tk)
    root = DummyRoot()
    controller = TaskController(Task('Main'))
    parent = Task('Parent')
    parent.add_sub_task(Task('Child', due_date='2025-01-01', priority=5))
    controller.task.add_sub_task(parent)
    win = window.Window(root, controller)
    sub_root = DummyRoot()
    sub_win = window.Window(sub_root, TaskController(parent))
    sub_win.listbox.selection = (0,)
    sub_win.edit_task()

    assert entries[0].get() == 'Child'
    assert entries[1].get() == '2025-01-01'
    assert entries[2].get() == '5'


def test_sort_button(monkeypatch):
    win = setup_window(monkeypatch)
    win.controller.add_task('Low', priority=5)
    win.controller.add_task('High', priority=1)
    win.controller.add_task('None')
    win.sort_tasks_by_priority()
    assert [t.name for t in win.controller.get_sub_tasks()] == ['High', 'Low', 'None']
    assert [item.split()[0] for item in win.listbox.items] == ['High', 'Low', 'None']


def test_sort_by_due_date(monkeypatch):
    win = setup_window(monkeypatch)
    win.controller.add_task('Later', due_date='2025-01-01')
    win.controller.add_task('Sooner', due_date='2024-01-01')
    win.controller.add_task('NoDue')
    win.sort_tasks_by_due_date()
    assert [t.name for t in win.controller.get_sub_tasks()] == ['Sooner', 'Later', 'NoDue']
    assert [item.split()[0] for item in win.listbox.items] == ['Sooner', 'Later', 'NoDue']


def test_double_click_opens_subtasks(monkeypatch):
    called = {}

    def fake_view(self):
        called['view'] = True

    monkeypatch.setattr(window.Window, 'view_subtasks', fake_view)
    win = setup_window(monkeypatch)
    win.controller.add_task('A')
    win.refresh_window()
    win.listbox.selection = (0,)
    bound = win.listbox.bindings.get('<Double-Button-1>')
    assert bound is not None
    bound(None)
    assert called.get('view')

