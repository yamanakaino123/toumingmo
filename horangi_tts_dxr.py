import customtkinter as ctk
import sys
# ===================== 跨平台初始化适配 =====================
if sys.platform == "win32":
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
import subprocess
import tempfile  # 引入系统临时文件模块，解决全平台写入权限

# ===================== 核心配置（保留原密钥） =====================
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

        # UI布局（保持原样）
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(expand=True, fill="both", padx=20, pady=15)

        self.label = ctk.CTkLabel(
            main_frame, text="🐯 KORTAC - HORANGI",
            font=("Arial", 15, "bold"), text_color="#009670"
        )
        self.label.pack(pady=(0, 10))

        self.input_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        self.input_frame.pack(fill="x", pady=5)

        self.entry = ctk.CTkEntry(
            self.input_frame, placeholder_text=" HORANGI is waiting...",
            height=50, font=("Arial", 16), corner_radius=12
        )
        self.entry.pack(side=ctk.LEFT, fill=ctk.X, expand=True, padx=(0, 10))
        self.entry.bind("<Return>", self.on_submit)

        self.lang_btn = ctk.CTkButton(
            self.input_frame, text="En", width=50, height=50,
            corner_radius=25, fg_color="#009670", font=("Impact", 18),
            command=self.toggle_language
        )
        self.lang_btn.pack(side=ctk.RIGHT)

        self.clear_btn = ctk.CTkButton(
            main_frame, text="CLEAR", width=120, height=35,
            corner_radius=8, fg_color="#333333", hover_color="#555555",
            font=("Arial", 12), command=self.clear_input
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
                params={"q": text, "from": "zh", "to": self.current_lang,
                        "appid": BAIDU_APP_ID, "salt": salt, "sign": sign},
                timeout=10
            )
            res.encoding = 'utf-8'
            return res.json()['trans_result'][0]['dst']
        except Exception as e:
            print(f"翻译异常: {e}")
            # 线程安全的UI更新
            self.after(0, lambda: self.status.configure(text="❌ 翻译失败", text_color="red"))
            return text

    def speak_horangi(self, text):
        temp_file = None
        try:
            # 线程安全更新状态
            self.after(0, lambda: self.status.configure(text="🔊 生成中...", text_color="#009670"))
            synthesizer = SpeechSynthesizer(model=TARGET_MODEL, voice=VOICE_ID)
            
            # 1. 输入文本校验
            clean_text = text.strip()
            if not clean_text:
                raise Exception("输入文本为空")

            # 2. 【核心优化】严格拦截 dashscope 异常返回值
            result = synthesizer.call(clean_text)
            
            # 拦截字符串错误信息
            if isinstance(result, str):
                raise Exception(f"API错误: {result[:50]}")
            # 拦截字典格式错误（部分版本SDK）
            elif isinstance(result, dict):
                err_msg = result.get("message", str(result))
                raise Exception(f"API失败: {err_msg[:50]}")
            # 拦截非字节流类型
            elif not isinstance(result, bytes):
                raise Exception(f"未知返回类型: {type(result)}")
            
            audio_data = result
            
            # 3. 额外校验音频数据长度
            if len(audio_data) < 100:
                raise Exception(f"音频过短 ({len(audio_data)}字节)")

            print(f"✅ 音频生成成功，长度: {len(audio_data)}")

            # 4. 使用系统临时目录（全平台权限兼容）
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                temp_file = f.name
                f.write(audio_data)

            # 5. 跨平台播放优化
            if sys.platform == "win32":
                os.startfile(temp_file)
            elif sys.platform == "darwin":
                # macOS 用 afplay 后台播放，无弹窗
                subprocess.run(["afplay", temp_file], capture_output=True, text=True)
            else:
                subprocess.run(["xdg-open", temp_file], capture_output=True, text=True)

            self.after(0, lambda: self.status.configure(text="✅ 播放成功", text_color="gray"))

        except Exception as e:
            print(f"❌ 错误详情: {e}")
            # 线程安全显示错误（截取前40字符）
            self.after(0, lambda: self.status.configure(text=f"❌ {str(e)[:40]}", text_color="red"))
        finally:
            # 兜底清理临时文件
            if temp_file and os.path.exists(temp_file):
                threading.Timer(1, lambda: os.remove(temp_file) if os.path.exists(temp_file) else None).start()

    def on_submit(self, e):
        txt = self.entry.get().strip()
        if txt and not self.is_processing:
            threading.Thread(target=self.run_flow, args=(txt,), daemon=True).start()

    def run_flow(self, txt):
        self.is_processing = True
        try:
            trans_text = self.translate(txt).strip()
            print(f"翻译后文本: {trans_text}")
            self.speak_horangi(trans_text)
        finally:
            self.is_processing = False

if __name__ == "__main__":
    app = AnimeTTSApp()
    app.mainloop()