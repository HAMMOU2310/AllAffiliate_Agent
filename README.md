# AllAffiliate_Agent

Hybrid AI System for Software Development, Automation, Content Creation, and Affiliate Marketing.

---

# Overview

AllAffiliate_Agent is a modular Hybrid AI platform designed to automate software development workflows while remaining scalable, maintainable, and easy to extend.

The project follows a layered architecture based on Agents, Services, Tools, and Core components.

Current Version:

**v1.0.0 Stable Release**

Current Status:

**Production Ready — Stable Baseline**

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
- Service Layer with Dependency Injection
- Tool Layer
- Result Pattern
- Process Runner
- Independent Agents
- Testable Components
- Documentation Driven Development
- Protocol-Based Provider Injection
- Plugin System
- SQLite FTS5 Memory Search
- Workflow Execution Engine
- Health Check and Graceful Lifecycle
- Structured Logging with Rotation
- Environment Configuration Overrides

---

# Architecture

```text
User
  ↓
MasterAgent
  ↓
TaskRouter
  ↓
CapabilityAgent / Specialized Agent
  ↓
Service
  ↓
Provider (Protocol-based)
  ↓
External Platform / OS
```

---

# Implemented Components

## Core

- `core/result.py` — Unified Result contract (UNCHANGED since v0.1)
- `core/task.py` — Task dataclass
- `core/command_parser.py` — User command to Task conversion
- `core/router.py` — TaskRouter with capability mappings
- `core/base_agent.py` — BaseAgent ABC
- `core/command_dispatcher.py` — Routes file/project commands
- `core/service_container.py` — Dependency injection container with lifecycle
- `core/registry.py` — AgentRegistry with duplicate prevention
- `core/logger.py` — Structured logger (stdlib + rich console + rotating file)
- `core/settings.py` — JSON config with environment variable overrides
- `core/health.py` — HealthChecker with HEALTHY/DEGRADED/UNAVAILABLE states
- `core/plugin_contract.py` — PluginContract Protocol
- `core/plugin_registry.py` — PluginRegistry with PluginState management
- `core/plugin_loader.py` — PluginLoader with importlib discovery

## Agents

- `agents/master_agent.py` — MasterAgent with shutdown, health_check, plugin loading
- `agents/memory_agent.py` — MemoryAgent wrapping MemoryManager
- `agents/browser_agent.py` — BrowserAgent with search/inspect/workflow routing
- `agents/computer_agent.py` — ComputerAgent (permission-gated)
- `agents/capability_agent.py` — CapabilityAgent pattern for service routing

## Services

- `services/workflow_service.py` — Planning + Execution through TaskRouter
- `services/research_service.py` — Provider-neutral research with evidence normalization
- `services/analysis_service.py` — Evidence classification (FACT/HYPOTHESIS/RECOMMENDATION)
- `services/content_service.py` — Structured content draft generation
- `services/digital_asset_service.py` — Digital asset registry
- `services/product_service.py` — Multi-signal product ranking
- `services/policy_service.py` — ALLOWED/BLOCKED/REVIEW_REQUIRED decisions
- `services/video_production_service.py` — Temporal video planning + execution
- `services/audio_service.py` — Audio planning + execution
- `services/media_pipeline_service.py` — Video/Audio composition validation
- `services/publishing_service.py` — Fail-closed publishing gateway
- `services/performance_monitoring_service.py` — Observation recording
- `services/diagnosis_service.py` — Anomaly diagnosis
- `services/experiment_service.py` — Experiment tracking
- `services/browser_service.py` — BrowserAdapter Protocol boundary
- `services/computer_service.py` — Permission-gated ComputerAdapter Protocol
- `services/image_service.py` — Image generation routing

## Providers

- `providers/gemini_provider.py` — Gemini Cloud AI provider
- `providers/openai_provider.py` — OpenAI Cloud AI provider
- `providers/gemini_image_provider.py` — Gemini image generation
- `providers/local_image_provider.py` — Local image generation
- `providers/gemini_voice_provider.py` — Gemini STT + TTS
- `providers/gemini_video_provider.py` — Gemini video generation
- `providers/ffmpeg_video_renderer.py` — FFmpeg video rendering
- `providers/openserp_search_provider.py` — OpenSERP OSS search
- `providers/search_browser_adapter.py` — SearchBrowserAdapter
- `providers/audio_utils.py` — Audio utility helpers
- `providers/cloud_ai_content_generator.py` — ContentGenerator adapter

## Memory

- `memory/memory_manager.py` — SQLite memory with FTS5 content search

## Tools

- `tools/file_tools.py` — File operations
- `tools/python_tools.py` — Python script execution

---

# Test Baseline (v1.0.0)

```text
1009 collected
1004 passed
3 failed (known Gemini external API flakiness)
2 skipped (expected OpenSERP environment skips)
0 errors
```

---

# Known Limitations (Non-Blocking)

- Playwright browser page interaction deferred — installation is network-blocked
- WorkflowService.plan() runtime planner registration remains unused architectural functionality
- ComputerService remains permission-gated with no adapter
- OpenAI providers unavailable without OPENAI_API_KEY
- Stability AI unavailable without credentials/package
- edge-tts unavailable; Gemini TTS remains available
- Gemini real API tests can be flaky
- OpenSERP tests require local OpenSERP environment

---

# Documentation

Documentation is located inside:

```text
docs/
project_context/
```

---

# Running Tests

```powershell
.\myenv\Scripts\python.exe -m pytest -q
```

---

# Development Principles

- Clean Architecture
- Separation of Concerns
- Single Responsibility Principle
- Modular Design
- Result Pattern
- Protocol-Based Provider Injection
- Independent Components
- Reusable Code
- Documentation First
- Test Before Integration

---

# Roadmap

v1.0.0 Stable Release — 2026-09-23

Post-v1.0 roadmap is pending definition.

---

# Status

Current Status:

**v1.0.0 Stable Release**

Release Commit: **be52c49**

Release Tag: **v1.0.0**

---

# License

This project is currently under private development.

Copyright © 2026 AllAffiliate_Agent.
