# Dify 知识库多模态向量化功能设计文档

## 1. 功能概述

### 1.1 目标
为Dify知识库添加图片和视频向量化支持，通过多模态大模型识别图片内容，通过语音转文本处理视频，将处理后的文本内容加入到知识库中进行向量化存储。

### 1.2 核心功能
- **图片向量化**：识别图片中的文字信息，生成描述文本，加入知识库
- **视频向量化**：提取视频音频，转换为文字，加入知识库
- **URL链接支持**：支持图片和视频URL链接的处理
- **动态模型切换**：支持通义千问和OpenAI等多模态模型的动态切换

## 2. 技术架构设计

### 2.1 整体架构
```
用户上传文件 → 文件类型检测 → 多模态处理 → 文本生成 → 知识库向量化
     ↓              ↓              ↓              ↓              ↓
  现有流程     新增类型检测    新增处理器      文本整合      现有流程
```

### 2.2 核心组件
- **文件类型检测器**：识别图片和视频文件
- **多模态提取器**：处理图片和视频内容
- **文本生成器**：生成结构化文本描述
- **URL处理器**：处理图片和视频URL链接

## 3. 详细技术方案

### 3.1 文件类型检测与拦截

#### 3.1.1 支持的文件格式
**图片格式**：
- `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.webp`, `.svg`

**视频格式**：
- `.mp4`, `.avi`, `.mov`, `.wmv`, `.flv`, `.webm`, `.mkv`

#### 3.1.2 拦截位置
- **修改文件**：`api/core/rag/extractor/extract_processor.py`
- **新增检测逻辑**：在 `ExtractProcessor.extract()` 方法中添加文件类型检测

### 3.2 多模态提取器设计

#### 3.2.1 图片提取器
**文件位置**：`api/core/rag/extractor/multimodal_image_extractor.py`

**功能**：
- 调用多模态大模型识别图片内容
- 生成图片描述文本
- 添加图片URL信息
- 返回结构化文本

#### 3.2.2 视频提取器
**文件位置**：`api/core/rag/extractor/multimodal_video_extractor.py`

**功能**：
- 提取视频音频
- 调用语音转文本模型
- 生成视频描述文本
- 添加视频URL信息
- 返回结构化文本

### 3.3 文本生成格式

#### 3.3.1 图片文本格式
```
[图片描述]
图片URL: {image_url}
图片内容: {image_description}
图片类型: {image_type}
文件大小: {file_size}
上传时间: {upload_time}
```

#### 3.3.2 视频文本格式
```
[视频描述]
视频URL: {video_url}
视频标题: {video_title}
视频时长: {duration}
音频转文本: {audio_transcription}
视频描述: {video_description}
文件大小: {file_size}
上传时间: {upload_time}
```

### 3.4 模型配置支持

#### 3.4.1 支持的模型
- **通义千问**：`qwen-vl-plus`（图片）, `qwen-audio`（音频）
- **OpenAI**：`gpt-4-vision-preview`（图片）, `whisper-1`（音频）

#### 3.4.2 动态切换机制
- 支持根据配置动态选择模型
- 支持负载均衡和故障转移
- 支持模型性能监控

## 4. 数据库设计

### 4.1 新增字段
在 `models/dataset.py` 的 `Document` 模型中添加：

```python
# 多模态相关字段
multimodal_type = db.Column(db.String(20), nullable=True)  # 'image', 'video'
original_url = db.Column(db.Text, nullable=True)  # 原始文件URL
processed_content = db.Column(db.Text, nullable=True)  # 处理后的内容
model_used = db.Column(db.String(100), nullable=True)  # 使用的模型
processing_time = db.Column(db.Float, nullable=True)  # 处理耗时
```

### 4.2 配置表
在 `models/dataset.py` 中新增：

```python
class MultimodalConfig(db.Model):
    __tablename__ = 'multimodal_configs'
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.String(128), nullable=False)
    dataset_id = db.Column(db.String(128), nullable=False)
    image_model_provider = db.Column(db.String(50), nullable=True)
    image_model_name = db.Column(db.String(100), nullable=True)
    video_model_provider = db.Column(db.String(50), nullable=True)
    video_model_name = db.Column(db.String(100), nullable=True)
    enabled = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

## 5. API接口设计

### 5.1 配置接口

#### 5.1.1 获取多模态配置
```
GET /console/api/workspaces/current/datasets/{dataset_id}/multimodal-config
```

#### 5.1.2 更新多模态配置
```
PUT /console/api/workspaces/current/datasets/{dataset_id}/multimodal-config
```

### 5.2 处理接口

#### 5.2.1 图片处理
```
POST /console/api/workspaces/current/datasets/{dataset_id}/process-image
```

#### 5.2.2 视频处理
```
POST /console/api/workspaces/current/datasets/{dataset_id}/process-video
```

## 6. 前端界面设计

### 6.1 配置页面
- 模型选择下拉框
- 启用/禁用开关
- 处理参数设置
- 测试按钮

### 6.2 上传界面
- 文件类型检测
- 处理进度显示
- 结果预览
- 错误处理

## 7. 开发计划

### 7.1 第一阶段：基础架构
- [ ] 创建多模态提取器基类
- [ ] 实现文件类型检测
- [ ] 添加数据库字段

### 7.2 第二阶段：图片处理
- [ ] 实现图片提取器
- [ ] 集成通义千问和OpenAI模型
- [ ] 添加图片处理API

### 7.3 第三阶段：视频处理
- [ ] 实现视频提取器
- [ ] 集成语音转文本模型
- [ ] 添加视频处理API

### 7.4 第四阶段：前端集成
- [ ] 添加配置界面
- [ ] 集成到上传流程
- [ ] 添加进度显示

### 7.5 第五阶段：测试优化
- [ ] 单元测试
- [ ] 集成测试
- [ ] 性能优化

## 8. 技术细节

### 8.1 错误处理
- 模型调用失败重试机制
- 文件格式不支持的错误提示
- 处理超时的超时控制

### 8.2 性能优化
- 异步处理机制
- 缓存机制
- 批量处理支持

### 8.3 安全考虑
- 文件大小限制
- 文件类型验证
- URL安全性检查

## 9. 部署说明

### 9.1 依赖要求
- 无需新增Python包依赖
- 复用现有的模型运行时架构
- 支持Docker部署

### 9.2 配置要求
- 需要配置多模态模型凭据
- 需要配置文件存储服务
- 需要配置数据库迁移

## 10. 测试计划

### 10.1 单元测试
- 文件类型检测测试
- 图片处理测试
- 视频处理测试

### 10.2 集成测试
- 端到端处理流程测试
- 模型切换测试
- 错误处理测试

### 10.3 性能测试
- 处理速度测试
- 并发处理测试
- 内存使用测试

## 11. 维护计划

### 11.1 监控指标
- 处理成功率
- 平均处理时间
- 模型调用次数

### 11.2 日志记录
- 处理过程日志
- 错误日志
- 性能日志

### 11.3 更新计划
- 支持更多文件格式
- 支持更多模型
- 优化处理算法
