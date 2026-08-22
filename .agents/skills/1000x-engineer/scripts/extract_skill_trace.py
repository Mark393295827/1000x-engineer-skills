#!/usr/bin/env python3
"""
Extract Skill Trace - Skillify Helper.
Scaffolds a new Skill package from problem statements, execution traces, or solutions.
"""

import sys
import os
import argparse

SKILL_TEMPLATE = """---
name: {skill_name}
description: >-
  {description}
---

# {title}

> **Origin & Context:** Distilled from autonomous execution trace on {context}.

---

## 1. Problem Signature & Invariants

### Problem Pattern
{problem_pattern}

### Non-Negotiable Invariants
- [ ] Maintain backward compatibility.
- [ ] Strict type integrity and deterministic error handling.
- [ ] Verify 100% pass on regression test suite.

---

## 2. Forbidden Anti-Patterns
- ❌ Do NOT repeat the previous root-cause error: `{root_cause}`
- ❌ Do NOT skip automated validation.

---

## 3. Standard Remediation & Execution Procedure

1. **Pre-flight**: Inspect current state and isolate failing edge case.
2. **Execute Solution**:
   ```text
   {solution_steps}
   ```
3. **Verify**:
   Run target test suite to confirm zero regressions.
4. **Issue Receipt**: Generate updated `RUN_RECEIPT.md`.
"""

def main():
    parser = argparse.ArgumentParser(description="Skillify: Turn an execution trace into a reusable Skill package.")
    parser.add_argument("--name", required=True, help="Skill name in kebab-case e.g. fix-async-deadlock")
    parser.add_argument("--desc", required=True, help="Third-person description for when to activate this skill")
    parser.add_argument("--title", help="Human-readable title", default=None)
    parser.add_argument("--problem", help="Description of the problem pattern", default="Describe problem pattern")
    parser.add_argument("--root-cause", help="Identified root cause", default="Identified failure mechanism")
    parser.add_argument("--solution", help="Remediation steps", default="1. Apply fix\n2. Verify")
    parser.add_argument("--out-dir", default=".agents/skills", help="Directory where skills reside")
    
    args = parser.parse_args()
    
    skill_dir = os.path.join(args.out_dir, args.name)
    os.makedirs(skill_dir, exist_ok=True)
    os.makedirs(os.path.join(skill_dir, "references"), exist_ok=True)
    os.makedirs(os.path.join(skill_dir, "resources"), exist_ok=True)
    os.makedirs(os.path.join(skill_dir, "scripts"), exist_ok=True)
    
    title = args.title or args.name.replace("-", " ").title()
    content = SKILL_TEMPLATE.format(
        skill_name=args.name,
        description=args.desc,
        title=title,
        context=args.name,
        problem_pattern=args.problem,
        root_cause=args.root_cause,
        solution_steps=args.solution
    )
    
    skill_file = os.path.join(skill_dir, "SKILL.md")
    with open(skill_file, "w", encoding="utf-8") as f:
        f.write(content)
        
    print(f"[+] Successfully skillified into: {skill_file}")

if __name__ == "__main__":
    main()
