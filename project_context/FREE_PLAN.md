# AllAffiliate_Agent - خطة التشغيل المجاني بالكامل

**الإصدار:** v1.0
**التاريخ:** 2026-08-29
**الهدف:** تشغيل جميع ميزات المنصة بدون أي تكلفة

---

## ملخص تنفيذي

```
┌─────────────────────────────────────────────────┬──────────┐
│ الميزة                                         │ التكلفة  │
├─────────────────────────────────────────────────┼──────────┤
│ توليد النصوص والمحتوى                         │ 0$       │
│ تحليل البيانات والبحث                          │ 0$       │
│ إنتاج الصور                                    │ 0$       │
│ إنتاج الفيديو                                  │ 0$       │
│ تحويل النص لكلام (TTS)                         │ 0$       │
│ تحويل الكلام لنص (STT)                         │ 0$       │
│ أتمتة المتصفح                                  │ 0$       │
│ النشر على المنصات                              │ 0$       │
│ النماذج المحلية (بدون إنترنت)                  │ 0$       │
├─────────────────────────────────────────────────┼──────────┤
│ المجموع الكلي                                  │ 0$       │
└─────────────────────────────────────────────────┴──────────┘
```

---

## المتطلبات الأساسية

```
نظام التشغيل:    Windows / Linux / macOS
الذاكرة:         8GB RAM كحد أدنى (16GB مُوصى به)
المساحة:         20GB قرص صلب
الإنترنت:        مطلوب للنماذج السحابية (اختياري مع Ollama)
GPU:             اختياري (يُسرّع توليد الصور والفيديو)
Python:          3.10 أو أعلى
```

---

## الخطوة 1: تثبيت الأدوات المجانية

### 1.1 تثبيت Ollama (النماذج المحلية)

```powershell
# Windows - حمّل من الموقع الرسمي
# https://ollama.com/download

# بعد التثبيت، شغّل الأوامر التالية:
ollama pull qwen2.5:1.5b
ollama pull llama3.2:3b
ollama pull mistral:7b
```

### 1.2 تثبيت FFmpeg (إنتاج الفيديو)

```powershell
# Windows - حمّل من الموقع الرسمي
# https://www.gyan.dev/ffmpeg/builds/

# أو باستخدام Chocolatey:
choco install ffmpeg

# أو باستخدام winget:
winget install Gyan.FFmpeg

# تحقق من التثبيت:
ffmpeg -version
```

### 1.3 تثبيت Playwright (أتمتة المتصفح)

```powershell
# داخل مجلد المشروع
pip install playwright
playwright install chromium
```

### 1.4 تثبيت المكتبات الصوتية

```powershell
pip install edge-tts
pip install openai-whisper
pip install pyttsx3
```

### 1.5 تثبيت مكتبات الصور

```powershell
pip install diffusers
pip install transformers
pip install accelerate
pip install safetensors
```

### 1.6 تثبيت باقي المتطلبات

```powershell
pip install google-generativeai
pip install groq
pip install requests
pip install beautifulsoup4
pip install ffmpeg-python
pip install Pillow
```

---

## الخطوة 2: إعداد مفاتيح API المجانية

### 2.1 Google Gemini (مجاني)

```
1. اذهب إلى: https://aistudio.google.com/apikey
2. سجّل دخول بحساب Google
3. اضغط "Create API Key"
4. انسخ المفتاح

الحد المجاني:
  → 15 طلب/دقيقة
  → 1500 طلب/يوم
  → 1 مليون توكن/يوم
```

### 2.2 Groq (مجاني - أسرع)

```
1. اذهب إلى: https://console.groq.com/keys
2. سجّل دخول بحساب Google
3. اضغط "Create API Key"
4. انسخ المفتاح

الحد المجاني:
  → 30 طلب/دقيقة
  → 14400 طلب/يوم
  → نماذج: llama-3.3-70b, llama-3.1-8b
```

### 2.3 Google Custom Search (مجاني)

```
1. اذهب إلى: https://console.cloud.google.com/
2. أنشئ مشروع جديد
3. فعّل "Custom Search API"
4. أنشئ API Key
5. اذهب إلى: https://programmablesearchengine.google.com/
6. أنشئ محرك بحث
7. انسخ API Key و Search Engine ID

الحد المجاني:
  → 100 طلب/يوم
  → 10 نتائج/طلب
```

