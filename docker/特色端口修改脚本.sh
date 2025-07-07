#!/bin/bash

# Dify 特色端口修改脚本
# 自动修改所有端口为特色端口，避免本地和线上冲突

set -e

echo "🎨 开始应用 Dify 特色端口配置..."

# 检查是否在正确的目录
if [ ! -f "docker-compose.yaml" ]; then
    echo "❌ 错误：请在 dify/docker 目录下运行此脚本"
    exit 1
fi

# 备份原文件
echo "📦 备份原配置文件..."
cp docker-compose.yaml docker-compose.yaml.backup.$(date +%Y%m%d_%H%M%S)

# 应用特色端口配置
echo "🔧 应用特色端口配置..."

# 复制特色端口配置文件
if [ -f "特色端口配置.env" ]; then
    cp 特色端口配置.env .env
    echo "✅ 已应用特色端口配置"
else
    echo "⚠️  特色端口配置文件不存在，使用默认配置"
fi

# 修改硬编码端口
echo "🔧 修改硬编码端口..."

# 修改 Milvus 端口
sed -i 's/- 19530:19530/- 19531:19530/' docker-compose.yaml
sed -i 's/- 9091:9091/- 9092:9091/' docker-compose.yaml

# 修改 Vastbase 端口
sed -i "s/- '5434:5432'/- '5435:5432'/" docker-compose.yaml

echo "✅ 硬编码端口修改完成！"

# 显示特色端口配置
echo ""
echo "🎨 Dify 特色端口配置："
echo "=========================================="
echo "🌐 主服务端口："
echo "  - HTTP:  5001 (原 80)"
echo "  - HTTPS: 5002 (原 443)"
echo ""
echo "🗄️  数据库端口："
echo "  - PostgreSQL: 5433 (原 5432)"
echo "  - Redis:      6381 (原 6379)"
echo ""
echo "🔍 向量数据库端口："
echo "  - Weaviate:     8081 (原 8080)"
echo "  - OceanBase:    2882 (原 2881)"
echo "  - OpenGauss:    6601 (原 6600)"
echo "  - MyScale:      8124 (原 8123)"
echo "  - MatrixOne:    6002 (原 6001)"
echo "  - Elasticsearch: 9201 (原 9200)"
echo "  - Kibana:       5602 (原 5601)"
echo ""
echo "🛠️  其他服务端口："
echo "  - Sandbox:      8195 (原 8194)"
echo "  - SSRF Proxy:   3129 (原 3128)"
echo "  - Plugin:       5003/5004 (原 5002/5003)"
echo ""
echo "🔧 硬编码端口修改："
echo "  - Milvus:       19531:19530 (原 19530:19530)"
echo "  - Milvus:       9092:9091 (原 9091:9091)"
echo "  - Vastbase:     5435:5432 (原 5434:5432)"
echo "=========================================="

# 检查端口占用
echo ""
echo "🔍 检查特色端口占用情况..."
for port in 5001 5002 5433 6381 8081 2882 6601 8124 6002 9201 5602 8195 3129 5003 5004; do
    if netstat -tlnp 2>/dev/null | grep ":$port " > /dev/null; then
        echo "⚠️  警告：特色端口 $port 已被占用"
    else
        echo "✅ 特色端口 $port 可用"
    fi
done

echo ""
echo "🎉 特色端口配置完成！"
echo ""
echo "📋 下一步操作："
echo "1. 启动服务: docker-compose up -d"
echo "2. 访问地址: http://your-server-ip:5001"
echo "3. 初始化页面: http://your-server-ip:5001/init"
echo "4. 初始化密码: dify2024"
echo ""
echo "🔧 如需恢复原配置："
echo "cp docker-compose.yaml.backup.* docker-compose.yaml"
