import os
import json
import tempfile
import subprocess
import uuid
from flask import Flask, request, jsonify
import whisper
# 关键！导入我们放在同一个文件夹下的翻译模块
# 修改后
from translator import MultiLangTranslator

# ───── 1. 初始化 ─────
app = Flask(__name__)
UPLOAD_FOLDER = '/app/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ───── 2. 模型懒加载 (Lazy Loading) ─────
_whisper_model = None
_translator = None

def get_whisper_model():
    global _whisper_model
    if _whisper_model is None:
        print("[INIT] 正在从本地文件加载 Whisper large-v3 模型...")
        _whisper_model = whisper.load_model("large-v3", download_root="/app/models")
        print("[SUCCESS] Whisper 模型加载成功！")
    return _whisper_model

def get_translator():
    global _translator
    if _translator is None:
        translator_model_path = "/app/models/nllb_translator"
        print(f"[INIT] 正在从本地文件加载翻译器模型: {translator_model_path}")
        _translator = MultiLangTranslator(model_path=translator_model_path)
        print("[SUCCESS] 翻译器加载成功！")
    return _translator

import json, re, sys

def punct(t: str) -> str:
    t = t.strip()
    # 若末尾无标点，则补句号
    if not re.search(r'[。！？…]$', t):
        t += '。'
    return t

def format_asr_and_trans_res(translator, ars_res):
    """格式化 ASR 和翻译结果"""
    asr_result = []
    trans_result = []
    for seg in ars_res["segments"]:
        start = f"{seg['start']:.2f}"
        end   = f"{seg['end']:.2f}"
        text  = punct(seg["text"])
        trans_text = translator.translate_text(text)
        asr_result.append(f"{start} --> {end}\t{text}")
        trans_result.append(f"{start} --> {end}\t{trans_text}")
    return {
        "asr_result": asr_result,
        "trans_result": trans_result
    }

# ───── 3. API 端点定义 ─────
@app.route('/')
def index():
    return "Ultimate Whisper Service (ASR + Translation) is running!"

@app.route('/transcribe', methods=['POST'])
def transcribe_and_translate_endpoint():
    if 'file' not in request.files: return jsonify({"error": "请求中未找到文件"}), 400
    uploaded_file = request.files['file']
    if uploaded_file.filename == '': return jsonify({"error": "未选择文件"}), 400
    save_path = os.path.join(UPLOAD_FOLDER, str(uuid.uuid4()))
    uploaded_file.save(save_path)

    whisper_model = get_whisper_model()
    translator = get_translator()

    print("[PROCESS] 正在进行语音转写...")
    transcription_result = whisper_model.transcribe(save_path, fp16=True)

    final_response = format_asr_and_trans_res(translator, transcription_result)


    return jsonify(final_response)

# ───── 4. 本地调试入口 ─────
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)