from setuptools import setup

APP = ['horangi_tts_dxr.py']  # 代码文件名，一致
DATA_FILES = []
OPTIONS = {
    'argv_emulation': False,
    'packages': ['customtkinter', 'dashscope', 'requests', 'websocket'],
    'includes': ['hashlib', 'random', 'threading', 'tempfile', 'subprocess', 'sys', 'os', 'time'],
    'plist': {
        'CFBundleName': 'Horangi-TTS',
        'CFBundleDisplayName': 'Horangi-TTS',
        'CFBundleIdentifier': 'com.horangi.tts',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0',
        'NSHighResolutionCapable': True,  # 支持macOS高分屏
        'NSAppTransportSecurity': {
            'NSAllowsArbitraryLoads': True  # 放行HTTP/HTTPS网络请求
        }
    },
    'iconfile': ''  # 可选：填写.icns图标文件路径，自定义App图标
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)