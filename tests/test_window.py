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


class DummyListbox(DummyWidget):
    END = 'end'
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.items = []
        self.selection = ()
    def delete(self, start, end):
        self.items = []
    def insert(self, index, item):
        self.items.append(item)
    def curselection(self):
        return self.selection


class DummyTkModule:
    END = 'end'
    Label = DummyWidget
    Button = DummyWidget
    Entry = DummyEntry
    Listbox = DummyListbox
    StringVar = DummyStringVar


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
    entry.textvariable.set('New')
    btn = DummyWidget()
    win.create_task_button(entry, btn)
    assert [t.name for t in win.controller.get_sub_tasks()] == ['New']
    assert win.listbox.items == ['New']


def test_confirm_edit(monkeypatch):
    win = setup_window(monkeypatch)
    win.controller.add_task('Old')
    win.refresh_window()
    var = DummyStringVar()
    var.set('Updated')
    win.listbox.selection = (0,)
    entry = DummyEntry(textvariable=var)
    btn = DummyWidget()
    win.confirm_edit(entry, (0,), btn)
    assert win.controller.get_sub_tasks()[0].name == 'Updated'

