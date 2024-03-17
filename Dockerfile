# 设置基础镜像
FROM python:3.8
RUN apt-get update
RUN apt-get -y upgrade
# 设置工作目录
WORKDIR /app

# 将当前目录下的所有文件复制到容器的工作目录
COPY . /app

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 暴露端口
EXPOSE 80

CMD ["python", "./fournisseur.py"]



