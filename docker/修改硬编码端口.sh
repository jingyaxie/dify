#!/bin/bash

# Dify 硬编码端口修改脚本
# 用于修改docker-compose.yaml中的硬编码端口

echo "开始修改硬编码端口..."

# 备份原文件
cp docker-compose.yaml docker-compose.yaml.backup
echo "已备份原文件为 docker-compose.yaml.backup"

# 修改 Milvus 端口
echo "修改 Milvus 端口..."
sed -i 's/- 19530:19530/- 19531:19530/' docker-compose.yaml
sed -i 's/- 9091:9091/- 9092:9091/' docker-compose.yaml

# 修改 Vastbase 端口
echo "修改 Vastbase 端口..."
sed -i "s/- '5434:5432'/- '5435:5432'/" docker-compose.yaml

echo "硬编码端口修改完成！"
echo ""
echo "修改内容："
echo "- Milvus: 19530:19530 → 19531:19530"
echo "- Milvus: 9091:9091 → 9092:9091"
echo "- Vastbase: 5434:5432 → 5435:5432"
echo ""
echo "现在可以运行: docker-compose up -d"
echo ""
echo "如果需要恢复原配置，运行: cp docker-compose.yaml.backup docker-compose.yaml"
