import json
from coding_agent import CodingAgent
from analytics_agent import AnalyticsAgent
from product_agent import ProductAgent
from system_logger import SystemLogger  # استيراد نظام السجلات

class MultiAgentSystem:
    def __init__(self, config_path="agent_config.json"):
        # تهيئة نظام السجلات
        self.logger = SystemLogger()
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except Exception as e:
            self.config = {}

        self.agents = {
            "CodingAgent": CodingAgent(),
            "AnalyticsAgent": AnalyticsAgent(),
            "ProductAgent": ProductAgent()
        }
            
        print(f"تم تهيئة النظام بنجاح. الوكلاء المتاحون: {list(self.agents.keys())}")
        self.logger.log_activity("SYSTEM", "Initialization", "Success", "System started and agents loaded.")

    def dispatch_task(self, agent_name: str, task_type: str, payload: dict):
        if agent_name in self.agents:
            try:
                # محاولة تنفيذ المهمة
                result = self.agents[agent_name].process_task(task_type, payload)
                
                # تسجيل النجاح
                status = result.get("status", "unknown")
                self.logger.log_activity(agent_name, task_type, status, f"Payload keys: {list(payload.keys())}")
                
                return result
            
            except Exception as e:
                # تسجيل الخطأ في حال حدوث عطل داخل الوكيل
                self.logger.log_activity(agent_name, task_type, "Error", str(e))
                return {"status": "error", "message": f"حدث خطأ داخلي في الوكيل: {e}"}
        else:
            # تسجيل محاولة استدعاء وكيل غير موجود
            self.logger.log_activity("SYSTEM", "Dispatch", "Error", f"Agent '{agent_name}' not found.")
            return {"status": "error", "message": f"الوكيل '{agent_name}' غير مسجل في النظام."}

# تجربة التشغيل
if __name__ == "__main__":
    system = MultiAgentSystem()
    
    print("\n[1] ProductAgent: جلب عروض الأفلييت (تخصص: التقنية)...")
    products_result = system.dispatch_task("ProductAgent", "fetch_offers", {"niche": "tech"})
    
    if products_result.get("status") == "success":
        offers_data = products_result.get("data")
        print(f"-> تم جلب {offers_data['total_found']} عروض بنجاح.")
        
        print("\n[2] AnalyticsAgent: تحليل العروض المستخرجة...")
        analytics_result = system.dispatch_task("AnalyticsAgent", "analyze_data", {"data": offers_data})
        print("-> نتيجة التحليل:\n", json.dumps(analytics_result, indent=4, ensure_ascii=False))
        
        # تجربة استدعاء مهمة خاطئة لاختبار السجلات
        print("\n[3] تجربة استدعاء مهمة خاطئة (لاختبار نظام الأخطاء)...")
        error_result = system.dispatch_task("ProductAgent", "unknown_task", {})
        print(f"-> النتيجة: {error_result['message']}")