from helpers import load_module

task = load_module("task")
controller_mod = load_module("controller")
window = load_module("window")
Task = task.Task
TaskController = controller_mod.TaskController
import datetime


class DummyRoot:
    def resizable(self, x, y):
        self.size = (x, y)


class DummyStringVar:
    def __init__(self):
        self.value = ""

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
        self.command = kwargs.get("command")

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
        return self.textvariable.get() if self.textvariable else ""


class DummyCheckbutton(DummyWidget):
    def __init__(self, *args, variable=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.variable = variable


class DummyTreeview(DummyWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.items = []
        self.nodes = {}
        self.children = {}
        self.bindings = {}
        self.config_called_with = {}
        self.tag_configs = {}
        self._counter = 0
        self._selection = ()
        self.node_states = {}

    def insert(self, parent, index, iid=None, text="", tags=()):
        if iid is None:
            iid = f"I{self._counter}"
            self._counter += 1
        self.nodes[iid] = {"text": text, "tags": tags, "parent": parent}
        self.node_states[iid] = {"open": False}
        self.children.setdefault(parent or "", []).append(iid)
        self.items.append(text)
        return iid

    def get_children(self, item=None):
        return list(self.children.get(item or "", []))

    def delete(self, *items):
        if not items:
            return
        for iid in items:
            self._delete(iid)

    def _delete(self, iid):
        for child in self.children.get(iid, []):
            self._delete(child)
        parent = self.nodes.get(iid, {}).get("parent", "")
        if parent in self.children:
            if iid in self.children[parent]:
                self.children[parent].remove(iid)
        self.children.pop(iid, None)
        node = self.nodes.pop(iid, None)
        if node and node["text"] in self.items:
            self.items.remove(node["text"])
        self.node_states.pop(iid, None)

    def selection(self):
        return self._selection

    def selection_set(self, iid):
        if isinstance(iid, (list, tuple)):
            self._selection = tuple(iid)
        else:
            self._selection = (iid,)

    def identify_row(self, y):
        # Return the first item for simplicity
        return self.get_children()[0] if self.nodes else ""

    def bind(self, event, func):
        self.bindings[event] = func

    def yview(self, *args):
        self.yview_args = args

    def config(self, **kwargs):
        self.config_called_with.update(kwargs)

    configure = config

    def tag_configure(self, tag, **opts):
        self.tag_configs[tag] = opts

    def item(self, iid, option=None, **kw):
        state = self.node_states.setdefault(iid, {"open": False})
        if kw:
            if "open" in kw:
                state["open"] = kw["open"]
        if option:
            return state.get(option)
        return state


class DummyListbox(DummyWidget):
    END = "end"

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

    def theme_names(self):
        return ["default"]


class DummyMenu:
    def __init__(self, *args, **kwargs):
        self.commands = []
        self.cascades = []

    def add_command(self, label=None, command=None):
        self.commands.append((label, command))

    def add_cascade(self, label=None, menu=None):
        self.cascades.append((label, menu))

    def add_separator(self):
        self.commands.append(("separator", None))

    def tk_popup(self, x, y):
        self.popup_at = (x, y)


class DummyRootWithConfig(DummyRoot):
    def config(self, **kwargs):
        self.config_kwargs = kwargs


class DummyTkModule:
    END = "end"
    Label = DummyWidget
    Button = DummyWidget
    Entry = DummyEntry
    Treeview = DummyTreeview
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


class MenuTkModule(DummyTkModule):
    Menu = DummyMenu
    Style = DummyStyle  # overridden later in tests if needed


class DummyStyleWithThemes(DummyStyle):
    def theme_names(self):
        return ["light", "dark"]


def setup_window(monkeypatch):
    fake_tk = DummyTkModule()
    monkeypatch.setattr(window, "tk", fake_tk)
    monkeypatch.setattr(window, "ttk", fake_tk)
    monkeypatch.setattr(window, "DateEntry", DummyEntry)
    root = DummyRoot()
    controller = TaskController(Task("Main"))
    return window.Window(root, controller)


def test_window_initial_refresh(monkeypatch):
    win = setup_window(monkeypatch)
    assert win.tree.items == []
    win.controller.add_task("Task1")
    win.refresh_window()
    assert win.tree.items == ["Task1"]


def test_scrollbar_connected(monkeypatch):
    win = setup_window(monkeypatch)
    assert isinstance(win.scrollbar, DummyScrollbar)
    assert win.scrollbar.command == win.tree.yview
    cmd = win.tree.config_called_with.get("yscrollcommand")
    assert getattr(cmd, "__self__", None) is win.scrollbar


def test_create_task_button(monkeypatch):
    win = setup_window(monkeypatch)
    entry = DummyEntry(textvariable=DummyStringVar())
    due = DummyEntry(textvariable=DummyStringVar())
    prio = DummyEntry(textvariable=DummyStringVar())
    chk_var = DummyIntVar()
    chk = DummyCheckbutton(variable=chk_var)
    entry.textvariable.set("New")
    due.textvariable.set("2025-12-31")
    prio.textvariable.set("2")
    chk_var.set(1)
    btn = DummyWidget()
    win.create_task_button(entry, due, prio, chk_var, chk, btn)
    t = win.controller.get_sub_tasks()[0]
    assert t.name == "New"
    assert t.due_date == "2025-12-31"
    assert t.priority == 2
    assert t.completed
    assert win.tree.items == ["New (Completed) - Due: 2025-12-31 - Priority: 2"]


def test_create_task_button_invalid_priority(monkeypatch):
    win = setup_window(monkeypatch)
    warnings = []
    monkeypatch.setattr(
        window.tkMessageBox, "showwarning", lambda *a, **k: warnings.append(True)
    )
    entry = DummyEntry(textvariable=DummyStringVar())
    due = DummyEntry(textvariable=DummyStringVar())
    prio = DummyEntry(textvariable=DummyStringVar())
    chk_var = DummyIntVar()
    chk = DummyCheckbutton(variable=chk_var)
    entry.textvariable.set("New")
    due.textvariable.set("2025-12-31")
    prio.textvariable.set("bad")
    chk_var.set(0)
    btn = DummyWidget()
    win.create_task_button(entry, due, prio, chk_var, chk, btn)
    t = win.controller.get_sub_tasks()[0]
    assert t.priority is None
    assert warnings


def test_confirm_edit(monkeypatch):
    win = setup_window(monkeypatch)
    win.controller.add_task("Old")
    win.refresh_window()
    var = DummyStringVar()
    var.set("Updated")
    due_var = DummyStringVar()
    due_var.set("2026-01-01")
    prio_var = DummyStringVar()
    prio_var.set("3")
    chk_var = DummyIntVar()
    chk_var.set(1)
    item = win.tree.get_children()[0]
    win.tree.selection_set(item)
    entry = DummyEntry(textvariable=var)
    due_entry = DummyEntry(textvariable=due_var)
    prio_entry = DummyEntry(textvariable=prio_var)
    chk = DummyCheckbutton(variable=chk_var)
    btn = DummyWidget()
    win.confirm_edit(entry, due_entry, prio_entry, chk_var, chk, item, btn)
    t = win.controller.get_sub_tasks()[0]
    assert t.name == "Updated"
    assert t.due_date == "2026-01-01"
    assert t.priority == 3
    assert t.completed


def test_confirm_edit_invalid_priority(monkeypatch):
    win = setup_window(monkeypatch)
    win.controller.add_task("Old")
    win.refresh_window()
    warnings = []
    monkeypatch.setattr(
        window.tkMessageBox, "showwarning", lambda *a, **k: warnings.append(True)
    )
    var = DummyStringVar()
    var.set("Updated")
    due_var = DummyStringVar()
    due_var.set("2026-01-01")
    prio_var = DummyStringVar()
    prio_var.set("bad")
    chk_var = DummyIntVar()
    chk_var.set(0)
    item = win.tree.get_children()[0]
    win.tree.selection_set(item)
    entry = DummyEntry(textvariable=var)
    due_entry = DummyEntry(textvariable=due_var)
    prio_entry = DummyEntry(textvariable=prio_var)
    chk = DummyCheckbutton(variable=chk_var)
    btn = DummyWidget()
    win.confirm_edit(entry, due_entry, prio_entry, chk_var, chk, item, btn)
    t = win.controller.get_sub_tasks()[0]
    assert t.priority is None
    assert warnings


def test_edit_task_prefills_fields(monkeypatch):
    entries = []

    class TrackedEntry(DummyEntry):
        def __init__(self, *args, textvariable=None, **kwargs):
            super().__init__(*args, textvariable=textvariable, **kwargs)
            entries.append(self)

    fake_tk = DummyTkModule()
    fake_tk.Entry = TrackedEntry
    monkeypatch.setattr(window, "tk", fake_tk)
    monkeypatch.setattr(window, "ttk", fake_tk)
    monkeypatch.setattr(window, "DateEntry", TrackedEntry)
    root = DummyRoot()
    controller = TaskController(Task("Main"))
    controller.add_task("Existing", due_date="2024-12-31", priority=2)
    win = window.Window(root, controller)
    entries.clear()  # ignore widgets created during initialization
    item = win.tree.get_children()[0]
    win.tree.selection_set(item)
    win.edit_task()

    assert entries[0].get() == "Existing"
    assert entries[1].get() == "2024-12-31"
    assert entries[2].get() == "2"


def test_edit_subtask_prefills_fields(monkeypatch):
    entries = []

    class TrackEntry(DummyEntry):
        def __init__(self, *args, textvariable=None, **kwargs):
            super().__init__(*args, textvariable=textvariable, **kwargs)
            entries.append(self)

    fake_tk = DummyTkModule()
    fake_tk.Entry = TrackEntry
    monkeypatch.setattr(window, "tk", fake_tk)
    monkeypatch.setattr(window, "ttk", fake_tk)
    monkeypatch.setattr(window, "DateEntry", TrackEntry)
    root = DummyRoot()
    controller = TaskController(Task("Main"))
    parent = Task("Parent")
    parent.add_sub_task(Task("Child", due_date="2025-01-01", priority=5))
    controller.task.add_sub_task(parent)
    win = window.Window(root, controller)
    sub_root = DummyRoot()
    sub_win = window.Window(sub_root, TaskController(parent))
    entries.clear()  # ignore widgets created during initialization
    item = sub_win.tree.get_children()[0]
    sub_win.tree.selection_set(item)
    sub_win.edit_task()

    assert entries[0].get() == "Child"
    assert entries[1].get() == "2025-01-01"
    assert entries[2].get() == "5"


def test_edit_task_keeps_vars(monkeypatch):
    """Dialog should keep references to StringVars so values stay visible."""
    captured = {}

    class CapRoot(DummyRoot):
        pass

    def fake_top(parent=None):
        dlg = CapRoot()
        captured["dlg"] = dlg
        return dlg

    fake_tk = DummyTkModule()
    fake_tk.Toplevel = fake_top
    monkeypatch.setattr(window, "tk", fake_tk)
    monkeypatch.setattr(window, "ttk", fake_tk)
    monkeypatch.setattr(window, "DateEntry", DummyEntry)
    root = DummyRoot()
    controller = TaskController(Task("Main"))
    controller.add_task("X", due_date="2023-01-01", priority=1)
    win = window.Window(root, controller)
    item = win.tree.get_children()[0]
    win.tree.selection_set(item)
    win.edit_task()

    dlg = captured["dlg"]
    assert hasattr(dlg, "task_name_var")
    assert dlg.task_name_var.get() == "X"
    assert dlg.due_date_var.get() == "2023-01-01"
    assert dlg.priority_var.get() == "1"


def test_sort_button(monkeypatch):
    win = setup_window(monkeypatch)
    win.controller.add_task("Low", priority=5)
    win.controller.add_task("High", priority=1)
    win.controller.add_task("None")
    win.sort_tasks_by_priority()
    assert [t.name for t in win.controller.get_sub_tasks()] == ["High", "Low", "None"]
    assert [item.split()[0] for item in win.tree.items] == ["High", "Low", "None"]


def test_sort_by_due_date(monkeypatch):
    win = setup_window(monkeypatch)
    win.controller.add_task("Later", due_date="2025-01-01")
    win.controller.add_task("Sooner", due_date="2024-01-01")
    win.controller.add_task("NoDue")
    win.sort_tasks_by_due_date()
    assert [t.name for t in win.controller.get_sub_tasks()] == [
        "Sooner",
        "Later",
        "NoDue",
    ]
    assert [item.split()[0] for item in win.tree.items] == ["Sooner", "Later", "NoDue"]


def test_move_selected_up(monkeypatch):
    win = setup_window(monkeypatch)
    win.controller.add_task("A")
    win.controller.add_task("B")
    win.controller.add_task("C")
    win.refresh_window()
    iid = win.tree.get_children()[1]
    win.tree.selection_set(iid)
    win.move_selected_up()
    assert [t.name for t in win.controller.get_sub_tasks()] == ["B", "A", "C"]
    assert [item.split()[0] for item in win.tree.items] == ["B", "A", "C"]


def test_move_selected_down(monkeypatch):
    win = setup_window(monkeypatch)
    win.controller.add_task("A")
    win.controller.add_task("B")
    win.refresh_window()
    iid = win.tree.get_children()[0]
    win.tree.selection_set(iid)
    win.move_selected_down()
    assert [t.name for t in win.controller.get_sub_tasks()] == ["B", "A"]
    assert [item.split()[0] for item in win.tree.items] == ["B", "A"]


def test_search_filter(monkeypatch):
    win = setup_window(monkeypatch)
    win.controller.add_task("Hello")
    win.controller.add_task("World")
    win.controller.add_task("Help")
    win.search_var.set("hel")
    win.refresh_window()
    assert [item.split()[0] for item in win.tree.items] == ["Hello", "Help"]


def test_hide_completed(monkeypatch):
    win = setup_window(monkeypatch)
    win.controller.add_task("Done")
    win.controller.add_task("Todo")
    win.controller.mark_task_completed(0)
    win.hide_completed_var.set(1)
    win.refresh_window()
    assert [item.split()[0] for item in win.tree.items] == ["Todo"]


def test_show_completed_only(monkeypatch):
    win = setup_window(monkeypatch)
    win.controller.add_task("Done")
    win.controller.add_task("Todo")
    win.controller.mark_task_completed(0)
    win.show_completed_only_var.set(1)
    win.refresh_window()
    assert [item.split()[0] for item in win.tree.items] == ["Done"]


def test_hide_checkbox_triggers_refresh(monkeypatch):
    created = {}

    class TrackCheck(DummyCheckbutton):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            created["cb"] = self

    fake_tk = DummyTkModule()
    fake_tk.Checkbutton = TrackCheck
    monkeypatch.setattr(window, "tk", fake_tk)
    monkeypatch.setattr(window, "ttk", fake_tk)
    monkeypatch.setattr(window, "DateEntry", DummyEntry)

    root = DummyRoot()
    controller = TaskController(Task("Main"))
    controller.add_task("Done")
    controller.add_task("Todo")
    controller.mark_task_completed(0)
    win = window.Window(root, controller)

    cb = created.get("cb")
    assert cb is not None
    assert cb.command == win.refresh_window

    win.hide_completed_var.set(1)
    cb.invoke()
    assert [item.split()[0] for item in win.tree.items] == ["Todo"]


def test_double_click_opens_subtasks(monkeypatch):
    called = {}

    def fake_view(self):
        called["view"] = True

    monkeypatch.setattr(window.Window, "view_subtasks", fake_view)
    win = setup_window(monkeypatch)
    win.controller.add_task("A")
    win.refresh_window()
    item = win.tree.get_children()[0]
    win.tree.selection_set(item)
    bound = win.tree.bindings.get("<Double-Button-1>")
    assert bound is not None
    bound(None)
    assert called.get("view")


def test_right_click_calls_menu(monkeypatch):
    called = {}

    def fake_menu(self, event=None):
        called["menu"] = True

    monkeypatch.setattr(window.Window, "_show_tree_menu", fake_menu)
    win = setup_window(monkeypatch)
    win.controller.add_task("A")
    win.refresh_window()
    bound = win.tree.bindings.get("<Button-3>")
    assert bound is not None
    class E:
        x_root = 0
        y_root = 0
        y = 0
    bound(E())
    assert called.get("menu")


def test_toggle_completion(monkeypatch):
    win = setup_window(monkeypatch)
    win.controller.add_task("A")
    win.refresh_window()
    iid = win.tree.get_children()[0]
    win.tree.selection_set(iid)
    win.toggle_completion()
    t = win.controller.get_sub_tasks()[0]
    assert t.completed
    assert "Completed" in win.tree.items[0]


def test_view_subtasks_uses_toplevel(monkeypatch):
    created = {}

    class FakeTk(DummyTkModule):
        pass

    fake_tk = FakeTk()

    def toplevel(parent=None):
        created["parent"] = parent
        return DummyRoot()

    fake_tk.Toplevel = toplevel

    def fake_tk_root(*args, **kwargs):
        created["tk_called"] = True
        return DummyRoot()

    fake_tk.Tk = fake_tk_root

    monkeypatch.setattr(window, "tk", fake_tk)
    monkeypatch.setattr(window, "ttk", fake_tk)
    monkeypatch.setattr(window, "DateEntry", DummyEntry)

    root = DummyRoot()
    controller = TaskController(Task("Main"))
    controller.add_task("Sub")
    win = window.Window(root, controller)
    item = win.tree.get_children()[0]
    win.tree.selection_set(item)

    win.view_subtasks()

    assert created.get("parent") is root
    assert "tk_called" not in created


def test_completed_task_gray(monkeypatch):
    win = setup_window(monkeypatch)
    win.controller.add_task("Done")
    win.controller.mark_task_completed(0)
    win.refresh_window()
    iid = win.tree.get_children()[0]
    assert win.tree.nodes[iid]["tags"][0] == "gray"


def test_overdue_task_red(monkeypatch):
    win = setup_window(monkeypatch)
    past = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
    win.controller.add_task("Late", due_date=past)
    win.refresh_window()
    iid = win.tree.get_children()[0]
    assert win.tree.nodes[iid]["tags"][0] == "red"


def test_due_date_filter_before(monkeypatch):
    win = setup_window(monkeypatch)
    win.controller.add_task("Soon", due_date="2024-01-01")
    win.controller.add_task("Later", due_date="2026-01-01")
    win.due_filter_var.set("2025-01-01")
    win.due_before_var.set(1)
    win.refresh_window()
    assert [item.split()[0] for item in win.tree.items] == ["Soon"]


def test_due_date_filter_after(monkeypatch):
    win = setup_window(monkeypatch)
    win.controller.add_task("Soon", due_date="2024-01-01")
    win.controller.add_task("Later", due_date="2026-01-01")
    win.due_filter_var.set("2025-01-01")
    win.due_after_var.set(1)
    win.refresh_window()
    assert [item.split()[0] for item in win.tree.items] == ["Later"]


def test_due_date_filter_invalid_input(monkeypatch):
    win = setup_window(monkeypatch)
    win.controller.add_task("Soon", due_date="2024-01-01")
    win.controller.add_task("Later", due_date="2026-01-01")
    win.due_filter_var.set("invalid")
    win.due_before_var.set(1)
    win.refresh_window()
    assert [item.split()[0] for item in win.tree.items] == ["Soon", "Later"]


def test_priority_filter_above(monkeypatch):
    win = setup_window(monkeypatch)
    win.controller.add_task("Low", priority=5)
    win.controller.add_task("High", priority=1)
    win.priority_filter_var.set("2")
    win.priority_above_var.set(1)
    win.refresh_window()
    assert [item.split()[0] for item in win.tree.items] == ["Low"]


def test_priority_filter_below(monkeypatch):
    win = setup_window(monkeypatch)
    win.controller.add_task("Low", priority=5)
    win.controller.add_task("High", priority=1)
    win.priority_filter_var.set("3")
    win.priority_below_var.set(1)
    win.refresh_window()
    assert [item.split()[0] for item in win.tree.items] == ["High"]


def test_priority_colors(monkeypatch):
    win = setup_window(monkeypatch)
    win.controller.add_task("High", priority=1)
    win.controller.add_task("Medium", priority=2)
    win.refresh_window()
    iid0, iid1 = win.tree.get_children()
    assert win.tree.nodes[iid0]["tags"][0] == "red"
    assert win.tree.nodes[iid1]["tags"][0] == "orange"


def test_priority_completed_overdue_coexist(monkeypatch):
    win = setup_window(monkeypatch)
    past = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
    win.controller.add_task("DoneHigh", priority=1)
    win.controller.mark_task_completed(0)
    win.controller.add_task("OverdueMedium", due_date=past, priority=2)
    win.refresh_window()
    # Completed task should remain gray despite priority
    iid0, iid1 = win.tree.get_children()
    assert win.tree.nodes[iid0]["tags"][0] == "gray"
    # Overdue task should be red despite medium priority
    assert win.tree.nodes[iid1]["tags"][0] == "red"


def test_view_menu_themes(monkeypatch):
    fake_tk = MenuTkModule()
    fake_tk.Style = DummyStyleWithThemes
    monkeypatch.setattr(window, "tk", fake_tk)
    monkeypatch.setattr(window, "ttk", fake_tk)
    monkeypatch.setattr(window, "DateEntry", DummyEntry)
    root = DummyRootWithConfig()
    controller = TaskController(Task("Main"))
    win = window.Window(root, controller)

    menubar = root.config_kwargs.get("menu")
    assert isinstance(menubar, DummyMenu)
    view_menu = None
    for label, menu in menubar.cascades:
        if label == "View":
            view_menu = menu
    assert view_menu is not None
    expected_default = "flatly" if window.USE_BOOTSTRAP else "clam"
    assert [lbl for lbl, _ in view_menu.commands] == [expected_default, "light", "dark"]

    called = {}
    monkeypatch.setattr(win, "use_theme", lambda t: called.setdefault("theme", t))
    # trigger third menu command ("dark" theme)
    view_menu.commands[2][1]()
    assert called.get("theme") == "dark"


def test_tree_shows_subtasks(monkeypatch):
    win = setup_window(monkeypatch)
    parent = Task("Parent")
    parent.add_sub_task(Task("Child"))
    win.controller.task.add_sub_task(parent)
    win.refresh_window()

    parent_ids = win.tree.get_children()
    parent_id = parent_ids[-1]
    child_ids = win.tree.get_children(parent_id)
    assert len(child_ids) == 1
    assert win.tree.nodes[child_ids[0]]["text"].startswith("Child")


def test_subwindow_add_refreshes_parent(monkeypatch):
    win = setup_window(monkeypatch)
    parent = Task("Parent")
    win.controller.task.add_sub_task(parent)
    win.refresh_window()

    sub_root = DummyRoot()
    sub_win = window.Window(sub_root, TaskController(parent), parent_window=win)

    entry = DummyEntry(textvariable=DummyStringVar())
    due = DummyEntry(textvariable=DummyStringVar())
    prio = DummyEntry(textvariable=DummyStringVar())
    chk_var = DummyIntVar()
    chk = DummyCheckbutton(variable=chk_var)
    entry.textvariable.set("Child")
    btn = DummyWidget()
    sub_win.create_task_button(entry, due, prio, chk_var, chk, btn)

    parent_ids = win.tree.get_children()
    parent_id = parent_ids[-1]
    child_ids = win.tree.get_children(parent_id)
    assert len(child_ids) == 1
    assert win.tree.nodes[child_ids[0]]["text"].startswith("Child")


def test_subwindow_inherits_theme(monkeypatch):
    fake_tk = MenuTkModule()
    fake_tk.Style = DummyStyleWithThemes
    monkeypatch.setattr(window, "tk", fake_tk)
    monkeypatch.setattr(window, "ttk", fake_tk)
    monkeypatch.setattr(window, "DateEntry", DummyEntry)

    root = DummyRoot()
    controller = TaskController(Task("Main"))
    main_win = window.Window(root, controller)
    # Change the main window's theme
    main_win.style.theme_use("dark")

    sub_root = DummyRoot()
    sub_controller = TaskController(Task("Sub"))
    sub_win = window.Window(sub_root, sub_controller, parent_window=main_win)

    assert sub_win.style.used == "dark"


def test_refresh_preserves_tree_expansion(monkeypatch):
    win = setup_window(monkeypatch)
    parent = Task("Parent")
    parent.add_sub_task(Task("Child"))
    win.controller.task.add_sub_task(parent)
    win.refresh_window()

    parent_id = win.tree.get_children()[0]
    win.tree.item(parent_id, open=True)

    win.refresh_window()
    parent_id = win.tree.get_children()[0]
    assert win.tree.item(parent_id, "open") is True


def test_move_selected_task(monkeypatch):
    win = setup_window(monkeypatch)
    win.controller.add_task("A")
    win.controller.add_task("B")
    win.refresh_window()
    items = win.tree.get_children()
    win.tree.selection_set(items[1])
    win.move_selected_task(-1)
    assert [t.name for t in win.controller.get_sub_tasks()] == ["B", "A"]
    assert [win.tree.nodes[i]["text"].split()[0] for i in win.tree.get_children()] == ["B", "A"]
