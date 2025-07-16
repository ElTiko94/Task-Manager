import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from task import Task
from controller import TaskController
import window
import datetime


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
    def grid(self, *args, **kwargs):
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
        self.config_called_with = {}
        self.itemconfigs = {}
    def delete(self, start, end):
        self.items = []
    def insert(self, index, item):
        self.items.append(item)
    def curselection(self):
        return self.selection
    def bind(self, event, func):
        self.bindings[event] = func
    def yview(self, *args):
        self.yview_args = args
    def config(self, **kwargs):
        self.config_called_with.update(kwargs)
    configure = config
    def itemconfig(self, index, **kwargs):
        self.itemconfigs[index] = kwargs


class DummyScrollbar(DummyWidget):
    def __init__(self, *args, orient=None, command=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.orient = orient
        self.command = command
    def set(self, *args):
        self.set_args = args


class DummyFrame(DummyWidget):
    pass


class DummyStyle:
    def __init__(self, root=None):
        self.root = root
        self.used = None

    def theme_use(self, name=None):
        if name is not None:
            self.used = name
        return self.used


class DummyTkModule:
    END = 'end'
    Label = DummyWidget
    Button = DummyWidget
    Entry = DummyEntry
    Listbox = DummyListbox
    Scrollbar = DummyScrollbar
    StringVar = DummyStringVar
    IntVar = DummyIntVar
    Checkbutton = DummyCheckbutton
    Frame = DummyFrame
    Style = DummyStyle

    @staticmethod
    def Toplevel(parent=None):
        return DummyRoot()


def setup_window(monkeypatch):
    fake_tk = DummyTkModule()
    monkeypatch.setattr(window, 'tk', fake_tk)
    monkeypatch.setattr(window, 'ttk', fake_tk)
    monkeypatch.setattr(window, 'DateEntry', DummyEntry)
    root = DummyRoot()
    controller = TaskController(Task('Main'))
    return window.Window(root, controller)


def test_window_initial_refresh(monkeypatch):
    win = setup_window(monkeypatch)
    assert win.listbox.items == []
    win.controller.add_task('Task1')
    win.refresh_window()
    assert win.listbox.items == ['Task1']


def test_scrollbar_connected(monkeypatch):
    win = setup_window(monkeypatch)
    assert isinstance(win.scrollbar, DummyScrollbar)
    assert win.scrollbar.command == win.listbox.yview
    cmd = win.listbox.config_called_with.get('yscrollcommand')
    assert getattr(cmd, '__self__', None) is win.scrollbar


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
    monkeypatch.setattr(window, 'ttk', fake_tk)
    monkeypatch.setattr(window, 'DateEntry', TrackedEntry)
    root = DummyRoot()
    controller = TaskController(Task('Main'))
    controller.add_task('Existing', due_date='2024-12-31', priority=2)
    win = window.Window(root, controller)
    entries.clear()  # ignore widgets created during initialization
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
    monkeypatch.setattr(window, 'ttk', fake_tk)
    monkeypatch.setattr(window, 'DateEntry', TrackEntry)
    root = DummyRoot()
    controller = TaskController(Task('Main'))
    parent = Task('Parent')
    parent.add_sub_task(Task('Child', due_date='2025-01-01', priority=5))
    controller.task.add_sub_task(parent)
    win = window.Window(root, controller)
    sub_root = DummyRoot()
    sub_win = window.Window(sub_root, TaskController(parent))
    entries.clear()  # ignore widgets created during initialization
    sub_win.listbox.selection = (0,)
    sub_win.edit_task()

    assert entries[0].get() == 'Child'
    assert entries[1].get() == '2025-01-01'
    assert entries[2].get() == '5'


def test_edit_task_keeps_vars(monkeypatch):
    """Dialog should keep references to StringVars so values stay visible."""
    captured = {}

    class CapRoot(DummyRoot):
        pass

    def fake_top(parent=None):
        dlg = CapRoot()
        captured['dlg'] = dlg
        return dlg

    fake_tk = DummyTkModule()
    fake_tk.Toplevel = fake_top
    monkeypatch.setattr(window, 'tk', fake_tk)
    monkeypatch.setattr(window, 'ttk', fake_tk)
    monkeypatch.setattr(window, 'DateEntry', DummyEntry)
    root = DummyRoot()
    controller = TaskController(Task('Main'))
    controller.add_task('X', due_date='2023-01-01', priority=1)
    win = window.Window(root, controller)
    win.listbox.selection = (0,)
    win.edit_task()

    dlg = captured['dlg']
    assert hasattr(dlg, 'task_name_var')
    assert dlg.task_name_var.get() == 'X'
    assert dlg.due_date_var.get() == '2023-01-01'
    assert dlg.priority_var.get() == '1'


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


def test_search_filter(monkeypatch):
    win = setup_window(monkeypatch)
    win.controller.add_task('Hello')
    win.controller.add_task('World')
    win.controller.add_task('Help')
    win.search_var.set('hel')
    win.refresh_window()
    assert [item.split()[0] for item in win.listbox.items] == ['Hello', 'Help']


def test_hide_completed(monkeypatch):
    win = setup_window(monkeypatch)
    win.controller.add_task('Done')
    win.controller.add_task('Todo')
    win.controller.mark_task_completed(0)
    win.hide_completed_var.set(1)
    win.refresh_window()
    assert [item.split()[0] for item in win.listbox.items] == ['Todo']


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


def test_view_subtasks_uses_toplevel(monkeypatch):
    created = {}

    class FakeTk(DummyTkModule):
        pass

    fake_tk = FakeTk()

    def toplevel(parent=None):
        created['parent'] = parent
        return DummyRoot()

    fake_tk.Toplevel = toplevel

    def fake_tk_root(*args, **kwargs):
        created['tk_called'] = True
        return DummyRoot()

    fake_tk.Tk = fake_tk_root

    monkeypatch.setattr(window, 'tk', fake_tk)
    monkeypatch.setattr(window, 'ttk', fake_tk)

    root = DummyRoot()
    controller = TaskController(Task('Main'))
    controller.add_task('Sub')
    win = window.Window(root, controller)
    win.listbox.selection = (0,)

    win.view_subtasks()

    assert created.get('parent') is root
    assert 'tk_called' not in created


def test_completed_task_gray(monkeypatch):
    win = setup_window(monkeypatch)
    win.controller.add_task('Done')
    win.controller.mark_task_completed(0)
    win.refresh_window()
    assert win.listbox.itemconfigs.get(0, {}).get('fg') == 'gray'


def test_overdue_task_red(monkeypatch):
    win = setup_window(monkeypatch)
    past = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
    win.controller.add_task('Late', due_date=past)
    win.refresh_window()
    assert win.listbox.itemconfigs.get(0, {}).get('fg') == 'red'

