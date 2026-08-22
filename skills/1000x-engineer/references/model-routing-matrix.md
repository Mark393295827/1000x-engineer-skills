# Model Routing & Subagent Topology Matrix

In an autonomous software factory, optimizing compute budgets, token limits, and reasoning capability is paramount. Match subagents and model tiers to task complexity.

---

## 1. Model Tier Classification

| Tier | Typical Models | Characteristics | Best Suited For |
| :--- | :--- | :--- | :--- |
| **Tier 1: Lite / Flash** | `flash_lite`, `flash`, `haiku` | Ultra-fast latency, low cost, high throughput | - Repetitive code conversion & boilerplate<br>- Markdown formatting & docstrings<br>- Quick file search & log summarization<br>- Simple regex & string manipulation |
| **Tier 2: General / Balanced** | `inherit`, `standard models` | Balanced speed, reasoning, and tool use | - Unit test generation<br>- Feature implementation matching existing patterns<br>- Refactoring localized components<br>- Integration test execution |
| **Tier 3: Pro / Thinking / Deep Reasoning** | `pro`, `opus`, `thinking` | Deep multi-step reasoning, mathematical & architectural deduction | - System architecture & interface contract design<br>- Concurrency & distributed consensus logic<br>- Complex bug diagnosis across multiple layers<br>- Evals framework & harness design |

---

## 2. Multi-Agent Topology: "Boil the Ocean" Pattern

When building or refactoring large systems, decouple work into isolated nodes in a Directed Acyclic Graph (DAG):

```text
               ┌─────────────────────────────┐
               │   Factory Commander (Lead)  │
               │   [Thinking / Spec Design]   │
               └──────────────┬──────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         ▼                    ▼                    ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│ Data & Persistence│ │ Service & Domain │ │ API & Transport  │
│  Worker (Flash)  │ │ Worker (Standard)│ │  Worker (Flash)  │
└────────┬─────────┘ └────────┬─────────┘ └────────┬─────────┘
         │                    │                    │
         └────────────────────┼────────────────────┘
                              ▼
               ┌─────────────────────────────┐
               │    QA & Eval Grader (Lead)   │
               │    [Run Receipt Generation]  │
               └─────────────────────────────┘
```

---

## 3. Subagent Dispatch Guidelines in Antigravity

- Use `invoke_subagent` with explicit `TypeName`, `Role`, `Prompt`, and `Model`:
  ```json
  {
    "TypeName": "research",
    "Role": "Schema Researcher",
    "Model": "flash",
    "Prompt": "Survey the database migration folder and list all schema definitions."
  }
  ```
- Use `Workspace: "share"` or `"branch"` when subagents perform independent git operations.
- Avoid circular delegation and prevent unmonitored nested spawning.
