# API\_CONTRACTS.md**

# AllAffiliate\_Agent**

**\*\*API Contracts\*\***

**\*\*Version:\*\*** v0.6

**\*\*Status:\*\*** Plugin & Capability Foundation

**\*\*Document Version:\*\*** 1.1

---

# Purpose**

يُعد هذا الملف المرجع الرسمي لجميع العقود البرمجية (Contracts) داخل المشروع.

الغرض منه هو توثيق الواجهات العامة (Public Interfaces) بين جميع الطبقات، بحيث يستطيع أي مطور أو نموذج ذكاء اصطناعي تطوير أي ملف دون الحاجة إلى قراءة المشروع بالكامل.

هذا الملف لا يشرح منطق التنفيذ، وإنما يحدد فقط:

\- أسماء الفئات (Classes)
\- أسماء الدوال (Methods)
\- المدخلات (Inputs)
\- المخرجات (Outputs)
\- العلاقات بين المكونات
\- حدود المسؤوليات العامة للمكونات

---

# Core Contracts**

---

## Result**

الموقع:

```text
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

```text
success
message
data
errors
metadata
timestamp
```

---

## Task**

الموقع:

```text
core/task.py
```

المسؤولية:

تمثيل المهمة الناتجة عن CommandParser.

الخصائص:

```text
task\_type
command
data
```

---

## CommandParser**

الموقع:

```text
core/command\_parser.py
```

المسؤولية:

تحويل أمر المستخدم إلى Task.

الواجهة:

```python
parse(command: str) -> Task
```

لا ينفذ أي أوامر.

---

## TaskRouter**

الموقع:

```text
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

## CommandDispatcher**

الموقع:

```text
core/command\_dispatcher.py
```

المسؤولية:

تحليل الأمر النصي واستدعاء الخدمة المناسبة.

الواجهة:

```python
dispatch(command: str) -> Result
```

لا ينفذ أي عملية بنفسه.

يعتمد على:

```text
CodeWriter
FileTools
TextEditor
PythonRunner
ProjectManager
```

---

## ServiceContainer**

الموقع:

```text
core/service\_container.py
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

# Agent Contracts**

---

## BaseAgent**

الموقع:

```text
core/base\_agent.py
```

المسؤولية:

العقد الأساسي لجميع الوكلاء.

الواجهة:

```python
execute(task)
```

---

## MasterAgent**

الموقع:

```text
agents/master\_agent.py
```

المسؤولية:

تنسيق دورة التنفيذ الكاملة.

لا ينفذ أي Business Logic.

يتعامل مع:

```text
CommandParser
TaskRouter
Result
```

المسؤوليات:

\- استقبال أوامر المستخدم
\- إنشاء Task
\- إرسال المهمة إلى Router
\- استلام النتيجة
\- عرض النتيجة
\- إدارة جلسة التنفيذ

---

## CodingAgent**

الموقع:

```text
agents/coding\_agent.py
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

## MemoryAgent**

الموقع:

```text
agents/memory\_agent.py
```

المسؤولية:

تنسيق عمليات الذاكرة عبر MemoryManager.

الحالة:

```text
Implemented
```

الواجهة:

```python
execute(task) -> Result
```

عمليات الذاكرة المدعومة حاليًا:

```text
save
get
get\_entry
search
list
delete
clear\_session
count
health\_check
```

---

## BrowserAgent**

الموقع:

```text
agents/browser\_agent.py
```

الحالة:

```text
Future
```

---

## ImageAgent**

الموقع:

```text
agents/image\_agent.py
```

الحالة:

```text
Future
```

---

## VideoAgent**

الموقع:

```text
agents/video\_agent.py
```

الحالة:

```text
Future
```

---

## VoiceAgent**

الموقع:

```text
agents/voice\_agent.py
```

الحالة:

```text
Future
```

---

# Service Contracts**

---

## CodeWriter**

الموقع:

```text
services/code\_writer.py
```

المسؤولية:

إنشاء الملفات.

الواجهات:

```python
create\_file(path, content="")
```

```python
write\_file(path, content)
```

```python
append\_file(path, content)
```

---

## FileTools**

الموقع:

```text
services/file\_tools.py
```

الواجهات:

```python
read\_file(path)
```

```python
delete\_file(path)
```

```python
list\_files(path="workspace")
```

---

## TextEditor**

الموقع:

```text
services/text\_editor.py
```

الواجهات:

```python
write(path, content)
```

```python
append(path, content)
```

---

## PythonRunner**

الموقع:

```text
services/python\_runner.py
```

