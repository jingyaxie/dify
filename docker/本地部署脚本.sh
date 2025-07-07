#!/bin/bash

# Dify 本地环境部署脚本
# 专门为本地开发环境设计，避免端口冲突

set -e

echo "🏠 开始本地环境部署 Dify..."

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

# 备份现有配置
if [ -f ".env" ]; then
    echo "📦 备份现有 .env 文件..."
    cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
fi

# 创建本地特色端口配置
echo "🔧 创建本地特色端口配置..."

cat > .env << 'ENV_EOF'
# ==========================================
# Dify 本地环境特色端口配置
# ==========================================

# ==========================================
# 主要服务端口 - 本地特色端口
# ==========================================
# Nginx 端口 - 避免与本地其他服务冲突
EXPOSE_NGINX_PORT=5001
EXPOSE_NGINX_SSL_PORT=5002
NGINX_PORT=80
NGINX_SSL_PORT=443

# ==========================================
# 数据库和缓存端口 - 本地特色端口
# ==========================================
# PostgreSQL - 避免与本地PostgreSQL冲突
EXPOSE_POSTGRES_PORT=5433
# Redis - 避免与本地Redis冲突
EXPOSE_REDIS_PORT=6381

# ==========================================
# 向量数据库端口 - 本地特色配置
# ==========================================
# Weaviate - 避免与本地Web服务冲突
EXPOSE_WEAVIATE_PORT=8081

# OceanBase - 本地特色端口
OCEANBASE_VECTOR_PORT=2882

# OpenGauss - 本地特色端口
OPENGAUSS_PORT=6601

# MyScale - 本地特色端口
MYSCALE_PORT=8124

# MatrixOne - 本地特色端口
MATRIXONE_PORT=6002

# Elasticsearch - 避免与本地ES冲突
ELASTICSEARCH_PORT=9201
KIBANA_PORT=5602

# ==========================================
# 其他服务端口 - 本地特色配置
# ==========================================
# Sandbox - 本地特色端口
EXPOSE_SANDBOX_PORT=8195

# SSRF Proxy - 本地特色端口
EXPOSE_SSRF_PROXY_PORT=3129

# Plugin Daemon - 本地特色端口
EXPOSE_PLUGIN_DAEMON_PORT=5003
EXPOSE_PLUGIN_DEBUGGING_PORT=5004

# ==========================================
# 管理员初始化配置
# ==========================================
# 设置本地初始化密码
INIT_PASSWORD=dify2024

# ==========================================
# 数据库配置 - 本地特色密码
# ==========================================
POSTGRES_USER=postgres
POSTGRES_PASSWORD=dify2024
POSTGRES_DB=dify
PGDATA=/var/lib/postgresql/data/pgdata

# Redis配置 - 本地特色密码
REDIS_PASSWORD=dify2024

# ==========================================
# 本地开发优化配置
# ==========================================
# 启用调试模式
DEBUG=true
FLASK_DEBUG=true

# 允许注册
ENABLE_REGISTER=true

# 开发环境配置
DEPLOY_ENV=DEVELOPMENT

# ==========================================
# 本地特色端口说明
# ==========================================
# 5001/5002: Dify 主服务端口 (Dify = 5个字母)
# 5433: PostgreSQL 本地特色端口
# 6381: Redis 本地特色端口
# 8081: Weaviate 本地特色端口
# 2882: OceanBase 本地特色端口
# 6601: OpenGauss 本地特色端口
# 8124: MyScale 本地特色端口
# 6002: MatrixOne 本地特色端口
# 9201: Elasticsearch 本地特色端口
# 5602: Kibana 本地特色端口
# 8195: Sandbox 本地特色端口
# 3129: SSRF Proxy 本地特色端口
# 5003/5004: Plugin 本地特色端口
ENV_EOF

echo "✅ 本地特色端口配置创建完成！"

# 修改硬编码端口
echo "🔧 修改硬编码端口..."

