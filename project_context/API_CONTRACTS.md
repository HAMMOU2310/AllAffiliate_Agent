# API_CONTRACTS.md

# AllAffiliate_Agent

**API Contracts**

**Version:** v1.0

**Status:** Synchronized contracts through v1.0 local validation

**Document Version:** 1.0

---

# Purpose

This document preserves the approved public contracts from v0.7 through
the v1.0 local integration checkpoint. Historical v0.4 wording below is
not a current roadmap and is superseded by `PROJECT_BLUEPRINT.md`.

يُعد هذا الملف المرجع الرسمي لجميع العقود البرمجية (Contracts) داخل المشروع.

الغرض منه هو توثيق الواجهات العامة (Public Interfaces) بين جميع الطبقات، بحيث يستطيع أي مطور أو نموذج ذكاء اصطناعي تطوير أي ملف دون الحاجة إلى قراءة المشروع بالكامل.

هذا الملف لا يشرح منطق التنفيذ، وإنما يحدد فقط:

- أسماء الفئات (Classes)
- أسماء الدوال (Methods)
- المدخلات (Inputs)
- المخرجات (Outputs)
- العلاقات بين المكونات

---

# Core Contracts

---

## Result

الموقع:

```
core/result.py
```

المسؤولية:

العقد الموحد لإرجاع نتائج جميع العمليات.

الواجهة:

```python
Result.ok(...)
Result.fail(...)
```

الخصائص:

```python
success
message
data
errors
metadata
timestamp
```

---

## Task

الموقع:

```
core/task.py
```

المسؤولية:

تمثيل المهمة الناتجة عن CommandParser.

الخصائص:

```python
task_type
command
```

---

## CommandParser

الموقع:

```
core/command_parser.py
```

المسؤولية:

تحويل أمر المستخدم إلى Task.

الواجهة:

```python
parse(command: str) -> Task
```

لا ينفذ أي أوامر.

---

## TaskRouter

الموقع:

```
core/router.py
```

المسؤولية:

اختيار الـ Agent المناسب اعتمادًا على Task.

الواجهة:

```python
route(task)
```

لا يحتوي أي منطق تنفيذ.

---

## CommandDispatcher

الموقع:

```
core/command_dispatcher.py
```

المسؤولية:

تحليل الأمر النصي واستدعاء الخدمة المناسبة.

الواجهة:

```python
dispatch(command: str) -> Result
```

لا ينفذ أي عملية بنفسه.

يعتمد على:

```
CodeWriter
FileTools
TextEditor
PythonRunner
ProjectManager
```

---

## ServiceContainer

الموقع:

```
core/service_container.py
```

المسؤولية:

إدارة جميع الخدمات (Dependency Injection).

الواجهات:

```python
register(name, service)
```

```python
get(name)
```

جميع الخدمات تُسجل داخله.

---

# Agent Contracts

---

## BaseAgent

الموقع:

```
core/base_agent.py
```

المسؤولية:

العقد الأساسي لجميع الوكلاء.

الواجهة:

```python
execute(task)
```

---

## MasterAgent

الموقع:

```
agents/master_agent.py
```

المسؤولية:

تنسيق دورة التنفيذ الكاملة.

لا ينفذ أي Business Logic.

يتعامل مع:

```
CommandParser

TaskRouter

Result
```

المسؤوليات:

- استقبال أوامر المستخدم
- إنشاء Task
- إرسال المهمة إلى Router
- استلام النتيجة
- عرض النتيجة

---

## CodingAgent

الموقع:

```
agents/coding_agent.py
```

المسؤولية:

استقبال مهمة برمجية فقط.

الواجهة:

```python
execute(task)
```

يقوم فقط باستدعاء:

```python
dispatcher.dispatch(task.command)
```

ولا يحتوي أي if خاص بالأوامر.

---

## BrowserAgent

الموقع:

```
agents/browser_agent.py
```

الحالة:

Implemented and locally validated

---

## ImageAgent

الموقع:

```
agents/image_agent.py
```

الحالة:

Future

---

## VideoAgent

الموقع:

```
agents/video_agent.py
```

الحالة:

Future

---

## VoiceAgent

الموقع:

```
agents/voice_agent.py
```

الحالة:

Future

---

## MemoryAgent

الموقع:

```
agents/memory_agent.py
```

الحالة:

Implemented and locally validated

---

# Service Contracts

---

## CodeWriter

الموقع:

```
services/code_writer.py
```

المسؤولية:

إنشاء الملفات.

الواجهات:

```python
create_file(path, content="")
```

```python
write_file(path, content)
```

```python
append_file(path, content)
```

---

## FileTools

الموقع:

```
services/file_tools.py
```

الواجهات:

```python
read_file(path)
```

```python
delete_file(path)
```

```python
list_files(path="workspace")
```

---

## TextEditor

الموقع:

```
services/text_editor.py
```

الواجهات:

```python
write(path, content)
```

```python
append(path, content)
```

---

## PythonRunner

الموقع:

```
services/python_runner.py
```

الواجهة:

```python
run_file(path)
```

---

## ProjectManager

الموقع:

```
services/project_manager.py
```

الواجهات:

```python
create_project(name)
```

```python
list_projects()
```

```python
exists(name)
```

---


# Cloud AI Contracts

---

## CloudAIProvider

الموقع:

```
مزود/تنفيذ مستقل خارج نطاق العقد الحالي
```

المسؤولية:

واجهة مجردة لمزود Cloud AI. لا يحدد هذا العقد مزودًا سحابيًا بعينه.

الواجهة:

```python
generate(prompt, model=None, parameters=None) -> Result
```

قواعد العقد:

- `CloudAIProvider` abstraction/interface فقط، وليس تنفيذًا لمزود محدد.
- تفاصيل الاعتمادات وSecrets وإدارة مفاتيح API خارج نطاق هذا العقد.
- Retry وStreaming وProvider-specific configuration خارج نطاق هذا العقد.
- أي تنفيذ لمزود محدد يحتاج عقدًا منفصلًا ومعتمدًا قبل إضافته للمشروع.

---

## CloudAIService

الموقع:

```
services/cloud_ai_service.py
```

المسؤولية:

خدمة موحدة للتعامل مع Cloud AI عبر `CloudAIProvider` abstraction دون ربط العقد بمزود سحابي محدد.

الواجهة العامة:

```python
register_provider(name, provider) -> Result
get_provider(name) -> Result
remove_provider(name) -> Result
list_providers() -> Result
generate(prompt, provider=None, model=None, parameters=None) -> Result
```

قواعد التكامل:

- تسجل الخدمة داخل `ServiceContainer`.
- تعتمد الخدمة على `CloudAIProvider` abstraction بدل الاعتماد على Provider محدد.
- جميع النتائج تعاد كـ `Result`.
- لا يحدد هذا العقد مزودًا سحابيًا بعينه.
- Provider-specific credentials, secrets, retry, streaming, transport configuration, and provider SDK details ليست جزءًا من هذا العقد.

---

# v0.7 Cloud AI Scope

الجزء المعتمد من v0.7 في هذا الملف هو `CloudAIProvider` abstraction و`CloudAIService` contract وOpenAI Cloud AI Provider contract.

لا يعتمد هذا الملف أي مكوّن Provider-specific آخر مثل Anthropic أو Gemini، ولا يعتمد ملفات credentials أو ai_config كعقود عامة مستقلة.

أي مكوّن v0.7 تالٍ يجب أن تكون هويته ومساره ومسؤوليته وواجهته العامة محددة في هذا الملف قبل تنفيذ ملف Python الخاص به.

---

# v0.7 Component #2 — OpenAI Cloud AI Provider

## Component Identity

```text
Component: OpenAI Cloud AI Provider
Version: v0.7
Component Number: #2
Status: Implemented and Tested
```

## Canonical Path

```text
providers/openai_provider.py
```

This is the sole approved implementation path for Component #2.

## Responsibility

