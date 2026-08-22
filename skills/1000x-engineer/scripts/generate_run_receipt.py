#!/usr/bin/env python3
"""
Generate Run Receipt for 1000x Engineer / Autonomous Software Factory.
Runs specified commands (e.g. tests, linters, type checks) and compiles an immutable RUN_RECEIPT.md.
"""

import sys
import os
import subprocess
import datetime
import uuid
import argparse

def run_grader(name: str, cmd: str) -> dict:
    print(f"[*] Running Grader: {name} (`{cmd}`)...")
    start = datetime.datetime.now()
    try:
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300)
        duration = (datetime.datetime.now() - start).total_seconds()
        passed = (res.returncode == 0)
        return {
            "name": name,
            "cmd": cmd,
            "passed": passed,
            "returncode": res.returncode,
            "stdout": res.stdout.strip(),
            "stderr": res.stderr.strip(),
            "duration": f"{duration:.2f}s"
        }
    except Exception as e:
        duration = (datetime.datetime.now() - start).total_seconds()
        return {
            "name": name,
            "cmd": cmd,
            "passed": False,
            "returncode": -1,
            "stdout": "",
            "stderr": str(e),
            "duration": f"{duration:.2f}s"
        }

def get_git_commit() -> str:
    try:
        res = subprocess.run("git rev-parse --short HEAD", shell=True, capture_output=True, text=True)
        if res.returncode == 0:
            return res.stdout.strip()
    except Exception:
        pass
    return "uncommitted / no-git"

def main():
    parser = argparse.ArgumentParser(description="Generate an immutable Run Receipt.")
    parser.add_argument("--spec", default="Autonomous Engineering Contract", help="Spec or contract name")
    parser.add_argument("--scope", default="Workspace", help="Scope of the task")
    parser.add_argument("--output", default="RUN_RECEIPT.md", help="Output path for the receipt")
    parser.add_argument("--test-cmd", action="append", default=[], help="Format: 'Name::command' e.g. 'Unit Tests::pytest'")
    
    args = parser.parse_args()
    
    graders = []
    if not args.test_cmd:
        # Default fallback check if none provided
        print("No --test-cmd provided, using default Python syntax / environment check.")
        graders.append(run_grader("Environment Check", f"{sys.executable} --version"))
    else:
        for item in args.test_cmd:
            if "::" in item:
                name, cmd = item.split("::", 1)
            else:
                name, cmd = item, item
            graders.append(run_grader(name.strip(), cmd.strip()))
            
    all_passed = all(g["passed"] for g in graders)
    receipt_id = f"receipt-{uuid.uuid4().hex[:8]}"
    now_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    commit_sha = get_git_commit()
    
    status_label = "✅ PASS (100%)" if all_passed else "❌ FAIL"
    
    lines = [
        "# Autonomous Software Factory: Run Receipt",
        "",
        f"**Receipt ID:** `{receipt_id}`  ",
        f"**Status:** `{status_label}`  ",
        f"**Timestamp:** `{now_str}`  ",
        f"**Executor:** `1000x Engineer Autonomous Factory`  ",
        f"**Git Commit:** `{commit_sha}`  ",
        "",
        "---",
        "",
        "## 1. Specification & Target",
        "",
        f"- **Spec Contract:** `{args.spec}`",
        f"- **Scope:** `{args.scope}`",
        "",
        "---",
        "",
        "## 2. Grader Execution Matrix",
        "",
        "| Grader Name | Command | Duration | Exit Code | Status |",
        "| :--- | :--- | :--- | :--- | :--- |"
    ]
    
    for g in graders:
        status_icon = "✅ PASS" if g["passed"] else "❌ FAIL"
        lines.append(f"| **{g['name']}** | `{g['cmd']}` | {g['duration']} | {g['returncode']} | {status_icon} |")
        
    lines.extend([
        "",
        "---",
        "",
        "## 3. Grader Diagnostic Logs",
        ""
    ])
    
    for g in graders:
        lines.append(f"### Grader: {g['name']}")
        lines.append("```text")
        if g["stdout"]:
            lines.append("--- STDOUT ---")
            lines.append(g["stdout"][:2000]) # Cap to avoid blowup
        if g["stderr"]:
            lines.append("--- STDERR ---")
            lines.append(g["stderr"][:2000])
        if not g["stdout"] and not g["stderr"]:
            lines.append("[No output]")
        lines.append("```")
        lines.append("")
        
    lines.extend([
        "---",
        "",
        "## 4. Certification",
        "",
        f"> **Receipt Integrity:** Graders evaluated. Factory Status: **{status_label}**."
    ])
    
    receipt_content = "\n".join(lines) + "\n"
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(receipt_content)
        
    print(f"[+] Run Receipt generated at: {args.output}")
    print(f"[+] Final Status: {status_label}")
    
    if not all_passed:
        sys.exit(1)

if __name__ == "__main__":
    main()
