import json
import os
import subprocess
from dotenv import load_dotenv
from openai import OpenAI

# تحميل المتغيرات البيئية من ملف .env
load_dotenv()

# 1. تهيئة عميل الذكاء الاصطناعي لقراءة المفتاح تلقائياً من .env
client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY")
)

# إنشاء مجلد للمخرجات
os.makedirs("output", exist_ok=True)


# --- الوكلاء التنفيذيون الحقيقيون ---

class CodingAgent:
    def execute(self, task_description, technologies="python"):
        print(f"\n[👨‍💻 CodingAgent] 🚀 جاري كتابة الكود البرمجي وحفظه...")
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "أنت مبرمج خبير. قم بكتابة الكود المطلوب فقط بدون أي شرح جانبي. أعد الكود كـ Plain Text."},
                {"role": "user", "content": f"اكتب كود {technologies} لـ: {task_description}"}
            ]
        )
        
        code_content = response.choices[0].message.content.strip()
        code_content = code_content.replace("```python", "").replace("```", "").strip()
        
        file_path = "output/app.py"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(code_content)
            
        print(f"[👨‍💻 CodingAgent] ✅ تم إنشاء الملف البرمجي في: {file_path}")
        return {
            "status": "success",
            "message": f"تم كتابة الكود وحفظه بنجاح في {file_path}",
            "generated_code_snippet": code_content[:300] + "\n...(تم الاختصار)"
        }


class AffiliateAgent:
    def execute(self, product_description, target_audience="المهتمين بالتقنية"):
        print(f"\n[💰 AffiliateAgent] 📣 جاري كتابة محتوى تسويقي للمنتج...")
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "أنت خبير تسويق بالعمولة (Affiliate Marketing). اكتب إعلاناً جذاباً ومباشراً يشجع على استخدام هذا المنتج أو الأداة."},
                {"role": "user", "content": f"اكتب إعلاناً تسويقياً لـ: {product_description}. الجمهور المستهدف: {target_audience}."}
            ]
        )
        
        ad_copy = response.choices[0].message.content.strip()
        file_path = "output/affiliate_ad.txt"
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(ad_copy)
            
        print(f"[💰 AffiliateAgent] ✅ تم حفظ النص التسويقي في: {file_path}")
        return {
            "status": "success",
            "message": f"تم كتابة النص التسويقي وحفظه في {file_path}",
            "marketing_copy": ad_copy
        }


class VideoAgent:
    def execute(self, prompt, duration=15):
        print(f"\n[🎬 VideoAgent] 🎥 جاري إنشاء سيناريو وأوامر الفيديو (Video Prompt)...")
        
        # تحويل المدة إلى رقم آمن في حال وصلت كنص
        try:
            duration = int(duration)
        except (ValueError, TypeError):
            duration = 15

        # هندسة الأوامر الصارمة (System Prompt)
        system_prompt = """أنت خبير محترف في هندسة أوامر الصور (Prompt Engineering) لإنشاء محتوى فيديو قصير (Reels/Shorts) بمدة 10-15 ثانية.
مهمتك الوحيدة هي تصميم "شبكات صور متسلسلة" (20-panel sequential image grids) توضح التطور الزمني والتحولات الجوهرية (Chronological & Transformational Evolution).
يجب أن يتضمن التصميم انتقالات بصرية سريعة جداً (Quick Transitions) وخدع بصرية (Visual Illusions).

تحذير صارم: لا تقم بكتابة أي قصة، أو سرد تعبيري، أو فقرات طويلة. فقط أعطني المخرجات بالهيكل التالي:
- [عنوان الريلز]
- [الفكرة العامة]
- [الصوت/المؤثرات]
- [أوامر اللوحات 1 إلى 20]: وصف دقيق جداً لكل لوحة (يفضل أن تكون أوامر اللوحات باللغة الإنجليزية لضمان دقة أدوات توليد الصور) مع الحفاظ على ترابط التحول."""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"بناءً على هذا الطلب: '{prompt}'، صمم مشهداً مدته {duration} ثانية مقسماً إلى 20 لوحة متسلسلة."}
            ]
        )

        video_prompt = response.choices[0].message.content.strip()
        file_path = "output/video_prompt.txt"

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(video_prompt)

        print(f"[🎬 VideoAgent] ✅ تم حفظ سيناريو الفيديو في {file_path}")
        return {
            "status": "success",
            "message": f"تم إنشاء سيناريو الفيديو وحفظه في {file_path}",
            "video_prompt": video_prompt
        }


class GitAgent:
    def execute(self, commit_message="Update generated affiliate assets"):
        print(f"\n[🌿 GitAgent] 📦 جاري رفع التعديلات والملفات إلى GitHub...")
        try:
            subprocess.run(["git", "add", "."], check=True, capture_output=True, text=True, encoding="utf-8", errors="ignore")
            subprocess.run(["git", "commit", "-m", commit_message], check=True, capture_output=True, text=True, encoding="utf-8", errors="ignore")
            
            subprocess.run(["git", "push", "origin", "HEAD"], check=True, capture_output=True, text=True, encoding="utf-8", errors="ignore")
            
            print("[🌿 GitAgent] ✅ تم الرفع بنجاح إلى المستودع!")
            return {"status": "success", "message": "تم رفع كل الملفات إلى GitHub بنجاح."}
        except subprocess.CalledProcessError as e:
            err = e.stderr or e.stdout
            print(f"[🌿 GitAgent] ⚠️ تنبيه Git: {err.strip()}")
            return {"status": "skipped_or_error", "details": err.strip()}