`OpenAIProvider` adapts the OpenAI cloud API to the existing
`CloudAIProvider` abstraction.

The provider is responsible for:

- OpenAI-specific API execution.
- OpenAI-specific SDK usage.
- Provider-owned credential resolution.
- Provider-owned request and response translation.
- Conversion of OpenAI failures into `Result.fail(...)`.

The provider must not modify Core, Agents, Memory, Routing,
`CloudAIService`, or `ServiceContainer`.

## Construction and Configuration Contract

```python
OpenAIProvider() -> OpenAIProvider
```

The constructor exposes no OpenAI-specific public configuration fields.

Provider-owned configuration includes credentials, OpenAI SDK client
configuration, and OpenAI-specific API behavior.

OpenAI credentials, SDK objects, endpoints, account identifiers, retry
settings, transport settings, streaming settings, and tool-calling
settings must remain inside the provider boundary.

These details must not be added to `CloudAIService`, the generic
`CloudAIProvider` contract, or the generic `CloudAIService` constructor.

## Public Generation Contract

```python
generate(
    prompt: str,
    model: str | None = None,
    parameters: dict | None = None,
) -> Result
```

This is the existing generic `CloudAIProvider` contract. Component #2
must implement it without expanding or changing the generic contract.

## Result Return Contract

Every generation operation returns `Result`.

- Successful output is returned through `Result.data`.
- Provider-neutral messages may be returned through `Result.message`.
- Provider-neutral metadata may be returned through `Result.metadata`.
- Failures are returned through `Result.fail(...)`.
- Credentials and secrets must not appear in messages, errors, or metadata.

## CloudAIService Relationship

The existing generic `CloudAIService` contract remains unchanged:

```python
register_provider(name, provider) -> Result
get_provider(name) -> Result
remove_provider(name) -> Result
list_providers() -> Result
generate(prompt, provider=None, model=None, parameters=None) -> Result
```

`CloudAIService` owns:

- Provider registration.
- Provider lookup through `get_provider(name) -> Result`.
- Provider selection and default-provider behavior.
- Provider invocation.
- Provider-neutral `Result` validation and normalization.

`OpenAIProvider` does not register, select, or invoke providers.

Completion of the already-approved generic `CloudAIService` contract,
including `get_provider(name) -> Result`, remains the responsibility of
`CloudAIService` and is not provider-specific behavior.

## Dependency Relationship

```text
CloudAIService
    ↓
CloudAIProvider
    ↓
OpenAIProvider
    ↓
OpenAI SDK / OpenAI Cloud API
```

Direct provider dependencies are limited to:

- `Result` from `core.result`.
- `CloudAIProvider` from `services.cloud_ai_service`.
- The OpenAI SDK and OpenAI cloud API.
- A provider-owned credential source.

The provider must not depend on Agents, Routing, Memory, or provider
selection logic.

## Failure Behavior

`OpenAIProvider` must return `Result.fail(...)` for missing credentials,
invalid provider configuration, OpenAI SDK failures, API failures, and
invalid provider responses.

Unexpected provider failures must not expose secrets.

`CloudAIService` remains responsible for service-level handling of
provider invocation exceptions, invalid provider return values, provider
lookup failures, and provider selection failures.

## Required Tests

Component #2 tests cover:

- `OpenAIProvider()` construction.
- Successful generation returning `Result.ok(...)`.
- Model forwarding.
- Parameter forwarding.
- Invalid prompt behavior.
- Missing or invalid credential behavior.
- OpenAI API and SDK failure conversion.
- Secret redaction from errors and metadata.
- Registration through `CloudAIService`.
- Lookup through `CloudAIService.get_provider(...)`.
- Provider selection and invocation through `CloudAIService`.
- Compatibility with the unchanged `CloudAIProvider` contract.

The existing Component #2 test file is `workspace/test_openai_provider.py`.

## Scope Boundaries

Component #2 does not include:

- Gemini, Anthropic, or local providers.
- A provider factory.
- Changes to `CloudAIProvider`.
- Provider-specific changes to `CloudAIService`. Completion of the already-
  approved generic `CloudAIService` contract remains in scope for
  `CloudAIService` itself.
- Changes to `ServiceContainer`.
- Streaming, multimodal, or tool-calling contracts.
- Rate limiting, cost optimization, or cross-provider failover.
- Generic credential or configuration files.

## Future Compatibility

Future providers may implement the same generic
`generate(prompt, model=None, parameters=None) -> Result` contract while
retaining independent constructors, credentials, SDKs, and request
translation.

## Approval State

```text
v0.7 Component #2: OpenAI Cloud AI Provider
Contract: Implemented and Tested
Canonical Path: providers/openai_provider.py
Implementation: Complete
Validation: Component #2 tests passed
```

# Execution Contract

دورة التنفيذ الرسمية:

```
User

↓

CommandParser

↓

Task

↓

TaskRouter

↓

Selected Agent

↓

CommandDispatcher

↓

Service

↓

Result

↓

MasterAgent

↓

Console
```

---

# Dependency Rules

يسمح فقط بالعلاقات التالية:

```
Agents
        ↓
Core
        ↓
Services
        ↓
Utilities
```

ويمنع:

```
Service → Agent

Service → Router

Service → Parser

Agent → Service مباشرة
```

ويجب أن يمر كل شيء عبر:

```
CommandDispatcher
```

---

# Return Contract

أي عملية داخل المشروع يجب أن تعيد:

```python
Result
```

ولا يجوز إعادة:

```
dict

list

str

bool
```

بشكل مباشر بين الطبقات.

---

# Extension Contract

أي Service جديدة يجب تسجيلها داخل:

```
ServiceContainer
```

وأي Agent جديد يجب تسجيله داخل:

```
TaskRouter
```

وأي أمر جديد يجب إضافته داخل:

```
CommandDispatcher
```

ولا يحتاج Agent إلى أي تعديل.

---

# Version Compatibility

تم اعتماد العقود الأساسية ابتداءً من:

```
AllAffiliate_Agent v0.4
```

أضيف عقد Cloud AI Foundation في الإصدار:

```
AllAffiliate_Agent v0.7
```

وأي تغيير في توقيع أي دالة (Method Signature) أو واجهة عامة (Public Interface) يُعد تغييرًا معماريًا، ويجب تحديث هذا الملف أولًا قبل تعديل الكود.

---

## v0.8 Component #1 — Research Engine

### Component Identity

```text
Component: Research Engine
Version: v0.8
Component Number: #1
Status: Contract Approved
```

### Canonical Path

```text
services/research_service.py
```

### Responsibility

`ResearchService` coordinates provider-neutral research sources and
normalizes their results into evidence records. It may research topics,
products, websites, markets, and problems when an injected source supports
the requested scope. It must distinguish observed facts from hypotheses.

### Direct Dependencies

- `Result` from `core.result`.
- Injected research sources implementing the source contract below.

The service must not depend on a cloud provider, browser implementation,
publishing platform, or external secret.

### Public Construction Contract

```python
ResearchService(sources=None) -> ResearchService
```

`sources` is an optional iterable of research sources. An omitted or empty
source collection is valid and produces a deterministic no-source failure
when research is requested.

### Research Source Contract

```python
search(query: str, scope: str | None = None) -> Result
```

Each source returns a `Result` whose successful `data` is an iterable of
evidence mappings. Each evidence mapping must contain or be normalized to:

```text
source
title
content
kind
```

`kind` is `FACT` for observed evidence. Unsupported or malformed source
records are rejected rather than silently treated as facts.

### Public Methods

```python
research(query: str, scope: str | None = None) -> Result
```

### Result Behavior

Successful research returns `Result.ok(...)` with normalized evidence in
`data` and metadata containing the query, scope, and source count.
Provider-neutral messages and metadata must not contain secrets.

### Failure Behavior

The service returns `Result.fail(...)` for invalid queries, invalid scopes,
missing sources, source failures, malformed source results, and unexpected
source exceptions. Source failure details are not exposed as proven facts.