# 备份docker-compose.yaml
cp docker-compose.yaml docker-compose.yaml.backup.$(date +%Y%m%d_%H%M%S)

# 修改 Milvus 端口
sed -i '' 's/- 19530:19530/- 19531:19530/' docker-compose.yaml
sed -i '' 's/- 9091:9091/- 9092:9091/' docker-compose.yaml

# 修改 Vastbase 端口
sed -i '' "s/- '5434:5432'/- '5435:5432'/" docker-compose.yaml

echo "✅ 硬编码端口修改完成！"

# 检查本地端口占用
echo "🔍 检查本地端口占用情况..."
local_ports=(5001 5002 5433 6381 8081 2882 6601 8124 6002 9201 5602 8195 3129 5003 5004)

for port in "${local_ports[@]}"; do
    if lsof -i :$port > /dev/null 2>&1; then
        echo "⚠️  警告：本地端口 $port 已被占用"
        echo "   占用进程: $(lsof -i :$port | tail -n +2)"
    else
        echo "✅ 本地端口 $port 可用"
    fi
done

# 停止可能冲突的本地服务
echo "🛑 检查并停止可能冲突的本地服务..."

# 检查本地PostgreSQL
if pg_isready -h localhost -p 5432 > /dev/null 2>&1; then
    echo "⚠️  检测到本地PostgreSQL运行在5432端口"
    echo "   建议停止或修改本地PostgreSQL端口"
fi

# 检查本地Redis
if redis-cli ping > /dev/null 2>&1; then
    echo "⚠️  检测到本地Redis运行"
    echo "   建议停止或修改本地Redis端口"
fi

# 检查本地Nginx
if pgrep nginx > /dev/null 2>&1; then
    echo "⚠️  检测到本地Nginx运行"
    echo "   建议停止或修改本地Nginx端口"
fi

# 启动Dify服务
echo "🚀 启动 Dify 本地服务..."
docker-compose up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 15

# 检查服务状态
echo "📊 检查本地服务状态..."
docker-compose ps

# 显示本地访问信息
echo ""
echo "🎉 本地部署完成！"
echo ""
echo "📋 本地访问信息："
echo "=========================================="
echo "🌐 主服务地址："
echo "  - HTTP:  http://localhost:5001"
echo "  - HTTPS: https://localhost:5002"
echo ""
echo "🔧 管理界面："
echo "  - 初始化页面: http://localhost:5001/init"
echo "  - 登录页面:   http://localhost:5001/signin"
echo ""
echo "🔐 默认账号信息："
echo "  - 初始化密码: dify2024"
echo "  - 数据库密码: dify2024"
echo "  - Redis密码:  dify2024"
echo ""
echo "📊 服务状态检查："
echo "  - 查看状态: docker-compose ps"
echo "  - 查看日志: docker-compose logs"
echo "  - 重启服务: docker-compose restart"
echo ""
echo "🔧 本地特色端口配置："
echo "  - Nginx:      5001/5002"
echo "  - PostgreSQL: 5433"
echo "  - Redis:      6381"
echo "  - Weaviate:   8081"
echo "  - 其他服务:   特色端口配置"
echo "=========================================="

# 提供快速访问链接
echo ""
echo "🚀 快速访问："
echo "curl -I http://localhost:5001"
echo ""

# 检查服务是否正常
if curl -s http://localhost:5001 > /dev/null; then
    echo "✅ 服务启动成功！可以访问 http://localhost:5001"
else
    echo "⚠️  服务可能还在启动中，请稍等片刻..."
    echo "   查看启动日志: docker-compose logs nginx"
fi

echo ""
echo "📝 本地开发提示："
echo "1. 如需修改配置，编辑 .env 文件后重启服务"
echo "2. 如需查看日志，使用: docker-compose logs -f"
echo "3. 如需停止服务，使用: docker-compose down"
echo "4. 如需清理数据，使用: docker-compose down -v"
