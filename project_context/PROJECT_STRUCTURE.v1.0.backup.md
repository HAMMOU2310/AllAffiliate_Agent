# PROJECT_STRUCTURE.md

# AllAffiliate_Agent

**Project Structure Document**

**Version:** v1.0

**Architecture:** Clean Architecture — v1.0 local integration validated

**Design Pattern:** Multi-Agent System

**Document Version:** 1.0

---

# Table of Contents

1. Document Purpose
2. Root Directory
3. Folder Hierarchy
4. Project Context Layer
5. Core Layer
6. Agents Layer
7. Services Layer
8. Memory Layer
9. Configuration Layer
10. Database Layer
11. Assets Layer
12. Documentation Layer
13. Logs Layer
14. Plugins Layer
15. Cloud AI Provider Implementations
16. Testing Layer
17. Project Files
18. Dependency Flow
19. Execution Flow
20. File Naming Rules
21. Folder Rules
22. Expansion Rules

---

# 1. Document Purpose

يشرح هذا الملف الهيكل الرسمي للمشروع.

يجب أن يتوافق أي ملف جديد مع هذا الهيكل.

أي تعديل على البنية يجب تحديثه هنا أولاً.

---

# 2. Root Directory

```
AllAffiliate_Agent/
│
├── project_context/
├── agents/
├── assets/
├── config/
├── core/
├── database/
├── docs/
├── logs/
├── memory/
├── plugins/
├── services/
├── providers/
├── tests/
│
├── assistant.py
├── requirements.txt
├── README.md
├── PROJECT_BLUEPRINT.md
├── PROJECT_STATE.md
├── PROJECT_STRUCTURE.md
├── DEVELOPMENT_RULES.md
└── CHANGELOG.md
```

---

# 3. Folder Hierarchy

| Folder | Responsibility |
|----------|---------------|
| project_context | حالة المشروع والتسليم والتوثيق المرجعي |
| agents | جميع الوكلاء |
| core | النواة |
| services | جميع منطق التنفيذ |
| providers | تطبيقات مزودي Cloud AI المستقلة |
| config | الإعدادات |
| database | قواعد البيانات |
| assets | الوسائط |
| memory | أنظمة الذاكرة |
| plugins | الإضافات |
| docs | التوثيق |
| logs | السجلات |
| tests | الاختبارات |

---

# 4. Project Context Layer

```
project_context/
│
├── PROJECT_HANDOFF.md
├── PROJECT_STATE.md
├── PROJECT_STRUCTURE.md
├── PROJECT_BLUEPRINT.md
├── DEVELOPMENT_RULES.md
├── API_CONTRACTS.md
└── CHANGELOG.md
```

الغرض

مركز الحالة والتسليم الرسمي للمشروع بين جلسات التطوير.

- لا يحتوي على كود تنفيذي.
- يحتوي على نسخة مرجعية واحدة لكل وثيقة حالة/تسليم رسمية.
- تبدأ أي جلسة تطوير جديدة بقراءة PROJECT_HANDOFF.md ثم PROJECT_STATE.md.
- لا توجد نسخ تشغيلية من ملفات Python داخله.

---

# 5. Core Layer

```
core/
│
├── __init__.py
├── base_agent.py
├── command_dispatcher.py
├── command_parser.py
├── result.py
├── router.py
├── service_container.py
├── task.py
└── utils.py
```

---

## base_agent.py

الفئة الأساسية لجميع الوكلاء.

يجب أن ترث منها جميع الـ Agents.

---

## command_parser.py

تحويل أمر المستخدم إلى Task.

لا ينفذ أي عملية.

---

## command_dispatcher.py

تحليل الأوامر.

استدعاء الخدمة المناسبة.

لا يحتوي منطق تنفيذ.

---

## router.py

اختيار الوكيل المناسب.

يعتمد على Task Type.

---

## service_container.py

مسؤول عن تسجيل الخدمات.

يوفر Dependency Injection.

---

## task.py

يمثل المهمة.

يحتوي بيانات التنفيذ.

---

## result.py

يوحد شكل النتائج.

نجاح.

فشل.

رسائل.

بيانات.

---

# 6. Agents Layer

```
agents/
│
├── master_agent.py
├── coding_agent.py
├── browser_agent.py
├── image_agent.py
├── memory_agent.py
├── product_agent.py
├── video_agent.py
└── voice_agent.py
```

---

## MasterAgent

منسق النظام.

يتحكم في سير التنفيذ.

---

## CodingAgent

وكيل البرمجة.

لا ينفذ.

يحول المهمة إلى Dispatcher.

---

## BrowserAgent

مسؤول عن البحث.

---

## ImageAgent

مسؤول عن الصور.

---

## VideoAgent

مسؤول عن الفيديو.

---

## MemoryAgent

مسؤول عن الذاكرة.

