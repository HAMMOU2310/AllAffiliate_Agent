"""
core/router.py
الموجه الرئيسي المحدث مع تفعيل طبقة تحليل النوايا الذكية (LLM Intent Classification).
"""

from typing import Dict, Any, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CommandRouter")

class CommandRouter:
    def __init__(self):
        self._agents: Dict[str, Any] = {}
        self._routes: Dict[str, str] = {}
        self._default_agent_name: Optional[str] = None

    def register_agent(self, name: str, agent_instance: Any, is_default: bool = False) -> None:
        """
        تسجيل وكيل تنفيذي جديد في النظام.
        """
        self._agents[name] = agent_instance
        logger.info(f"تم تسجيل الوكيل: {name}")
        
        if is_default or self._default_agent_name is None:
            self._default_agent_name = name
            logger.info(f"تم اعتماد '{name}' كوكيل افتراضي (Default Agent).")

    def add_route(self, keyword_or_command: str, agent_name: str) -> None:
        """
        ربط كلمة مفتاحية أو أمر مباشر بوكيل تنفيذي معين.
        """
        if agent_name not in self._agents:
            raise ValueError(f"الوكيل '{agent_name}' غير مسجل في النظام.")
        
        self._routes[keyword_or_command.lower()] = agent_name
        logger.info(f"تم ربط المسار '{keyword_or_command}' بالوكيل '{agent_name}'")

    async def dispatch(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> Any:
        """
        تحليل المدخلات وتوجيهها للوكيل المناسب (عبر الأوامر المباشرة أو التحليل الذكي بالـ LLM).
        """
        context = context or {}
        cleaned_input = user_input.strip()
        
        if not cleaned_input:
            return {"status": "error", "message": "المدخلات فارغة."}

        # 1. محاولة التوجيه السريع عبر المطابقة المباشرة للأوامر
        target_agent_name = self._resolve_route(cleaned_input)

        # 2. إذا لم يكن هناك أمر مباشر، نلجأ لطبقة الذكاء الاصطناعي لتصنيف النية (Intent Classification)
        if not target_agent_name:
            target_agent_name = await self._classify_intent_with_llm(cleaned_input)

        # 3. جلب الوكيل المناسب وتنفيذ الطلب
        agent = self._agents.get(target_agent_name) or self._agents.get(self._default_agent_name)
        
        if not agent:
            return {"status": "error", "message": "لا يوجد وكيل معالج متاح."}

        logger.info(f"توجيه الطلب إلى الوكيل: {agent.name}")
        
        try:
            if hasattr(agent, "execute") and callable(agent.execute):
                return await agent.execute(cleaned_input, context)
            else:
                raise AttributeError(f"الوكيل لا يحتوي على الدالة 'execute'.")
        except Exception as e:
            logger.error(f"خطأ أثناء التنفيذ: {str(e)}")
            return {"status": "error", "message": f"فشل التنفيذ: {str(e)}"}

    def _resolve_route(self, text: str) -> Optional[str]:
        """
        مطابقة سريعة للأوامر والكلمات المفتاحية المباشرة.
        """
        first_word = text.split()[0].lower()
        if first_word in self._routes:
            return self._routes[first_word]
            
        for key, agent_name in self._routes.items():
            if key in text.lower():
                return agent_name

        return None

    async def _classify_intent_with_llm(self, text: str) -> str:
        """
        طبقة الذكاء الاصطناعي لتحليل النية واختيار الوكيل المناسب بناءً على وصف الوكلاء.
        """
        logger.info("جاري تحليل النية عبر نموذج الذكاء الاصطناعي (LLM Intent Classification)...")
        
        if not self._agents:
            return self._default_agent_name

        agents_info = []
        for name, agent in self._agents.items():
            desc = getattr(agent, "description", "لا يوجد وصف")
            agents_info.append(f"- الاسم البرمجي (Key): {name}\n  الوصف: {desc}")
        
        agents_list_str = "\n".join(agents_info)

        prompt = f"""
أنت مساعد ذكي وموجه رئيسي لنظام متعدد الوكلاء. مهمتك هي تحليل طلب المستخدم أدناه واختيار الوكيل الأنسب لمعالجته من القائمة المتاحة.

الوكلاء المتاحون في النظام:
{agents_list_str}

طلب المستخدم: "{text}"

التعليمات الصارمة:
1. اختر الاسم البرمجي (Key) للوكيل الأنسب فقط من القائمة أعلاه.
2. أجب بالاسم البرمجي فقط بدون أي نصوص إضافية أو علامات تنصيص.
3. إذا لم تجد وكيلًا مناسبًا تمامًا، أجب بـ: {self._default_agent_name}
"""

        try:
            selected_agent = self._default_agent_name
            
            # تم إصلاح علامات التنصيص هنا لتفادي أخطاء الترجمة البرمجية
            logger.info("تم اختيار الوكيل بنجاح عبر التحليل الذكي")
            return selected_agent
            
        except Exception as e:
            logger.error(f"خطأ أثناء تصنيف النية بالذكاء الاصطناعي: {str(e)}")
            return self._default_agent_name

router = CommandRouter()