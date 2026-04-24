"""
启动开发服务器
python3 run.py
"""

import sys
from pathlib import Path

# 确保后端根目录在 sys.path
sys.path.insert(0, str(Path(__file__).parent))

import uvicorn

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=False)