### 2.4 ملف .env

```env
# الذكاء الاصطناعي
GEMINI_API_KEY=your_gemini_api_key_here
GROQ_API_KEY=your_groq_api_key_here

# البحث
GOOGLE_SEARCH_API_KEY=your_google_search_api_key_here
GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id_here

# النشر (اختياري)
WORDPRESS_URL=your_wordpress_url_here
WORDPRESS_USERNAME=your_username_here
WORDPRESS_PASSWORD=your_app_password_here
```

---

## الخطوة 3: بناء المزودات المجانية

### 3.1 مزود Groq (سريع + مجاني)

```python
# providers/groq_provider.py

from core.result import Result
from groq import Groq


class GroqProvider:

    def __init__(self, api_key: str):
        self._client = Groq(api_key=api_key)

    def generate(self, prompt: str, model: str = None, parameters: dict = None) -> Result:
        try:
            model = model or "llama-3.3-70b-versatile"
            response = self._client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=parameters.get("temperature", 0.7) if parameters else 0.7,
                max_tokens=parameters.get("max_tokens", 2048) if parameters else 2048,
            )
            text = response.choices[0].message.content
            return Result.ok(data=text, meta={"provider": "groq", "model": model})
        except Exception as e:
            return Result.fail(error=str(e), meta={"provider": "groq"})
```

### 3.2 مزود Ollama (محلي + بدون إنترنت)

```python
# providers/ollama_provider.py

import requests
from core.result import Result


class OllamaProvider:

    def __init__(self, base_url: str = "http://localhost:11434"):
        self._base_url = base_url

    def generate(self, prompt: str, model: str = None, parameters: dict = None) -> Result:
        try:
            model = model or "qwen2.5:1.5b"
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": parameters.get("temperature", 0.7) if parameters else 0.7,
                    "num_predict": parameters.get("max_tokens", 2048) if parameters else 2048,
                }
            }
            response = requests.post(f"{self._base_url}/api/generate", json=payload, timeout=120)
            response.raise_for_status()
            text = response.json()["response"]
            return Result.ok(data=text, meta={"provider": "ollama", "model": model})
        except Exception as e:
            return Result.fail(error=str(e), meta={"provider": "ollama"})
```

### 3.3 مزود Pollinations (API مجاني بدون مفتاح)

```python
# providers/pollinations_provider.py

import requests
from core.result import Result


class PollinationsProvider:

    def generate_image(self, prompt: str, width: int = 1024, height: int = 1024) -> Result:
        try:
            url = f"https://image.pollinations.ai/prompt/{prompt}"
            params = {"width": width, "height": height, "nologo": True}
            response = requests.get(url, params=params, timeout=60)
            response.raise_for_status()
            return Result.ok(data=response.content, meta={"provider": "pollinations"})
        except Exception as e:
            return Result.fail(error=str(e), meta={"provider": "pollinations"})
```

---

## الخطوة 4: بناء مزودات الوسائط

### 4.1 مزود الصوت edge-tts (مجاني)

```python
# adapters/edge_tts_adapter.py

import edge_tts
import asyncio
from core.result import Result


class EdgeTTSAdapter:

    VOICES = {
        "ar-male": "ar-SA-HamedNeural",
        "ar-female": "ar-SA-ZariyahNeural",
        "en-male": "en-US-GuyNeural",
        "en-female": "en-US-JennyNeural",
    }

    async def _synthesize(self, text: str, voice: str, output_path: str):
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_path)

    def text_to_speech(self, text: str, output_path: str, voice: str = "en-female") -> Result:
        try:
            voice_id = self.VOICES.get(voice, voice)
            asyncio.run(self._synthesize(text, voice_id, output_path))
            return Result.ok(data={"path": output_path}, meta={"adapter": "edge-tts"})
        except Exception as e:
            return Result.fail(error=str(e), meta={"adapter": "edge-tts"})
```

### 4.2 مزود Whisper (مجاني محلي)

