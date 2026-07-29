"""
main.py
ملف التشغيل والاختبار
"""
import asyncio
from core.router import router
from agents.affiliate_agent import AffiliateAgent

async def main():
    # 1. تهيئة وكيل التسويق
    affiliate_agent = AffiliateAgent()
    
    # 2. تسجيل الوكيل في الموجه
    router.register_agent(name="affiliate", agent_instance=affiliate_agent, is_default=True)
    
    # 3. ربط مسارات محددة بالوكيل
    router.add_route("/product", "affiliate")
    router.add_route("تسويق", "affiliate")
    
    # 4. اختبار توجيه طلب
    user_request = "/product استخراج تفاصيل المنتج الجديد"
    print(f"الطلب المدخل: {user_request}\n")
    
    # 5. تنفيذ الطلب
    response = await router.dispatch(user_request)
    print("نتيجة التنفيذ:", response)

if __name__ == "__main__":
    asyncio.run(main())