import customtkinter as ctk
# 修复：解决空白界面
ctk.deactivate_automatic_dpi_awareness()
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

import threading
import requests
import hashlib
import random
import dashscope
from dashscope.audio.tts_v2 import SpeechSynthesizer
import os
import time
import sys
import subprocess

# ===================== 核心配置=====================
BAIDU_APP_ID = '20260415002594998'
BAIDU_APP_KEY = 'QypzL518sg87_JMdd26y'
dashscope.api_key = 'sk-177a106c48d446759cdb749a03bf26a0'
TARGET_MODEL = "cosyvoice-v3.5-flash"
VOICE_ID = "cosyvoice-v3.5-flash-dxrvoice-021dcaef180646d99a071e28cc6c80e9"
dashscope.base_http_api_url = "https://dashscope.aliyuncs.com/api/v1"
# ======================================================================


class AnimeTTSApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("ID：单休日")
        self.geometry("650x250")
        self.attributes("-topmost", True)
        self.attributes("-alpha", 0.92)
        self.current_lang = "en"
        self.is_processing = False

        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(expand=True, fill="both", padx=20, pady=15)

        self.label = ctk.CTkLabel(
            main_frame,
            text="🐯 KORTAC - HORANGI",
            font=("Arial", 15, "bold"),
            text_color="#009670"
        )
        self.label.pack(pady=(0, 10))

        self.input_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        self.input_frame.pack(fill="x", pady=5)
        self.entry = ctk.CTkEntry(
            self.input_frame,
            placeholder_text=" HORANGI is waiting...",
            height=50,
            font=("Arial", 16),
            corner_radius=12
        )
        self.entry.pack(side=ctk.LEFT, fill=ctk.X, expand=True, padx=(0, 10))
        self.entry.bind("<Return>", self.on_submit)

        self.lang_btn = ctk.CTkButton(
            self.input_frame,
            text="En",
            width=50,
            height=50,
            corner_radius=25,
            fg_color="#009670",
            font=("Impact", 18),
            command=self.toggle_language
        )
        self.lang_btn.pack(side=ctk.RIGHT)

        self.clear_btn = ctk.CTkButton(
            main_frame,
            text="CLEAR",
            width=120,
            height=35,
            corner_radius=8,
            fg_color="#333333",
            hover_color="#555555",
            font=("Arial", 12),
            command=self.clear_input
        )
        self.clear_btn.pack(pady=5)

        self.status = ctk.CTkLabel(main_frame, text="System Ready", text_color="gray")
        self.status.pack(pady=(2, 0))

    def toggle_language(self):
        if self.current_lang == "en":
            self.current_lang = "kor"
            self.lang_btn.configure(text="Kr", fg_color="#B91C3B")
        else:
            self.current_lang = "en"
            self.lang_btn.configure(text="En", fg_color="#009670")

    def clear_input(self):
        self.entry.delete(0, ctk.END)

    def translate(self, text):
        try:
            salt = str(random.randint(32768, 65536))
            sign = hashlib.md5((BAIDU_APP_ID + text + salt + BAIDU_APP_KEY).encode('utf-8')).hexdigest()
            res = requests.get(
                "https://api.fanyi.baidu.com/api/trans/vip/translate",
                params={
                    "q": text,
                    "from": "zh",
                    "to": self.current_lang,
                    "appid": BAIDU_APP_ID,
                    "salt": salt,
                    "sign": sign
                },
                timeout=4
            )
            res.encoding = 'utf-8'
            return res.json()['trans_result'][0]['dst']
        except:
            return text

    # 修复：Mac打包后生成音频+播放
    def speak_horangi(self, text):
        temp_file = os.path.expanduser(f"~/temp_{int(time.time()*1000)}.mp3")
        try:
            self.status.configure(text="🔊 生成语音中...", text_color="#009670")
            synthesizer = SpeechSynthesizer(
                model=TARGET_MODEL,
                voice=VOICE_ID,
                format="mp3"
            )

            # 1. 尝试调用 API
            responses = synthesizer.call(text.strip())

            # 2. 检查返回结果并写入文件
            with open(temp_file, "wb") as f:
                for response in responses:
                    if response.status_code == 200:
                        # 修复：使用 get_audio_data() 获取字节流
                        f.write(response.get_audio_data())
                    else:
                        # 如果 API 报错，抛出详细信息
                        raise Exception(f"API错误({response.status_code}): {response.message}")

            # 3. 播放逻辑
            self.status.configure(text="🔊 播放中...", text_color="#009670")
            subprocess.run(["afplay", temp_file])

            # 4. 清理
            if os.path.exists(temp_file):
                os.remove(temp_file)
            self.status.configure(text="✅ 完成", text_color="gray")

        except Exception as e:
            # 报错显示
            error_info = str(e)
            print(f"DEBUG ERROR: {error_info}")
            self.status.configure(text=f"❌ {error_info[:20]}", text_color="red")
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def on_submit(self, e):
        txt = self.entry.get().strip()
        if txt and not self.is_processing:
            threading.Thread(target=self.run_flow, args=(txt,), daemon=True).start()

    def run_flow(self, txt):
        self.is_processing = True
        try:
            trans_text = self.translate(txt).replace('\n', '').strip()
            self.speak_horangi(trans_text)
        finally:
            self.is_processing = False


if __name__ == "__main__":
    app = AnimeTTSApp()
    app.mainloop()