```python
# adapters/whisper_adapter.py

import whisper
from core.result import Result


class WhisperAdapter:

    def __init__(self, model_name: str = "base"):
        self._model = whisper.load_model(model_name)

    def transcribe(self, audio_path: str, language: str = None) -> Result:
        try:
            options = {}
            if language:
                options["language"] = language
            result = self._model.transcribe(audio_path, **options)
            return Result.ok(
                data={"text": result["text"], "segments": result["segments"]},
                meta={"adapter": "whisper"}
            )
        except Exception as e:
            return Result.fail(error=str(e), meta={"adapter": "whisper"})
```

### 4.3 مزود FFmpeg (منتج فيديو مجاني)

```python
# adapters/ffmpeg_adapter.py

import subprocess
import os
from core.result import Result


class FFmpegAdapter:

    def create_video_from_images(self, images_dir: str, output_path: str,
                                  fps: int = 30, duration_per_image: float = 3.0) -> Result:
        try:
            frames_per_image = int(fps * duration_per_image)
            pattern = os.path.join(images_dir, "frame_%04d.png")

            cmd = [
                "ffmpeg", "-y",
                "-framerate", str(fps),
                "-i", pattern,
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                "-r", str(fps),
                output_path
            ]
            subprocess.run(cmd, check=True, capture_output=True)
            return Result.ok(data={"path": output_path}, meta={"adapter": "ffmpeg"})
        except Exception as e:
            return Result.fail(error=str(e), meta={"adapter": "ffmpeg"})

    def add_audio(self, video_path: str, audio_path: str, output_path: str) -> Result:
        try:
            cmd = [
                "ffmpeg", "-y",
                "-i", video_path,
                "-i", audio_path,
                "-c:v", "copy",
                "-c:a", "aac",
                "-shortest",
                output_path
            ]
            subprocess.run(cmd, check=True, capture_output=True)
            return Result.ok(data={"path": output_path}, meta={"adapter": "ffmpeg"})
        except Exception as e:
            return Result.fail(error=str(e), meta={"adapter": "ffmpeg"})

    def add_subtitles(self, video_path: str, srt_path: str, output_path: str) -> Result:
        try:
            cmd = [
                "ffmpeg", "-y",
                "-i", video_path,
                "-vf", f"subtitles={srt_path}",
                "-c:a", "copy",
                output_path
            ]
            subprocess.run(cmd, check=True, capture_output=True)
            return Result.ok(data={"path": output_path}, meta={"adapter": "ffmpeg"})
        except Exception as e:
            return Result.fail(error=str(e), meta={"adapter": "ffmpeg"})
```

### 4.4 مزود Stable Diffusion (توليد صور مجاني)

```python
# adapters/stable_diffusion_adapter.py

from diffusers import StableDiffusionPipeline
import torch
from core.result import Result


class StableDiffusionAdapter:

    def __init__(self, model_id: str = "stabilityai/stable-diffusion-xl-base-1.0"):
        self._pipe = StableDiffusionPipeline.from_pretrained(
            model_id, torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
        )
        if torch.cuda.is_available():
            self._pipe = self._pipe.to("cuda")

    def generate_image(self, prompt: str, output_path: str,
                       width: int = 1024, height: int = 1024) -> Result:
        try:
            image = self._pipe(prompt, width=width, height=height, num_inference_steps=20).images[0]
            image.save(output_path)
            return Result.ok(data={"path": output_path}, meta={"adapter": "stable-diffusion"})
        except Exception as e:
            return Result.fail(error=str(e), meta={"adapter": "stable-diffusion"})
```

### 4.5 مزود Playwright (متصفح مجاني)

