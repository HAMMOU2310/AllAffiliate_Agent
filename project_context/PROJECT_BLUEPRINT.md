# PROJECT_BLUEPRINT.md

# AllAffiliate_Agent

**Official Project Blueprint**

**Version:** v1.0

**Status:** Integrated Autonomous Digital Operations Platform — Local DoD Validated

**Document Version:** 1.0

---

# Table of Contents

1. Introduction
2. Project Vision
3. Mission
4. Project Goals
5. Scope
6. Core Philosophy
7. Design Principles
8. System Architecture
9. Execution Pipeline
10. Core Components
11. Agents Layer
12. Services Layer
13. Core Layer
14. Memory Layer
15. Configuration Layer
16. Logging Layer
17. Plugin System
18. AI Integration
19. Local AI Migration
20. Video Creation Pipeline
21. Affiliate Workflow
22. Development Roadmap
23. Architectural Rules
24. Coding Standards
25. Future Vision

---

# 1. Introduction

AllAffiliate_Agent هو مشروع طويل الأمد يهدف إلى بناء منصة ذكاء اصطناعي متعددة الوكلاء (Multi-Agent System) تعتمد على لغة Python ومعمارية نظيفة (Clean Architecture).

المشروع لا يُبنى لحل مشكلة واحدة فقط، بل ليكون منصة متكاملة تستطيع تنفيذ المهام البرمجية، وإدارة المشاريع، والبحث، وتحليل البيانات، وإنشاء المحتوى، وإنتاج الصور والفيديو، وإدارة مشاريع التسويق بالعمولة، مع قابلية التوسع المستمرة دون الحاجة إلى إعادة كتابة النظام.

يُعد هذا الملف المرجع الرسمي للمشروع، ويجب أن تتوافق جميع التغييرات البرمجية مع ما هو موثق فيه.

---

# 2. Project Vision

إنشاء منصة احترافية تعمل كمساعد ذكي متعدد الوكلاء، قادر على تنفيذ المهام المعقدة بطريقة منظمة وقابلة للتوسع، مع إمكانية العمل باستخدام النماذج السحابية حاليًا، ثم الانتقال إلى النماذج المحلية مستقبلًا دون تعديل بنية المشروع.

---

# 3. Mission

بناء نظام مرن ومستقر يعتمد على الفصل الكامل بين المسؤوليات، بحيث يمكن إضافة قدرات جديدة دون التأثير على المكونات الموجودة مسبقًا.

---

# 4. Project Goals

## الأهداف قصيرة المدى

- تثبيت نواة المشروع.
- إنشاء نظام أوامر مستقر.
- إدارة الملفات والمشاريع.
- تشغيل البرامج.
- توفير بنية قابلة للاختبار.

## الأهداف متوسطة المدى

- دعم الذاكرة.
- دعم الإضافات.
- دعم أكثر من Agent.
- تحسين تحليل الأوامر.
- دمج النماذج السحابية.

## الأهداف بعيدة المدى

- إنشاء الفيديوهات.
- إنشاء الصور.
- البحث الذكي.
- تحليل المنتجات.
- إنشاء المحتوى الكامل.
- دعم النماذج المحلية.
- الوصول إلى الإصدار v1.0.

---

# 5. Scope

يغطي المشروع المجالات التالية:

- البرمجة.
- إدارة المشاريع.
- إدارة الملفات.
- الذكاء الاصطناعي.
- إنشاء المحتوى.
- البحث.
- تحليل البيانات.
- إنشاء الصور.
- إنشاء الفيديو.
- التسويق بالعمولة.

---

# 6. Core Philosophy

يعتمد المشروع على المبادئ التالية:

- البساطة.
- الاستقرار.
- القابلية للتوسع.
- الفصل بين المسؤوليات.
- سهولة الاختبار.
- سهولة الصيانة.
- قابلية استبدال أي مكون.

---

# 7. Design Principles

يعتمد المشروع على:

- Clean Architecture
- SOLID Principles
- Modular Design
- Dependency Injection
- Service-Oriented Design
- Single Responsibility Principle

---

# 8. System Architecture

```
User
 │
 ▼
CommandParser
 │
 ▼
Task
 │
 ▼
TaskRouter
 │
 ▼
MasterAgent
 │
 ▼
Selected Agent
 │
 ▼
CommandDispatcher
 │
 ▼
Service
 │
 ▼
Result
 │
 ▼
Console
```

