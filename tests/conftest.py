"""
firmware/main.py is real MicroPython code written for an ESP32 - it
imports `machine`, which only exists on real hardware (or the MicroPython
Unix port). To actually exercise its logic on a desktop CPython
interpreter, we register a minimal fake `machine` module in sys.modules
*before* firmware.main is ever imported, so the module-level hardware
initialization (Pin(...), UART(...), RTC()) succeeds harmlessly instead of
raising ModuleNotFoundError.
"""
import sys
import types


class _FakePin:
    OUT = 'OUT'

    def __init__(self, *args, **kwargs):
        self._value = 0

    def value(self, v=None):
        if v is not None:
            self._value = v
        return self._value


class _FakeUART:
    def __init__(self, *args, **kwargs):
        self._lines = []

    def any(self):
        return len(self._lines) > 0

    def readline(self):
        return self._lines.pop(0) if self._lines else b''


class _FakeRTC:
    def __init__(self, *args, **kwargs):
        self._dt = (2026, 1, 1, 0, 0, 0, 0, 0)

    def datetime(self, dt=None):
        if dt is not None:
            self._dt = dt
        return self._dt


_fake_machine = types.ModuleType('machine')
_fake_machine.Pin = _FakePin
_fake_machine.UART = _FakeUART
_fake_machine.RTC = _FakeRTC
sys.modules.setdefault('machine', _fake_machine)
