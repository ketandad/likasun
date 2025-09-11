import importlib
import os

import pytest

from app.security import egress


def reload_module():
    importlib.reload(egress)


def test_egress_blocked_by_default():
    os.environ.pop("EGRESS_ALLOWLIST", None)
    reload_module()
    with pytest.raises(RuntimeError):
        egress.guard_outbound("https://example.com")


def test_egress_allowed_with_allowlist():
    os.environ["EGRESS_ALLOWLIST"] = "example.com"
    reload_module()
    egress.guard_outbound("https://example.com")
