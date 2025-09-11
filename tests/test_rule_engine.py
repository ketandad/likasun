from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))
from packages.rules import RuleEngine, load_templates


def test_rule_engine_expansion():
    templates = load_templates(Path('packages/rules/templates'))
    engine = RuleEngine(templates)
    envs = ['prod', 'dev']
    types = ['db', 'vm']
    params = [{'enabled': True}, {'enabled': False}]
    controls = engine.expand(envs, types, params)
    assert len(controls) == 4