### Integration Relationships

`ResearchService` is a Service-layer component. Future ResearchAgent or
workflow components may call it through the established service/container
boundaries. It does not perform routing, browser control, publishing,
analysis, or policy decisions.

### Required Tests

- construction with and without sources
- successful normalization through a deterministic fake source
- invalid query and scope behavior
- no-source and source-failure paths
- malformed evidence rejection
- source exception conversion
- `Result` contract compatibility
- preservation of FACT classification

### Scope Boundaries

This component does not implement web scraping, browser automation,
provider selection, reasoning, ranking, product decisions, policy
compliance, caching, streaming, or external API calls.

### Definition of Done

The component is complete when its implementation, focused tests, and
applicable regression validation pass, and `PROJECT_STATE.md` records the
checkpoint without changing the generic Cloud AI contract.

---

## v0.8 Component #2 — Analysis and Reasoning Layer

### Component Identity

```text
Component: Analysis and Reasoning Layer
Version: v0.8
Component Number: #2
Status: Contract Approved
```

### Canonical Path

```text
services/analysis_service.py
```

### Responsibility

`AnalysisService` validates and normalizes evidence classifications for
downstream decisions. It must preserve the distinction between observed
facts, hypotheses, recommendations, actions, and results. It must never
present a hypothesis as a proven fact.

### Direct Dependencies

- `Result` from `core.result`.
- An optional injected reasoning function implementing the analyzer
  boundary below.

The service must not depend on a specific AI provider, browser, publisher,
policy authority, or external secret.

### Public Construction Contract

```python
AnalysisService(analyzer=None) -> AnalysisService
```

When no analyzer is supplied, the service performs deterministic evidence
validation and returns the supplied facts without inventing conclusions.

### Analyzer Contract

```python
analyze(evidence: list[dict], question: str | None = None) -> Result
```

An analyzer may return a list of classified records. Each record must use
one of `FACT`, `HYPOTHESIS`, `RECOMMENDATION`, `ACTION`, or `RESULT`.

### Public Methods

```python
analyze(evidence: list[dict], question: str | None = None) -> Result
```

### Result Behavior

Successful output returns normalized records in `Result.data`, with
classification counts in metadata. FACT records remain facts; other
classifications are never promoted to FACT.

### Failure Behavior

The service returns `Result.fail(...)` for invalid evidence, invalid
questions, invalid analyzer results, unsupported classifications, analyzer
failures, and malformed records. Analyzer exception details are not
exposed.

### Integration Relationships

`AnalysisService` consumes research evidence and may later serve planning,
product, content, monitoring, and diagnosis workflows. It does not perform
research, routing, browser control, publishing, or policy decisions.

### Required Tests

- construction with and without an analyzer
- deterministic fact validation
- analyzer success and classification preservation
- invalid evidence and question behavior
- unsupported classification rejection
- analyzer failure and exception conversion
- `Result` contract compatibility
- proof that hypotheses are not promoted to facts

### Scope Boundaries

This component does not implement an AI provider, religious authority,
ranking algorithm, policy firewall, workflow planner, or external API call.

### Definition of Done

The component is complete when its implementation, focused tests, and
applicable regression validation pass, and project state records the
checkpoint without changing the provider-neutral Cloud AI contract.

---

## v0.8 Component #3 — Workflow and Planning Engine

### Component Identity

```text
Component: Workflow and Planning Engine
Version: v0.8
Component Number: #3
Status: Contract Approved
```

### Canonical Path

```text
services/workflow_service.py
```

### Responsibility

`WorkflowService` validates and normalizes plans for a user goal. It
coordinates an injected planner but does not invent a plan when no planner
is available. Plans are explicit ordered steps with lifecycle status.

### Direct Dependencies

- `Result` from `core.result`.
- An optional injected planner implementing the planner boundary below.

The service must not depend on a specific AI provider, browser, publisher,
or media implementation.

### Public Construction Contract

```python
WorkflowService(planner=None) -> WorkflowService
```

### Planner Contract

```python
plan(goal: str, context: dict | None = None) -> Result
```

The planner returns an iterable of step mappings. Every step must contain a
non-empty `id`, `description`, and `status`. Supported statuses are
`PENDING`, `READY`, `BLOCKED`, and `COMPLETED`.

### Public Methods

```python
plan(goal: str, context: dict | None = None) -> Result
```

### Result and Failure Behavior

Successful output returns normalized ordered steps in `Result.data` and
goal/step metadata. The service returns `Result.fail(...)` for invalid
goals or contexts, missing planners, planner failures, malformed plans,
duplicate step IDs, and unsupported statuses. Planner exception details are
not exposed.

### Integration Relationships

The service consumes analysis output and may later coordinate coding,
content, media, browser, publishing, monitoring, and diagnosis workflows.
It does not execute steps itself.

### Required Tests

- construction with and without a planner
- planner success and ordered-step normalization
- invalid goal/context behavior
- missing planner and planner failure paths
- malformed steps, duplicate IDs, and unsupported status rejection
- planner exception conversion
- `Result` contract compatibility

### Scope Boundaries

This component does not execute plans, select providers, call external
APIs, control browsers, render media, publish assets, or apply fixes.

### Definition of Done

The component is complete when its implementation, focused tests, and
Research/Analysis regression validation pass, with project state and
structure documentation synchronized.

---

## v0.8 Component #4 — Content Intelligence

### Component Identity

```text
Component: Content Intelligence
Version: v0.8
Component Number: #4
Status: Contract Approved
```

### Canonical Path

```text
services/content_service.py
```

### Responsibility

`ContentService` validates and normalizes structured content drafts from an
injected generator. It supports a reusable brief, optional persona data,
format, body, and explicit claims. It does not publish, render media, or
decide policy compliance.

### Public Construction Contract

```python
ContentService(generator=None) -> ContentService
```

### Generator Contract

```python
generate(
    brief: str,
    persona: dict | None = None,
    format: str | None = None,
) -> Result
```

Successful generator data must be a mapping containing non-empty `title`,
`body`, and `claims` (a list). Claims remain explicit data for later policy
review; they are not treated as approved statements.

### Public Methods

```python
create(brief: str, persona: dict | None = None, format: str | None = None) -> Result
```

### Result and Failure Behavior

Successful output returns a normalized draft mapping and metadata for the
requested format. The service returns `Result.fail(...)` for invalid briefs,
personas, formats, missing generators, generator failures, exceptions, and
malformed drafts. Generator exception details are not exposed.

### Integration Relationships

Content Intelligence consumes research, analysis, planning, and optional
persona data. It produces drafts for later policy, media, publishing, and
monitoring workflows. It does not invoke Cloud AI directly.

### Required Tests

- construction with and without a generator
- successful draft normalization
- invalid brief/persona/format behavior
- missing generator and generator failure paths
- malformed draft and claims rejection
- exception conversion and secret redaction
- `Result` contract compatibility

### Scope Boundaries

This component does not implement policy decisions, religious authority,
video rendering, image generation, publishing adapters, or platform APIs.

### Definition of Done

The component is complete when focused tests, v0.8 prior-component
regression, compilation, and synchronized documentation all pass.

---

## v0.8 Component #5 — Digital Asset Registry

### Component Identity

```text
Component: Digital Asset Registry
Version: v0.8
Component Number: #5
Status: Contract Approved
```

### Canonical Path

```text
services/digital_asset_service.py
```

### Responsibility

`DigitalAssetService` stores and retrieves reusable digital asset records.
Supported asset types include website, landing page, product, affiliate
link, video, channel, campaign, social account, and content asset.

### Public Construction Contract

```python
DigitalAssetService() -> DigitalAssetService
```

Each instance owns an isolated registry.

### Public Methods

```python
register(asset_type: str, name: str, metadata: dict | None = None) -> Result
get(asset_id: str) -> Result
list_assets(asset_type: str | None = None) -> Result
```

