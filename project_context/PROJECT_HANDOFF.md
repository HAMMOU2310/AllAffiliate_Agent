# AllAffiliate_Agent — PROJECT HANDOFF

## Purpose

Official handoff contract between ChatGPT development conversations.

This file is located at:

`project_context/PROJECT_HANDOFF.md`

The `project_context/` directory is the official source of project state, handoff, contracts, architecture, rules, structure, and changelog.

---

## Start Here

A new conversation must read, in this exact order:

1. `project_context/PROJECT_HANDOFF.md`
2. `project_context/PROJECT_STATE.md`
3. `project_context/PROJECT_STRUCTURE.md`

Then, when required:

4. `project_context/API_CONTRACTS.md`
5. `project_context/PROJECT_BLUEPRINT.md`
6. `project_context/DEVELOPMENT_RULES.md`

Only after reading the relevant project-context files should the conversation inspect the current working file or a directly required dependency.

A new conversation must NOT request:

- the full repository
- the full project tree
- all `core/` files
- all `agents/` files
- all `services/` files
- test files

as a prerequisite.

Only request a specific missing dependency or the explicitly identified current working file when the project-context documents show that it is required and unavailable.

---

## Official Project Context

The official project-context directory is:

`project_context/`

It contains exactly one official copy of each state/reference document:

```text
project_context/
├── PROJECT_HANDOFF.md
├── PROJECT_STATE.md
├── PROJECT_STRUCTURE.md
├── PROJECT_BLUEPRINT.md
├── DEVELOPMENT_RULES.md
├── API_CONTRACTS.md
└── CHANGELOG.md