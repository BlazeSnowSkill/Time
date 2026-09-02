# -*- coding: utf-8 -*-
"""time skill 的共享基础库，按职责拆分：

- sources：网络校时源（NTP 优先，HTTP Date 头回退）
- timezones：时区解析
- formatting：校时结果组装与渲染
- utf8io：标准输入输出编码处理（GBK 规避）

后续新功能的实现优先复用这些模块，不要把逻辑堆回 CLI 入口脚本。
"""
