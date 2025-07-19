import types, sys
from helpers import load_module

class DummyCal:
    def __init__(self, *args, **kwargs):
        self.received = {}
        if kwargs:
            self.configure(**kwargs)

    def configure(self, **kwargs):
        for k, v in kwargs.items():
            self[k] = v

    def __setitem__(self, key, value):
        raise AttributeError(f"Calendar object has no attribute {key}.")

class DummyDateEntry(DummyCal):
    pass


def test_style_patch_applies(monkeypatch):
    dummy_module = types.ModuleType("tkcalendar")
    dummy_module.DateEntry = DummyDateEntry
    dummy_module.calendar_ = types.SimpleNamespace(Calendar=DummyCal)

    monkeypatch.setitem(sys.modules, "tkcalendar", dummy_module)
    monkeypatch.setitem(sys.modules, "tkcalendar.calendar_", dummy_module.calendar_)

    monkeypatch.delitem(sys.modules, "window", raising=False)
    win = load_module("window")
    assert hasattr(win._TkCalendar, "_bootstrap_patch")

    cal = win._TkCalendar(style="test")
    assert cal._properties.get("style") == "test"


def test_builder_missing_methods_patched(monkeypatch):
    """Older ttkbootstrap versions provide only some date style methods."""
    dummy_ttkb = types.ModuleType("ttkbootstrap")

    class DummyStyle:
        def __init__(self, master=None):
            self.master = master
            self.configured = []

        def configure(self, style, **kw):
            self.configured.append((style, kw))

    class DummyBuilder:
        def __init__(self, *args, **kwargs):
            self.style = DummyStyle()

        def create_date_frame_style(self, style, **kw):
            self.style.configure(style, **kw)

        def name_to_method(self, name):
            return getattr(self, name)

    dummy_ttkb.Style = DummyStyle
    dummy_ttkb.style = types.SimpleNamespace(StyleBuilderTTK=DummyBuilder)

    monkeypatch.setitem(sys.modules, "ttkbootstrap", dummy_ttkb)
    monkeypatch.setitem(sys.modules, "ttkbootstrap.style", dummy_ttkb.style)

    dummy_cal_mod = types.ModuleType("tkcalendar")
    dummy_cal_mod.DateEntry = DummyDateEntry
    dummy_cal_mod.calendar_ = types.SimpleNamespace(Calendar=DummyCal)

    monkeypatch.setitem(sys.modules, "tkcalendar", dummy_cal_mod)
    monkeypatch.setitem(sys.modules, "tkcalendar.calendar_", dummy_cal_mod.calendar_)

    monkeypatch.delitem(sys.modules, "window", raising=False)
    win = load_module("window")

    builder_cls = dummy_ttkb.style.StyleBuilderTTK
    assert hasattr(builder_cls, "create_date_toplevel_style")
    b = builder_cls()
    b.create_date_toplevel_style("foo", color="red")
    assert ("foo", {"color": "red"}) in b.style.configured
