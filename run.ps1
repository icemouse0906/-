# ===================================================================
#         Ultimate Whisper 服务一键部署脚本 (TAR.GZ 离线版)
# ===================================================================

# 1. 权限与环境检查
# -------------------------------------------------------------------
# 确保以管理员身份运行
if (-Not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Warning "此脚本需要管理员权限！请右键点击脚本，选择‘以管理员身份运行’。"
    Read-Host "按 Enter 键退出..."; exit 1
}

# 检查 WSL 是否安装，因为解压 .tar.gz 需要它
if (-not (Get-Command wsl.exe -ErrorAction SilentlyContinue)) {
    Write-Error "错误：未在本系统中找到 WSL (Windows Subsystem for Linux)！"
    Write-Warning "此脚本需要 WSL 的 gunzip 命令来解压镜像文件。请先安装 WSL。"
    Write-Host "您可以尝试以管理员身份运行 PowerShell 并执行: wsl --install"
    Read-Host "按 Enter 键退出..."; exit 1
}

# 切换到脚本所在的目录，确保路径正确
cd $PSScriptRoot
Write-Host "当前工作目录: $(Get-Location)"

Write-Host "========================================================" -ForegroundColor Green
Write-Host "==         Ultimate Whisper 服务一键部署脚本          ==" -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Green
Write-Host ""

# 2. 离线安装 Python 依赖包 (用于客户端测试脚本)
# -------------------------------------------------------------------
Write-Host "[步骤 1/3] 正在离线安装 Python 依赖包..." -ForegroundColor Yellow
pip install --no-index --find-links=./python_pkgs -r requirements.txt

if (-not $?) {
    Write-Error "错误：Python 依赖安装失败！请确保 Python 和 pip 已安装并配置在系统路径中。"
    Read-Host "按 Enter 键退出..."; exit 1
}
Write-Host "Python 依赖安装成功！" -ForegroundColor Green
Write-Host ""

# 3. 加载 Docker 镜像
# -------------------------------------------------------------------
Write-Host "[步骤 2/3] 正在从 .tar.gz 加载 Docker 镜像..." -ForegroundColor Yellow
Write-Host "这个过程需要几分钟，请耐心等待，期间没有进度条是正常现象。"

# 使用 WSL 的 gunzip 解压并通过管道导入 Docker
wsl gunzip -c ./docker-images/ultimate_stack.tar.gz | docker load

if (-not $?) {
    Write-Error "错误：加载 Docker 镜像失败！请检查 Docker 是否已在服务器上运行，以及文件路径是否正确。"
    Read-Host "按 Enter 键退出..."; exit 1
}
Write-Host "镜像加载成功！" -ForegroundColor Green
Write-Host ""

# 4. 启动服务
# -------------------------------------------------------------------
Write-Host "[步骤 3/3] 正在使用 Docker Compose 启动服务..." -ForegroundColor Yellow
docker compose up -d

if (-not $?) {
    Write-Error "错误：Docker Compose 启动失败！请检查 docker-compose.yml 文件是否存在以及内容是否正确。"
    Read-Host "按 Enter 键退出..."; exit 1
}

Write-Host ""
Write-Host "========================================================" -ForegroundColor Green
Write-Host "==             🎉 部署成功！服务已在后台运行 🎉             ==" -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Green
Write-Host "你可以通过以下方式检查："
Write-Host "1. 在终端运行 'docker ps' 查看容器状态。"
Write-Host "2. 运行 'python transcribe_and_translate.py <你的音频文件>' 进行功能测试。"
Write-Host ""
Read-Host "按 Enter 键退出脚本..."