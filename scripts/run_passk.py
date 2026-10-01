"""
Vong 2 — chay 1 codebase microservice qua test suite -> dem pass/total.

Lam moi thu in-process (robust tren Windows):
  1. detect entry (FastAPI main:app / Flask app.py) trong code_dir
  2. start server o 127.0.0.1:8080 bang python cua venv runner (subprocess)
  3. poll /api/v1/health
  4. chay pytest <tests_dir> -> parse "X passed, Y failed"
  5. kill server (process tree)

Dung: python run_passk.py <code_dir> [--tests <dir>] [--port 8080]
Mac dinh tests = <code_dir>/tests. In JSON ket qua ra stdout dong cuoi.
"""
import sys
import subprocess
import time
import json
import argparse
import re
import os
import signal
from pathlib import Path

RUN_PY = Path(__file__).resolve().parents[1] / ".venv-run" / "Scripts" / "python.exe"


def detect_start_cmd(code_dir: Path, port: int):
    """Tra ve list argv de start server, hoac None."""
    if (code_dir / "main.py").exists():
        txt = (code_dir / "main.py").read_text("utf-8", "replace")
        if "app" in txt:  # FastAPI/Flask expose `app`
            # Bind "::" (IPv6 dual-stack) vi test dung http://localhost ->
            # resolve ::1 TRUOC tren Windows. Bind 127.0.0.1 lam moi request
            # cho ::1 timeout -> pytest cham hang phut (README oracle canh bao).
            return [str(RUN_PY), "-m", "uvicorn", "main:app",
                    "--host", "::", "--port", str(port),
                    "--log-level", "warning"]
    if (code_dir / "app.py").exists():
        return [str(RUN_PY), str(code_dir / "app.py")]
    # fallback: tim file co uvicorn.run / app.run
    for py in code_dir.glob("*.py"):
        t = py.read_text("utf-8", "replace")
        if "uvicorn" in t or "app.run" in t:
            return [str(RUN_PY), str(py)]
    return None


def wait_health(port, timeout=25):
    import requests
    url = f"http://localhost:{port}/api/v1/health"  # nhu test (localhost)
    for _ in range(timeout):
        try:
            if requests.get(url, timeout=2).status_code == 200:
                return True
        except Exception:
            pass
        time.sleep(1)
    return False


def parse_pytest(output: str):
    """Trich (passed, failed, errors, total) tu output pytest.
    total = passed+failed+errors+skipped (= so test collected, ~44)."""
    def g(pat):
        m = re.search(pat, output)
        return int(m.group(1)) if m else 0
    passed = g(r"(\d+) passed")
    failed = g(r"(\d+) failed")
    errors = g(r"(\d+) error")
    skipped = g(r"(\d+) skipped")
    return passed, failed, errors, passed + failed + errors + skipped


def run(code_dir: Path, tests_dir: Path, port: int):
    result = {"code_dir": str(code_dir), "server_started": False,
              "health_ok": False, "passed": 0, "failed": 0, "errors": 0,
              "total": 0, "note": ""}

    cmd = detect_start_cmd(code_dir, port)
    if cmd is None:
        result["note"] = "khong tim thay entry point (main.py/app.py)"
        return result

    env = dict(os.environ, HOST="127.0.0.1", PORT=str(port),
               PYTHONIOENCODING="utf-8")
    creationflags = 0
    if os.name == "nt":
        creationflags = subprocess.CREATE_NEW_PROCESS_GROUP
    # Ghi log server ra FILE (tranh deadlock PIPE khong drain).
    logf = code_dir / "_server.log"
    logh = open(logf, "wb")
    proc = subprocess.Popen(cmd, cwd=str(code_dir), env=env,
                            stdout=logh, stderr=subprocess.STDOUT,
                            creationflags=creationflags)
    result["server_started"] = True
    try:
        health = wait_health(port)
        result["health_ok"] = health
        if not health:
            # Server thieu /api/v1/health (vd code tu requirement ngheo).
            # conftest wait_for_server se skip MOI test (retry 30s/test -> treo).
            # -> KHONG chay test that; collect-only de lay mau so, passed=0.
            result["note"] = "health FAIL (thieu /api/v1/health) -> tat ca test skip"
            pc = subprocess.run(
                [str(RUN_PY), "-m", "pytest", str(tests_dir), "--collect-only",
                 "-q", "-p", "no:cacheprovider"],
                cwd=str(code_dir), env=env, capture_output=True, text=True,
                timeout=60)
            m = re.search(r"(\d+) tests? collected", pc.stdout + pc.stderr)
            total = int(m.group(1)) if m else 0
            result.update(passed=0, failed=0, errors=0, total=total)
            result["pytest_tail"] = f"health fail -> 0/{total} (skip)"
            return result

        # health OK -> chay test that
        p = subprocess.run(
            [str(RUN_PY), "-m", "pytest", str(tests_dir), "-q", "--tb=no",
             "-p", "no:cacheprovider"],
            cwd=str(code_dir), env=env, capture_output=True, text=True,
            timeout=300)
        out = p.stdout + p.stderr
        passed, failed, errors, total = parse_pytest(out)
        result.update(passed=passed, failed=failed, errors=errors, total=total)
        result["pytest_tail"] = out.strip().splitlines()[-1] if out.strip() else ""
    finally:
        try:
            if os.name == "nt":
                subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                               capture_output=True, timeout=10)
            else:
                proc.terminate()
            proc.wait(timeout=5)
        except Exception:
            pass
        try:
            logh.close()
        except Exception:
            pass
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("code_dir")
    ap.add_argument("--tests", default=None)
    ap.add_argument("--port", type=int, default=8080)
    args = ap.parse_args()
    code_dir = Path(args.code_dir).resolve()
    tests_dir = Path(args.tests).resolve() if args.tests else code_dir / "tests"

    r = run(code_dir, tests_dir, args.port)
    print("\n" + "=" * 50)
    print(f"code   : {r['code_dir']}")
    print(f"server : {'started' if r['server_started'] else 'FAIL'}"
          f" | health: {'OK' if r['health_ok'] else 'FAIL'}")
    print(f"pass   : {r['passed']}/{r['total']}  "
          f"(failed={r['failed']}, errors={r['errors']})")
    if r.get("pytest_tail"):
        print(f"pytest : {r['pytest_tail']}")
    if r["note"]:
        print(f"note   : {r['note']}")
    print("RESULT_JSON " + json.dumps({k: r[k] for k in
          ("passed", "failed", "errors", "total", "health_ok")}))


if __name__ == "__main__":
    main()
