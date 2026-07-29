# AllAffiliate_Agent

Hybrid AI System for Software Development, Automation, Content Creation, and Affiliate Marketing.

---

# Overview

AllAffiliate_Agent is a modular Hybrid AI platform designed to automate software development workflows while remaining scalable, maintainable, and easy to extend.

The project follows a layered architecture based on Agents, Services, Tools, and Core components.

Current Version:

**v0.3.0**

Current Development Phase:

**Version 0.4 — Memory System**

---

# Vision

Build a complete AI platform capable of:

- Software Development
- Affiliate Marketing
- Content Creation
- File Management
- Project Automation
- Multi-Agent Collaboration
- Future AI Integrations

---

# Main Features

- Hybrid AI Architecture
- Clean Architecture
- Modular Design
- Service Layer
- Tool Layer
- Result Pattern
- Process Runner
- Independent Agents
- Testable Components
- Documentation Driven Development

---

# Current Project Structure

```text
AllAffiliate_Agent/

├── agents/
├── config/
├── core/
├── database/
├── docs/
├── logs/
├── memory/
├── modules/
├── outputs/
├── prompts/
├── providers/
├── services/
├── tests/
├── tools/
├── workflows/
├── workspace/

├── assistant.py
├── launcher.py
├── README.md
├── requirements.txt
└── .gitignore
```

---

# Architecture

```text
User

↓

MasterAgent

↓

TaskRouter

↓

Agent

↓

Service

↓

Tool

↓

Operating System / External Providers
```

---

# Implemented Components

## Core

- Result
- Process

## Tools

- FileTools
- TerminalTools
- PythonTools

## Services

- BaseService
- ProjectManager
- CodeWriter
- PythonRunner
- ErrorAnalyzer

---

# Documentation

Documentation is located inside:

```text
docs/
```

Including:

- ROADMAP.md
- ARCHITECTURE.md
- DEVELOPMENT.md
- CHANGELOG.md
- TESTING.md

---

# Running Tests

Examples:

```powershell
python -m workspace.test_result
```

```powershell
python -m workspace.test_file_tools
```

```powershell
python -m workspace.test_terminal_tools
```

```powershell
python -m workspace.test_python_tools
```

```powershell
python -m workspace.test_project_manager
```

```powershell
python -m workspace.test_code_writer
```

```powershell
python -m workspace.test_python_runner
```

```powershell
python -m workspace.test_error_analyzer
```

---

# Development Principles

- Clean Architecture
- Separation of Concerns
- Single Responsibility Principle
- Modular Design
- Result Pattern
- Independent Components
- Reusable Code
- Documentation First
- Test Before Integration

---

# Roadmap

Current Development:

**Version 0.4**

Next milestones:

- Memory System
- BrowserAgent
- ImageAgent
- VoiceAgent
- VideoAgent

---

# Status

Current Status:

**Active Development**

Stable Release Target:

**Version 1.0**

---

# License

This project is currently under private development.

Copyright © 2026 AllAffiliate_Agent.