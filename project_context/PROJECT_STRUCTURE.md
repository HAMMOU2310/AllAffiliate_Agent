# AllAffiliate_Agent

## Project Structure Document

**Version:** v1.0

**Architecture:** Clean Architecture — v1.0 local integration validated

**Design Pattern:** Multi-Agent System

**Document Version:** 1.0

**Status:** Synchronized with the validated v1.0 repository structure

---

# 1. Document Purpose

هذا الملف هو المرجع الرسمي للهيكل الفعلي لمشروع AllAffiliate_Agent.

يحدد:

- المجلدات الرسمية.
- مسؤولية كل طبقة.
- مواقع المكونات الحالية.
- حدود الاعتماد بين الطبقات.
- ملفات الدخول والتشغيل.
- مواقع الاختبارات الحالية.
- قواعد التوسع البنيوي.

أي ملف أو مجلد جديد يغير البنية الرسمية يجب أن ينعكس في هذا الملف.

النصوص الخاصة بالإصدارات السابقة تمثل التاريخ المعماري ولا تُعد وصفًا للبنية الحالية.

---

# 2. Current Repository Structure

البنية الحالية المعتمدة لـ v1.0 هي:

```text
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
├── providers/
├── services/
├── workspace/
│
├── assistant.py
├── launcher.py
├── requirements.txt
├── README.md
└── .gitignore