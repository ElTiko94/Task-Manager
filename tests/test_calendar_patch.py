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