---

# 9. Execution Pipeline

يقوم المستخدم بإرسال أمر.

↓

يقوم CommandParser بتحويله إلى Task.

↓

يقوم Router باختيار الوكيل المناسب.

↓

يقوم MasterAgent بإدارة عملية التنفيذ.

↓

يقوم Agent باستقبال المهمة فقط.

↓

يقوم CommandDispatcher بتحليل الأمر.

↓

يقوم Dispatcher باستدعاء Service المناسبة.

↓

تنفذ Service العملية المطلوبة.

↓

ترجع النتيجة إلى MasterAgent.

↓

يعرض MasterAgent النتيجة للمستخدم.

---

# 10. Core Components

يتكون المشروع من الطبقات التالية:

- Core
- Agents
- Services
- Memory
- Plugins
- Configuration
- Database
- Assets
- Logs

---

# 11. Agents Layer

الـ Agents تمثل نقطة الاتصال بين النظام وبين الخدمات.

لا تحتوي على أي منطق تنفيذ.

كل Agent مسؤول عن نوع واحد فقط من المهام.

أمثلة:

- MasterAgent
- CodingAgent
- BrowserAgent
- ImageAgent
- VideoAgent
- MemoryAgent
- VoiceAgent
- ProductAgent

---

# 12. Services Layer

تحتوي جميع منطق التنفيذ الحقيقي.

كل Service مسؤولة عن وظيفة واحدة فقط.

أمثلة:

- FileTools
- TextEditor
- PythonRunner
- ProjectManager
- CodeWriter

أي عملية تنفيذ مستقبلية يجب أن تضاف داخل Services وليس داخل Agents.

---

# 13. Core Layer

تمثل النواة المسؤولة عن تنسيق النظام.

تشمل:

- Router
- CommandParser
- CommandDispatcher
- ServiceContainer
- Result
- Task

لا تقوم النواة بتنفيذ العمليات، وإنما تدير تدفقها.

---

# 14. Memory Layer

تم تنفيذ طبقة الذاكرة والتحقق منها محليًا.

تشمل:

- Session Memory
- Long-term Memory
- Context Memory

الغرض منها حفظ المعلومات اللازمة لتحسين أداء النظام واستمرارية العمل.

---

# 15. Configuration Layer

مسؤولة عن:

- إعدادات المشروع.
- إعدادات النماذج.
- مفاتيح API.
- إعدادات الخدمات.
- إعدادات البيئة.

---

# 16. Logging Layer

تسجل جميع العمليات المهمة داخل المشروع.

تشمل:

- معلومات التشغيل.
- الأخطاء.
- التحذيرات.
- الأداء.
- العمليات المنفذة.

---

# 17. Plugin System

يسمح بإضافة ميزات جديدة دون تعديل النواة.

كل إضافة (Plugin) يجب أن تكون مستقلة ويمكن تفعيلها أو تعطيلها بسهولة.

---

# 18. AI Integration

سيتم دعم أكثر من مزود للنماذج الذكية من خلال واجهة موحدة، بحيث لا تعتمد بقية أجزاء المشروع على مزود معين.

سيكون استبدال المزود أو إضافة مزود جديد ممكنًا دون تعديل بقية المكونات.

---

# 19. Local AI Migration

المرحلة الحالية تعتمد على النماذج السحابية.

عند توفر عتاد مناسب، سيتم استبدال مزود الذكاء الاصطناعي بالنماذج المحلية مع الحفاظ على نفس الواجهات البرمجية، بحيث لا تتأثر بقية طبقات النظام.

---

# 20. Video Creation Pipeline

الهدف النهائي لمسار إنشاء الفيديو هو:

1. استقبال الفكرة.
2. تحليلها.
3. البحث عن المعلومات.
4. كتابة السيناريو.
5. إنشاء المشاهد.
6. إنشاء الصور أو الوسائط.
7. تركيب الفيديو.
8. إضافة الصوت.
9. إضافة الترجمة.
10. تصدير الفيديو النهائي.

---

# 21. Affiliate Workflow

يدعم المشروع مستقبلًا دورة عمل كاملة للتسويق بالعمولة، تشمل:

