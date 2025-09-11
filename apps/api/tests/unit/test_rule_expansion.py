import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[4]))

from packages.rules.engine import ControlTemplate, RuleEngine
from packages.rules.frameworks import Framework


def test_rule_expansion_generates_controls():
    templates = [
        ControlTemplate(
            template_id=f"tmpl{i}",
            title="tmpl",
            logic={"==": [1, 1]},
            frameworks=[
                Framework.FEDRAMP_LOW,
                Framework.FEDRAMP_MODERATE,
                Framework.FEDRAMP_HIGH,
            ],
        )
        for i in range(60)
    ]
    engine = RuleEngine(templates)
    envs = ["demo"]
    types = [f"type{j}" for j in range(5)]
    params = [{}]
    controls = engine.expand(envs, types, params)
    assert len(controls) == 300
    assert {"FedRAMP Low", "FedRAMP Moderate", "FedRAMP High"}.issubset(
        set(controls[0]["frameworks"])
    )