Registered records contain a generated stable `id`, normalized `type` and
`name`, and a metadata mapping. Metadata must not contain secrets.

### Result and Failure Behavior

All methods return `Result`. Invalid types, names, IDs, metadata, duplicate
IDs, and missing assets return `Result.fail(...)`. Listing an empty registry
is a successful result with an empty list.

### Integration Relationships

The registry is consumed by future content, affiliate, publishing,
monitoring, diagnosis, and experiment workflows. It does not monitor,
publish, or mutate external platforms.

### Required Tests

- construction and isolated registry state
- registration and normalized records
- lookup and list behavior
- type/name/metadata validation
- missing asset and filter behavior
- `Result` contract compatibility

### Scope Boundaries

This component does not implement persistence, platform APIs, monitoring,
metrics, diagnosis, publishing, affiliate ranking, or secret storage.

### Definition of Done

The component is complete when focused tests, v0.8 regression, compilation,
and synchronized documentation pass.

---

## v0.8 Component #6 — Product and Affiliate Intelligence

### Component Identity

```text
Component: Product and Affiliate Intelligence
Version: v0.8
Component Number: #6
Status: Contract Approved
```

### Canonical Path

```text
services/product_service.py
```

### Responsibility

`ProductService` ranks supplied product candidates using multiple numeric
signals. It records the signals used and never treats a single sales metric
as sufficient evidence. It does not discover products or publish content.

### Public Construction Contract

```python
ProductService() -> ProductService
```

### Public Methods

```python
rank(candidates: list[dict]) -> Result
```

Each candidate must contain a non-empty `id`, `name`, and `signals` mapping.
The signals mapping must contain at least two numeric finite values. Scores
are the arithmetic mean of the supplied signal values and are not claimed
to be business truth.

### Result and Failure Behavior

Success returns candidates ordered by descending score, retaining normalized
signals and adding `score` and `signals_used`. Invalid candidates,
duplicate IDs, non-numeric signals, and insufficient signals return
`Result.fail(...)`.

### Integration Relationships

The service consumes research and analysis outputs and may feed content,
policy, affiliate identity, publishing, and monitoring workflows. It does
not call external platforms or decide policy compliance.

### Required Tests

- construction and multi-signal ranking
- descending score and signal provenance
- invalid candidates and duplicate IDs
- insufficient/non-numeric signals
- `Result` compatibility

### Scope Boundaries

This component does not discover products, assert authoritative suitability,
embed affiliate links, publish content, or use a single metric as truth.

### Definition of Done

The component is complete when focused tests, v0.8 regression, compilation,
and synchronized documentation pass.

---

## v0.8 Component #7 — Policy and Shariah Compliance Firewall

### Component Identity

```text
Component: Policy and Shariah Compliance Firewall
Version: v0.8
Component Number: #7
Status: Contract Approved
```

### Canonical Path

```text
services/policy_service.py
```

### Responsibility

`PolicyService` isolates policy decisions from providers and content
generation. It represents `ALLOWED`, `BLOCKED`, and `REVIEW_REQUIRED`
outcomes and never claims that an AI model is an authoritative religious
authority.

### Public Construction Contract

```python
PolicyService(evaluator=None) -> PolicyService
```

### Evaluator Contract

```python
evaluate(asset: dict) -> Result
```

An evaluator returns a mapping with a decision and reasons. The decision
must be one of `ALLOWED`, `BLOCKED`, or `REVIEW_REQUIRED`; reasons must be a
list of strings.

### Public Methods

```python
evaluate(asset: dict) -> Result
```

### Result and Failure Behavior

Successful evaluation returns the normalized decision and reasons. Missing
evaluators, invalid assets, invalid decisions, malformed reasons, and
evaluator failures return `Result.fail(...)`. A blocked decision is a
successful policy result but must never be silently treated as publishable.

### Integration Relationships

Content, product, affiliate, and publishing workflows consume this
boundary. Provider code is not allowed to own policy decisions.

### Required Tests

- construction with and without evaluator
- ALLOWED, BLOCKED, and REVIEW_REQUIRED outcomes
- invalid asset and malformed evaluator output
- evaluator failure and exception conversion
- explicit blocked behavior and Result compatibility

### Scope Boundaries

This component does not provide religious authority, generate content,
publish assets, call external APIs, or silently approve blocked content.

### Definition of Done

The component is complete when all three decision states and failure paths
pass focused tests, v0.8 regression passes, and documentation is
synchronized.

---

## v0.8 Component #8 — Content Persona

### Component Identity

```text
Component: Content Persona
Version: v0.8
Component Number: #8
Status: Contract Approved
```

### Canonical Path

```text
services/persona_service.py
```

### Responsibility

`PersonaService` validates reusable content persona profiles. A profile may
represent audience, language, tone, storytelling style, narration style,
visual identity, marketing style, CTA behavior, platform constraints, and
prohibited claims.

### Public Construction Contract

```python
PersonaService() -> PersonaService
```

### Public Methods

```python
validate(persona: dict) -> Result
```

The returned profile is normalized and remains reusable; no channel identity
is hard-coded into another service.

### Result and Failure Behavior

All methods return `Result`. Invalid profiles, missing required fields, and
invalid field types return `Result.fail(...)`. Prohibited claims remain
data and are not silently removed.

### Integration Relationships

Content Intelligence and future publishing workflows may consume the
profile. The service does not generate, publish, or enforce policy.

### Required Tests

- construction and valid reusable profile
- required-field and type validation
- prohibited-claim preservation
- `Result` compatibility

### Scope Boundaries

This component does not own content generation, policy decisions, platform
adapters, or a single channel's identity.

### Definition of Done

The component is complete when focused tests, v0.8 regression, compilation,
and synchronized documentation pass.

---

## v0.8 Component #9 — Affiliate Identity and Tracking Abstraction

### Component Identity

```text
Component: Affiliate Identity and Tracking abstraction
Version: v0.8
Component Number: #9
Status: Contract Approved
```

### Canonical Path

```text
services/affiliate_identity_service.py
```

### Responsibility

`AffiliateIdentityService` stores reusable affiliate identity and tracking
configuration. It keeps identity separate from content, products, and
platform adapters and never stores secrets.

### Public Construction Contract

```python
AffiliateIdentityService() -> AffiliateIdentityService
```

### Public Methods

```python
create(network: str, account: str, campaign: str | None = None,
       parameters: dict | None = None) -> Result
get(identity_id: str) -> Result
```

Records contain a generated stable ID, normalized network/account/campaign,
and tracking parameters. Secret-like parameter keys are rejected.

### Result and Failure Behavior

All methods return `Result`. Invalid fields, protected parameters, and
missing identities return `Result.fail(...)`. Identity creation has no
external side effects.

### Integration Relationships

Content, product, publishing, and monitoring workflows may reference an
identity by ID. Platform-specific link construction remains outside this
component.

### Required Tests

- construction and reusable identity creation
- lookup and normalization
- optional campaign/parameters
- invalid fields and secret protection
- missing identity and `Result` compatibility

### Scope Boundaries

This component does not call affiliate networks, publish links, store
credentials, or hard-code a platform.

### Definition of Done

The component is complete when focused tests, v0.8 regression, compilation,
and synchronized documentation pass.

---

## v0.9 Component #1 — Temporal Video Production Engine

### Component Identity

```text
Component: Temporal Video Production Engine
Version: v0.9
Component Number: #1
Status: Contract Approved
```

### Canonical Path

```text
services/video_production_service.py
```

### Responsibility

`VideoProductionService` validates a temporal production plan. A plan must
represent timeline, stages, scenes, motion, camera, audio, continuity, and
validation data. It must not reduce temporal evolution to a collection of
still images.

### Public Construction Contract

```python
VideoProductionService(interpreter=None) -> VideoProductionService
```

### Interpreter Contract

```python
interpret(instruction: str) -> Result
```

