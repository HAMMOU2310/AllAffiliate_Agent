import json  # <-- هذا هو السطر الذي يحل المشكلة
import os
import glob
import subprocess
import time
from dotenv import load_dotenv
from openai import OpenAI
from google import genai
from PIL import Image
from io import BytesIO
from moviepy.editor import ImageSequenceClip

# ... باقي الكود كما هو ...

# تحميل المتغيرات البيئية من ملف .env
load_dotenv()

# 1. تهيئة عميل Groq للوكلاء الأساسيين
client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY")
)

# إنشاء مجلدات للمخرجات إن لم تكن موجودة
os.makedirs("output", exist_ok=True)
os.makedirs("output/images", exist_ok=True)


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


class PromptExpansionAgent:
    def execute(self, topic, target_platforms="Midjourney, DALL-E, Social Media"):
        print(f"\n[📝 PromptExpansionAgent] 💡 جاري إنشاء وتوسيع الأوامر النصية الاحترافية للمنصات...")
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system", 
                    "content": "أنت خبير محترف في هندسة الأوامر (Prompt Engineering). مهمتك هي تحليل الموضوع وتوليد أوامر نصية (Text Prompts) إبداعية ومفصلة وعالية الجودة لتناسب مختلف المنصات الإبداعية والتسويقية."
                },
                {
                    "role": "user", 
                    "content": f"الموضوع الأساسي: {topic}. المنصات المستهدفة: {target_platforms}. يرجى تقديم أوامر مفصلة ومنظمة لكل منصة."
                }
            ]
        )
        
        expanded_content = response.choices[0].message.content.strip()
        file_path = "output/expanded_prompts.txt"
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(expanded_content)
            
        print(f"[📝 PromptExpansionAgent] ✅ تم حفظ الأوامر الموسعة في: {file_path}")
        return {
            "status": "success",
            "message": f"تم حفظ الأوامر الموسعة في {file_path}",
            "expanded_prompts": expanded_content
        }


class VideoAgent:
    def execute(self, prompt, duration=20):
        print(f"\n[🎬 VideoAgent] 🎥 جاري إنشاء سيناريو وأوامر الفيديو (Video Prompt)...")
        
        try:
            duration = int(duration)
        except (ValueError, TypeError):
            duration = 20

        system_prompt = """أنت خبير محترف في هندسة أوامر الصور لصناعة محتوى فيديو قصير (Reels/Shorts).
مهمتك تصميم "شبكات صور متسلسلة" (20-panel sequential image grids) توضح التطور الزمني والتحولات الجوهرية.
أعط المخرجات بالهيكل التالي:
- [عنوان الريلز]
- [الفكرة العامة]
- [أوامر اللوحات 1 إلى 20]: وصف دقيق باللغة الإنجليزية لكل لوحة مع الحفاظ على ترابط التحول."""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"صمم مشهداً مدته {duration} ثانية مقسماً إلى 20 لوحة متسلسلة لـ: {prompt}"}
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
        # تهيئة عميل Google لتوليد الصور فقط (Imagen)
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    def execute(self, *args, **kwargs):
        print(f"\n[🎨 ImageAgent] 🖼️ جاري توليد الصور فعلياً وحفظها في مجلد المشروع...")
        
        file_path_in = "output/video_prompt.txt"
        try:
            with open(file_path_in, "r", encoding="utf-8") as f:
                video_script = f.read()
        except FileNotFoundError:
            print("[🎨 ImageAgent] ❌ لم يتم العثور على ملف السيناريو!")
            return {"status": "error", "message": "ملف video_prompt.txt غير موجود."}

        extract_prompt = """Read the provided video script and extract/generate 20 distinct English image generation prompts for a 20-panel sequential grid. Return ONLY the 20 prompts as a numbered list from 1 to 20, with no extra conversational text."""

        # 💡 الحل الجذري: استخدام Groq الموثوق لاستخراج الأوامر لتفادي خطأ 404 الخاص بـ Gemini
        try:
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": extract_prompt},
                    {"role": "user", "content": f"Script:\n{video_script}"}
                ]
            )
            text_output = response.choices[0].message.content.strip()
            
            # استخراج الأوامر وتقسيمها
            prompts = [p.strip() for p in text_output.split('\n') if p.strip()]
            prompts = [p.lstrip('1234567890.-) ') for p in prompts if any(c.isdigit() for c in p[:3])] or prompts
            prompts = prompts[:20]
        except Exception as e:
            print(f"[🎨 ImageAgent] ❌ خطأ في استخراج الأوامر عبر Groq: {e}")
            return {"status": "error", "message": str(e)}

        generated_files = []
        for idx, prompt_text in enumerate(prompts, start=1):
            clean_prompt = prompt_text.strip()
            if not clean_prompt:
                continue
                
            print(f"[🎨 ImageAgent] 🖌️ توليد الصورة رقم {idx}/20 عبر Imagen 3...")
            try:
                # توليد الصورة الفعلية باستخدام نموذج Imagen 3 من Google
                result = self.client.models.generate_images(
                    model='imagen-3.0-generate-002',
                    prompt=clean_prompt,
                    config=dict(
                        number_of_images=1,
                        output_mime_type="image/jpeg",
                        aspect_ratio="9:16"
                    )
                )
                for gen_img in result.generated_images:
                    img_bytes = gen_img.image.image_bytes
                    img = Image.open(BytesIO(img_bytes))
                    file_path = os.path.join("output/images", f"panel_{idx:02d}.jpg")
                    img.save(file_path)
                    generated_files.append(file_path)
            except Exception as img_err:
                # هذا الاستثناء يمنع انهيار البرنامج إذا كان مفتاح API لا يدعم توليد الصور
                print(f"[🎨 ImageAgent] ⚠️ تعذر توليد الصورة {idx} (قد تتطلب الصلاحية مفتاحاً يدعم Imagen): {img_err}")

        print(f"[🎨 ImageAgent] ✅ تم توليد وحفظ {len(generated_files)} صورة في مجلد output/images/")
        return {
            "status": "success",
            "message": f"تم توليد {len(generated_files)} صورة بنجاح وحفظها.",
            "images_generated": len(generated_files)
        }