الواجهة:

```python
run\_file(path)
```

---

## ProjectManager**

الموقع:

```text
services/project\_manager.py
```

الواجهات:

```python
create\_project(name)
```

```python
list\_projects()
```

```python
exists(name)
```

---

## MemoryManager**

الموقع:

```text
memory/memory\_manager.py
```

المسؤولية:

تنفيذ منطق تخزين واسترجاع الذاكرة.

الحالة:

```text
Implemented
```

الأنواع المدعومة:

```text
session
long\_term
context
```

الواجهات العامة:

```python
save(...)
get(...)
get\_entry(...)
search(...)
list\_memories(...)
delete(...)
clear\_session(...)
count(...)
health\_check(...)
```

يتم حقنه عبر:

```text
ServiceContainer
    ↓
TaskRouter
    ↓
MemoryAgent
```

---

# Plugin Contracts**

هذه العقود تخص v0.6 فقط، ولا تتجاوز حدود المكونات المنفذة حاليًا.

---

## PluginLoader**

الموقع:

```text
plugins/plugin\_loader.py
```

المسؤولية:

تحميل Python module واحد من مصدر/مسار ملف محدد.

الواجهة:

```python
PluginLoader.load(source) -> Result
```

العقد:

\- يتحقق من صلاحية المصدر قبل التحميل.
\- عند النجاح يعيد `Result.ok(...)`.
\- تكون الـmodule المحملة داخل `Result.data`.
\- يمكن أن يتضمن `Result.metadata` اسم الـmodule.
\- عند الفشل يعيد `Result.fail(...)`.
\- لا يرفع Exception غير معالج إلى المستدعي.

الحدود:

\- لا يسجل Plugins.
\- لا يدير Plugin lifecycle.
\- لا يفعّل أو يعطّل Plugins.
\- لا ينفذ Dynamic Discovery على مجموعة Plugins.
\- لا يعدّل Core.
\- لا يعدّل Services.

---

## PluginManager**

الموقع:

```text
plugins/plugin\_manager.py
```

المسؤولية:

إدارة Plugins التي تم تحميلها صراحةً.

الواجهة:

```python
PluginManager.load(source) -> Result
```

```python
PluginManager.get(name) -> Result
```

```python
PluginManager.remove(name) -> Result
```

```python
PluginManager.list() -> Result
```

العقد:

### load**

\- يستدعي `PluginLoader`.
\- يسجل الـPlugin المحمّل باسم الـmodule.
\- يمنع التسجيل المكرر.
\- يعيد `Result`.
\- يعيد اسم الـPlugin وعدد الـPlugins في `metadata` عند الحاجة.

### get**

\- يستقبل اسم Plugin صالح.
\- يعيد الـPlugin المحمّل عبر `Result.ok(...)`.
\- يعيد `Result.fail(...)` إذا لم يكن مسجلًا أو كان الاسم غير صالح.

### remove**

\- يزيل Plugin مسجلًا من حالة المدير.
\- يعيد الـPlugin الذي تمت إزالته عبر `Result.ok(...)`.
\- يفشل إذا كان الاسم غير صالح أو غير مسجل.

### list**

\- يعيد أسماء Plugins المحمّلة حاليًا.
\- يعيد القائمة مرتبة.
\- يعيد عدد العناصر في `metadata`.

الحدود:

\- يعتمد على `PluginLoader` لتحميل Plugin واحد.
\- لا ينفذ Dynamic Discovery المتقدم.
\- لا يطبق enable/disable lifecycle المتقدم.
\- لا يعدّل Core.
\- لا يعدّل Services.

---

# Plugin Extension Boundary

الإضافات المستقبلية في v0.6 وما بعده يجب أن تحافظ على الفصل بين:

```text
PluginLoader
    ↓
PluginManager
    ↓
Plugin Lifecycle
    ↓
Capability Registration / Discovery
```

تم اعتماد `enable` و`disable` ضمن `Advanced Plugin Lifecycle Contract`.

تم اعتماد واجهات Capability Registration / Discovery التالية: `register`, `get`, `list`, `remove`.

أما Dynamic Plugin Discovery فتظل غير معرّفة حتى اعتماد عقدها رسميًا.

---

# Advanced Plugin Lifecycle Contract

## PluginLifecycle

الموقع:

```text
plugins/plugin_lifecycle.py
```

المسؤولية:

إدارة الحالة التشغيلية للـPlugins المسجلة، دون تحميلها أو اكتشافها أو إدارة السجل المركزي.

الواجهات:

```python
PluginLifecycle.enable(name: str) -> Result
PluginLifecycle.disable(name: str) -> Result
```

### enable

- يستقبل اسم Plugin صالح.
- يفشل إذا كان الـPlugin غير مسجل.
- يغيّر حالة الـPlugin إلى `enabled`.
- إذا كان الـPlugin مفعّلًا بالفعل، يعيد `Result.fail(...)`.
- لا يحمل Plugin جديدًا.
- لا ينفذ Dynamic Discovery.

### disable

- يستقبل اسم Plugin صالح.
- يفشل إذا كان الـPlugin غير مسجل.
- يغيّر حالة الـPlugin إلى `disabled`.
- إذا كان الـPlugin معطّلًا بالفعل، يعيد `Result.fail(...)`.
- لا يحذف Plugin من Registry.
- لا ينفذ Dynamic Discovery.

### Return Contract

جميع العمليات العامة تعيد:

```python
Result
```

### الحدود

PluginLifecycle لا يقوم بـ:

- تحميل Python modules.
- استدعاء `importlib`.
- تسجيل Plugin في Registry.
- إزالة Plugin من Registry.
- Dynamic Plugin Discovery.
- Capability Registration / Discovery.
- تنفيذ منطق Core.
- تنفيذ منطق Services.

حالة العقد:

```text
Approved — Implementation Pending
```

---


---

# Capability Registration / Discovery Contract**

## CapabilityRegistry**

الموقع:

```text
plugins/capability_registry.py
```

المسؤولية:

إدارة تسجيل واكتشاف القدرات التي تعلنها الـPlugins داخل نظام Plugins.

الواجهات:

```python
CapabilityRegistry.register(
    plugin_name: str,
    capability_name: str,
    capability: object,
) -> Result
```

```python
CapabilityRegistry.get(
    capability_name: str,
) -> Result
```

```python
CapabilityRegistry.list(
    plugin_name: str | None = None,
) -> Result
```

```python
CapabilityRegistry.remove(
    plugin_name: str,
    capability_name: str,
) -> Result
```

### register**

- يستقبل اسم Plugin صالحًا.
- يستقبل اسم Capability صالحًا.
- يسجل الـCapability تحت الـPlugin المحدد.
- يرفض التسجيل المكرر لنفس الـPlugin ونفس اسم الـCapability.
- يعيد `Result.ok(...)` عند النجاح.
- يعيد `Result.fail(...)` عند فشل التحقق أو وجود تسجيل مكرر.

### get**

- يستقبل اسم Capability صالح.
- يعيد الـCapability المسجلة عبر `Result.ok(...)`.
- يعيد `Result.fail(...)` إذا لم تكن Capability مسجلة.

### list**

- بدون `plugin_name`: يعيد جميع الـCapabilities المسجلة.
- مع `plugin_name`: يعيد Capabilities الخاصة بالـPlugin المحدد.
- يعيد `Result.ok(...)`.
- يعيد قائمة مرتبة.
- لا ينفذ أي Capability.

### remove**

- يستقبل اسم Plugin واسم Capability صالحين.
- يزيل Capability المسجلة تحت Plugin المحدد.
- يعيد `Result.ok(...)` عند النجاح.
- يعيد `Result.fail(...)` إذا لم تكن Capability مسجلة.

### الحدود**

CapabilityRegistry لا يقوم بـ:

- تحميل Python modules.
- تسجيل أو إزالة Plugins في `PluginRegistry`.
- إدارة Plugin lifecycle.
- enable/disable.
- Dynamic Plugin Discovery.
- تنفيذ Capability.
- تنفيذ منطق Core.
- تنفيذ منطق Services.

### Return Contract**

جميع الواجهات العامة تعيد:

```python
Result
```

حالة العقد:

```text
Approved — Implementation Pending
```

---

# Execution Contract**

دورة التنفيذ الرسمية للنواة الحالية:

```text
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

# Dependency Rules**

يسمح فقط بالعلاقات التالية:

```text
Agents
        ↓
Core
        ↓
Services
        ↓