The interpreter returns a mapping containing a non-empty `timeline` list.
Each stage contains an `id`, `duration`, and `scenes` list. Each scene
contains `id`, `motion`, `camera`, `audio`, and `continuity` mappings.

### Public Methods

```python
create_plan(instruction: str) -> Result
```

### Result and Failure Behavior

Successful output returns a normalized temporal plan and metadata with
stage/scene counts. Missing interpreters, invalid instructions, malformed
timelines, missing motion/camera/audio/continuity data, and interpreter
failures return `Result.fail(...)`. No renderer or external API is called.

### Integration Relationships

The plan may later feed separate audio, media, rendering, and quality
validation components. Optional image assets remain supporting inputs, not
the production architecture.

### Required Tests

- construction and missing interpreter behavior
- successful temporal plan normalization
- invalid instruction and malformed timeline behavior
- missing stage/scene continuity fields
- interpreter failure and exception conversion
- `Result` compatibility

### Scope Boundaries

This component does not render video, generate images, call media APIs,
produce audio, control browsers, or publish content.

### Definition of Done

The component is complete when its focused tests, v0.9 regression,
compilation, and synchronized documentation pass.

---

## v0.9 Component #2 — Audio Engine

### Component Identity

```text
Component: Audio Engine
Version: v0.9
Component Number: #2
Status: Contract Approved
```

### Canonical Path

```text
services/audio_service.py
```

### Responsibility

`AudioService` validates a separable audio plan for a production workflow.
An audio plan contains ordered tracks with timing, type, and continuity
references. It does not render audio or own video production logic.

### Public Construction Contract

```python
AudioService(interpreter=None) -> AudioService
```

### Interpreter Contract

```python
interpret(instruction: str) -> Result
```

The interpreter returns a mapping with a non-empty `tracks` list. Each track
contains `id`, `start`, `duration`, `kind`, and `continuity`.

### Public Methods

```python
create_plan(instruction: str) -> Result
```

### Result and Failure Behavior

Successful output returns normalized ordered tracks. Missing interpreters,
invalid instructions, malformed tracks, invalid timing, duplicate IDs, and
interpreter failures return `Result.fail(...)` without exposing exception
details.

### Integration Relationships

Audio plans may be consumed by the temporal video engine, media pipeline,
and quality validation components through explicit plan data. Audio remains
separate from video and image capabilities.

### Required Tests

- construction and missing interpreter behavior
- successful track normalization
- invalid instruction/timing and malformed track behavior
- duplicate ID rejection
- interpreter failure and exception conversion
- `Result` compatibility

### Scope Boundaries

This component does not render audio, call external media APIs, generate
video, or implement image generation.

### Definition of Done

The component is complete when focused tests, v0.9 regression, compilation,
and synchronized documentation pass.

---

## v0.9 Component #3 — Media Pipeline

### Component Identity

```text
Component: Media Pipeline
Version: v0.9
Component Number: #3
Status: Contract Approved
```

### Canonical Path

```text
services/media_pipeline_service.py
```

### Responsibility

`MediaPipelineService` validates composition inputs from temporal video and
audio plans and returns a provider-neutral composition manifest. It does
not render media or call external APIs.

### Public Construction Contract

```python
MediaPipelineService() -> MediaPipelineService
```

### Public Methods

```python
compose(video_plan: dict, audio_plan: dict) -> Result
```

Both plans must contain non-empty lists for `timeline` and `tracks`,
respectively. The returned manifest preserves both plans and records the
composition stage as `VALIDATED`.

### Result and Failure Behavior

Invalid plans, missing lists, and malformed inputs return `Result.fail(...)`.
Successful composition is a manifest validation result, not a rendered
file.

### Integration Relationships

The pipeline consumes Video Production and Audio Engine plans and may later
feed rendering and quality validation components. It remains separate from
browser, publishing, and provider boundaries.

### Required Tests

- construction and valid composition manifest
- invalid/missing video and audio plan behavior
- preservation of temporal and audio data
- `Result` compatibility

### Scope Boundaries

This component does not render, encode, publish, call media providers, or
replace the temporal video architecture with still-image composition.

### Definition of Done

The component is complete when focused tests, v0.9 regression, compilation,
and synchronized documentation pass.

---

## v0.9 Component #4 — Publishing Gateway

### Component Identity

```text
Component: Publishing Gateway
Version: v0.9
Component Number: #4
Status: Contract Approved
```

### Canonical Path

```text
services/publishing_service.py
```

### Responsibility

`PublishingService` routes publish requests through an injected platform
adapter. It fails closed for assets with a `BLOCKED` policy decision and
does not hard-code a social platform.

### Public Construction Contract

```python
PublishingService(adapter=None) -> PublishingService
```

### Adapter Contract

```python
publish(asset: dict, destination: str) -> Result
```

### Public Methods

```python
publish(asset: dict, destination: str) -> Result
```

### Result and Failure Behavior

Invalid assets/destinations, blocked policy decisions, missing adapters,
adapter failures, and adapter exceptions return `Result.fail(...)`.
Successful adapter results are normalized with destination metadata.

### Required Tests

- construction and adapter success
- blocked fail-closed behavior
- invalid inputs and missing adapter
- adapter failure and exception conversion
- `Result` compatibility

### Scope Boundaries

This component does not implement a platform, hold credentials, create
content, or bypass policy decisions.

### Definition of Done

The component is complete when focused tests, v0.9 regression, compilation,
and synchronized documentation pass.

---

## v0.9 Component #5 — Performance Monitoring

### Component Identity

```text
Component: Performance Monitoring
Version: v0.9
Component Number: #5
Status: Contract Approved
```

### Canonical Path

```text
services/performance_monitoring_service.py
```

### Responsibility

`PerformanceMonitoringService` records observations for registered digital
assets. It preserves the relationship between asset identity, timestamped
metrics, and evidence. It does not diagnose causes or mutate external
platforms.

### Public Construction Contract

```python
PerformanceMonitoringService() -> PerformanceMonitoringService
```

### Public Methods

```python
record(asset_id: str, metrics: dict[str, int | float]) -> Result
list_observations(asset_id: str | None = None) -> Result
```

Metrics must be numeric finite values. Each observation receives a stable
observation ID and UTC timestamp.

### Result and Failure Behavior

Invalid asset IDs, invalid metrics, non-numeric/non-finite values, and invalid
filters return `Result.fail(...)`. Listing with no observations succeeds with
an empty list. Observations are copied on input and output.

### Integration Relationships

The service consumes digital asset identities and later feeds anomaly
detection, diagnosis, experiments, and reporting. It does not infer
hypotheses or claim causal explanations.

### Required Tests

- construction and isolated observation state
- recording numeric metrics
- listing and asset filtering
- invalid IDs and metrics
- non-finite value rejection
- `Result` compatibility

### Scope Boundaries

This component does not scrape platforms, diagnose causes, publish fixes,
call external APIs, or store credentials.

### Definition of Done

The component is complete when focused tests, v0.9 regression, compilation,
and synchronized documentation pass.

---

## v0.9 Component #6 — Diagnosis Engine

### Component Identity

```text
Component: Diagnosis Engine
Version: v0.9
Component Number: #6
Status: Contract Approved
```

### Canonical Path

```text
services/diagnosis_service.py
```

### Responsibility

`DiagnosisService` organizes asset observations into evidence-backed
diagnoses. It preserves FACT, HYPOTHESIS, and RECOMMENDATION distinctions
and never presents a hypothesis as a proven cause.

### Public Construction Contract

```python
DiagnosisService(analyzer=None) -> DiagnosisService
```

### Public Methods

```python
diagnose(asset_id: str, observations: list[dict]) -> Result
```

The optional analyzer may return hypothesis/recommendation records. Without
one, the service returns validated observation facts and no invented cause.

### Result and Failure Behavior

Invalid asset IDs/observations, malformed analyzer output, analyzer failure,
and exceptions return `Result.fail(...)`. Successful output contains
classified records and metadata identifying the asset.

### Required Tests