---

## ProductAgent

تحليل المنتجات.

---

## VoiceAgent

التعامل مع الصوت.

---

# 7. Services Layer

```
services/
│
├── code_writer.py
├── cloud_ai_service.py
├── file_tools.py
├── project_manager.py
├── python_runner.py
└── text_editor.py
```

---

## CodeWriter

إنشاء الأكواد.

---

## FileTools

إدارة الملفات.

---

## TextEditor

الكتابة.

القراءة.

الإضافة.

---

## PythonRunner

تشغيل ملفات Python.

---

## ProjectManager

إنشاء المشاريع.

عرض المشاريع.

إدارة المشاريع.

---

# 8. Memory Layer

```
memory/
│
├── session/
├── long_term/
└── cache/
```

---

الغرض

حفظ السياق.

إدارة الذاكرة.

تحسين أداء النظام.

---

# 9. Configuration Layer

```
config/
│
├── settings.py
├── models.py
├── prompts.py
└── paths.py
```

---

الغرض

إعدادات المشروع.

إعدادات النماذج.

إعدادات المسارات.

---

# 10. Database Layer

```
database/
│
├── sqlite/
├── json/
└── cache/
```

---

الغرض

حفظ البيانات.

الإعدادات.

المشاريع.

الذاكرة.

---

# 11. Assets Layer

```
assets/
│
├── images/
├── videos/
├── audio/
├── icons/
└── temp/
```

---

الغرض

جميع الملفات الوسائطية.

---

# 12. Documentation Layer

```
docs/
│
├── architecture.md
├── api.md
├── roadmap.md
└── tutorials.md
```

---

الغرض

جميع الوثائق الإضافية.

---

# 13. Logs Layer

```
logs/
│
├── system.log
├── errors.log
├── debug.log
└── execution.log
```

---

الغرض

تسجيل الأحداث.

تسجيل الأخطاء.

تحليل الأداء.

---

# 14. Plugins Layer

```
plugins/
│
├── plugin_loader.py
├── plugin_manager.py
├── plugin_registry.py
├── plugin_lifecycle.py
└── installed/
```

---

الغرض

إضافة ميزات جديدة.

تحميل الإضافات.

إدارة الإضافات.

تسجيل الإضافات في السجل المركزي.

إدارة حالة Plugin lifecycle الأساسية (enable/disable).

---

# 15. Cloud AI Provider Implementations

```text
providers/
└── openai_provider.py
```

`providers/openai_provider.py` is the canonical path for v0.7 Component #2:

```text
OpenAI Cloud AI Provider
```

Public contract:

```python
OpenAIProvider()
generate(prompt, model=None, parameters=None) -> Result
```

The provider owns OpenAI-specific credentials, SDK configuration,
OpenAI API execution, response translation, and provider failure
translation.

`CloudAIService` remains responsible for provider registration, lookup
through `get_provider(name)`, selection, and invocation.

Provider implementations must not modify the generic `CloudAIProvider`
contract or add provider-specific behavior to `CloudAIService`.

Completing an already-approved generic `CloudAIService` contract, including
`get_provider(name) -> Result`, is service-contract completion and is not
provider-specific behavior.

Component #2 tests cover construction, generation, failures, secret
redaction, registration, lookup, selection, and invocation. Component #2
implementation and testing are complete. The current Component #2 test file
is `workspace/test_openai_provider.py`; this records the existing location
without changing the documented folder responsibilities.

---

# 16. Research Engine

```text
services/
└── research_service.py
```

`services/research_service.py` is the canonical path for v0.8 Research
Engine Component #1. It remains provider-neutral and coordinates injected
research sources through `Result`.

Public contract:

```python
ResearchService(sources=None)
research(query, scope=None) -> Result
```

The component normalizes evidence records and preserves the distinction
between observed `FACT` records and unsupported or malformed data. It does
not implement browser automation, analysis, ranking, policy, publishing,
or provider-specific behavior.

The focused component test is:

```text
workspace/test_research_service.py
```

---

# 17. Analysis and Reasoning Layer

```text
services/
├── research_service.py
├── analysis_service.py
├── workflow_service.py
├── content_service.py
├── digital_asset_service.py
├── product_service.py
├── policy_service.py
├── persona_service.py
└── affiliate_identity_service.py
```

`services/analysis_service.py` is the canonical path for v0.8 Analysis and
Reasoning Layer Component #2. It validates and normalizes classified
evidence while preserving the distinction between facts, hypotheses,
recommendations, actions, and results.

Public contract:

```python
AnalysisService(analyzer=None)
analyze(evidence, question=None) -> Result
```

The service remains provider-neutral and does not implement policy,
ranking, publishing, or browser behavior.

The focused component test is:

```text
workspace/test_analysis_service.py
```

---

# 18. Workflow and Planning Engine

