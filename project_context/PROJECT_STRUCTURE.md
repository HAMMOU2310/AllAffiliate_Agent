# PROJECT_STRUCTURE.md

# AllAffiliate_Agent

**Project Structure Document**

**Version:** v0.4

**Architecture:** Clean Architecture

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
15. Testing Layer
16. Project Files
17. Dependency Flow
18. Execution Flow
19. File Naming Rules
20. Folder Rules
21. Expansion Rules

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

# 15. Testing Layer

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

# 16. Project Files

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

# 17. Dependency Flow

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

# 18. Execution Flow

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

# 19. File Naming Rules

- جميع الملفات تستخدم snake_case.
- أسماء الفئات تستخدم PascalCase.
- أسماء الدوال تستخدم snake_case.
- أسماء المتغيرات واضحة.
- يمنع استخدام أسماء مبهمة.

---

# 20. Folder Rules

- كل مجلد مسؤول عن مجال واحد فقط.
- يمنع وضع ملفات عشوائية في الجذر.
- يمنع تكرار الوظائف بين المجلدات.
- يمنع إنشاء مجلد جديد دون سبب واضح.
- كل ملف يجب أن يكون له مسؤولية واحدة.

---

# 21. Expansion Rules

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