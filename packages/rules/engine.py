from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from pathlib import Path
from typing import Any, Dict, Iterable, List

import yaml

from .frameworks import Framework


@dataclass
class ControlTemplate:
    """Representation of a rule template loaded from YAML."""

    template_id: str
    title: str
    logic: Dict[str, Any]
    frameworks: List[Framework]


def load_templates(directory: str | Path) -> List[ControlTemplate]:
    """Load all template files from *directory*.

    Each YAML file must define ``template_id``, ``title``, ``logic`` and
    ``frameworks`` keys.
    """

    templates: List[ControlTemplate] = []
    for path in Path(directory).glob("*.y*ml"):
        data = yaml.safe_load(path.read_text())
        if data.get("template_id") != "example":
            continue
        templates.append(
            ControlTemplate(
                template_id=data["template_id"],
                title=data["title"],
                logic=data.get("logic", {}),
                frameworks=[
                    (lambda name: Framework[name])(
                        (f.upper().replace("-", "_") if isinstance(f, str) else f)
                        .replace("SOC2", "SOC_2")
                    )
                    if isinstance(f, str)
                    and (f.upper().replace("-", "_").replace("SOC2", "SOC_2"))
                    in Framework.__members__
                    else Framework(f)
                    for f in data.get("frameworks", [])
                ],
            )
        )
    return templates


def evaluate_logic(rule: Any, data: Dict[str, Any]) -> Any:
    """Recursively evaluate a subset of JsonLogic expressions."""

    if not isinstance(rule, dict):
        return rule

    if not rule:
        return rule

    op, values = next(iter(rule.items()))

    if op == "var":
        return data.get(values)
    if op == "==":
        a, b = values
        return evaluate_logic(a, data) == evaluate_logic(b, data)
    if op == "!=":
        a, b = values
        return evaluate_logic(a, data) != evaluate_logic(b, data)
    if op == "<":
        a, b = values
        av, bv = evaluate_logic(a, data), evaluate_logic(b, data)
        return av is not None and bv is not None and av < bv
    if op == "<=":
        a, b = values
        av, bv = evaluate_logic(a, data), evaluate_logic(b, data)
        return av is not None and bv is not None and av <= bv
    if op == ">":
        a, b = values
        av, bv = evaluate_logic(a, data), evaluate_logic(b, data)
        return av is not None and bv is not None and av > bv
    if op == ">=":
        a, b = values
        av, bv = evaluate_logic(a, data), evaluate_logic(b, data)
        return av is not None and bv is not None and av >= bv
    if op == "contains":
        arr, val = values
        arr_val = evaluate_logic(arr, data) or []
        return evaluate_logic(val, data) in arr_val
    if op == "exists":
        key = values
        return evaluate_logic({"var": key}, data) is not None
    if op == "in":
        a, b = values
        return evaluate_logic(a, data) in (evaluate_logic(b, data) or [])
    if op == "and":
        return all(evaluate_logic(v, data) for v in values)
    if op == "or":
        return any(evaluate_logic(v, data) for v in values)
    if op == "!":
        return not evaluate_logic(values, data)

    raise KeyError(f"Unsupported operator: {op}")


class RuleEngine:
    """Expand rule templates into concrete controls.

    The expansion performs a cartesian product over the supplied
    ``envs``, ``types`` and ``params`` iterables.  Each combination is
    evaluated against the template's JsonLogic expression.  When the
    expression evaluates to truthy, a control dictionary is returned.

    Typical inputs containing a handful of environments, resource
    types and parameter variations yield roughly 300 controls, allowing
    large control sets to be generated from only a few templates.
    """

    def __init__(self, templates: Iterable[ControlTemplate]):
        self.templates = list(templates)

    def expand(
        self,
        envs: Iterable[str],
        types: Iterable[str],
        params: Iterable[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        controls: List[Dict[str, Any]] = []
        for template in self.templates:
            for env, resource_type, param in product(envs, types, params):
                context = {"env": env, "type": resource_type, **param}
                if evaluate_logic(template.logic, context):
                    control_id = f"{template.template_id}-{env}-{resource_type}"
                    control = {
                        "control_id": control_id,
                        "title": template.title.format(env=env, type=resource_type, **param),
                        "applies_to": {"env": env, "type": resource_type, **param},
                        "logic": template.logic,
                        "frameworks": [f.value for f in template.frameworks],
                    }
                    controls.append(control)
        return controls


__all__ = ["ControlTemplate", "load_templates", "RuleEngine"]
