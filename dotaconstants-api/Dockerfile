# 使用 Node.js 官方镜像
FROM node:18

# 设置工作目录
WORKDIR /app

# 复制文件
COPY package*.json ./
COPY index.js ./

# 安装依赖
RUN npm install

# 暴露端口
EXPOSE 3000

# 启动服务
CMD ["node", "index.js"]