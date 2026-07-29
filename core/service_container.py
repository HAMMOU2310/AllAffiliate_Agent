import os
from dotenv import load_dotenv

class ServiceContainer:
    """حاوية مركزية لإدارة كافة الخدمات والاتصالات الخارجية في النظام"""

    def __init__(self):
        # تحميل متغيرات البيئة من ملف .env لتأمين مفاتيح التشفير
        load_dotenv()
        
        # قاموس داخلي لتخزين الموارد والخدمات النشطة
        self._services = {}
        
        # تهيئة الخدمات فور انطلاق الحاوية
        self._initialize_services()

    def _initialize_services(self):
        """تجهيز وإعداد الاتصالات الخارجية (APIs, Databases, etc.)"""
        
        # 1. تهيئة خدمة الذكاء الاصطناعي (سيتم بناء ملف الخدمة لاحقاً)
        # api_key = os.getenv("AI_API_KEY")
        # self._services["llm"] = LLMProvider(api_key)
        
        # 2. تهيئة خدمات إدارة الملفات والنظام
        # self._services["file_system"] = FileSystemService()
        pass

    def register(self, service_name: str, service_instance):
        """تسجيل خدمة جديدة ديناميكياً داخل الحاوية"""
        self._services[service_name] = service_instance

    def get(self, service_name: str):
        """استدعاء خدمة محددة. يعيد None في حال عدم توفرها"""
        return self._services.get(service_name)