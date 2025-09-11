import importlib
import os
import sys
from pathlib import Path

import pytest

BASE = Path(__file__).resolve().parents[2]
ROOT = Path(__file__).resolve().parents[4]
sys.path.extend([str(BASE), str(ROOT)])

from app.security import egress  # noqa: E402


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
