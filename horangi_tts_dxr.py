import customtkinter as ctk
# Mac专属修复：解决空白界面 + 统一主题
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

# ===================== 核心配置=====================
BAIDU_APP_ID = '20260415002594998'
BAIDU_APP_KEY = 'QypzL518sg87_JMdd26y'
dashscope.api_key = 'sk-177a106c48d446759cdb749a03bf26a0'
# 模型：flash 低延迟直播版
TARGET_MODEL = "cosyvoice-v3.5-flash"
# 和flash模型匹配的 VoiceID
VOICE_ID = "cosyvoice-v3.5-flash-dxrvoice-021dcaef180646d99a071e28cc6c80e9"
# 阿里云北京地域接口
dashscope.base_http_api_url = "https://dashscope.aliyuncs.com/api/v1"
dashscope.base_websocket_api_url='wss://dashscope.aliyuncs.com/api-ws/v1/inference'
# ======================================================================
class AnimeTTSApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("ID：单休日")
        self.geometry("650x250")
        ctk.set_appearance_mode("dark")
        self.attributes("-topmost", True)
        self.attributes("-alpha", 0.92)
        self.current_lang = "en"
        self.is_processing = False
        # ========== 全局居中布局 ==========
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(expand=True, fill="both", padx=20, pady=15)
        # 标题（跨平台字体，布局完全不变）
        self.label = ctk.CTkLabel(
            main_frame, 
            text="🐯 KORTAC - HORANGI", 
            font=("Arial", 15, "bold"), 
            text_color="#009670"
        )
        self.label.pack(pady=(0, 10))
        # 输入框区域
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
        
        # 语言切换按钮
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
        # 清除按钮
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
        # 状态文本
        self.status = ctk.CTkLabel(main_frame, text="System Ready", text_color="gray")
        self.status.pack(pady=(2, 0))
    # 切换语言
    def toggle_language(self):
        if self.current_lang == "en":
            self.current_lang = "kor"
            self.lang_btn.configure(text="Kr", fg_color="#B91C3B")
        else:
            self.current_lang = "en"
            self.lang_btn.configure(text="En", fg_color="#009670")
    # 清空输入框函数
    def clear_input(self):
        self.entry.delete(0, ctk.END)
    # 百度翻译
    def translate(self, text):
        try:
            salt = str(random.randint(32768, 65536))
            sign = hashlib.md5((BAIDU_APP_ID + text + salt + BAIDU_APP_KEY).encode('utf-8')).hexdigest()
            res = requests.get("https://api.fanyi.baidu.com/api/trans/vip/translate",
                params={"q": text, "from": "zh", "to": self.current_lang, "appid": BAIDU_APP_ID, "salt": salt, "sign": sign}, timeout=4)
            res.encoding = 'utf-8'
            return res.json()['trans_result'][0]['dst']
        except:
            return text
    #  跨平台音频播放
    def speak_horangi(self, text):
        temp_file = f"temp_{int(time.time()*1000)}.mp3"
        try:
            synthesizer = SpeechSynthesizer(model=TARGET_MODEL, voice=VOICE_ID)
            audio_data = synthesizer.call(text.strip())
            
            with open(temp_file, "wb") as f:
                f.write(audio_data)
            
            # Mac/Windows 自动适配播放
            if sys.platform == "darwin":
                os.system(f"afplay '{temp_file}'")
            else:
                os.system(f"start {temp_file}")
                
            threading.Timer(2, lambda: os.remove(temp_file) if os.path.exists(temp_file) else None).start()
        except Exception as e:
            print(f"TTS错误: {e}")
    def on_submit(self, e):
        txt = self.entry.get().strip()
        if txt and not self.is_processing:
            threading.Thread(target=self.run_flow, args=(txt,), daemon=True).start()
    def run_flow(self, txt):
        self.is_processing = True
        try:
            self.status.configure(text="🔊 处理中...", text_color="#009670")
            trans_text = self.translate(txt).replace('\n', '').strip()
            self.speak_horangi(trans_text)
            self.status.configure(text="✅ 就绪", text_color="gray")
        finally:
            self.is_processing = False
if __name__ == "__main__":
    app = AnimeTTSApp()
    app.mainloop()