# --- الموجه الرئيسي (Master Agent) ---

class MasterAgent:
    def __init__(self):
        self.coding_agent = CodingAgent()
        self.affiliate_agent = AffiliateAgent()
        self.video_agent = VideoAgent()
        self.git_agent = GitAgent()

    def get_agent_tools(self):
        return [
            {
                "type": "function",
                "function": {
                    "name": "route_to_coding_agent",
                    "description": "استخدم هذا الوكيل عند الحاجة لكتابة كود برمجي أو تطبيق بايثون.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_description": {"type": "string", "description": "وصف المهمة البرمجية"},
                            "technologies": {"type": "string", "description": "لغة البرمجة أو التقنية"}
                        },
                        "required": ["task_description"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "route_to_affiliate_agent",
                    "description": "استخدم هذا الوكيل لكتابة نص إعلاني أو تسويقي مخصص للتسويق بالعمولة بناءً على منتج أو كود تم إنشاؤه.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "product_description": {"type": "string", "description": "وصف المنتج أو الأداة التسويقية"},
                            "target_audience": {"type": "string", "description": "الجمهور المستهدف"}
                        },
                        "required": ["product_description"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "route_to_video_agent",
                    "description": "استخدم هذا الوكيل لإنشاء سيناريو مرئي وأوامر فيديو ترويجية.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "prompt": {"type": "string", "description": "فكرة الفيديو والوصف البصري"},
                            "duration": {"type": "string", "description": "المدة بالثواني"}
                        },
                        "required": ["prompt"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "route_to_git_agent",
                    "description": "استخدم هذا الوكيل كخطوة أخيرة دائماً لرفع جميع الملفات المُنشأة حديثاً إلى GitHub.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "commit_message": {"type": "string", "description": "رسالة الـ Commit"}
                        },
                        "required": ["commit_message"]
                    }
                }
            }
        ]

    def process_request(self, user_prompt):
        print(f"\n[Master Agent] 🧠 بدء معالجة الطلب...")
        
        messages = [
            {
                "role": "system", 
                "content": (
                    "أنت Master Agent قيادي في نظام متعدد الوكلاء.\n"
                    "قم بتنفيذ طلب المستخدم عبر استدعاء الوكلاء المناسبين بالتسلسل.\n"
                    "مرر مخرجات كل وكيل للوكيل الذي يليه إذا كان ذلك مطلوباً، وفي النهاية ارفع العمل عبر Git."
                )
            },
            {"role": "user", "content": user_prompt}
        ]

        max_turns = 7
        for turn in range(max_turns):
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                tools=self.get_agent_tools(),
                tool_choice="auto"
            )

            message = response.choices[0].message

            if not message.tool_calls:
                messages.append(message)
                return {"status": "completed", "final_response": message.content}

            messages.append(message)

            for tool_call in message.tool_calls:
                func_name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)

                print(f"\n[Turn {turn + 1}] 🔀 توجيه إلى: {func_name}")

                if func_name == "route_to_coding_agent":
                    result = self.coding_agent.execute(**args)
                elif func_name == "route_to_affiliate_agent":
                    result = self.affiliate_agent.execute(**args)
                elif func_name == "route_to_video_agent":
                    result = self.video_agent.execute(**args)
                elif func_name == "route_to_git_agent":
                    result = self.git_agent.execute(**args)
                else:
                    result = {"error": "Unknown tool"}

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": func_name,
                    "content": json.dumps(result)
                })

        return {"status": "max_turns_reached"}


if __name__ == "__main__":
    master = MasterAgent()

    # هذا هو الطلب (Prompt) الجديد والمفصل الذي سيختبر كل الوكلاء
    # ويركز تحديداً على إجبار وكيل الفيديو على استخدام الشبكة المتسلسلة (20-panel) والانتقالات السريعة
    complex_user_prompt = (
        "أريد تطوير نظام آلة حاسبة متقدمة بلغة بايثون، "
        "واكتب إعلاناً تسويقياً ترويجياً لهذه الآلة الحاسبة، "
        "ثم قم بإنشاء سيناريو فيديو ريلز قصير (10 إلى 15 ثانية) يعتمد كلياً على شبكة صور متسلسلة (20-panel grid) "
        "يوضح التطور الزمني لأدوات الحساب؛ بدءاً من العداد الخشبي القديم (Abacus) وصولاً إلى الآلة الحاسبة الذكية المتقدمة، "
        "مع دمج خدع بصرية وانتقالات خاطفة بين اللوحات، "
        "وأخيراً قم برفع كافة الملفات الناتجة إلى مستودع GitHub."
    )

    final_result = master.process_request(complex_user_prompt)
    print("\n[النتيجة النهائية من النظام المتسلسل]:")
    print(json.dumps(final_result, ensure_ascii=False, indent=2))