`services/workflow_service.py` is the canonical path for v0.8 Workflow and
Planning Engine Component #3. It validates ordered planner output without
executing steps.

Public contract:

```python
WorkflowService(planner=None)
plan(goal, context=None) -> Result
```

The focused component test is:

```text
workspace/test_workflow_service.py
```

---

# 19. Content Intelligence

`services/content_service.py` is the canonical path for v0.8 Content
Intelligence Component #4. It validates structured drafts and preserves
claims as explicit data for later policy review.

Public contract:

```python
ContentService(generator=None)
create(brief, persona=None, format=None) -> Result
```

The focused component test is:

```text
workspace/test_content_service.py
```

---

# 20. Digital Asset Registry

`services/digital_asset_service.py` is the canonical path for v0.8 Digital
Asset Registry Component #5. It stores isolated reusable asset records for
future monitoring, publishing, affiliate, and diagnosis workflows.

Public contract:

```python
DigitalAssetService()
register(asset_type, name, metadata=None) -> Result
get(asset_id) -> Result
list_assets(asset_type=None) -> Result
```

The focused component test is:

```text
workspace/test_digital_asset_service.py
```

---

# 21. Product and Affiliate Intelligence

`services/product_service.py` is the canonical path for v0.8 Product and
Affiliate Intelligence Component #6. It ranks candidates using multiple
signals and records signal provenance without making policy decisions.

Public contract:

```python
ProductService()
rank(candidates) -> Result
```

The focused component test is:

```text
workspace/test_product_service.py
```

---

# 22. Policy and Shariah Compliance Firewall

`services/policy_service.py` is the canonical path for v0.8 Policy and
Shariah Compliance Firewall Component #7. It isolates policy outcomes from
providers and represents `ALLOWED`, `BLOCKED`, and `REVIEW_REQUIRED`.

Public contract:

```python
PolicyService(evaluator=None)
evaluate(asset) -> Result
```

The focused component test is:

```text
workspace/test_policy_service.py
```

---

# 23. Content Persona

`services/persona_service.py` is the canonical path for v0.8 Content
Persona Component #8. It validates reusable profiles without hard-coding a
channel identity into content generation.

Public contract:

```python
PersonaService()
validate(persona) -> Result
```

The focused component test is:

```text
workspace/test_persona_service.py
```

---

# 24. Affiliate Identity and Tracking

`services/affiliate_identity_service.py` is the canonical path for v0.8
Affiliate Identity and Tracking Component #9. It stores reusable,
secret-safe identity configuration separate from content and platform
adapters.

Public contract:

```python
AffiliateIdentityService()
create(network, account, campaign=None, parameters=None) -> Result
get(identity_id) -> Result
```

The focused component test is:

```text
workspace/test_affiliate_identity_service.py
```

---

# 25. Temporal Video Production Engine

`services/video_production_service.py` is the canonical path for v0.9
Temporal Video Production Engine Component #1. It validates timeline,
stage, scene, motion, camera, audio, and continuity plans.

Public contract:

```python
VideoProductionService(interpreter=None)
create_plan(instruction) -> Result
```

The focused component test is:

```text
workspace/test_video_production_service.py
```

---

# 26. Audio Engine

`services/audio_service.py` is the canonical path for v0.9 Audio Engine
Component #2. It validates separable timed audio tracks for production
workflows.

Public contract:

```python
AudioService(interpreter=None)
create_plan(instruction) -> Result
```

The focused component test is:

```text
workspace/test_audio_service.py
```

---

# 27. Media Pipeline

`services/media_pipeline_service.py` is the canonical path for v0.9 Media
Pipeline Component #3. It validates composition manifests from separate
video and audio plans without rendering media.

Public contract:

```python
MediaPipelineService()
compose(video_plan, audio_plan) -> Result
```

The focused component test is:

```text
workspace/test_media_pipeline_service.py
```

---

# 28. Publishing Gateway

`services/publishing_service.py` is the canonical path for v0.9 Publishing
Gateway Component #4. It uses replaceable platform adapters and fails
closed for blocked policy decisions.

Public contract:

```python
PublishingService(adapter=None)
publish(asset, destination) -> Result
```

The focused component test is:

```text
workspace/test_publishing_service.py
```

---

# 29. Performance Monitoring

`services/performance_monitoring_service.py` is the canonical path for
v0.9 Performance Monitoring Component #5. It records timestamped numeric
observations against digital asset IDs without diagnosing causes.

Public contract:

```python
PerformanceMonitoringService()
record(asset_id, metrics) -> Result
list_observations(asset_id=None) -> Result
```

The focused component test is:

```text
workspace/test_performance_monitoring_service.py
```

---

# 30. Diagnosis Engine

`services/diagnosis_service.py` is the canonical path for v0.9 Diagnosis
Engine Component #6. It preserves facts, hypotheses, and recommendations.

