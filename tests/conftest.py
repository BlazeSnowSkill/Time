# -*- coding: utf-8 -*-
"""pytest 共享配置：把 scripts/ 加入导入路径，使测试可直接 import timelib 与 CLI 入口。"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
