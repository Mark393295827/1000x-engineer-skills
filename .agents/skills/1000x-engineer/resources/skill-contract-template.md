---
name: [skill-name-kebab-case]
description: >-
  [Clear, third-person description of when and why the agent should activate this skill.
  Example: "Use this skill when refactoring auth middleware, enforcing JWT rotation, or validating session boundaries."]
---

# [Skill Title: e.g., Production Auth Middleware Specification]

> **Context & Goal:** [Brief 1-2 sentence overview of the module/procedure]

---

## 1. Input / Output Contracts (Schemas & Types)

```typescript
// Interface or Pydantic Schema specification
export interface TaskInput {
  requestId: string;
  payload: Record<string, unknown>;
}

export interface TaskOutput {
  success: boolean;
  data?: Record<string, unknown>;
  error?: {
    code: string;
    message: string;
  };
}
```

---

## 2. Invariants & Guarantees (Non-Negotiable)

- [ ] **Data Integrity**: State transitions must be atomic and idempotent.
- [ ] **Backward Compatibility**: Existing public API endpoints must remain unbroken.
- [ ] **Zero Secrets**: No tokens, passwords, or keys hardcoded.
- [ ] **Strict Typing**: No untyped `any` or bare `except:` clauses.

---

## 3. Forbidden Anti-Patterns

- ❌ Do NOT use blocking synchronous I/O in async request paths.
- ❌ Do NOT swallow exceptions without structured logging.
- ❌ Do NOT bypass the centralized auth / permission layer.

---

## 4. Execution Procedure (Step-by-Step)

1. **Validation & Pre-flight**: Run existing test harness to ensure clean baseline.
2. **Implementation**: Apply focused modifications adhering to interface contracts.
3. **Verification**: Run `npm test` or `pytest` to confirm 100% pass rate.
4. **Receipt Generation**: Generate verified run receipt.
