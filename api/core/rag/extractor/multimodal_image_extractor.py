"""
图片多模态提取器
支持图片内容识别和文本生成
"""

import base64
import logging
import os
import time
from pathlib import Path
from typing import Optional, Dict, Any, List

from core.rag.extractor.multimodal_base_extractor import MultimodalBaseExtractor
from core.rag.models.document import Document
from core.model_runtime.entities.message_entities import PromptMessage
from core.model_runtime.entities.llm_entities import LLMResult

logger = logging.getLogger(__name__)


class MultimodalImageExtractor(MultimodalBaseExtractor):
    """
    图片多模态提取器
    """
    
    def __init__(self, tenant_id: str):
        super().__init__(tenant_id)
        
    def get_supported_extensions(self) -> List[str]:
        """
        获取支持的图片文件扩展名
        
        Returns:
            支持的图片文件扩展名列表
        """
        return [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg"]
    
    def extract(self, file_path: str, file_url: Optional[str] = None, **kwargs) -> List[Document]:
        """
        提取图片内容
        
        Args:
            file_path: 图片文件路径
            file_url: 图片URL（可选）
            **kwargs: 其他参数
            
        Returns:
            文档列表
        """
        start_time = time.time()
        
        try:
            # 获取图片数据
            image_data = self._get_image_data(file_path, file_url)
            if not image_data:
                logger.error(f"Failed to get image data from {file_path}")
                return []
            
            # 获取模型配置
            model_config = self._get_model_config()
            if not model_config:
                logger.warning("No multimodal model configured, using default text extractor")
                return self._fallback_to_text_extractor(file_path)
            
            # 调用多模态模型识别图片
            image_description = self._recognize_image_content(image_data, model_config)
            
            # 生成结构化文本
            structured_text = self.generate_structured_text('image', **{
                'image_url': file_url or file_path,
                'image_description': image_description,
                'image_type': Path(file_path).suffix.lower(),
                'file_size': self._get_file_size(file_path),
                'upload_time': time.strftime('%Y-%m-%d %H:%M:%S')
            })
            
            # 创建文档
            document = Document(
                page_content=structured_text,
                metadata={
                    'source': file_path,
                    'type': 'image',
                    'multimodal_type': 'image',
                    'original_url': file_url,
                    'processed_content': image_description,
                    'model_used': f"{model_config['provider']}/{model_config['model']}",
                    'processing_time': time.time() - start_time
                }
            )
            
            # 记录处理信息
            self.log_processing_info(
                'image', 
                file_path, 
                time.time() - start_time,
                model_used=f"{model_config['provider']}/{model_config['model']}",
                description_length=len(image_description)
            )
            
            return [document]
            
        except Exception as e:
            logger.error(f"Error processing image {file_path}: {str(e)}")
            # 发生错误时回退到文本提取器
            return self._fallback_to_text_extractor(file_path)
    
    def _get_image_data(self, file_path: str, file_url: Optional[str] = None) -> Optional[str]:
        """
        获取图片数据
        
        Args:
            file_path: 图片文件路径
            file_url: 图片URL
            
        Returns:
            图片数据（base64或URL）
        """
        if file_url:
            # 如果有URL，直接使用URL
            return file_url
        
        # 读取本地文件并转换为base64
        try:
            with open(file_path, 'rb') as f:
                image_bytes = f.read()
                image_base64 = base64.b64encode(image_bytes).decode('utf-8')
                # 获取MIME类型
                mime_type = self._get_mime_type(file_path)
                return f"data:{mime_type};base64,{image_base64}"
        except Exception as e:
            logger.error(f"Error reading image file {file_path}: {str(e)}")
            return None
    
    def _get_mime_type(self, file_path: str) -> str:
        """
        获取文件的MIME类型
        
        Args:
            file_path: 文件路径
            
        Returns:
            MIME类型
        """
        extension = Path(file_path).suffix.lower()
        mime_map = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.bmp': 'image/bmp',
            '.webp': 'image/webp',
            '.svg': 'image/svg+xml'
        }
        return mime_map.get(extension, 'image/jpeg')
    
    def _get_file_size(self, file_path: str) -> str:
        """
        获取文件大小
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件大小字符串
        """
        try:
            size_bytes = os.path.getsize(file_path)
            if size_bytes < 1024:
                return f"{size_bytes} B"
            elif size_bytes < 1024 * 1024:
                return f"{size_bytes / 1024:.1f} KB"
            else:
                return f"{size_bytes / (1024 * 1024):.1f} MB"
        except Exception:
            return "Unknown"
    
    def _get_model_config(self) -> Optional[Dict[str, str]]:
        """
        获取模型配置
        
        Returns:
            模型配置字典
        """
        # 这里可以从数据库或配置文件中获取模型配置
        # 暂时使用默认配置
        try:
            # 尝试获取通义千问配置
            return {
                'provider': 'tongyi',
                'model': 'qwen-vl-plus'
            }
        except Exception:
            try:
                # 尝试获取OpenAI配置
                return {
                    'provider': 'openai',
                    'model': 'gpt-4-vision-preview'
                }
            except Exception:
                logger.warning("No multimodal model available")
                return None
    
    def _recognize_image_content(self, image_data: str, model_config: Dict[str, str]) -> str:
        """
        使用多模态模型识别图片内容
        
        Args:
            image_data: 图片数据
            model_config: 模型配置
            
        Returns:
            图片描述文本
        """
        try:
            # 获取模型实例
            model_instance = self.get_llm_model_instance(
                model_config['provider'], 
                model_config['model']
            )
            
            # 格式化提示信息
            prompt_messages = self.format_image_prompt(
                image_data, 
                "请详细描述这张图片的内容，包括图片中的文字、物体、场景、颜色、布局等信息。"
            )
            
            # 调用模型
            result = model_instance.invoke(
                model=model_config['model'],
                credentials={},  # 凭据应该从配置中获取
                prompt_messages=prompt_messages,
                model_parameters={
                    'temperature': 0.3,
                    'max_tokens': 1000
                },
                stream=False
            )
            
            if isinstance(result, LLMResult):
                return result.message.content
            else:
                # 处理流式结果
                content = ""
                for chunk in result:
                    if hasattr(chunk, 'delta') and hasattr(chunk.delta, 'message'):
                        if hasattr(chunk.delta.message, 'content'):
                            content += chunk.delta.message.content
                return content
                
        except Exception as e:
            logger.error(f"Error recognizing image content: {str(e)}")
            return "图片内容识别失败"
    
    def _fallback_to_text_extractor(self, file_path: str) -> List[Document]:
        """
        回退到文本提取器
        
        Args:
            file_path: 文件路径
            
        Returns:
            文档列表
        """
        try:
            from core.rag.extractor.text_extractor import TextExtractor
            extractor = TextExtractor(file_path, autodetect_encoding=True)
            return extractor.extract()
        except Exception as e:
            logger.error(f"Fallback text extraction failed: {str(e)}")
            # 创建默认文档
            document = Document(
                page_content=f"图片文件: {Path(file_path).name}",
                metadata={
                    'source': file_path,
                    'type': 'image',
                    'error': 'Processing failed'
                }
            )
            return [document]
