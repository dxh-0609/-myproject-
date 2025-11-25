# 使用 Python 基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 复制当前目录文件到容器中
COPY . .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 暴露端口
EXPOSE 5000

# 启动命令
CMD ["python", "app.py"]
