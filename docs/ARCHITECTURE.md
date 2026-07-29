# Architecture

**Project:** AllAffiliate_Agent

**Version:** 0.3

**Status:** Active

**Last Updated:** 2026-07-16

**Owner:** AllAffiliate_Agent Team

---

# الهدف

يوضح هذا المستند معمارية مشروع AllAffiliate_Agent وكيفية تفاعل جميع المكونات مع بعضها.

يعتبر هذا المستند المرجع الرسمي للبنية الهندسية للمشروع.

---

# المبادئ المعمارية

يعتمد المشروع على المبادئ التالية:

- Hybrid Architecture
- Clean Architecture
- Separation of Concerns
- Single Responsibility Principle
- Open/Closed Principle
- Dependency Injection (مستقبلاً)
- Modular Design
- Testable Components
- Reusable Components

---

# الطبقات

يتكون المشروع من الطبقات التالية:

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

---

# مسؤولية كل طبقة

## User

هو مصدر جميع الطلبات.

لا يتعامل مباشرة مع أي طبقة أخرى.

---

## MasterAgent

المسؤول عن استقبال جميع الطلبات.

يقوم بتحويل الطلب إلى Task.

ثم يرسله إلى TaskRouter.

---

## TaskRouter

يحدد الوكيل المناسب لتنفيذ المهمة.

لا يحتوي على if/elif طويلة.

يعتمد على AgentRegistry.

---

## AgentRegistry

يحتوي على جميع الوكلاء المسجلين داخل النظام.

يسمح بإضافة وكلاء جدد دون تعديل TaskRouter.

---

## Agent

يمثل منطق اتخاذ القرار.

يقوم بـ:

- تحليل المهمة.
- استدعاء Service المناسب.
- إعادة Result.

لا يحتوي على منطق تنفيذ منخفض المستوى.

---

## Service

يمثل منطق الأعمال (Business Logic).

يقوم بتنسيق العمليات.

يمكنه استخدام أكثر من Tool.

لا يتعامل مع المستخدم مباشرة.

---

## Tool

يمثل العمليات منخفضة المستوى.

مثل:

- الملفات.
- الطرفية.
- Python.
- الشبكات.
- قواعد البيانات.

لا يعرف شيئًا عن Agents أو Services.

---

## Operating System

الطبقة الأخيرة.

تنفذ العمليات الفعلية داخل Windows أو أي نظام تشغيل آخر.

---

# تدفق التنفيذ

User

↓

MasterAgent

↓

Task

↓

TaskRouter

↓

Agent

↓

Service

↓

Tool

↓

Operating System

↓

Result

↓

Agent

↓

MasterAgent

↓

User

---

# قواعد الاتصال

يسمح بالاتصال فقط بالاتجاه التالي:

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

Operating System

---

لا يسمح بـ:

- Agent → Operating System مباشرة.
- Agent → Tool مباشرة.
- Tool → Agent.
- Tool → User.
- Service → User.

---

# إضافة Agent جديد

لإضافة Agent جديد يجب:

1. إنشاء Agent.
2. إنشاء Service الخاص به.
3. إنشاء Tools عند الحاجة.
4. تسجيله داخل AgentRegistry.
5. اختباره.
6. تحديث الوثائق.

---

# إضافة Tool جديد

لإضافة Tool جديد يجب:

- أن يكون مستقلاً.
- قابلاً للاختبار.
- لا يعتمد على Agent.
- لا يعتمد على Service.
- يعيد Result.

---

# قواعد التطوير

- جميع العمليات تعيد Result.
- جميع الطلبات تمثل Task.
- جميع Agents يرثون من BaseAgent.
- جميع Services مستقلة.
- جميع Tools مستقلة.
- يمنع استخدام if/elif الطويل.
- يمنع الوصول المباشر إلى نظام التشغيل من Agent.
- كل ملف يجب أن يكون قابلاً للاختبار.

---

# سجل المراجعات

| التاريخ | الإصدار | التغيير |
|----------|----------|----------|
| 2026-07-16 | 0.3 | إنشاء الوثيقة لأول مرة |