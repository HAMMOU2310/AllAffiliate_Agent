import streamlit as st
import os
import json
from agent_system import MasterAgent

# إعداد الصفحة وتصميمها
st.set_page_config(
    page_title="AllAffiliate_Agent Dashboard",
    page_icon="🤖",
    layout="wide"
)

# دعم التنسيق من اليمين لليسار (للغة العربية)
st.markdown(
    """
    <style>
    body, .stApp {
        direction: rtl;
        text-align: right;
    }
    .stTextInput, .stTextArea, .stButton {
        direction: rtl;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🚀 لوحة تحكم النظام المتعدد الوكلاء (AllAffiliate_Agent)")
st.markdown("تحكم في توليد الأكواد، المحتوى التسويقي، سيناريوهات الفيديوهات، وأوامر الصور والصوت بضغط زر واحدة.")

# القيمة الافتراضية للطلب
default_prompt = (
    "أريد تطوير نظام آلة حاسبة متقدمة بلغة بايثون، "
    "واكتب إعلاناً تسويقياً ترويجياً لهذه الآلة الحاسبة، "
    "ثم قم بإنشاء سيناريو فيديو ريلز قصير (10 إلى 15 ثانية) يعتمد كلياً على شبكة صور متسلسلة (20-panel grid) "
    "يوضح التطور الزمني لأدوات الحساب؛ بدءاً من العداد الخشبي القديم (Abacus) وصولاً إلى الآلة الحاسبة الذكية المتقدمة، "
    "مع دمج خدع بصرية وانتقالات خاطفة بين اللوحات، "
    "بعد ذلك قم بتحويل هذا السيناريو إلى أوامر نصية لتوليد الصور باللغة الإنجليزية (Text-based Image Prompts)، "
    "ثم اقترح موسيقى خلفية مشرقة ومجانية تماماً (بدون حقوق طبع والنشر) تتناسب مع هذا التحول الزمني، "
    "وأخيراً قم برفع كافة الملفات الناتجة إلى مستودع GitHub."
)

user_prompt = st.text_area("أدخل طلبك للنظام (Prompt):", value=default_prompt, height=150)

if st.button("🚀 بدء تشغيل الوكلاء وتوليد الأصول", type="primary"):
    if not user_prompt.strip():
        st.warning("الرجاء إدخال وصف الطلب أولاً!")
    else:
        with st.status("🧠 جاري معالجة الطلب عبر الوكلاء...", expanded=True) as status:
            st.write("[MasterAgent] تهيئة النظام وبدء التوجيه...")
            
            # تشغيل الموجه الرئيسي
            master = MasterAgent()
            result = master.process_request(user_prompt)
            
            st.write("✅ تم اكتمال العمليات بنجاح ورفع الملفات إلى GitHub!")
            status.update(label="✨ اكتملت العملية بنجاح!", state="complete", expanded=False)

        st.success("تم تنفيذ المهام وتحديث الملفات في مجلد `output` ومستودع GitHub بنجاح.")

st.markdown("---")
st.subheader("📂 معاينة المخرجات الحالية (Output Files)")

# مجلد المخرجات
output_dir = "output"

if os.path.exists(output_dir):
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "💻 الكود البرمجي", 
        "📢 الإعلان التسويقي", 
        "🎬 سيناريو الفيديو", 
        "🎨 أوامر الصور", 
        "🎵 اقتراحات الصوت"
    ])

    with tab1:
        app_path = os.path.join(output_dir, "app.py")
        if os.path.exists(app_path):
            with open(app_path, "r", encoding="utf-8") as f:
                st.code(f.read(), language="python")
        else:
            st.info("لم يتم العثور على ملف الكود بعد.")

    with tab2:
        ad_path = os.path.join(output_dir, "affiliate_ad.txt")
        if os.path.exists(ad_path):
            with open(ad_path, "r", encoding="utf-8") as f:
                st.text_area("النص التسويقي:", f.read(), height=300)
        else:
            st.info("لم يتم العثور على النص التسويقي بعد.")

    with tab3:
        video_path = os.path.join(output_dir, "video_prompt.txt")
        if os.path.exists(video_path):
            with open(video_path, "r", encoding="utf-8") as f:
                st.text_area("سيناريو الفيديو:", f.read(), height=300)
        else:
            st.info("لم يتم العثور على سيناريو الفيديو بعد.")

    with tab4:
        img_path = os.path.join(output_dir, "image_prompts_en.txt")
        if os.path.exists(img_path):
            with open(img_path, "r", encoding="utf-8") as f:
                st.text_area("أوامر الصور الإنجليزية:", f.read(), height=300)
        else:
            st.info("لم يتم العثور على أوامر الصور بعد.")

    with tab5:
        audio_path = os.path.join(output_dir, "audio_suggestions.txt")
        if os.path.exists(audio_path):
            with open(audio_path, "r", encoding="utf-8") as f:
                st.text_area("اقتراحات الموسيقي:", f.read(), height=300)
        else:
            st.info("لم يتم العثور على اقتراحات الصوت بعد.")
else:
    st.info("مجلد المخرجات غير موجود بعد. قم بتشغيل النظام لأول مرة.")