- deterministic fact-only diagnosis
- analyzer classification preservation
- invalid observations
- analyzer failure and exception conversion
- no hypothesis promotion to FACT

### Scope Boundaries

This component does not apply fixes, publish changes, call external APIs,
or claim causal certainty without evidence.

### Definition of Done

Focused tests, v0.9 regression, compilation, and synchronized
documentation pass.

---

## v0.9 Component #7 — Experiment and Optimization Engine

### Component Identity

```text
Component: Experiment and Optimization Engine
Version: v0.9
Component Number: #7
Status: Contract Approved
```

### Canonical Path

```text
services/experiment_service.py
```

### Responsibility

`ExperimentService` records a generic experiment lifecycle across digital
assets: observation, hypothesis, experiment, action, measurement, result,
and learning. It does not apply external changes automatically.

### Public Construction Contract

```python
ExperimentService() -> ExperimentService
```

### Public Methods

```python
create(asset_id: str, hypothesis: str, action: str) -> Result
record_measurement(experiment_id: str, metrics: dict) -> Result
complete(experiment_id: str, result: str, learning: str | None = None) -> Result
get(experiment_id: str) -> Result
```

### Result and Failure Behavior

All methods return `Result`. Invalid IDs, empty hypotheses/actions/results,
invalid metrics, and missing experiments fail. Lifecycle records retain
explicit `FACT`, `HYPOTHESIS`, `EXPERIMENT`, `ACTION`, and `RESULT` data.

### Scope Boundaries

This component does not call platforms, apply irreversible fixes, infer
causes as facts, or hard-code a video, website, product, or channel.

### Required Tests and Definition of Done

Focused lifecycle, invalid-input, missing-record, metric, Result, v0.9
regression, and compilation tests must pass with synchronized documentation.

---

## v0.9 Component #8 — Browser Agent

### Canonical Paths

```text
agents/browser_agent.py
services/browser_service.py
```

`BrowserAgent` delegates browser workflows to `BrowserService`; the service
delegates to an injected `BrowserAdapter`. The adapter owns any browser
runtime details. Public operations are `navigate`, `inspect`, `extract`,
`interact`, `validate`, and `execute_workflow`.

All operations return `Result`, reject invalid operations, and fail safely
when no adapter is configured. Unit tests use deterministic fakes and make
no real browser calls. Browser and computer automation remain separate.

### Definition of Done

Focused delegation/failure tests, v0.9 regression, compilation, and
synchronized documentation pass.

---

## v0.9 Component #9 — Computer Agent

### Canonical Paths

```text
agents/computer_agent.py
services/computer_service.py
```

`ComputerAgent` delegates to `ComputerService`, which delegates to a
replaceable `ComputerAdapter`. Computer operations require explicit
permission and are limited to an allowlisted operation vocabulary. No
destructive operation is enabled by default.

Supported conceptual operations are `keyboard`, `mouse`, `window`,
`application`, `screen`, and `verify_state`. All operations return
`Result`; missing permission, invalid operations, missing adapters, and
adapter failures return `Result.fail(...)`.

Unit tests use deterministic adapter fakes and never control the real OS.

### Definition of Done

Focused delegation, permission, failure, regression, compilation, and
documentation validation pass.

---

# End of Document
---

## CapabilityAgent

Canonical path:

```text
agents/capability_agent.py
```

`CapabilityAgent` is a minimal task-level orchestration bridge for
service-only capabilities that do not require a dedicated specialized
Agent. It does not implement business logic, low-level execution, or
provider behavior. It selects one documented service and invokes one
documented public method through the existing `ServiceContainer`.

Constructor:

```python
CapabilityAgent(services, task_type, service_name, method_name)
```

Public method:

```python
execute(task) -> Result
```

The agent accepts structured values in `task.data["payload"]`. For the
string-oriented `research`, `video`, and `audio` tasks, the command body
may be used as the single service argument when no payload is supplied.
Other capabilities require a mapping payload matching the service
contract; malformed or missing payloads return `Result.fail(...)`.

The agent validates the registered service and method, catches service
exceptions at the agent boundary, and returns the service's `Result`
unchanged on successful invocation. It never creates adapters, performs
external calls, or contains capability-specific business logic.

The initial task/service mappings are:

```text
research    -> ResearchService.research
analyze     -> AnalysisService.analyze
plan        -> WorkflowService.plan
content     -> ContentService.create
video       -> VideoProductionService.create_plan
audio       -> AudioService.create_plan
media       -> MediaPipelineService.compose
asset       -> DigitalAssetService.register
product     -> ProductService.rank
policy      -> PolicyService.evaluate
monitor     -> PerformanceMonitoringService.record
diagnose    -> DiagnosisService.diagnose
experiment  -> ExperimentService.create
publishing  -> PublishingService.publish
```

This bridge is limited to routing and argument-shape validation. Dedicated
Agents remain preferred when a capability needs multi-step orchestration.

Required tests cover construction, mapping, successful service Result
propagation, invalid/missing payloads, missing services, service failures,
and registry integration.

---

# External Integration Phase

## External Integration #1 — OpenAI Cloud Runtime
### Integration Identity

```text
Component: OpenAI Cloud Runtime Integration
Provider: OpenAI
Phase: EXTERNAL INTEGRATION PHASE
Status: INTEGRATION READY
Role: OPTIONAL CLOUD AI PROVIDER
Real Verification: NOT VERIFIED
```

### Purpose

تمكين AllAffiliate_Agent من استخدام OpenAI Cloud API من خلال
`OpenAIProvider` و`CloudAIService` مع الحفاظ على العقود العامة
وحدود الطبقات الحالية.

هذا التكامل لا يغيّر `CloudAIProvider` ولا `CloudAIService` ولا
`ContentService`.

### Canonical Boundary

```text
ContentService
      ↓
ContentGenerator
      ↓
CloudAIService
      ↓
OpenAIProvider
      ↓
OpenAI SDK
      ↓
OpenAI Cloud API
```

### Canonical Provider

```text
providers/openai_provider.py
```

`OpenAIProvider` هو الحد الرسمي لتنفيذ OpenAI-specific behavior.

### Public Construction Contract

```python
OpenAIProvider() -> OpenAIProvider
```

لا يحتوي الـ constructor على إعدادات عامة خاصة بمزود OpenAI.

بيانات الاعتماد، عميل SDK، وتفاصيل تنفيذ OpenAI تبقى داخل حدود
المزود.

### Credential Contract

يستخدم المزود متغير البيئة:

```text
OPENAI_API_KEY
```

قواعد الاعتماد:

* لا يجوز وضع المفتاح داخل الكود.
* لا يجوز وضع المفتاح داخل ملفات العقود.
* لا يجوز وضع المفتاح داخل الاختبارات.
* لا يجوز تسجيل المفتاح في logs.
* لا يجوز إرجاع المفتاح داخل `Result.data`.
* لا يجوز إرجاع المفتاح داخل `Result.errors`.
* لا يجوز إرجاع المفتاح داخل `Result.metadata`.

عند غياب المفتاح يجب أن يفشل المزود بأمان.

### SDK Boundary

تفاصيل OpenAI SDK يجب أن تبقى داخل:

```text
providers/openai_provider.py
```

ولا يجوز للخدمات العامة استدعاء OpenAI SDK مباشرة.

### Public Generation Contract

يجب أن يطبق المزود العقد العام الحالي دون تغيير:

```python
generate(
    prompt: str,
    model: str | None = None,
    parameters: dict | None = None,
) -> Result
```

لا يجوز إضافة OpenAI-specific arguments إلى العقد العام.

### Result Contract

عند نجاح التوليد:

```python
Result.ok(...)
```

وتكون الاستجابة في:

```python
Result.data
```

وعند الفشل:

```python
Result.fail(...)
```

لا يجوز تسريب الأسرار أو بيانات الاعتماد.

### Failure Behavior

يجب تحويل الحالات التالية إلى `Result.fail(...)`:

