# Testing Guide

**Project:** AllAffiliate_Agent

**Version:** 1.0.0

**Status:** Stable Release

**Last Updated:** 2026-09-23

**Owner:** AllAffiliate_Agent Team

---

# الهدف

يوضح هذا المستند سياسة الاختبارات المعتمدة في مشروع AllAffiliate_Agent.

الهدف هو ضمان أن كل مكون يعمل بصورة صحيحة قبل الانتقال إلى المكون التالي.

---

# المبادئ الأساسية

- لا يعتبر أي ملف مكتملاً قبل اختباره.
- لا يتم تجاوز أي خطأ دون إصلاحه.
- جميع الاختبارات يجب أن تكون قابلة لإعادة التنفيذ.
- يتم اختبار كل مكون بشكل مستقل قبل دمجه مع بقية النظام.

---

# أنواع الاختبارات

## 1. Unit Test

اختبار ملف أو مكون واحد بشكل مستقل.

أمثلة:

- FileTools
- TerminalTools
- PythonTools
- Result
- Task

---

## 2. Integration Test

اختبار تفاعل أكثر من مكون معًا.

أمثلة:

Agent

↓

Service

↓

Tool

---

## 3. System Test

اختبار تدفق تنفيذ المهمة بالكامل.

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

Result

---

# خطوات الاختبار

لكل ملف جديد نتبع الترتيب التالي:

1. إنشاء الملف.
2. مراجعة الكود.
3. تشغيل الاختبار.
4. التحقق من النتائج.
5. إصلاح الأخطاء إن وجدت.
6. إعادة الاختبار.
7. اعتماد الملف.

---

# معايير النجاح

يعتبر الاختبار ناجحًا إذا:

- لم تظهر أي أخطاء (Exceptions).
- كانت النتائج مطابقة للمتوقع.
- لم يتم كسر أي جزء من المشروع.
- اجتاز الملف جميع حالات الاختبار الخاصة به.

---

# تنظيم ملفات الاختبار

حالياً:

workspace/

يستخدم للاختبارات المؤقتة.

---

مستقبلاً:

tests/

سيحتوي على جميع ملفات الاختبارات الدائمة.

مثل:

- test_file_tools.py
- test_terminal_tools.py
- test_python_tools.py
- test_project_manager.py

---

# توثيق الاختبارات

كل اختبار يجب أن يتضمن:

- اسم الملف.
- الهدف من الاختبار.
- خطوات التنفيذ.
- النتيجة المتوقعة.
- النتيجة الفعلية.
- الحالة (نجاح / فشل).

---

# سياسة إصلاح الأخطاء

عند ظهور أي خطأ:

1. تحديد سبب المشكلة.
2. إصلاح السبب الجذري.
3. إعادة تشغيل الاختبار.
4. التأكد من عدم تأثر بقية المشروع.

---

# أدوات الاختبار

حالياً:

- Python
- VS Code
- PowerShell

مستقبلاً:

- pytest
- unittest
- CI/CD Pipelines

---

# سجل المراجعات

| التاريخ | الإصدار | التغيير |
|----------|----------|----------|
| 2026-07-16 | 0.3 | إنشاء الوثيقة لأول مرة |
| 2026-09-23 | 1.0.0 | تحديث الإصدار وخط الأساس النهائي للاختبارات |

---

## نتائج الاختبارات النهائية — v1.0.0 Stable Release — 23 سبتمبر 2026

### بيئة العمل
- المشروع: AllAffiliate_Agent
- الإصدار: v1.0.0 Stable Release
- Release Commit: be52c49
- Release Tag: v1.0.0
- Python: 3.12.0
- البيئة الافتراضية: myenv

### خط الأساس النهائي للاختبارات

```text
1009 collected
1004 passed
3 failed (known Gemini external API flakiness)
2 skipped (expected OpenSERP environment skips)
0 errors
```

### الفئات المعروفة

- **3 Gemini-flaky failures**: test_full_pipeline_returns_validated_draft, test_pipeline_preserves_provider_neutrality, test_metadata_contains_format — اختبارات API خارجي، غير حاسمة
- **2 OpenSERP skips**: اختبارات تتطلب خادم OpenSERP محلي، متوقعة

### ملاحظة

يجب استخدام Python الموجود داخل myenv أثناء الاختبار والتطوير.

```powershell
.\myenv\Scripts\python.exe -m pytest -q
```