```python
# adapters/playwright_adapter.py

from playwright.sync_api import sync_playwright
from core.result import Result


class PlaywrightAdapter:

    def __init__(self):
        self._playwright = None
        self._browser = None

    def start(self):
        self._playwright = sync_playwright().start()
        self._browser = self._playwright.chromium.launch(headless=True)

    def stop(self):
        if self._browser:
            self._browser.close()
        if self._playwright:
            self._playwright.stop()

    def navigate(self, url: str) -> Result:
        try:
            page = self._browser.new_page()
            page.goto(url, wait_until="networkidle")
            title = page.title()
            return Result.ok(data={"title": title, "url": url}, meta={"adapter": "playwright"})
        except Exception as e:
            return Result.fail(error=str(e), meta={"adapter": "playwright"})

    def extract_text(self, url: str, selector: str = "body") -> Result:
        try:
            page = self._browser.new_page()
            page.goto(url, wait_until="networkidle")
            content = page.inner_text(selector)
            return Result.ok(data={"text": content}, meta={"adapter": "playwright"})
        except Exception as e:
            return Result.fail(error=str(e), meta={"adapter": "playwright"})

    def screenshot(self, url: str, output_path: str) -> Result:
        try:
            page = self._browser.new_page()
            page.goto(url, wait_until="networkidle")
            page.screenshot(path=output_path, full_page=True)
            return Result.ok(data={"path": output_path}, meta={"adapter": "playwright"})
        except Exception as e:
            return Result.fail(error=str(e), meta={"adapter": "playwright"})
```

### 4.6 مزود WordPress (نشر مجاني)

```python
# adapters/wordpress_adapter.py

import requests
from core.result import Result


class WordPressAdapter:

    def __init__(self, site_url: str, username: str, app_password: str):
        self._base_url = f"{site_url}/wp-json/wp/v2"
        self._auth = (username, app_password)

    def create_post(self, title: str, content: str, status: str = "draft") -> Result:
        try:
            response = requests.post(
                f"{self._base_url}/posts",
                auth=self._auth,
                json={"title": title, "content": content, "status": status},
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()
            return Result.ok(
                data={"id": data["id"], "link": data["link"]},
                meta={"adapter": "wordpress"}
            )
        except Exception as e:
            return Result.fail(error=str(e), meta={"adapter": "wordpress"})

    def upload_media(self, file_path: str, filename: str) -> Result:
        try:
            with open(file_path, "rb") as f:
                response = requests.post(
                    f"{self._base_url}/media",
                    auth=self._auth,
                    headers={"Content-Disposition": f"attachment; filename={filename}"},
                    data=f.read(),
                    timeout=60,
                )
            response.raise_for_status()
            data = response.json()
            return Result.ok(
                data={"id": data["id"], "url": data["source_url"]},
                meta={"adapter": "wordpress"}
            )
        except Exception as e:
            return Result.fail(error=str(e), meta={"adapter": "wordpress"})
```

### 4.7 مزود Blogger (نشر مجاني)

```python
# adapters/blogger_adapter.py

import requests
from core.result import Result


class BloggerAdapter:

    def __init__(self, blog_id: str, access_token: str):
        self._blog_id = blog_id
        self._headers = {"Authorization": f"Bearer {access_token}"}
        self._base_url = "https://www.googleapis.com/blogger/v3"

    def create_post(self, title: str, content: str) -> Result:
        try:
            response = requests.post(
                f"{self._base_url}/blogs/{self._blog_id}/posts",
                headers=self._headers,
                json={"kind": "blogger#post", "title": title, "content": content},
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()
            return Result.ok(
                data={"id": data["id"], "url": data["url"]},
                meta={"adapter": "blogger"}
            )
        except Exception as e:
            return Result.fail(error=str(e), meta={"adapter": "blogger"})
```

### 4.8 مزود Google Search (بحث مجاني)

```python
# adapters/google_search_adapter.py

import requests
from core.result import Result


class GoogleSearchAdapter:

    def __init__(self, api_key: str, search_engine_id: str):
        self._api_key = api_key
        self._cx = search_engine_id
        self._base_url = "https://www.googleapis.com/customsearch/v1"

    def search(self, query: str, num_results: int = 10) -> Result:
        try:
            params = {
                "key": self._api_key,
                "cx": self._cx,
                "q": query,
                "num": min(num_results, 10),
            }
            response = requests.get(self._base_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            results = []
            for item in data.get("items", []):
                results.append({
                    "title": item.get("title", ""),
                    "link": item.get("link", ""),
                    "snippet": item.get("snippet", ""),
                })
            return Result.ok(data=results, meta={"adapter": "google-search"})
        except Exception as e:
            return Result.fail(error=str(e), meta={"adapter": "google-search"})
```

### 4.9 OpenSERP OSS (بحث محلي مجاني بالكامل)

