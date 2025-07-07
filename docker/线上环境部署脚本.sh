#!/bin/bash

# Dify 线上环境部署脚本
# 适用于生产环境部署

set -e

echo "🚀 开始部署 Dify 到线上环境..."

# 检查是否在正确的目录
if [ ! -f "docker-compose.yaml" ]; then
    echo "❌ 错误：请在 dify/docker 目录下运行此脚本"
    exit 1
fi

# 备份现有配置
if [ -f ".env" ]; then
    echo "📦 备份现有 .env 文件..."
    cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
fi

# 复制示例配置文件
echo "📋 复制环境变量配置文件..."
cp .env.example .env

# 修改关键配置以适应线上环境
echo "🔧 修改配置以适应线上环境..."

# 修改端口以避免冲突
sed -i 's/EXPOSE_NGINX_PORT=80/EXPOSE_NGINX_PORT=8080/' .env
sed -i 's/EXPOSE_NGINX_SSL_PORT=443/EXPOSE_NGINX_SSL_PORT=8443/' .env

# 设置初始化密码
echo "🔐 设置初始化密码..."
if [ -z "$INIT_PASSWORD" ]; then
    # 生成随机密码
    INIT_PASSWORD=$(openssl rand -base64 12 | tr -d "=+/" | cut -c1-12)
    echo "生成的初始化密码: $INIT_PASSWORD"
fi
sed -i "s/INIT_PASSWORD=/INIT_PASSWORD=$INIT_PASSWORD/" .env

# 修改数据库密码（可选）
if [ ! -z "$DB_PASSWORD" ]; then
    echo "🔑 使用自定义数据库密码..."
    sed -i "s/POSTGRES_PASSWORD=\${DB_PASSWORD}/POSTGRES_PASSWORD=$DB_PASSWORD/" .env
    sed -i "s/REDIS_PASSWORD=difyai123456/REDIS_PASSWORD=$DB_PASSWORD/" .env
fi

# 修改其他端口以避免冲突
sed -i 's/EXPOSE_POSTGRES_PORT=5432/EXPOSE_POSTGRES_PORT=5433/' .env
sed -i 's/EXPOSE_REDIS_PORT=6379/EXPOSE_REDIS_PORT=6380/' .env

echo "✅ 配置修改完成！"

# 检查端口占用
echo "�� 检查端口占用情况..."
for port in 8080 8443 5433 6380; do
    if netstat -tlnp 2>/dev/null | grep ":$port " > /dev/null; then
        echo "⚠️  警告：端口 $port 已被占用"
    else
        echo "✅ 端口 $port 可用"
    fi
done

# 启动服务
echo "🚀 启动 Dify 服务..."
docker-compose up -d

# 检查服务状态
echo "📊 检查服务状态..."
sleep 10
docker-compose ps

echo ""
echo "🎉 部署完成！"
echo ""
echo "📋 重要信息："
echo "- 访问地址: http://your-server-ip:8080"
echo "- 初始化密码: $INIT_PASSWORD"
echo "- 初始化页面: http://your-server-ip:8080/init"
echo ""
echo "�� 下一步操作："
echo "1. 访问 http://your-server-ip:8080/init"
echo "2. 输入初始化密码: $INIT_PASSWORD"
echo "3. 创建管理员账号"
echo "4. 登录系统开始使用"
echo ""
echo "🔧 如需修改配置，编辑 .env 文件后运行: docker-compose restart"
