import json
import os
import subprocess
from dotenv import load_dotenv
from openai import OpenAI
import google.generativeai as genai

# تحميل المتغيرات البيئية من ملف .env
load_dotenv()

# 1. تهيئة عميل Groq للوكلاء الأساسيين
client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY")
)

# 2. تهيئة عميل Gemini لوكيل الصور
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

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
        
        try:
            duration = int(duration)
        except (ValueError, TypeError):
            duration = 15

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


class ImageAgent:
    def __init__(self):
        # استخدام نموذج مستقر ومتوافق مع توليد النصوص والأوامر
        self.model = genai.GenerativeModel('gemini-1.5-flash-latest')

    def execute(self, **kwargs):
        print(f"\n[🎨 ImageAgent] 🖼️ جاري صياغة أوامر نصية تفصيلية لتوليد الصور باللغة الإنجليزية باستخدام Gemini...")
        
        file_path_in = "output/video_prompt.txt"
        try:
            with open(file_path_in, "r", encoding="utf-8") as f:
                video_script = f.read()
        except FileNotFoundError:
            print("[🎨 ImageAgent] ❌ لم يتم العثور على ملف السيناريو!")
            return {"status": "error", "message": "ملف video_prompt.txt غير موجود."}

        system_prompt = """You are an expert AI Prompt Engineer specialized in image generation tools.
Your task is to read the provided Arabic video script and convert the 20 panels into 20 highly detailed, professional English text-based prompt instructions.
Focus strictly on elements of chronological growth, sequential evolution, and rapid visual transformations across the grid.
Ensure lighting, style, and transitions are described explicitly.
Format the output as a numbered list from 1 to 20. Do NOT output any introductory or concluding text, only the English text prompts."""

        full_prompt = f"{system_prompt}\n\nArabic Video Script:\n{video_script}"

        try:
            response = self.model.generate_content(full_prompt)
            image_prompts = response.text.strip()
        except Exception as e:
            print(f"[🎨 ImageAgent] ❌ خطأ في الاتصال بـ Gemini: {e}")
            return {"status": "error", "message": str(e)}

        file_path_out = "output/image_prompts_en.txt"

        with open(file_path_out, "w", encoding="utf-8") as f:
            f.write(image_prompts)

        print(f"[🎨 ImageAgent] ✅ تم حفظ أوامر توليد الصور الإنجليزية في {file_path_out}")
        return {
            "status": "success",
            "message": f"تم تجهيز أوامر الصور وحفظها في {file_path_out}",
            "image_prompts": image_prompts
        }


class AudioAgent:
    def execute(self, video_theme, mood="مشرقة ومبهجة"):
        print(f"\n[🎵 AudioAgent] 🎧 جاري البحث عن اقتراحات لموسيقى خلفية ({mood}) خالية من حقوق الطبع والنشر...")

        system_prompt = """أنت خبير في الإشراف الموسيقي لصناعة المحتوى المرئي.
مهمتك اقتراح موسيقى خلفية مجانية تماماً وبدون حقوق طبع ونشر (Royalty-Free) تناسب الفيديوهات القصيرة (Reels) بمدة 20 ثانية.
يجب أن تعطي المخرجات بالتنسيق التالي:
1. المزاج والإيقاع المطلوب (مثلاً: موسيقى مشرقة، سريعة، متصاعدة تتناسب مع التحول الزمني).
2. كلمات بحث مفتاحية دقيقة للبحث بها باللغة الإنجليزية (Search Keywords).
3. روابط لأشهر المواقع التي تقدم هذه الموسيقى مجاناً (مثل Pixabay Music, YouTube Audio Library).
اجعل الإجابة مختصرة، منظمة، ومباشرة."""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"موضوع الفيديو: {video_theme}. المزاج المطلوب: {mood}."}
            ]
        )

        audio_suggestions = response.choices[0].message.content.strip()
        file_path = "output/audio_suggestions.txt"

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(audio_suggestions)

        print(f"[🎵 AudioAgent] ✅ تم حفظ اقتراحات الموسيقى في {file_path}")
        return {
            "status": "success",
            "message": f"تم حفظ اقتراحات الموسيقى في {file_path}",
            "audio_suggestions": audio_suggestions
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
        self.image_agent = ImageAgent()
        self.audio_agent = AudioAgent()
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
                    "name": "route_to_image_agent",
                    "description": "استخدم هذا الوكيل لتحويل سيناريو الفيديو العربي إلى أوامر نصية لتوليد صور باللغة الإنجليزية (Image Prompts).",
                    "parameters": {
                        "type": "object",
                        "properties": {}
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "route_to_audio_agent",
                    "description": "استخدم هذا الوكيل لاقتراح وجلب مسارات أو كلمات بحث لموسيقى خلفية مجانية وبدون حقوق طبع ونشر تناسب الفيديو.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "video_theme": {"type": "string", "description": "موضوع الفيديو أو فكرته"},
                            "mood": {"type": "string", "description": "المزاج الموسيقي المطلوب"}
                        },
                        "required": ["video_theme"]
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

        max_turns = 10
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
                
                try:
                    args = json.loads(tool_call.function.arguments) if tool_call.function.arguments else {}
                except json.JSONDecodeError:
                    args = {}

                if not isinstance(args, dict):
                    args = {}

                print(f"\n[Turn {turn + 1}] 🔀 توجيه إلى: {func_name}")

                if func_name == "route_to_coding_agent":
                    result = self.coding_agent.execute(**args)
                elif func_name == "route_to_affiliate_agent":
                    result = self.affiliate_agent.execute(**args)
                elif func_name == "route_to_video_agent":
                    result = self.video_agent.execute(**args)
                elif func_name == "route_to_image_agent":
                    result = self.image_agent.execute(**args)
                elif func_name == "route_to_audio_agent":
                    result = self.audio_agent.execute(**args)
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

    complex_user_prompt = (
        "أريد تطوير نظام آلة حاسبة متقدمة بلغة بايثون، "
        "واكتب إعلاناً تسويقياً ترويجياً لهذه الآلة الحاسبة، "
        "ثم قم بإنشاء سيناريو فيديو ريلز قصير (10 إلى 15 ثانية) يعتمد كلياً على شبكة صور متسلسلة (20-panel grid) "
        "يوضح التطور الزمني لأدوات الحساب؛ بدءاً من العداد الخشبي القديم (Abacus) وصولاً إلى الآلة الحاسبة الذكية المتقدمة، "
        "مع دمج خدع بصرية وانتقالات خاطفة بين اللوحات، "
        "بعد ذلك قم بتحويل هذا السيناريو إلى أوامر نصية لتوليد الصور باللغة الإنجليزية (Text-based Image Prompts)، "
        "ثم اقترح موسيقى خلفية مشرقة ومجانية تماماً (بدون حقوق طبع ونشر) تتناسب مع هذا التحول الزمني، "
        "وأخيراً قم برفع كافة الملفات الناتجة إلى مستودع GitHub."
    )

    final_result = master.process_request(complex_user_prompt)
    print("\n[النتيجة النهائية من النظام المتسلسل]:")
    print(json.dumps(final_result, ensure_ascii=False, indent=2))