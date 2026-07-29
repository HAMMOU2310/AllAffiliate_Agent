import logging
import os
from datetime import datetime

class SystemLogger:
    def __init__(self, log_dir="logs"):
        # إنشاء مجلد السجلات إذا لم يكن موجوداً
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        # إنشاء ملف سجل جديد لكل يوم
        current_date = datetime.now().strftime("%Y-%m-%d")
        log_file = os.path.join(log_dir, f"system_{current_date}.log")
        
        # إعداد إعدادات التسجيل
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format='%(asctime)s | [%(levelname)s] | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        # لإيقاف طباعة السجلات من المكتبات الخارجية وإبقائها نقية لنظامنا
        self.logger = logging.getLogger("MultiAgentLogger")

    def log_activity(self, agent_name: str, task_type: str, status: str, details: str = ""):
        """تسجيل أي نشاط يحدث داخل النظام."""
        message = f"Agent: {agent_name} | Task: {task_type} | Status: {status.upper()} | Details: {details}"
        
        if status.lower() == "error":
            self.logger.error(message)
        else:
            self.logger.info(message)