#!/usr/bin/env python3
import requests
import sys
import pathlib
import json
import time

# --- 配置 ---
BASE_URL = "http://localhost:5005"
# --- 配置结束 ---

def main():
    if len(sys.argv) < 2:
        print(f"用法: python3 {sys.argv[0]} <音频文件路径>")
        sys.exit(1)

    file_path = pathlib.Path(sys.argv[1])
    if not file_path.is_file():
        print(f"错误：文件不存在或不是一个有效文件 -> {file_path}")
        sys.exit(1)

    print(f"正在上传文件: {file_path.name} ...")
    print("这可能需要一些时间，具体取决于音频长度和服务器性能，请耐心等待...")
    submit_url = f"{BASE_URL}/transcribe"
    
    try:
        start_time = time.time()
        with open(file_path, "rb") as f:
            resp = requests.post(submit_url, files={"file": f}, timeout=1800)
            resp.raise_for_status()
        end_time = time.time()
        
        print(f"请求处理完毕，耗时: {end_time - start_time:.2f} 秒。")

        data = resp.json()
        print(data)

        

    except requests.exceptions.RequestException as e:
        print(f"\n错误：请求失败。请检查服务端日志。详细错误: {e}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"\n错误：服务器返回的不是有效的JSON。请检查服务端日志。")
        print(f"服务器原始响应内容: {resp.text}")
        sys.exit(1)

if __name__ == "__main__":
    main()