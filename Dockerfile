FROM python:3.10-slim

WORKDIR /app

# 复制所有项目文件到工作目录
COPY ./backend .

# 安装所需依赖
RUN pip install --no-cache-dir -r requirements.txt

# 运行主程序
CMD ["python", "main.py"]