- اختيار المجال.
- البحث عن المنتجات.
- تحليل المنافسين.
- إنشاء المقالات.
- إنشاء الفيديوهات.
- إنشاء الصور.
- إدارة الروابط.
- تحسين المحتوى.
- متابعة الأداء.

---

# 22. Development Roadmap

## v0.4

Core Stabilization

- تثبيت النواة.
- تثبيت الخدمات.
- تثبيت الوكلاء.
- اختبار النظام.

## v0.5

Memory System

## v0.6

Plugin System

## v0.7

Cloud AI Foundation

The v0.7 foundation consists of the approved `CloudAIProvider`
abstraction and the approved, implemented, tested, and integrated
`CloudAIService`.

v0.7 Component #2 is approved:

```text
OpenAI Cloud AI Provider
```

Canonical path:

```text
providers/openai_provider.py
```

Public contract:

```python
OpenAIProvider()
generate(prompt, model=None, parameters=None) -> Result
```

`OpenAIProvider` owns OpenAI-specific credentials, SDK configuration,
API execution, response translation, and provider failure handling.

`CloudAIService` remains responsible for provider registration, lookup,
selection, invocation, and provider-neutral `Result` handling. Its
generic lookup contract remains:

```python
get_provider(name) -> Result
```

Component #2 does not modify `CloudAIProvider`, `CloudAIService`,
`ServiceContainer`, or the provider-neutral architecture.

Component #2 does not include Gemini, Anthropic, local providers,
factory layers, streaming, multimodal behavior, tool calling, or
cross-provider orchestration.

Required tests must cover construction, generation, Result behavior,
failure behavior, secret redaction, registration, lookup, selection,
and invocation.

```text
Component #2 Contract: Approved
Component #2 Implementation: Complete and Tested
```

### v0.7 Definition of Done

v0.7 is complete when the repository demonstrates all of the following:

- The provider-neutral `CloudAIProvider` contract is available.
- `CloudAIService` registers, looks up, selects, invokes, and normalizes
  providers through `Result`.
- The OpenAI provider implements the generic contract behind its own
  provider boundary.
- Success, invalid-input, failure, secret-redaction, integration, and
  contract-compatibility tests pass using deterministic test doubles.
- Core, Agents, Memory, Plugins, and ServiceContainer boundaries remain
  intact.
- No provider-specific feature is required by consumers.

## v0.8

Intelligence and Planning

The v0.8 capability families are recorded at roadmap level only. Each
family requires an independently approved contract before implementation:

- Research Engine
- Analysis and Reasoning Layer
- Coding Intelligence
- Content Intelligence
- Workflow and Planning Engine
- Digital Asset Registry
- Content Persona
- Policy and Shariah Compliance Firewall
- Product and Affiliate Intelligence
- Affiliate Identity and Tracking abstraction

The preferred dependency direction is research, analysis, planning and
workflow, content intelligence, coding intelligence, digital assets,
product and affiliate intelligence, policy, persona, and tracking. This
ordering does not authorize implementation without a component contract.

Product and affiliate workflows must remain extensible and evidence-based;
product selection must not reduce to a single sales metric. Affiliate
identity and tracking are reusable entities or configurations rather than
embedded ad hoc code.

The Policy and Shariah Compliance Firewall is an isolated policy boundary,
not provider logic. Its future decision vocabulary must distinguish
`ALLOWED`, `BLOCKED`, and `REVIEW_REQUIRED`; borderline cases must remain
representable as review cases, and blocked assets must never be silently
published.

## v0.9

Production and Computer Operations

The v0.9 capability families are:

- Video Production Engine
- Audio Engine
- Media Pipeline
- Browser Agent
- Computer Agent
- Publishing Gateway
- Performance Monitoring
- Diagnosis Engine
- Experiment and Optimization Engine

Video is a temporal production capability, not a slideshow pipeline. The
future production flow is semantic understanding, temporal plan, stage
graph, scene graph, motion, camera, audio, asset generation or acquisition,
composition, continuity validation, rendering, and quality validation.
Image generation is an optional supporting media capability.

Publishing uses replaceable platform adapters. Monitoring operates on
digital assets and records observations, metrics, evidence, hypotheses,
diagnoses, actions, and results.

### v0.9 Definition of Done

