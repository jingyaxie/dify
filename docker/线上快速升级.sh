#!/bin/bash

# Dify 线上快速升级脚本
# 专门用于生产环境的快速升级

set -e

echo "🚀 开始 Dify 线上快速升级..."

# 检查是否在正确的目录
if [ ! -f "docker-compose.yaml" ]; then
    echo "❌ 错误：请在 dify/docker 目录下运行此脚本"
    exit 1
fi

# 检查Docker是否运行
if ! docker info > /dev/null 2>&1; then
    echo "❌ 错误：Docker 未运行，请先启动 Docker"
    exit 1
fi

# 创建备份
echo "📦 创建配置备份..."
BACKUP_TIME=$(date +%Y%m%d_%H%M%S)
if [ -f ".env" ]; then
    cp .env ".env.backup.$BACKUP_TIME"
    echo "✅ 已备份 .env 文件"
fi

# 停止服务
echo "🛑 停止现有服务..."
docker-compose down

# 拉取最新代码
echo "📥 拉取最新代码..."
cd ..
git fetch origin
git pull origin main
cd docker

# 更新镜像
echo "📦 更新Docker镜像..."
docker-compose pull

# 启动服务
echo "🚀 启动服务..."
docker-compose up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 30

# 执行数据库迁移
echo "🔄 执行数据库迁移..."
if docker-compose ps | grep -q "api.*Up"; then
    docker-compose exec -T api flask db upgrade || {
        echo "⚠️  数据库迁移失败，尝试手动执行..."
        docker-compose exec -T api python -c "
from api import create_app
from api.models import db
app = create_app()
with app.app_context():
    db.create_all()
print('数据库表创建完成')
"
    }
    echo "✅ 数据库迁移完成"
fi

# 检查服务状态
echo "📊 检查服务状态..."
docker-compose ps

# 检查Web服务
echo "🌐 检查Web服务..."
if curl -s http://localhost:5001 > /dev/null; then
    echo "✅ Web服务可正常访问"
else
    echo "⚠️  Web服务可能还在启动中"
fi

echo ""
echo "🎉 线上快速升级完成！"
echo "🌐 访问地址：http://localhost:5001"
echo "📊 服务状态：docker-compose ps" 