```text
OpenSERP هو بحث SERP مفتوح المصدر ومجاني بالكامل.
يعمل محلياً على localhost:7000 بدون مفتاح API أو فواتير.

المتطلبات:
  → Docker (اختياري) أو Go
  → إنترنت للبحث في محركات البحث الخارجية

التثبيت:
  docker run --rm -p 127.0.0.1:7000:7000 karust/openserp:latest serve -a 0.0.0.0 -p 7000

الميزات:
  → Google, Bing, Yandex, Baidu, DuckDuckGo, Ecosia
  → بحث متعدد المحركات في طلب واحد
  → استخراج محتوى الصفحات
  → بدون حدود أو قيود
  → MIT License
```

```env
# OpenSERP OSS (في ملف .env)
OPENSERP_BASE_URL=http://127.0.0.1:7000
OPENSERP_ENGINES=google,bing
OPENSERP_MODE=balanced
OPENSERP_LIMIT=5
OPENSERP_EXTRACT=0
OPENSERP_TIMEOUT_SECONDS=30
```

**الهيكل العملياتي:**

```text
AllAffiliate_Agent → http://127.0.0.1:7000 → OpenSERP OSS → محركات البحث على الإنترنت
```

**ملاحظة:** OpenSERP يعمل محلياً لكنه يحتاج إلى إنترنت للبحث في Google/Bing/etc.

---

## الخطوة 5: التسجيل في Service Container

```python
# أضف هذا الكود في service_container.py بعد التسجيل الحالي

from providers.groq_provider import GroqProvider
from providers.ollama_provider import OllamaProvider
from providers.pollinations_provider import PollinationsProvider
from adapters.edge_tts_adapter import EdgeTTSAdapter
from adapters.ffmpeg_adapter import FFmpegAdapter
from adapters.playwright_adapter import PlaywrightAdapter
from adapters.wordpress_adapter import WordPressAdapter
from adapters.google_search_adapter import GoogleSearchAdapter


def register_free_providers(container):
    """تسجيل جميع المزودات المجانية"""

    # مزودات الذكاء الاصطناعي
    groq_key = os.getenv("GROQ_API_KEY")
    if groq_key:
        container.register("groq_provider", GroqProvider(api_key=groq_key))

    container.register("ollama_provider", OllamaProvider())
    container.register("pollinations_provider", PollinationsProvider())

    # مزودات الوسائط
    container.register("edge_tts", EdgeTTSAdapter())
    container.register("ffmpeg", FFmpegAdapter())
    container.register("playwright", PlaywrightAdapter())

    # مزودات النشر
    wp_url = os.getenv("WORDPRESS_URL")
    wp_user = os.getenv("WORDPRESS_USERNAME")
    wp_pass = os.getenv("WORDPRESS_PASSWORD")
    if wp_url and wp_user and wp_pass:
        container.register("wordpress", WordPressAdapter(wp_url, wp_user, wp_pass))

    # مزود البحث
    search_key = os.getenv("GOOGLE_SEARCH_API_KEY")
    search_cx = os.getenv("GOOGLE_SEARCH_ENGINE_ID")
    if search_key and search_cx:
        container.register("google_search", GoogleSearchAdapter(search_key, search_cx))
```

---

## الخطوة 6: سيناريو استخدام كامل (مجاني)