* `OPENAI_API_KEY` مفقود.
* بيانات اعتماد غير صالحة.
* prompt غير صالح.
* model غير صالح أو مفقود.
* parameters غير صالحة.
* SDK failure.
* API failure.
* quota failure.
* rate-limit failure.
* invalid provider response.
* unexpected provider exception.

### CloudAIService Relationship

يبقى العقد العام لـ `CloudAIService` دون تغيير:

```python
register_provider(name, provider) -> Result
get_provider(name) -> Result
remove_provider(name) -> Result
list_providers() -> Result
generate(prompt, provider=None, model=None, parameters=None) -> Result
```

العلاقة:

```text
CloudAIService
      ↓
CloudAIProvider
      ↓
OpenAIProvider
      ↓
OpenAI SDK
      ↓
OpenAI Cloud API
```

`CloudAIService` مسؤول عن التسجيل والبحث والاختيار والاستدعاء
والتعامل مع `Result`.

`OpenAIProvider` لا يختار المزود ولا يدير الـ Router.

### Content Integration Boundary

يبقى:

```text
ContentService
      ↓
ContentGenerator
      ↓
CloudAIService
      ↓
OpenAIProvider
```

ولا يجوز لـ `ContentService` استيراد OpenAI SDK مباشرة.

### Required Tests

يجب أن تغطي الاختبارات:

* construction.
* successful generation.
* model forwarding.
* parameter forwarding.
* invalid prompt.
* invalid model.
* invalid parameters.
* missing credentials.
* invalid credentials.
* SDK failure.
* API failure.
* quota/rate-limit failure.
* invalid response.
* secret redaction.
* `Result.ok(...)` compatibility.
* `Result.fail(...)` compatibility.
* compatibility with unchanged `CloudAIProvider`.
* registration through `CloudAIService`.
* provider lookup.
* provider selection.
* provider invocation.

### Real Smoke Test

يتطلب التحقق التشغيلي الحقيقي:

```text
Environment:
OPENAI_API_KEY = PRESENT

Operation:
Generate one short sentence about renewable energy.

Expected:
Result.success == True
Result.data contains generated text
```

### Current Real Verification Evidence

تم تنفيذ اختبار حقيقي إلى OpenAI Cloud API.

الأدلة المثبتة:

```text
OPENAI_API_KEY:
PRESENT

OpenAI Client:
INITIALIZED

Models API:
ACCESSIBLE

Generation Request:
REJECTED
```

سبب الرفض:

```text
HTTP 429
Error Type: RateLimitError
Error Code: insufficient_quota
```

وبالتالي تم إثبات إمكانية الوصول إلى OpenAI API، ولكن لم يتم إثبات
توليد استجابة حقيقية بنجاح.

### Operational Verification Status

لا يجوز تصنيف OpenAI على أنه:

```text
OPERATIONALLY VERIFIED
```

حتى ينجح طلب توليد حقيقي.

الحالة الحالية:

```text
Status: INTEGRATION READY
Real Verification: NOT VERIFIED
Reason: Real generation blocked by insufficient API quota
```

يجب عدم اعتبار خطأ `insufficient_quota` عيبًا في المعمارية أو
في `OpenAIProvider` ما لم يظهر دليل آخر على خلل برمجي.

### Scope Boundaries

هذا التكامل لا يشمل:

* automatic paid-tier activation.
* automatic billing.
* automatic quota bypass.
* provider failover.
* streaming contract.
* multimodal contract.
* tool-calling contract.
* provider factory.
* تغييرات في `CloudAIProvider`.
* تغييرات في العقد العام لـ `CloudAIService`.
* credential management system.

أي توسعة لهذه القدرات تحتاج Contract منفصلًا ومعتمدًا.

### Definition of Done

يعتبر External Integration #1 مكتملًا تشغيليًا فقط عند تحقق:

* `OpenAIProvider` implemented.
* OpenAI SDK available.
* `OPENAI_API_KEY` configured externally.
* focused tests pass.
* regression remains passing.
* compilation passes.
* secret redaction passes.
* generic Cloud AI contract remains unchanged.
* real generation request succeeds.
* operational status is updated truthfully.
* `PROJECT_STATE.md` is synchronized.
* `CHANGELOG.md` is synchronized.

### Approval State

```text
External Integration #1
Provider: OpenAI
Role: OPTIONAL CLOUD AI PROVIDER
Canonical Path: providers/openai_provider.py
Contract: APPROVED
Implementation: COMPLETE
Real Verification: NOT VERIFIED
Current Status: INTEGRATION READY
Reason: insufficient_quota
```

---

## External Integration #2 — Google Gemini Cloud Runtime

## Integration Identity

```text
Component: Google Gemini Cloud Runtime Integration
Provider: Google Gemini
Phase: EXTERNAL INTEGRATION PHASE
Status: Contract Approved — Implementation Pending
Role: PRIMARY FREE CLOUD AI PROVIDER
```

## Purpose

تمكين AllAffiliate_Agent من استخدام Google Gemini Cloud API كمسار Cloud AI
مجاني أساسي عند توفر Free Tier، مع الحفاظ الكامل على العقد العام الحالي
`CloudAIProvider` وعدم ربط بقية المشروع بتفاصيل Gemini.

هذا التكامل مخصص في المرحلة الأولى للمهام النصية التي تحتاج إلى Cloud AI،
خصوصًا:

* Content Generation
* Analysis
* Planning
* Reasoning

ويجب ألا يؤدي التكامل إلى تغيير العقود العامة للخدمات الحالية.

## Free-Tier Policy

يعتمد التكامل في مرحلته الأولى على النماذج والحصص المتاحة ضمن
Gemini API Free Tier.

Free Tier ليس مضمونًا ليكون بلا حدود، وتخضع حدود الاستخدام والنماذج
المتاحة لسياسات Google الحالية.

لا يجوز للتكامل تفعيل فوترة مدفوعة أو تجاوز حدود Free Tier تلقائيًا.

عند انتهاء الحصة المجانية أو رفض الطلب بسبب حدود الاستخدام أو الفوترة،
يجب إعادة `Result.fail(...)` وعدم تنفيذ أي انتقال تلقائي إلى Tier مدفوع.

## Canonical Path

```text
providers/gemini_provider.py
```

هذا هو المسار الرسمي الوحيد لتنفيذ Google Gemini Cloud Runtime.

## Responsibility

`GeminiProvider` مسؤول فقط عن تكييف Google Gemini Cloud API مع العقد العام:

```python
CloudAIProvider
```

وتشمل مسؤوليته:

* إنشاء عميل Gemini.
* قراءة بيانات الاعتماد من مصدر البيئة الخاص بالمزود.
* تحويل الطلب العام إلى صيغة Gemini.
* تنفيذ طلب Cloud AI.
* تحويل استجابة Gemini إلى `Result`.
* تحويل أخطاء Gemini وSDK إلى `Result.fail(...)`.
* منع تسرب الأسرار في الأخطاء والرسائل والبيانات الوصفية.

ولا يجوز له تعديل:

```text
Core
Agents
Router
Memory
CloudAIService
ServiceContainer
ContentService
```

## Public Construction Contract

```python
GeminiProvider() -> GeminiProvider
```

لا يعرض الـ constructor أي إعدادات عامة خاصة بـ Gemini.

إعدادات Gemini الخاصة، وبيانات الاعتماد، وعميل SDK، وتفاصيل الاتصال
تبقى داخل حدود المزود.

## Credential Contract

يستخدم التكامل متغير البيئة الرسمي:

```text
GEMINI_API_KEY
```

قواعد الاعتماد:

* لا يجوز وضع API key داخل الكود.
* لا يجوز وضع API key داخل `API_CONTRACTS.md`.
* لا يجوز وضع API key داخل ملفات الاختبارات.
* لا يجوز تسجيل API key في logs.
* لا يجوز إرجاع API key داخل `Result.data`.
* لا يجوز إرجاع API key داخل `Result.errors`.
* لا يجوز إرجاع API key داخل `Result.metadata`.

