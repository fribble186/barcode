# 基础镜像使用官方的python image : 后面表示标签，3.6也就是3.6版本
FROM python:3.6
# 在镜像中创建目录，用来存放本机中的django项目
RUN mkdir /backend
# 将本机 . 也就是当前目录下所有文件都拷贝到image文件中指定目录
COPY . /backend
# 将/usr/src/app指定为工作目录
WORKDIR /backend
# 在image中安装运行django项目所需要的依赖
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
# 开放容器的8080端口，允许外部链接这个端口
EXPOSE 8000