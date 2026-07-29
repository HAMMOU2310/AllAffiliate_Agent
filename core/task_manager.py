from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class Task:
    """كائن يمثل المهمة بعد تحليلها وتجهيزها للتوجيه"""
    command: str
    intent: str
    parameters: Dict[str, Any]

class TaskManager:
    """مدير المهام المسؤول عن تحليل الأوامر النصية واستخراج النوايا"""
    
    def __init__(self):
        # تمهيد لإضافة نماذج معالجة اللغة الطبيعية (NLP) لاحقاً لزيادة دقة التحليل
        pass

    def create_task(self, command: str) -> Task:
        """يستقبل الأمر النصي ويعيد كائن مهمة مهيكل"""
        intent = self._extract_intent(command)
        
        # استخراج المعطيات الإضافية يمكن برمجته هنا
        parameters = {} 
        
        return Task(command=command, intent=intent, parameters=parameters)

    def _extract_intent(self, command: str) -> str:
        """تحليل أولي دقيق لتحديد نوع المهمة بناءً على الكلمات المفتاحية"""
        command_lower = command.lower()
        
        # تصنيف نوايا توليد المحتوى المرئي
        if any(keyword in command_lower for keyword in ["فيديو", "صور", "reels", "شبكة", "مشهد"]):
            return "video_image_generation"
            
        # تصنيف نوايا إدارة الأعمال والتسويق
        elif any(keyword in command_lower for keyword in ["عمولة", "تسويق", "منتج", "affiliate", "رابط"]):
            return "affiliate_management"
            
        # تصنيف نوايا البرمجة والتطوير
        elif any(keyword in command_lower for keyword in ["كود", "برنامج", "تطبيق", "git"]):
            return "coding"
            
        # النية الافتراضية للبحث أو الأوامر العامة
        return "general_query"