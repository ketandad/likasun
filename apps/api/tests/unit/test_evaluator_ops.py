import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[4]))

from app.services.evaluator import _evaluate, evaluate_control
from app.models import controls as control_m, assets as asset_m


def test_evaluator_basic_ops():
    data = {"a": 1, "b": 2, "list": [1, 2], "text": "abc"}
    assert _evaluate({"==": [1, 1]}, data)
    assert _evaluate({"!=": [1, 2]}, data)
    assert _evaluate({"in": [1, {"var": "list"}]}, data)
    assert _evaluate({"regex": [{"var": "text"}, "^a"]}, data)
    assert _evaluate({"and": [True, {"==": [1, 1]}]}, data)
    assert _evaluate({"or": [False, {"==": [1, 1]}]}, data)


def test_na_handling():
    control = control_m.Control(
        control_id="C1",
        title="c",
        category="cat",
        severity="low",
        applies_to={},
        logic={"==": [{"var": "config.missing"}, True]},
        frameworks=[],
        fix={},
    )
    asset = asset_m.Asset(
        asset_id="A1",
        cloud="aws",
        type="User",
        region="us",
        tags={},
        config={},
        evidence={},
        ingest_source="test",
    )
    result = evaluate_control(control, [asset])[0]
    assert result.status == "NA"
