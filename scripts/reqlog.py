"""Pytest plugin: log THEO TUNG TEST -> {test, outcome, requests[]}.
Moi dong JSONL = 1 test: ten, ket qua (passed/failed/error), va cac
request/response HTTP no goi. Dung: pytest ... -p reqlog ; REQLOG=<file>."""
import os
import json
import requests
import pytest

LOG = os.environ.get("REQLOG", "reqlog.jsonl")
_orig = requests.sessions.Session.request
_cur = {"test": "<setup>"}
_rec = {}   # nodeid -> {"outcome":..., "requests":[...]}


def _slot(tid):
    return _rec.setdefault(tid, {"outcome": None, "requests": []})


def _patched(self, method, url, **kw):
    resp = _orig(self, method, url, **kw)
    r = {"method": method.upper(), "url": url,
         "req": kw.get("json", kw.get("data")),
         "status": getattr(resp, "status_code", None)}
    try:
        r["resp"] = resp.json()
    except Exception:
        r["resp"] = getattr(resp, "text", "")[:300]
    _slot(_cur["test"])["requests"].append(r)
    return resp


def pytest_configure(config):
    requests.sessions.Session.request = _patched


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_protocol(item, nextitem):
    _cur["test"] = item.nodeid
    _slot(item.nodeid)
    yield


def pytest_runtest_logreport(report):
    rec = _slot(report.nodeid)
    if report.when == "setup" and report.outcome != "passed":
        rec["outcome"] = "error@setup"
    elif report.when == "call":
        rec["outcome"] = report.outcome   # passed / failed
        if report.failed and report.longrepr:
            rec["fail_reason"] = str(report.longrepr).splitlines()[-1][:200]


def pytest_sessionfinish(session, exitstatus):
    with open(LOG, "w", encoding="utf-8") as f:
        for tid, rec in _rec.items():
            if tid == "<setup>":
                continue
            name = tid.split("::")[-1]
            f.write(json.dumps({"test": name, "nodeid": tid, **rec},
                               ensure_ascii=False, default=str) + "\n")
