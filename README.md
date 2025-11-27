# 🚀 Server Monitor System (服务器监控系统)

## 项目简介
这是一个轻量级、可视化的多主机服务器监控系统。支持实时 CPU/内存监控、历史数据回溯、自动告警检测以及数据导出功能。采用前后端分离思想（但在 Flask 中集成），基于 Docker 容器化部署。

## 👥 团队分工
*   **Member A (Backend)**: 负责 Flask 后端搭建、SQLite 数据库设计、API 接口开发。
*   **Member B (Frontend)**: 负责 Web 界面设计、ECharts 数据可视化、Ajax 交互。
*   **Member C (O&M)**: 负责 Agent 数据采集脚本、Docker 环境编排、集成测试。

## 🛠️ 技术栈
*   **Backend**: Python 3, Flask, SQLite
*   **Frontend**: HTML5, CSS3, JavaScript, ECharts, SheetJS
*   **Deployment**: Docker, Docker Compose

## 📂 目录结构
```text
myproject/
├── app.py                # Web 应用主程序
├── requirements.txt      # Python 依赖包
├── Dockerfile            # Docker 镜像构建文件
├── docker-compose.yml    # 容器编排文件
├── agent.py              # 客户端采集脚本 (部署在被监控主机上)
├── monitor.db            # SQLite 数据库 (自动生成)
└── templates/
    └── index.html        # 前端页面