class VideoComposerAgent:
    def execute(self, fps=1, output_filename="output/final_reel.mp4"):
        print(f"\n[🎞️ VideoComposerAgent] 🎬 جاري تجميع الصور وإنتاج الفيديو النهائي...")
        
        image_files = sorted(glob.glob("output/images/panel_*.jpg"))
        
        if not image_files:
            print("[🎞️ VideoComposerAgent] ❌ لا توجد صور في مجلد output/images/ لتجميعها!")
            return {"status": "error", "message": "لم يتم العثور على صور مدمجة."}

        try:
            clip = ImageSequenceClip(image_files, fps=fps)
            clip.write_videofile(output_filename, fps=fps, codec="libx264", audio=False)
            
            print(f"[🎞️ VideoComposerAgent] ✅ تم إنتاج الفيديو بنجاح في: {output_filename}")
            return {
                "status": "success",
                "message": f"تم تجميع الصور وإنتاج الفيديو في {output_filename}",
                "video_path": output_filename
            }
        except Exception as e:
            print(f"[🎞️ VideoComposerAgent] ❌ خطأ أثناء تجميع الفيديو: {e}")
            return {"status": "error", "message": str(e)}


class AudioAgent:
    def execute(self, video_theme, mood="مشرقة ومبهجة"):
        print(f"\n[🎵 AudioAgent] 🎧 جاري البحث عن اقتراحات لموسيقى خلفية ({mood})...")

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "أنت خبير إشراف موسيقي. اقترح موسيقى مجانية بدون حقوق طبع ونشر مع كلمات بحث وروابط لمصادر مثل Pixabay."},
                {"role": "user", "content": f"موضوع الفيديو: {video_theme}. المزاج: {mood}."}
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
    def execute(self, commit_message="Update generated affiliate assets, expanded prompts and video"):
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
        self.prompt_expansion_agent = PromptExpansionAgent()  # 1. تهيئة الوكيل الجديد هنا
        self.video_agent = VideoAgent()
        self.image_agent = ImageAgent()
        self.video_composer_agent = VideoComposerAgent()
        self.audio_agent = AudioAgent()
        self.git_agent = GitAgent()

    def get_agent_tools(self):
        return [
            {
                "type": "function",
                "function": {
                    "name": "route_to_coding_agent",
                    "description": "لكتابة كود برمجي أو تطبيق.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_description": {"type": "string"},
                            "technologies": {"type": "string"}
                        },
                        "required": ["task_description"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "route_to_affiliate_agent",
                    "description": "لكتابة نص إعلاني تسويقي بالعمولة.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "product_description": {"type": "string"},
                            "target_audience": {"type": "string"}
                        },
                        "required": ["product_description"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "route_to_prompt_expansion_agent",
                    "description": "لتوليد وإنشاء الأوامر النصية (Text Prompts) الاحترافية وحفظها في expanded_prompts.txt.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "topic": {"type": "string"},
                            "target_platforms": {"type": "string"}
                        },
                        "required": ["topic"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "route_to_video_agent",
                    "description": "لإنشاء سيناريو فيديو وأوامر شبكة الصور المتسلسلة.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "prompt": {"type": "string"},
                            "duration": {"type": "string"}
                        },
                        "required": ["prompt"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "route_to_image_agent",
                    "description": "لتوليد الصور فعلياً برمجياً وحفظها في مجلد المشروع.",
                    "parameters": {"type": "object", "properties": {}}
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "route_to_video_composer_agent",
                    "description": "لتجميع الصور المُولدة وإنتاج الفيديو النهائي.",
                    "parameters": {"type": "object", "properties": {}}
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "route_to_audio_agent",
                    "description": "لاقتراح الموسيقى الخلفية المناسبة.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "video_theme": {"type": "string"},
                            "mood": {"type": "string"}
                        },
                        "required": ["video_theme"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "route_to_git_agent",
                    "description": "لرفع جميع المخرجات إلى GitHub.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "commit_message": {"type": "string"}
                        },
                        "required": ["commit_message"]
                    }
                }
            }
        ]

    def process_request(self, user_prompt):
        print(f"\n[Master Agent] 🧠 بدء معالجة الطلب المتسلسل...\n")
        
        messages = [
            {
                "role": "system", 
                "content": (
                    "أنت Master Agent قيادي لنظام متعدد الوكلاء.\n"
                    "نفذ الطلب عبر استدعاء الوكلاء بالتسلسل الصحيح:\n"
                    "1. Coding/Affiliate\n"
                    "2. PromptExpansionAgent (لتوليد الأوامر النصية وحفظها في expanded_prompts.txt)\n"
                    "3. VideoAgent (السيناريو)\n"
                    "4. ImageAgent (توليد الصور برمجياً)\n"
                    "5. VideoComposerAgent (تجميع الفيديو)\n"
                    "6. AudioAgent (الموسيقى)\n"
                    "7. GitAgent (الرفع النهائي)"
                )
            },
            {"role": "user", "content": user_prompt}
        ]

        max_turns = 14
        for turn in range(max_turns):
            # استخدام النموذج الحديث والمدعوم حالياً من Groq: llama-3.1-8b-instant
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
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

                print(f"\n[Turn {turn + 1}] 🔀 تشغيل الوكيل: {func_name}")

                if func_name == "route_to_coding_agent":
                    result = self.coding_agent.execute(**args)
                elif func_name == "route_to_affiliate_agent":
                    result = self.affiliate_agent.execute(**args)
                elif func_name == "route_to_prompt_expansion_agent":
                    result = self.prompt_expansion_agent.execute(**args)
                elif func_name == "route_to_video_agent":
                    result = self.video_agent.execute(**args)
                elif func_name == "route_to_image_agent":
                    result = self.image_agent.execute(**args)
                elif func_name == "route_to_video_composer_agent":
                    result = self.video_composer_agent.execute(**args)
                elif func_name == "route_to_audio_agent":
                    result = self.audio_agent.execute(**args)
                elif func_name == "route_to_git_agent":
                    result = self.git_agent.execute(**args)
                else:
                    result = {"error": "Unknown tool"}

                # اختصار الرد المسجل في الذاكرة لتجنب تضخم حجم الرسائل والتوكنات
                clean_result = {"status": result.get("status", "success"), "message": "Task executed successfully."} if isinstance(result, dict) else result

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": func_name,
                    "content": json.dumps(clean_result)
                })

                # ⏳ فترة انتظار قصيرة لضمان استقرار العمليات المتتالية
                time.sleep(3)

        return {"status": "max_turns_reached"}


if __name__ == "__main__":
    master = MasterAgent()

    complex_user_prompt = (
        "أريد تطوير نظام آلة حاسبة متقدمة بلغة بايثون، "
        "مع كتابة إعلان تسويقي، "
        "ثم إنشاء أوامر نصية موسعة ومفصلة لمختلف المنصات وحفظها في expanded_prompts.txt، "
        "ثم إنشاء سيناريو فيديو ريلز قصير (20 لوحة متسلسلة لطور الحاسبة من الأبكس إلى الحواسيب الذكية)، "
        "ثم توليد الصور الـ 20 برمجياً وحفظها في مجلد الصور، "
        "ثم تجميع هذه الصور في ملف فيديو نهائي، "
        "ثم اقتراح موسيقى خلفية، "
        "وأخيراً رفع كافة الملفات والنتائج والفيديو إلى مستودع GitHub."
    )

    final_result = master.process_request(complex_user_prompt)
    print("\n[النتيجة النهائية من النظام المتسلسل]:")
    print(json.dumps(final_result, ensure_ascii=False, indent=2))