Utilities
```

ويمنع:

```text
Service → Agent
Service → Router
Service → Parser
Agent → Service مباشرة
```

ويجب أن تمر عمليات Coding عبر:

```text
CommandDispatcher
```

أما Memory وPlugin فلهما حدود طبقية مستقلة وفق عقودهما الخاصة.

---

# Return Contract**

أي عملية عامة داخل المشروع يجب أن تعيد:

```python
Result
```

ولا يجوز إعادة:

```text
dict
list
str
bool
```

بشكل مباشر بين طبقات المشروع عندما تكون العملية جزءًا من عقد عام بين الطبقات.

---

# Extension Contract**

أي Service جديدة يجب تسجيلها داخل:

```text
ServiceContainer
```

وأي Agent جديد يجب تسجيله داخل:

```text
TaskRouter
```

وأي أمر جديد يجب إضافته داخل:

```text
CommandDispatcher
```

وأي Plugin capability جديدة يجب اعتماد عقدها العام في هذا الملف قبل تنفيذها.

---

# Version Compatibility**

تم اعتماد العقود الأساسية ابتداءً من:

```text
AllAffiliate\_Agent v0.4
```

وأضيفت عقود Plugin الحالية في:

```text
AllAffiliate\_Agent v0.6
```

وأي تغيير في توقيع أي دالة (Method Signature) أو واجهة عامة (Public Interface) يُعد تغييرًا معماريًا، ويجب تحديث هذا الملف أولًا قبل تعديل الكود المتأثر.

---

# Contract Status**

```text
Core Contracts
    Stable

Agent Contracts
    Stable

Service Contracts
    Stable

Memory Contracts
    Implemented

PluginLoader Contract
    Implemented

PluginManager Contract
    Implemented

Plugin Registry Contract
    Approved — Implementation Pending

Advanced Plugin Lifecycle Contract
    Approved — Implementation Pending

Capability Registration / Discovery Contract
    Approved — Implementation Pending

Dynamic Plugin Discovery Contract
    Not Defined
```

---

# Plugin Registry Contract**

## PluginRegistry**

الموقع:

```text
plugins/plugin\_registry.py
```

المسؤولية:

إدارة السجل المركزي للـPlugins المسجلة داخل النظام.

الواجهات:

```python
PluginRegistry.register(name: str, plugin: object) -> Result
PluginRegistry.get(name: str) -> Result
PluginRegistry.remove(name: str) -> Result
PluginRegistry.list() -> Result
```

### الحدود**

PluginRegistry لا يقوم بـ:

\- تحميل Python modules.
\- استدعاء `importlib`.
\- Dynamic Plugin Discovery.
\- enable/disable.
\- إدارة دورة الحياة المتقدمة.
\- تنفيذ منطق Core.
\- تنفيذ منطق Services.

حالة العقد:

```text
Approved — Implementation Pending
```

---

# End of Document**
---

# Cloud AI Foundation Contract

## Version

v0.7

## Status

Approved - Implementation Pending

## Official Path

services/cloud_ai_service.py

## Purpose

Provides a provider-neutral service boundary for cloud AI integration while preserving Core, Agents, Memory, and Plugin boundaries.

## Architecture

`	ext
Agent
    ↓
Core / Routing
    ↓
CloudAIService
    ↓
CloudAIProvider
    ↓
External Cloud AI API
`

## CloudAIProvider

Public interface:

`python
generate(prompt: str, model: str | None = None, parameters: dict | None = None) -> Result
`

Rules:

- Returns Result.
- Performs provider-specific execution.
- Does not modify Core, Agents, Memory, or Routing.
- Keeps provider-specific credentials and API details inside the provider implementation.

## CloudAIService

Public interfaces:

`python
register_provider(name: str, provider: CloudAIProvider) -> Result
remove_provider(name: str) -> Result
list_providers() -> Result
generate(prompt: str, provider: str | None = None, model: str | None = None, parameters: dict | None = None) -> Result
`

Rules:

- Provider names must be unique.
- Providers are registered explicitly.
- Missing providers return Result.fail(...).
- Provider execution failures return Result.fail(...).
- Successful operations return Result.ok(...).
- All public operations return Result.
- Provider-specific logic remains outside CloudAIService.
- CloudAIService is registered through ServiceContainer.

## Request Boundary

`	ext
prompt
provider
model
parameters
`

## Return Contract

All public operations return Result. Generation output is returned through Result.data. General execution metadata may be returned through Result.metadata.

## Dependency Rules

`	ext
Agents
    ↓
Core
    ↓
Services
    ↓
CloudAIProvider
    ↓
External Cloud AI API
`

Forbidden:

`	ext
Agent -> External Cloud AI API
Core -> External Cloud AI API
CloudAIService -> Router
CloudAIService -> Parser
CloudAIProvider -> Agent
`

## Scope Boundary

The contract is provider-neutral. Specific provider implementations, credential storage, secrets management, retries, rate limiting, cost optimization, streaming, tool calling, multimodal generation, browser automation, and video generation are outside this contract until separately approved.

## Contract Status

Approved - Implementation Pending
