# -*- coding: utf-8 -*-
import torch
# 关键修复：导入正确的加载器
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
import langid  # 用于语言检测
import re


class MultiLangTranslator:
    def __init__(self, model_path="./models/nllb-200-distilled-600M"):
        self.model_name = model_path
        
        # 语言代码映射 (保持不变)
        self.lang_codes = {
            'en': 'eng_Latn', 'ru': 'rus_Cyrl', 'ja': 'jpn_Jpan',
            'fr': 'fra_Latn', 'de': 'deu_Latn', 'es': 'spa_Latn',
            'ko': 'kor_Hang', 'ar': 'arb_Arab', 'pt': 'por_Latn',
            'it': 'ita_Latn', 'zh': 'zho_Hans'
        }

        # 语言名称映射 (保持不变)
        self.lang_names = {
            'en': '英语', 'ru': '俄语', 'ja': '日语',
            'fr': '法语', 'de': '德语', 'es': '西班牙语',
            'ko': '韩语', 'ar': '阿拉伯语', 'pt': '葡萄牙语',
            'it': '意大利语', 'zh': '中文'
        }

        # --- 关键的修复部分 ---
        # 我们将在这里以正确的方式加载模型，替换掉原来有问题的代码
        try:
            print(f"正在从本地路径加载翻译模型: {self.model_name}")
            
            # 1. 从本地路径加载分词器 (Tokenizer)
            tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            
            # 2. 从本地路径加载模型本身
            model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
            
            # 3. 将加载好的模型和分词器传给 pipeline
            self.translator = pipeline(
                'translation',
                model=model,
                tokenizer=tokenizer,
                device=0 if torch.cuda.is_available() else -1
            )

            print("模型加载成功！")
            print(f"使用设备: {'GPU' if torch.cuda.is_available() else 'CPU'}")
        except Exception as e:
            print(f"模型加载失败: {e}")
            print("请检查模型文件是否完整，或尝试安装依赖: pip install transformers torch sentencepiece langid sacremoses")
            self.translator = None
        # --- 修复结束 ---

    def detect_language(self, text):
        """检测输入文本的语言"""
        lang, confidence = langid.classify(text)
        lang_name = self.lang_names.get(lang, "未知语言")
        return lang, lang_name, confidence

    def translate_text(self, text, src_lang=None, max_length=400):
        """
        将文本翻译成中文
        (此方法及以下所有方法都保持您原来的逻辑不变)
        """
        if not self.translator:
            return "翻译器未初始化，请检查模型加载状态"
        text = text.strip()
        if not text:
            return ""
        if src_lang is None:
            src_lang, lang_name, confidence = self.detect_language(text)
            print(f"检测到语言: {lang_name} (置信度: {confidence:.2%})")
        else:
            lang_name = self.lang_names.get(src_lang, "未知语言")
        if src_lang == 'zh':
            return text
        src_code = self.lang_codes.get(src_lang)
        if not src_code:
            return f"不支持的语言: {lang_name}"
        tgt_code = self.lang_codes['zh']
        if len(text) > max_length:
            print(f"文本过长({len(text)}字符)，进行分段翻译...")
            segments = self._split_text(text, max_length)
            results = []
            for i, seg in enumerate(segments, 1):
                print(f"翻译段 {i}/{len(segments)}...")
                result = self._translate_segment(seg, src_code, tgt_code)
                results.append(result)
            return "".join(results)
        return self._translate_segment(text, src_code, tgt_code)

    def _translate_segment(self, text, src_code, tgt_code):
        """翻译单段文本"""
        try:
            result = self.translator(
                text,
                src_lang=src_code,
                tgt_lang=tgt_code,
                max_length=512
            )
            return result[0]['translation_text']
        except Exception as e:
            return f"翻译错误: {str(e)}"

    def _split_text(self, text, max_length=400):
        """智能分割文本（按句子分割）"""
        sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s', text)
        segments = []
        current_segment = ""
        for sentence in sentences:
            if len(current_segment) + len(sentence) <= max_length:
                current_segment += sentence + " "
            else:
                if current_segment:
                    segments.append(current_segment.strip())
                current_segment = sentence + " "
        if current_segment:
            segments.append(current_segment.strip())
        return segments

def main():
    """主交互函数 (保持不变)"""
    translator = MultiLangTranslator()
    if not translator.translator:
        print("无法启动翻译器，请检查错误信息")
        return
    print("\n===== 多语种翻译系统 =====")
    print("支持语言: 英语(en), 俄语(ru), 日语(ja), 法语(fr), 德语(de), 西班牙语(es)")
    print("韩语(ko), 阿拉伯语(ar), 葡萄牙语(pt), 意大利语(it), 中文(zh)")
    print("输入文本后自动检测语言并翻译成中文")
    print("输入 'q' 退出程序")
    print("=" * 30)
    while True:
        text = input("\n请输入要翻译的文本: ").strip()
        if text.lower() == 'q':
            break
        if not text:
            continue
        result = translator.translate_text(text)
        print("\n翻译结果:")
        print("-" * 50)
        print(result)
        print("-" * 50)

if __name__ == "__main__":
    main()