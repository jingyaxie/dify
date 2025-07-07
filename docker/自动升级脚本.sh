#!/bin/bash

# Dify 自动升级脚本
# 包含数据库迁移、代码更新、配置备份等功能

set -e

echo "🚀 开始 Dify 自动升级..."

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

# 创建备份目录
BACKUP_DIR="backup_$(date +%Y%m%d_%H%M%S)"
echo "📦 创建备份目录: $BACKUP_DIR"
mkdir -p "$BACKUP_DIR"

# 备份现有配置
echo "📦 备份现有配置..."
if [ -f ".env" ]; then
    cp .env "$BACKUP_DIR/.env.backup"
    echo "✅ 已备份 .env 文件"
fi

if [ -f "docker-compose.yaml" ]; then
    cp docker-compose.yaml "$BACKUP_DIR/docker-compose.yaml.backup"
    echo "✅ 已备份 docker-compose.yaml 文件"
fi

# 备份数据库（可选）
echo "📦 备份数据库..."
if docker-compose ps | grep -q "db.*Up"; then
    echo "🔄 正在备份数据库..."
    docker-compose exec -T db pg_dump -U postgres dify > "$BACKUP_DIR/database_backup.sql" 2>/dev/null || {
        echo "⚠️  数据库备份失败，但继续升级..."
    }
    echo "✅ 数据库备份完成"
else
    echo "⚠️  数据库容器未运行，跳过数据库备份"
fi

# 停止现有服务
echo "🛑 停止现有服务..."
docker-compose down

# 拉取最新代码
echo "📥 拉取最新代码..."
cd ..
git fetch origin
git pull origin main

# 回到docker目录
cd docker

# 更新Docker镜像
echo "📦 更新Docker镜像..."
docker-compose pull

# 启动服务
echo "🚀 启动服务..."
docker-compose up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 20

# 执行数据库迁移
echo "🔄 执行数据库迁移..."
if docker-compose ps | grep -q "api.*Up"; then
    echo "🔄 正在执行数据库迁移..."
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
else
    echo "⚠️  API容器未运行，跳过数据库迁移"
fi

# 检查服务状态
echo "📊 检查服务状态..."
docker-compose ps

# 等待所有服务完全启动
echo "⏳ 等待所有服务完全启动..."
sleep 30

# 检查服务健康状态
echo "🔍 检查服务健康状态..."
SERVICES=("nginx" "api" "web" "worker" "db" "redis" "weaviate")

for service in "${SERVICES[@]}"; do
    if docker-compose ps | grep -q "$service.*Up"; then
        echo "✅ $service 服务运行正常"
    else
        echo "❌ $service 服务未正常运行"
    fi
done

# 检查Web服务可访问性
echo "🌐 检查Web服务可访问性..."
if curl -s http://localhost:5001 > /dev/null; then
    echo "✅ Web服务可正常访问"
else
    echo "⚠️  Web服务可能还在启动中"
fi

# 显示升级完成信息
echo ""
echo "🎉 Dify 自动升级完成！"
echo ""
echo "📋 升级信息："
echo "=========================================="
echo "📦 备份位置：$BACKUP_DIR"
echo "🌐 访问地址：http://localhost:5001"
echo "🔧 管理界面：http://localhost:5001/signin"
echo ""
echo "📊 服务状态："
docker-compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"
echo ""
echo "📝 升级后操作："
echo "1. 访问 http://localhost:5001 检查功能"
echo "2. 登录管理界面验证账号"
echo "3. 检查图片和视频功能是否默认开启"
echo "4. 如有问题，查看日志: docker-compose logs"
echo ""
echo "🔧 常用命令："
echo "  - 查看状态: docker-compose ps"
echo "  - 查看日志: docker-compose logs -f"
echo "  - 重启服务: docker-compose restart"
echo "  - 停止服务: docker-compose down"
echo ""
echo "📦 备份文件："
echo "  - 配置文件: $BACKUP_DIR/.env.backup"
echo "  - 数据库: $BACKUP_DIR/database_backup.sql"
echo "=========================================="

# 检查多模态功能是否默认开启
echo ""
echo "🔍 检查多模态功能配置..."
if docker-compose ps | grep -q "api.*Up"; then
    echo "🔄 检查数据库中的多模态配置..."
    docker-compose exec -T db psql -U postgres -d dify -c "
SELECT 
    dataset_id,
    enabled,
    image_model_provider,
    image_model_name,
    video_model_provider,
    video_model_name
FROM multimodal_configs 
LIMIT 5;
" 2>/dev/null || echo "⚠️  无法查询数据库，请手动检查"
fi

echo ""
echo "✅ 自动升级脚本执行完成！" 