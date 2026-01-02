from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class RuleMatch:
    matched: bool
    reasons: list[str]


def _get_path(obj: Any, path: str) -> Any:
    cur = obj
    for part in path.split("."):
        if part == "":
            continue
        if isinstance(cur, dict):
            cur = cur.get(part)
            continue
        if isinstance(cur, list) and part.isdigit():
            idx = int(part)
            cur = cur[idx] if 0 <= idx < len(cur) else None
            continue
        return None
    return cur


def _match_condition(payload: dict[str, Any], cond: dict[str, Any]) -> RuleMatch:
    op = str(cond.get("op") or "").strip()
    reasons: list[str] = []

    headers = payload.get("headers") if isinstance(payload.get("headers"), dict) else {}
    headers_lc = {str(k).lower(): str(v) for k, v in headers.items()} if isinstance(headers, dict) else {}
    json_body = payload.get("json") if isinstance(payload.get("json"), dict) else None

    if op == "header_present":
        name = str(cond.get("name") or "").lower()
        ok = bool(name) and name in headers_lc
        return RuleMatch(ok, [f"header_present:{name}"] if ok else [f"missing_header:{name}"])

    if op == "header_equals":
        name = str(cond.get("name") or "").lower()
        expected = str(cond.get("value") or "")
        got = headers_lc.get(name)
        ok = got is not None and got == expected
        return RuleMatch(ok, [f"header_equals:{name}"] if ok else [f"header_mismatch:{name}"])

    if op == "json_path_exists":
        path = str(cond.get("path") or "")
        ok = json_body is not None and _get_path(json_body, path) is not None
        return RuleMatch(ok, [f"json_path_exists:{path}"] if ok else [f"json_path_missing:{path}"])

    if op == "json_path_equals":
        path = str(cond.get("path") or "")
        expected = cond.get("value")
        got = _get_path(json_body, path) if json_body is not None else None
        ok = got == expected
        return RuleMatch(ok, [f"json_path_equals:{path}"] if ok else [f"json_path_mismatch:{path}"])

    if op == "json_path_regex":
        path = str(cond.get("path") or "")
        pattern = str(cond.get("pattern") or "")
        got = _get_path(json_body, path) if json_body is not None else None
        ok = got is not None and re.search(pattern, str(got)) is not None
        return RuleMatch(ok, [f"json_path_regex:{path}"] if ok else [f"json_path_no_match:{path}"])

    return RuleMatch(False, [f"unknown_op:{op}"])


def rule_matches(payload: dict[str, Any], rule_conditions: dict[str, Any]) -> RuleMatch:
    if "all" in rule_conditions and isinstance(rule_conditions["all"], list):
        reasons: list[str] = []
        for cond in rule_conditions["all"]:
            if not isinstance(cond, dict):
                return RuleMatch(False, ["invalid_condition"])
            match = _match_condition(payload, cond)
            reasons.extend(match.reasons)
            if not match.matched:
                return RuleMatch(False, reasons)
        return RuleMatch(True, reasons)

    if "any" in rule_conditions and isinstance(rule_conditions["any"], list):
        reasons: list[str] = []
        any_ok = False
        for cond in rule_conditions["any"]:
            if not isinstance(cond, dict):
                continue
            match = _match_condition(payload, cond)
            reasons.extend(match.reasons)
            any_ok = any_ok or match.matched
        return RuleMatch(any_ok, reasons)

    if isinstance(rule_conditions.get("op"), str):
        return _match_condition(payload, rule_conditions)  # single condition

    return RuleMatch(False, ["invalid_rule_conditions"])