عند غياب `GEMINI_API_KEY` يجب أن يفشل المزود بشكل آمن.

## SDK Boundary

الاعتماد الخارجي المسموح به:

```text
google-genai
```

ويجب أن تبقى جميع تفاصيل SDK داخل:

```text
providers/gemini_provider.py
```

لا يجوز للخدمات العامة استيراد:

```text
google.genai
google-genai
```

مباشرة.

## Model Contract

النموذج الأول المعتمد للتكامل المجاني هو:

```text
gemini-2.5-flash-lite
```

ويُستخدم كإعداد افتراضي داخل حدود المزود أو طبقة التوصيل الخاصة به،
دون توسيع العقد العام لـ `CloudAIProvider`.

يمكن لاحقًا تغيير النموذج أو إضافة نماذج أخرى ضمن حدود عقد منفصل أو
تحديث معتمد، دون تعديل `CloudAIProvider`.

## Public Generation Contract

يجب أن يطبق المزود العقد العام الحالي دون أي تغيير:

```python
generate(
    prompt: str,
    model: str | None = None,
    parameters: dict | None = None,
) -> Result
```

لا يجوز إضافة Gemini-specific arguments إلى العقد العام.

## Request Translation

يقوم `GeminiProvider` بتحويل:

```text
prompt
model
parameters
```

إلى طلب Gemini مناسب داخل حدود المزود فقط.

لا يجوز للخدمات الأخرى معرفة:

* Gemini request objects
* Gemini response objects
* SDK-specific message structures
* Gemini client objects
* Gemini-specific exceptions

## Result Return Contract

عند نجاح طلب Gemini:

```python
Result.ok(...)
```

وتكون الاستجابة المولدة داخل:

```python
Result.data
```

ويجب أن يكون الناتج provider-neutral قدر الإمكان.

عند الفشل:

```python
Result.fail(...)
```

ولا يجوز تسريب:

* API keys
* authentication headers
* raw secret values
* internal credential data

## Failure Behavior

يجب على `GeminiProvider` تحويل الحالات التالية إلى `Result.fail(...)`:

* `GEMINI_API_KEY` مفقود.
* بيانات الاعتماد غير صالحة.
* prompt غير صالح.
* model غير صالح.
* parameters غير صالحة.
* SDK failure.
* API failure.
* quota/rate-limit failure.
* blocked request.
* invalid Gemini response.
* unexpected provider exception.

عند انتهاء Free Tier أو حدوث مشكلة quota يجب أن يفشل الطلب بأمان.

لا يجوز إنشاء فوترة مدفوعة أو تجاوز Free Tier تلقائيًا.

## CloudAIService Relationship

العقد العام لـ `CloudAIService` يبقى دون تغيير:

```python
register_provider(name, provider) -> Result
get_provider(name) -> Result
remove_provider(name) -> Result
list_providers() -> Result
generate(prompt, provider=None, model=None, parameters=None) -> Result
```

العلاقة:

```text
CloudAIService
      ↓
CloudAIProvider
      ↓
GeminiProvider
      ↓
google-genai
      ↓
Google Gemini Cloud API
```

`CloudAIService` مسؤول عن:

* تسجيل المزود.
* البحث عن المزود.
* اختيار المزود.
* استدعاء المزود.
* التعامل مع `Result`.

`GeminiProvider` لا يختار المزود ولا يسجل نفسه ولا يتعامل مع Router.

## ContentService Integration Boundary

يجب أن يبقى:

```text
ContentService
      ↓
ContentGenerator
      ↓
CloudAIService
      ↓
GeminiProvider
```

ويجب ألا يتعامل `ContentService` مباشرة مع Gemini SDK.

الـ `ContentGenerator` contract يبقى دون تغيير:

```python
generate(
    brief: str,
    persona: dict | None = None,
    format: str | None = None,
) -> Result
```

## Direct Dependencies

الاعتماديات المباشرة المسموح بها:

```text
Result
CloudAIProvider
google-genai
GEMINI_API_KEY
```

ولا يجوز للمزود الاعتماد على:

```text
Agents
Router
Memory
Publishing
BrowserService
ComputerService
```

## Required Tests

يجب أن تغطي اختبارات `GeminiProvider`:

* `GeminiProvider()` construction.
* successful generation.
* model forwarding.
* parameter forwarding.
* invalid prompt.
* invalid model.
* invalid parameters.
* missing API key.
* invalid credentials.
* SDK failure.
* API failure.
* quota/rate-limit failure.
* invalid response.
* secret redaction.
* `Result.ok(...)` compatibility.
* `Result.fail(...)` compatibility.
* compatibility with unchanged `CloudAIProvider`.
* registration through `CloudAIService`.
* provider lookup.
* provider selection.
* provider invocation.

## Real Smoke Test Contract

بعد تنفيذ المزود، يجب إجراء اختبار حقيقي مستقل باستخدام API key صالح:

```text
Environment:
GEMINI_API_KEY = PRESENT

Model:
gemini-2.5-flash-lite

Operation:
Generate one short sentence about renewable energy.

Expected:
Result.success == True
Result.data contains generated text
```

ويجب تسجيل نتيجة الاختبار بوضوح.

## Operational Verification Rules

لا يُعتبر Gemini:

```text
OPERATIONALLY VERIFIED
```

إلا بعد نجاح طلب حقيقي إلى Gemini Cloud API.

نجاح:

* الاستيراد.
* إنشاء العميل.
* الاختبارات الوهمية.
* الاختبارات المحلية.
* compilation.

لا يكفي وحده لإثبات الاتصال التشغيلي الحقيقي.

قبل نجاح الـ Real Smoke Test يبقى الوضع:

```text
Status: INTEGRATION READY
```

بعد نجاح الطلب الحقيقي يصبح:

```text
Status: OPERATIONALLY VERIFIED
```

مع تسجيل التاريخ ونتيجة الاختبار في:

```text
PROJECT_STATE.md
CHANGELOG.md
```

## Scope Boundaries

هذا التكامل لا يشمل في مرحلته الأولى:

* Gemini multimodal workflows.
* Gemini image generation.
* Gemini audio generation.
* Gemini video generation.
* Google Search grounding.
* Google Maps grounding.
* tool calling.
* streaming.
* batching.
* automatic model failover.
* automatic paid-tier activation.
* credential management system.
* provider factory.
* changes to `CloudAIProvider`.
* changes to `CloudAIService` generic contract.

أي من هذه القدرات يحتاج Contract منفصلًا قبل التنفيذ.

## Architecture Preservation

يجب الحفاظ على:

```text
User
  ↓
CommandParser
  ↓
Task
  ↓
TaskRouter
  ↓
Agent
  ↓
CommandDispatcher
  ↓
Service
  ↓
CloudAIService
  ↓
GeminiProvider
  ↓
Google Gemini API
  ↓
Result
```

ولا يجوز اختصار الطبقات أو ربط الخدمات مباشرة بـ Gemini SDK.

## Definition of Done

يعتبر External Integration #2 مكتملًا فقط عند تحقق جميع الشروط:

* `GeminiProvider` implemented.
* `google-genai` installed.
* `GEMINI_API_KEY` configured externally.
* focused tests pass.
* existing regression tests remain passing.
* compilation passes.
* secret redaction passes.
* generic `CloudAIProvider` contract remains unchanged.
* `CloudAIService` generic contract remains unchanged.
* Content integration remains provider-neutral.
* real Gemini API request succeeds.
* integration status is truthfully updated.
* `PROJECT_STATE.md` is synchronized.
* `CHANGELOG.md` is synchronized.

## Approval State

```text
External Integration #2
Provider: Google Gemini
Role: PRIMARY FREE CLOUD AI PROVIDER
Canonical Path: providers/gemini_provider.py
Contract: APPROVED
Implementation: PENDING
Real Verification: PENDING
Current Status: INTEGRATION READY
```