```python
DiagnosisService(analyzer=None)
diagnose(asset_id, observations) -> Result
```

Focused test:

```text
workspace/test_diagnosis_service.py
```

---

# 31. Experiment and Optimization Engine

`services/experiment_service.py` is the canonical path for v0.9 Experiment
and Optimization Engine Component #7. It records generic experiments and
measurements without applying external changes.

```python
ExperimentService()
create(asset_id, hypothesis, action) -> Result
record_measurement(experiment_id, metrics) -> Result
complete(experiment_id, result, learning=None) -> Result
get(experiment_id) -> Result
```

Focused test:

```text
workspace/test_experiment_service.py
```

---

# 32. Browser Automation

```text
agents/browser_agent.py
services/browser_service.py
```

BrowserAgent delegates to BrowserService, and BrowserService delegates to
an injected BrowserAdapter. No browser engine is selected by the core
architecture.

Focused test:

```text
workspace/test_browser_agent.py
```

---

# 33. Computer Automation

```text
agents/computer_agent.py
services/computer_service.py
```

ComputerAgent delegates to a permission-gated ComputerService and a
replaceable ComputerAdapter. No real OS runtime is selected by the core.

Focused test:

```text
workspace/test_computer_agent.py
```

---

# 34. Service Capability Orchestration

```text
agents/capability_agent.py
```

`CapabilityAgent` is the canonical minimal bridge for service-only
capabilities that must be reachable from `TaskRouter`. It delegates one
documented task type to one existing Service method and keeps all business
logic, provider behavior, and adapter execution in the Service layer.

Its focused tests are maintained with the v1.0 integration validation.

---

# 35. v1.0 Integration Validation

```text
workspace/test_v1_integration.py
```

The v1.0 validation suite composes existing provider-neutral services
through deterministic local fakes. It validates planning, research,
analysis, content, temporal video, audio, media composition, asset
monitoring, diagnosis, experimentation, policy, and fail-closed
publishing without external runtimes or credentials.

---

# 36. Testing Layer

```
tests/
│
├── test_core.py
├── test_agents.py
├── test_services.py
└── test_memory.py
```

---

الغرض

اختبار المشروع بالكامل.

---

# 17. Project Files

| File | Responsibility |
|------|----------------|
| assistant.py | نقطة تشغيل المشروع |
| README.md | تعريف المشروع |
| requirements.txt | التبعيات |
| PROJECT_BLUEPRINT.md | المرجع المعماري |
| PROJECT_STATE.md | حالة المشروع |
| PROJECT_STRUCTURE.md | هيكل المشروع |
| DEVELOPMENT_RULES.md | قواعد التطوير |
| CHANGELOG.md | سجل الإصدارات |

---

# 18. Dependency Flow

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
Router
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
Services
    │
    ▼
Result
```

---

# 19. Execution Flow

1. المستخدم يرسل الأمر.

2. CommandParser يحوله إلى Task.

3. Router يحدد الوكيل.

4. MasterAgent يبدأ التنفيذ.

5. Agent يستقبل المهمة.

6. CommandDispatcher يحلل الأمر.

7. Service تنفذ العملية.

8. Result يرجع النتيجة.

9. MasterAgent يعرض النتيجة.

---

# 20. File Naming Rules

- جميع الملفات تستخدم snake_case.
- أسماء الفئات تستخدم PascalCase.
- أسماء الدوال تستخدم snake_case.
- أسماء المتغيرات واضحة.
- يمنع استخدام أسماء مبهمة.

---

# 21. Folder Rules

- كل مجلد مسؤول عن مجال واحد فقط.
- يمنع وضع ملفات عشوائية في الجذر.
- يمنع تكرار الوظائف بين المجلدات.
- يمنع إنشاء مجلد جديد دون سبب واضح.
- كل ملف يجب أن يكون له مسؤولية واحدة.

---

# 22. Expansion Rules

أي ميزة جديدة يجب أن:

- تحافظ على المعمارية.
- لا تكسر التبعيات.
- لا تضيف منطق تنفيذ داخل Agents.
- تعتمد على Services.
- تستخدم ServiceContainer عند الحاجة.
- توثق في PROJECT_STRUCTURE.md إذا أضافت ملفات أو مجلدات جديدة.

---

# Official Folder Responsibilities Summary

| Layer | Responsibility |
|--------|----------------|
| Core | تنسيق النظام |
| Agents | استقبال المهام |
| Services | تنفيذ العمليات |
| Memory | إدارة الذاكرة |
| Config | إعدادات المشروع |
| Database | تخزين البيانات |
| Assets | الوسائط |
| Plugins | التوسعة |
| Docs | التوثيق |
| Logs | السجلات |
| Tests | الاختبارات |

---

# End of Document