v0.9 is complete when the nine documented production and computer
capability families have canonical implementations, provider/tool or
platform boundaries where applicable, focused deterministic tests,
regression validation, successful compilation, and synchronized contract,
structure, and state documentation. Computer control must remain
permission-gated and must not select a real operating-system runtime in
the core architecture. No external credentials are required for the
local validation gate.

## v1.0

Integrated Autonomous Digital Operations Platform

The target end-to-end workflow is:

```text
Goal -> Planning -> Research -> Analysis -> Decision -> Creation
-> Coding / Video / Media -> Browser / Computer execution
-> Publishing -> Monitoring -> Diagnosis -> Safe Fix / Human Action
-> Experiment -> Measurement -> Memory / Learning -> Report
```

The v1.0 integration must preserve the existing Core, Agents, Services,
Memory, Plugin, and provider-neutral Cloud AI boundaries. It is not
complete until the repository demonstrates the documented integrated
workflow through implementation and validation.

### Permanent Language Policy

Arabic is the control and interaction language for user commands,
explanations, reports, diagnostics, and project-owner communication.
English is the default language for foreign-facing generated output,
including videos, scripts, narration, captions, websites, marketing copy,
and public content. Control language and output language are separate
concerns.

### v1.0 Integration Validation Scope

The local validation suite exercises goal planning, research and analysis,
content-to-temporal-video/audio composition, digital-asset monitoring and
evidence-preserving diagnosis, experiment measurement and learning,
product policy decisions, and fail-closed publishing. These tests use
deterministic injected fakes; external credentials and real browser or
operating-system runtimes remain integration-ready rather than required
by the local gate.

Service-only capabilities may be exposed to the main task route through a
minimal CapabilityAgent orchestration bridge. The bridge must only select
an existing Service method and pass structured task payloads; it must not
duplicate business logic or create provider/tool implementations. Dedicated
Agents remain preferred for multi-step capability workflows.

The older v0.3/v0.4 roadmap and architecture wording in `docs/` and in
historical sections of the project context are retained as history. This
master blueprint supersedes them for current implementation decisions.

### v0.8 Definition of Done

v0.8 is complete when the repository demonstrates the documented
Research, Analysis, Workflow, Content, Digital Asset, Product/Affiliate,
Policy, Persona, and Affiliate Identity foundations through approved
contracts, focused tests, regression validation, and synchronized
documentation. These foundations must preserve facts versus hypotheses,
keep policy decisions isolated, protect secrets, and avoid provider-
specific coupling.

---

# 23. Architectural Rules

- لا يجوز وضع منطق التنفيذ داخل Agents.
- جميع العمليات تنفذ داخل Services.
- Core مسؤول عن التنسيق فقط.
- كل طبقة مستقلة عن الأخرى.
- يمنع الربط المباشر بين الطبقات بطريقة تكسر المعمارية.
- يمنع إنشاء تبعيات دائرية.
- أي توسعة يجب أن تحافظ على التصميم الحالي.

---

# 24. Coding Standards

- الالتزام بمعايير Python الحديثة.
- أسماء واضحة للملفات والفئات والدوال.
- كتابة توثيق مناسب عند الحاجة.
- الفصل بين المسؤوليات.
- تجنب تكرار الكود.
- كتابة كود قابل للاختبار والصيانة.
- الحفاظ على التوافق مع بنية المشروع.

---

# 25. Future Vision

الهدف النهائي هو أن يصبح AllAffiliate_Agent منصة ذكاء اصطناعي متكاملة تستطيع:

- إدارة المشاريع البرمجية.
- كتابة وتشغيل الأكواد.
- إدارة الملفات.
- البحث الذكي.
- تحليل البيانات.
- إنشاء المقالات.
- إنشاء الصور.
- إنشاء الفيديوهات.
- إدارة مشاريع التسويق بالعمولة.
- دعم النماذج السحابية والمحلية.
- التوسع المستقبلي دون الحاجة إلى إعادة تصميم النظام.

---

# Document Policy

يُعد هذا الملف المرجع الرسمي لمعمارية المشروع.

أي تغيير معماري يجب أن يُراجع ويُحدّث في هذا الملف أولًا قبل تعديل الكود.

أي قرار يخالف ما ورد في هذا الملف يُعتبر تغييرًا معماريًا ويجب اعتماده رسميًا قبل تنفيذه.

---

**End of Document**
