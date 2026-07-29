class ProductAgent:
    def __init__(self):
        self.name = "ProductAgent"
        self.version = "1.0.0"

    def process_task(self, task_type: str, payload: dict):
        """معالجة المهام الموجهة إلى وكيل المنتجات."""
        if task_type == "fetch_offers":
            return self.fetch_offers(payload.get("niche", "general"))
        else:
            return {"status": "error", "message": f"نوع المهمة '{task_type}' غير مدعوم في ProductAgent."}

    def fetch_offers(self, niche: str):
        """محاكاة جلب عروض أفلييت من شبكات مختلفة."""
        # محاكاة لبيانات قادمة من API (مثل ClickBank أو CJ Affiliate)
        all_offers = [
            {"id": 101, "name": "استضافة الويب السحابية", "commission": 50.0, "niche": "tech", "status": "active"},
            {"id": 102, "name": "دورة التسويق الرقمي", "commission": 25.0, "niche": "education", "status": "active"},
            {"id": 103, "name": "أداة السيو الاحترافية", "commission": 40.0, "niche": "tech", "status": "active"},
            {"id": 104, "name": "مكمل غذائي للطاقة", "commission": 15.0, "niche": "health", "status": "inactive"}
        ]
        
        # تصفية العروض بناءً على التخصص (Niche)
        if niche != "general":
            filtered_offers = [offer for offer in all_offers if offer["niche"] == niche]
        else:
            filtered_offers = all_offers
            
        return {
            "status": "success", 
            "data": {
                "niche_requested": niche,
                "offers": filtered_offers, 
                "total_found": len(filtered_offers)
            }
        }