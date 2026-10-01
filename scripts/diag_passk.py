"""Chan doan pass@k 1 muc: chay pytest -v + log req/resp, luu file.
Dung: python diag_passk.py <code_dir> <level>   (level=L1/L2/L3)
Luu: output/pytest_<level>.txt  va  output/testlog_<level>.jsonl
"""
import sys
import subprocess
import time
import os
from pathlib import Path

V = str(Path(".venv-run/Scripts/python.exe").resolve())
ORACLE = Path("data/RepoGenesis-Verified-GoldenOracle-v1/expert_supervised/"
              "python/TaskManagement").resolve()


def main():
    code_dir = Path(sys.argv[1]).resolve()
    level = sys.argv[2]
    logjsonl = Path(f"output/testlog_{level}.jsonl").resolve()
    txtout = Path(f"output/pytest_{level}.txt")

    import requests
    env = dict(os.environ, PORT="8080", PYTHONIOENCODING="utf-8",
               REQLOG=str(logjsonl),
               PYTHONPATH=str(Path("scripts").resolve()))
    proc = subprocess.Popen(
        [V, "-m", "uvicorn", "main:app", "--host", "::", "--port", "8080",
         "--log-level", "warning"], cwd=str(code_dir), env=env,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
    health = False
    try:
        for _ in range(15):
            try:
                if requests.get("http://localhost:8080/api/v1/health",
                                timeout=2).status_code == 200:
                    health = True
                    break
            except Exception:
                pass
            time.sleep(1)
        print(f"[{level}] health={health}")
        # neu khong health, van chay -v nhung gioi han thoi gian ngan
        timeout = 300 if health else 90
        try:
            p = subprocess.run(
                [V, "-m", "pytest", str(ORACLE / "tests"), "-v", "--tb=short",
                 "-p", "reqlog", "-p", "no:cacheprovider"],
                cwd=str(code_dir), env=env, capture_output=True, text=True,
                timeout=timeout)
            out = p.stdout + p.stderr
        except subprocess.TimeoutExpired as e:
            out = (e.stdout or "") + f"\n[TIMEOUT {timeout}s — co the thieu /health, "
            out += "conftest retry moi test]"
            if isinstance(out, bytes):
                out = out.decode("utf-8", "replace")
        txtout.write_text(out, encoding="utf-8")
        # tom tat
        tail = [l for l in out.splitlines()
                if "passed" in l or "failed" in l or "error" in l][-1:]
        print(f"[{level}] {tail}")
        print(f"[{level}] pytest -v -> {txtout}")
        print(f"[{level}] req/resp log -> {logjsonl}")
    finally:
        subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                       capture_output=True)


if __name__ == "__main__":
    main()
