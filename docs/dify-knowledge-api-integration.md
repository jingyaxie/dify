# Dify知识库API对接技术文档

## 1. 概述

本文档详细说明如何通过API方式访问和操作Dify知识库，包括知识库检索、文档管理、多模态处理等功能。

## 2. 基础信息

### 2.1 环境信息
- **基础URL**: `https://your-dify-instance.com`
- **API版本**: v1
- **认证方式**: Bearer Token
- **数据格式**: JSON

### 2.2 认证方式
```bash
# 请求头格式
Authorization: Bearer your-api-key
Content-Type: application/json
```

## 3. 核心API接口

### 3.1 知识库检索API

#### 3.1.1 应用级别检索（推荐）
```bash
POST /v1/chat-messages
```

**请求参数:**
```json
{
  "inputs": {},
  "query": "你的问题",
  "response_mode": "blocking",
  "user": "user123",
  "conversation_id": "conv_123"  // 可选，用于连续对话
}
```

**响应格式:**
```json
{
  "answer": "基于知识库的回答内容",
  "message_id": "msg_123",
  "conversation_id": "conv_456",
  "metadata": {
    "retrieval_from": "knowledge_base",
    "documents": [
      {
        "content": "相关文档内容",
        "score": 0.85,
        "source": "document_123"
      }
    ]
  }
}
```

#### 3.1.2 数据集直接检索
```bash
POST /console/api/workspaces/current/datasets/{dataset_id}/query
```

**请求参数:**
```json
{
  "query": "你的问题",
  "top_k": 5,
  "score_threshold": 0.7,
  "search_method": "semantic_search"
}
```

**响应格式:**
```json
{
  "data": [
    {
      "content": "相关文档片段",
      "score": 0.85,
      "document_id": "doc_123",
      "segment_id": "seg_456"
    }
  ],
  "total": 10
}
```

### 3.2 数据集管理API

#### 3.2.1 获取数据集列表
```bash
GET /console/api/workspaces/current/datasets?page=1&limit=20
```

**响应格式:**
```json
{
  "data": [
    {
      "id": "dataset_123",
      "name": "产品文档",
      "description": "产品相关文档",
      "document_count": 150,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 5,
  "page": 1,
  "limit": 20
}
```

#### 3.2.2 获取数据集详情
```bash
GET /console/api/workspaces/current/datasets/{dataset_id}
```