```python
# examples/free_affiliate_workflow.py

"""
سيناريو كامل: إنشاء مقال تسويق بالعمولة مجاناً
"""

import os
from services.content_service import ContentService
from services.research_service import ResearchService
from services.workflow_service import WorkflowService
from adapters.edge_tts_adapter import EdgeTTSAdapter
from adapters.ffmpeg_adapter import FFmpegAdapter
from adapters.playwright_adapter import PlaywrightAdapter
from adapters.google_search_adapter import GoogleSearchAdapter


def run_free_affiliate_workflow():
    """تشغيل سيناريو التسويق بالعمولة بالكامل مجاناً"""

    # 1. البحث عن منتج (مجاني - Google Search)
    print("🔍 الخطوة 1: البحث عن منتج...")
    search = GoogleSearchAdapter(
        api_key=os.getenv("GOOGLE_SEARCH_API_KEY"),
        search_engine_id=os.getenv("GOOGLE_SEARCH_ENGINE_ID")
    )
    results = search.search("أفضل منتجات التسويق بالعمولة 2026")

    # 2. تحليل النتائج (مجاني - Gemini)
    print("📊 الخطوة 2: تحليل النتائج...")
    # استخدام Gemini لتحليل نتائج البحث
    # analysis = gemini_provider.generate(f"حلل هذه النتائج: {results}")

    # 3. كتابة مقال (مجاني - Gemini)
    print("✍️ الخطوة 3: كتابة المقال...")
    content = ContentService(generator=gemini_content_generator)
    article = content.generate_content(
        brief="اكتب مقال مراجعة شاملة عن أفضل منتج للتسويق بالعمولة",
        persona="خبير تسويق بالعمولة",
        format="article"
    )

    # 4. إنشاء صور (مجاني - Pollinations)
    print("🖼️ الخطوة 4: إنشاء الصور...")
    pollinations = PollinationsProvider()
    image = pollinations.generate_image("professional product review banner")

    # 5. تحويل المقال لصوت (مجاني - edge-tts)
    print("🔊 الخطوة 5: تحويل لصوت...")
    tts = EdgeTTSAdapter()
    tts.text_to_speech(article.data["body"], "output/narration.mp3", voice="en-male")

    # 6. إنشاء فيديو (مجاني - FFmpeg)
    print("🎬 الخطوة 6: إنشاء فيديو...")
    ffmpeg = FFmpegAdapter()
    ffmpeg.create_video_from_images("assets/images/", "output/video.mp4")

    # 7. النشر (مجاني - WordPress)
    print("📤 الخطوة 7: النشر...")
    wp = WordPressAdapter(
        site_url=os.getenv("WORDPRESS_URL"),
        username=os.getenv("WORDPRESS_USERNAME"),
        app_password=os.getenv("WORDPRESS_PASSWORD")
    )
    post = wp.create_post(title="أفضل منتج للتسويق بالعمولة", content=article.data["body"])

    print("✅ تم الانتهاء!")
    print(f"   المقال: {post.data['link']}")
    print(f"   الصوت: output/narration.mp3")
    print(f"   الفيديو: output/video.mp4")


if __name__ == "__main__":
    run_free_affiliate_workflow()
```

---

## الخطوة 7: الاختبار

```powershell
# تشغيل جميع الاختبارات
python -m pytest -q

# اختبار مزود Groq
python -m workspace.test_groq_provider

# اختبار مزود Ollama
python -m workspace.test_ollama_provider

# اختبار edge-tts
python -m workspace.test_edge_tts

# اختبار FFmpeg
python -m workspace.test_ffmpeg_adapter
```

---

## الخطوة 8: التشغيل

```powershell
# تشغيل النظام الرئيسي
python assistant.py

# تشغيل سيناريو التسويق المجاني
python examples/free_affiliate_workflow.py
```

---

## ملخص النماذج المجانية المتاحة

### نماذج سحابية مجانية

| المزود | النموذج | الحد المجاني | الاستخدام |
|--------|---------|-------------|----------|
| **Gemini** | gemini-2.5-flash-lite | 1500 طلب/يوم | نصوص + تحليل |
| **Groq** | llama-3.3-70b-versatile | 14400 طلب/يوم | نصوص + برمجة |
| **Groq** | llama-3.1-8b-instant | 14400 طلب/يوم | مهام بسيطة |
| **OpenRouter** | نماذج متعددة | 200 طلب/يوم | مرونة |
| **Pollinations** | صور AI | غير محدود | توليد صور |

### نماذج محلية مجانية (بدون إنترنت)

| النموذج | الحجم | الحد الأدنى | الاستخدام |
|---------|-------|-------------|----------|
| **qwen2.5:1.5b** | 1GB | 4GB RAM | مهام بسيطة |
| **llama3.2:3b** | 2GB | 6GB RAM | محتوى عام |
| **mistral:7b** | 4GB | 8GB RAM | تحليل متقدم |
| **llama3.1:8b** | 5GB | 10GB RAM | الأفضل عموماً |

---

