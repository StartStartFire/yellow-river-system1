#!/usr/bin/env python
"""启动脚本

用法：
    python run.py
"""

import uvicorn
from app.config import config

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=config.host,
        port=config.port,
        reload=False,
        log_level="info"
    )
