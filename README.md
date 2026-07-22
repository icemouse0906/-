# Ultimate Whisper — 离线多语种音视频转写与翻译服务

面向**断网 / 涉密本地化部署**场景的 ASR + 机器翻译一体化服务。支持将外文音视频（如 `.mp4`）转写为原文，并自动翻译为中文，返回带时间轴的双语结果。

## 技术栈

| 模块 | 技术 |
|------|------|
| 语音识别 (ASR) | OpenAI **Whisper `large-v3`** |
| 机器翻译 | Meta **NLLB-200 distilled 600M**（HuggingFace Transformers） |
| 语种检测 | `langid` |
| 服务端 | Flask + Gunicorn |
| 部署 | Docker Compose + 离线镜像包 |
| 一键部署 | PowerShell（Windows）/ Shell（Linux） |

## 核心流水线

```
音视频上传 → Whisper large-v3 转写 → 分段 + 标点整理
         → langid 检语种 → NLLB 译中文 → 返回双语时间轴 JSON
```

服务端入口：`custom_app/app.py`  
翻译模块：`custom_app/translator.py`  
客户端测试：`transcribe_and_translate.py`（POST 到 `localhost:5005/transcribe`）

## 离线部署亮点

`run.ps1` / `run.sh` 针对纯离线环境做了完整自动化：

1. **本地 `.whl` 离线安装**：`pip install --no-index --find-links=./python_pkgs`
2. **本地 Docker 镜像加载**：`gunzip … | docker load`（不依赖外网 pull）
3. **Compose 一键拉起服务**：模型与代码通过 volume 挂载本地路径
4. 模型权重指向本地目录（如 `/app/models`、`/app/models/nllb_translator`），运行时不下载

详见 `部署说明.txt`。

## 仓库结构

```
├── custom_app/                 # 核心服务代码
│   ├── app.py                  # Flask API：转写 + 翻译
│   ├── translator.py           # NLLB 多语→中文翻译器
│   └── post_process.py         # 结果格式化
├── models/nllb_translator/     # NLLB 本地模型配置 / tokenizer
├── python_pkgs/                # 离线 pip 依赖包（.whl）
├── docker-compose.yml          # 容器编排
├── run.ps1 / run.sh            # 一键离线部署脚本
├── transcribe_and_translate.py # 客户端调用示例
├── requirements.txt
└── 部署说明.txt
```

> 说明：完整 Docker 镜像与 Whisper `large-v3.pt` 权重体积较大，未纳入本仓库；部署时需按交付包另行放置到 `docker-images/` 与 `models/`。

## 快速验证（有 Docker 与镜像时）

```bash
# Linux
./run.sh

# 或 Windows（管理员 PowerShell）
.\run.ps1

# 功能测试
python transcribe_and_translate.py your_video.mp4
```

服务端口映射：`5005 → 容器内 5000`。