**响应格式:**
```json
{
  "id": "dataset_123",
  "name": "产品文档",
  "description": "产品相关文档",
  "document_count": 150,
  "segment_count": 1200,
  "indexing_status": "completed",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### 3.2.3 创建数据集
```bash
POST /console/api/workspaces/current/datasets
```

**请求参数:**
```json
{
  "name": "新数据集",
  "description": "数据集描述",
  "indexing_technique": "high_quality",
  "embedding_model": "text-embedding-ada-002",
  "embedding_model_provider": "openai"
}
```

### 3.3 文档管理API

#### 3.3.1 获取文档列表
```bash
GET /console/api/workspaces/current/datasets/{dataset_id}/documents?page=1&limit=20
```

**响应格式:**
```json
{
  "data": [
    {
      "id": "doc_123",
      "name": "产品手册.pdf",
      "status": "completed",
      "word_count": 5000,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 150,
  "page": 1,
  "limit": 20
}
```

#### 3.3.2 上传文档（支持多模态文件）
```bash
POST /console/api/workspaces/current/datasets/{dataset_id}/documents
```

**支持的文件类型:**
- **文本文档**: pdf, docx, txt, md, csv, xlsx
- **图片文件**: jpg, jpeg, png, gif, bmp, webp, svg
- **视频文件**: mp4, avi, mov, wmv, flv, webm, mkv

**请求参数:**
```bash
# 使用multipart/form-data格式
file: 文件内容
data_source_type: "upload_file"
```

**响应格式:**
```json
{
  "id": "doc_123",
  "name": "产品手册.pdf",
  "status": "processing",
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### 3.3.3 多模态文件上传详细说明

**图片文件上传:**
```bash
curl -X POST "https://your-dify-instance.com/console/api/workspaces/current/datasets/dataset_123/documents" \
  -H "Authorization: Bearer your-api-key" \
  -F "file=@product_image.jpg" \
  -F "data_source_type=upload_file"
```

**视频文件上传:**
```bash
curl -X POST "https://your-dify-instance.com/console/api/workspaces/current/datasets/dataset_123/documents" \
  -H "Authorization: Bearer your-api-key" \
  -F "file=@product_demo.mp4" \
  -F "data_source_type=upload_file"
```

**处理流程:**
1. 上传图片/视频文件到指定数据集
2. 系统自动检测文件类型
3. 如果启用了多模态功能，调用相应的AI模型进行内容识别
4. 图片：使用视觉语言模型识别图片中的文字和内容
5. 视频：使用语音识别模型提取视频中的口播文案
6. 生成结构化文本描述并存储到知识库
7. 进行向量化处理，支持后续检索

#### 3.3.4 删除文档
```bash
DELETE /console/api/workspaces/current/datasets/{dataset_id}/documents/{document_id}
```

### 3.4 多模态配置API（新增功能）

#### 3.4.1 获取多模态配置
```bash
GET /console/api/workspaces/current/datasets/{dataset_id}/multimodal-config
```

**响应格式:**
```json
{
  "data": {
    "id": "config_123",
    "tenant_id": "tenant_123",
    "dataset_id": "dataset_123",
    "image_model_provider": "tongyi",
    "image_model_name": "qwen-vl-plus",
    "video_model_provider": "openai",
    "video_model_name": "whisper-1",
    "enabled": true,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  },
  "code": 0
}
```

#### 3.4.2 更新多模态配置
```bash
PUT /console/api/workspaces/current/datasets/{dataset_id}/multimodal-config
```

**请求参数:**
```json
{
  "enabled": true,
  "image_model_provider": "tongyi",
  "image_model_name": "qwen-vl-plus",
  "video_model_provider": "openai",
  "video_model_name": "whisper-1"
}
```

## 4. 完整示例代码

### 4.1 Python示例

```python
import requests
import json
import os

class DifyKnowledgeAPI:
    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def query_knowledge_base(self, query, conversation_id=None):
        """知识库检索"""
        url = f"{self.base_url}/v1/chat-messages"
        data = {
            "inputs": {},
            "query": query,
            "response_mode": "blocking",
            "user": "user123"
        }
        if conversation_id:
            data["conversation_id"] = conversation_id
        
        response = requests.post(url, headers=self.headers, json=data)
        return response.json()
    
    def get_datasets(self, page=1, limit=20):
        """获取数据集列表"""
        url = f"{self.base_url}/console/api/workspaces/current/datasets"
        params = {"page": page, "limit": limit}
        response = requests.get(url, headers=self.headers, params=params)
        return response.json()
    
    def upload_document(self, dataset_id, file_path):
        """上传文档（支持多模态文件）"""
        url = f"{self.base_url}/console/api/workspaces/current/datasets/{dataset_id}/documents"
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        # 获取文件扩展名
        file_ext = os.path.splitext(file_path)[1].lower()
        
        # 支持的文件类型
        supported_types = {
            # 文本文档
            '.pdf', '.docx', '.txt', '.md', '.csv', '.xlsx',
            # 图片文件
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg',
            # 视频文件
            '.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mkv'
        }
        
        if file_ext not in supported_types:
            raise ValueError(f"不支持的文件类型: {file_ext}")
        
        with open(file_path, 'rb') as f:
            files = {'file': (os.path.basename(file_path), f, 'application/octet-stream')}
            data = {'data_source_type': 'upload_file'}
            
            # 移除Content-Type头，让requests自动设置multipart/form-data
            upload_headers = {k: v for k, v in self.headers.items() if k != 'Content-Type'}
            response = requests.post(url, headers=upload_headers, files=files, data=data)
        
        return response.json()
    
    def upload_multimodal_files(self, dataset_id, file_paths):
        """批量上传多模态文件"""
        results = []
        for file_path in file_paths:
            try:
                result = self.upload_document(dataset_id, file_path)
                results.append({
                    'file': file_path,
                    'success': True,
                    'result': result
                })
            except Exception as e:
                results.append({
                    'file': file_path,
                    'success': False,
                    'error': str(e)
                })
        return results
    
    def get_multimodal_config(self, dataset_id):
        """获取多模态配置"""
        url = f"{self.base_url}/console/api/workspaces/current/datasets/{dataset_id}/multimodal-config"
        response = requests.get(url, headers=self.headers)
        return response.json()
    
    def update_multimodal_config(self, dataset_id, config):
        """更新多模态配置"""
        url = f"{self.base_url}/console/api/workspaces/current/datasets/{dataset_id}/multimodal-config"
        response = requests.put(url, headers=self.headers, json=config)
        return response.json()

# 使用示例
if __name__ == "__main__":
    dify_api = DifyKnowledgeAPI(
        base_url="https://your-dify-instance.com",
        api_key="your-api-key"
    )
    
    # 1. 知识库检索
    result = dify_api.query_knowledge_base("请介绍一下Dify的功能特点")
    print("检索结果:", result)
    
    # 2. 获取数据集列表
    datasets = dify_api.get_datasets()
    print("数据集列表:", datasets)
    
    # 3. 上传单个文档
    upload_result = dify_api.upload_document("dataset_123", "document.pdf")
    print("上传结果:", upload_result)
    
    # 4. 批量上传多模态文件
    multimodal_files = [
        "product_image.jpg",
        "demo_video.mp4", 
        "manual.pdf"
    ]
    batch_results = dify_api.upload_multimodal_files("dataset_123", multimodal_files)
    print("批量上传结果:", batch_results)
    
    # 5. 配置多模态功能
    config = {
        "enabled": True,
        "image_model_provider": "tongyi",
        "image_model_name": "qwen-vl-plus",
        "video_model_provider": "openai",
        "video_model_name": "whisper-1"
    }
    config_result = dify_api.update_multimodal_config("dataset_123", config)
    print("配置结果:", config_result)
```

### 4.2 JavaScript/TypeScript示例

```typescript
interface DifyConfig {
  baseUrl: string;
  apiKey: string;
}

interface QueryRequest {
  query: string;
  conversationId?: string;
  user?: string;
}

interface MultimodalConfig {
  enabled: boolean;
  imageModelProvider?: string;
  imageModelName?: string;
  videoModelProvider?: string;
  videoModelName?: string;
}

interface UploadResult {
  file: string;
  success: boolean;
  result?: any;
  error?: string;
}

class DifyKnowledgeAPI {
  private baseUrl: string;
  private headers: Record<string, string>;

  constructor(config: DifyConfig) {
    this.baseUrl = config.baseUrl;
    this.headers = {
      'Authorization': `Bearer ${config.apiKey}`,
      'Content-Type': 'application/json'
    };
  }

  async queryKnowledgeBase(request: QueryRequest): Promise<any> {
    const url = `${this.baseUrl}/v1/chat-messages`;
    const data = {
      inputs: {},
      query: request.query,
      response_mode: 'blocking',
      user: request.user || 'user123',
      ...(request.conversationId && { conversation_id: request.conversationId })
    };

    const response = await fetch(url, {
      method: 'POST',
      headers: this.headers,
      body: JSON.stringify(data)
    });

    return response.json();
  }

  async getDatasets(page = 1, limit = 20): Promise<any> {
    const url = `${this.baseUrl}/console/api/workspaces/current/datasets?page=${page}&limit=${limit}`;
    const response = await fetch(url, {
      method: 'GET',
      headers: this.headers
    });

    return response.json();
  }

  async uploadDocument(datasetId: string, file: File): Promise<any> {
    const url = `${this.baseUrl}/console/api/workspaces/current/datasets/${datasetId}/documents`;
    
    // 检查文件类型
    const supportedTypes = [
      // 文本文档
      '.pdf', '.docx', '.txt', '.md', '.csv', '.xlsx',
      // 图片文件
      '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg',
      // 视频文件
      '.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mkv'
    ];
    
    const fileExt = file.name.toLowerCase().substring(file.name.lastIndexOf('.'));
    if (!supportedTypes.includes(fileExt)) {
      throw new Error(`不支持的文件类型: ${fileExt}`);
    }
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('data_source_type', 'upload_file');

    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Authorization': this.headers.Authorization
      },
      body: formData
    });

    return response.json();
  }

  async uploadMultimodalFiles(datasetId: string, files: File[]): Promise<UploadResult[]> {
    const results: UploadResult[] = [];
    
    for (const file of files) {
      try {
        const result = await this.uploadDocument(datasetId, file);
        results.push({
          file: file.name,
          success: true,
          result
        });
      } catch (error) {
        results.push({
          file: file.name,
          success: false,
          error: error instanceof Error ? error.message : String(error)
        });
      }
    }
    
    return results;
  }

  async getMultimodalConfig(datasetId: string): Promise<any> {
    const url = `${this.baseUrl}/console/api/workspaces/current/datasets/${datasetId}/multimodal-config`;
    const response = await fetch(url, {
      method: 'GET',
      headers: this.headers
    });

    return response.json();
  }

  async updateMultimodalConfig(datasetId: string, config: MultimodalConfig): Promise<any> {
    const url = `${this.baseUrl}/console/api/workspaces/current/datasets/${datasetId}/multimodal-config`;
    const response = await fetch(url, {
      method: 'PUT',
      headers: this.headers,
      body: JSON.stringify(config)
    });

    return response.json();
  }
}

// 使用示例
const difyAPI = new DifyKnowledgeAPI({
  baseUrl: 'https://your-dify-instance.com',
  apiKey: 'your-api-key'
});

// 知识库检索
difyAPI.queryKnowledgeBase({
  query: '请介绍一下Dify的功能特点'
}).then(result => {
  console.log('检索结果:', result);
});

// 获取数据集
difyAPI.getDatasets().then(datasets => {
  console.log('数据集列表:', datasets);
});

// 上传单个文件
const fileInput = document.getElementById('fileInput') as HTMLInputElement;
if (fileInput.files && fileInput.files[0]) {
  difyAPI.uploadDocument('dataset_123', fileInput.files[0]).then(result => {
    console.log('上传结果:', result);
  });
}

// 批量上传多模态文件
const fileList = document.getElementById('fileList') as HTMLInputElement;
if (fileList.files) {
  const files = Array.from(fileList.files);
  difyAPI.uploadMultimodalFiles('dataset_123', files).then(results => {
    console.log('批量上传结果:', results);
  });
}

// 配置多模态
difyAPI.updateMultimodalConfig('dataset_123', {
  enabled: true,
  imageModelProvider: 'tongyi',
  imageModelName: 'qwen-vl-plus',
  videoModelProvider: 'openai',
  videoModelName: 'whisper-1'
}).then(result => {
  console.log('配置结果:', result);
});
```

### 4.3 cURL示例

```bash
# 1. 知识库检索
curl -X POST "https://your-dify-instance.com/v1/chat-messages" \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "inputs": {},
    "query": "请介绍一下Dify的功能特点",
    "response_mode": "blocking",
    "user": "user123"
  }'

# 2. 获取数据集列表
curl -X GET "https://your-dify-instance.com/console/api/workspaces/current/datasets?page=1&limit=20" \
  -H "Authorization: Bearer your-api-key"

# 3. 上传图片文件
curl -X POST "https://your-dify-instance.com/console/api/workspaces/current/datasets/dataset_123/documents" \
  -H "Authorization: Bearer your-api-key" \
  -F "file=@product_image.jpg" \
  -F "data_source_type=upload_file"

# 4. 上传视频文件
curl -X POST "https://your-dify-instance.com/console/api/workspaces/current/datasets/dataset_123/documents" \
  -H "Authorization: Bearer your-api-key" \
  -F "file=@demo_video.mp4" \
  -F "data_source_type=upload_file"

# 5. 上传PDF文档
curl -X POST "https://your-dify-instance.com/console/api/workspaces/current/datasets/dataset_123/documents" \
  -H "Authorization: Bearer your-api-key" \
  -F "file=@manual.pdf" \
  -F "data_source_type=upload_file"

# 6. 配置多模态功能
curl -X PUT "https://your-dify-instance.com/console/api/workspaces/current/datasets/dataset_123/multimodal-config" \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "enabled": true,
    "image_model_provider": "tongyi",
    "image_model_name": "qwen-vl-plus",
    "video_model_provider": "openai",
    "video_model_name": "whisper-1"
  }'
```

## 5. 错误处理

### 5.1 常见错误码

| 错误码 | 说明 | 解决方案 |
|--------|------|----------|
| 401 | 认证失败 | 检查API Key是否正确 |
| 403 | 权限不足 | 检查用户权限 |
| 404 | 资源不存在 | 检查数据集ID等参数 |
| 429 | 请求频率限制 | 降低请求频率 |
| 500 | 服务器错误 | 联系管理员 |

### 5.2 错误响应格式

```json
{
  "code": 401,
  "message": "认证失败",
  "details": "API Key无效或已过期"
}
```

## 6. 最佳实践

### 6.1 性能优化
- 使用连接池复用HTTP连接
- 实现请求重试机制
- 合理设置超时时间
- 使用异步处理大量请求

### 6.2 安全建议
- 定期轮换API Key
- 使用HTTPS传输
- 限制API Key权限范围
- 监控异常访问

### 6.3 错误处理
- 实现完善的错误处理机制
- 记录详细的错误日志
- 提供用户友好的错误提示
- 实现自动重试机制

## 7. 多模态功能说明

### 7.1 支持的文件类型
- **图片**: jpg, jpeg, png, gif, bmp, webp, svg
- **视频**: mp4, avi, mov, wmv, flv, webm, mkv

### 7.2 处理流程
1. 上传图片/视频文件
2. 系统自动检测文件类型
3. 调用多模态模型进行内容识别
4. 生成结构化文本描述
5. 存储到知识库进行向量化

### 7.3 配置说明
- 默认关闭多模态功能
- 需要手动开启才能使用
- 支持动态切换模型
- 完全兼容现有流程

## 8. 更新日志

### v1.0.0 (2024-12-19)
- 新增多模态配置API
- 支持图片和视频内容识别
- 支持通义千问和OpenAI模型
- 完善错误处理和文档

---

**注意**: 使用前请确保已正确配置Dify实例和API Key，并根据实际环境调整基础URL。 