## هيكل الملفات النهائي

```
AllAffiliate_Agent/
├── providers/
│   ├── gemini_provider.py          (موجود ✓)
│   ├── openai_provider.py          (موجود ✓)
│   ├── groq_provider.py            (جديد)
│   ├── ollama_provider.py          (جديد)
│   └── pollinations_provider.py    (جديد)
│
├── adapters/
│   ├── edge_tts_adapter.py         (جديد)
│   ├── whisper_adapter.py          (جديد)
│   ├── ffmpeg_adapter.py           (جديد)
│   ├── stable_diffusion_adapter.py (جديد)
│   ├── playwright_adapter.py       (جديد)
│   ├── wordpress_adapter.py        (جديد)
│   ├── blogger_adapter.py          (جديد)
│   └── google_search_adapter.py    (جديد)
│
├── examples/
│   └── free_affiliate_workflow.py   (جديد)
│
├── .env                            (تحديث)
├── requirements.txt                (تحديث)
└── FREE_PLAN.md                    (هذا الملف)
```

---

## تحديث requirements.txt

```
# الذكاء الاصطناعي (مجاني)
google-generativeai>=0.5.0
groq>=0.11.0
requests>=2.31.0

# الصوت (مجاني)
edge-tts>=6.1.0
openai-whisper>=20231117
pyttsx3>=2.90

# الصور (مجاني)
diffusers>=0.25.0
transformers>=4.37.0
accelerate>=0.25.0
safetensors>=0.4.0
Pillow>=10.0.0

# الفيديو (مجاني)
ffmpeg-python>=0.2.0

# المتصفح (مجاني)
playwright>=1.40.0

# البحث (مجاني)
beautifulsoup4>=4.12.0

# النماذج المحلية
ollama>=0.1.0
```

---

## ملاحظات مهمة

```
1. Gemini هو المزود الأساسي المجاني الأفضل
   → 1500 طلب/يوم يكفي لمعظم الاستخدامات

2. Groq هو الاحتياطي الأسرع
   → استخدمه عندما يكون Gemini بطيئاً

3. Ollama هو الحل بدون إنترنت
   → يحتاج 8GB RAM كحد أدنى

4. edge-tts هو أفضل حل صوتي مجاني
   → 300+ صوت بجودة احترافية

5. FFmpeg هو المعيار القياسي للفيديو
   → مجاني ومفتوح المصدر ويستخدمه الجميع

6. Playwright هو الأحدث في أتمتة المتصفحات
   → يدعم Chromium, Firefox, WebKit

7. Pollinations هو الأسهل لتوليد الصور
   → بدون مفتاح API وبدون تسجيل
```

---

**End of FREE_PLAN.md**

**End of FREE_PLAN.md**"
اكتب في نهاية FREE_PLAN.md قسمًا جديدًا بعنوان "خارطة التكاملات الخارجية المستقبلية".

المطلوب:
- لا تعدّل أي محتوى سابق في الملف.
- لا تنشئ أي ملف أو مجلد جديد.
- أضف القسم قبل السطر النهائي "**End of FREE_PLAN.md**".
- وضّح أن الهدف المستقبلي هو جعل AllAffiliate_Agent Orchestrator يحدد القدرات المطلوبة ثم يختار الوسيلة المناسبة لتنفيذها.
- ميّز بين القدرات الداخلية والخارجية.
- أدرج كأمثلة:
  - Claude Code → code generation / code execution / debugging
  - OmniRoute → model routing / provider routing
  - Task Observer → task monitoring
- أضف مفهوم Capability Map بحيث لا يعتمد النظام مستقبلًا على أسماء أدوات محددة بشكل مباشر.
- وضّح أن التكاملات الخارجية مخططة وليست منفذة حاليًا.
- وضّح أن التكامل المستقبلي يجب أن يحافظ على استقلال Core وAgents وServices وMemory وPlugins.
- لا تنشئ adapters أو integrations أو أي كود Python في هذه المرحلة.
- اختم بالقسم الحالي "**End of FREE_PLAN.md**" باعتباره آخر سطر في الملف.

اكتب القسم بصياغة تقنية واضحة ومتوافقة مع أسلوب FREE_PLAN.md الحالي.