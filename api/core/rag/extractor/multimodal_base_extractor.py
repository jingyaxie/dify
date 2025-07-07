"""
多模态提取器基类
支持图片和视频内容的提取和处理
"""

import logging
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from datetime import datetime

from core.model_runtime.entities.model_entities import ModelType
from core.model_runtime.model_providers.model_provider_factory import ModelProviderFactory
from core.model_runtime.model_providers.__base.large_language_model import LargeLanguageModel
from core.model_runtime.model_providers.__base.speech2text_model import Speech2TextModel
from core.model_runtime.entities.message_entities import (
    PromptMessage,
    TextPromptMessageContent,
    ImagePromptMessageContent,
    PromptMessageContentUnionTypes,
    AssistantPromptMessage,
)
from core.model_runtime.entities.llm_entities import LLMResult

logger = logging.getLogger(__name__)


class MultimodalBaseExtractor(ABC):
    """
    多模态提取器基类
    """
    
    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.model_provider_factory = ModelProviderFactory(tenant_id)
        
    @abstractmethod
    def extract(self, file_path: str, file_url: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        提取文件内容
        
        Args:
            file_path: 文件路径
            file_url: 文件URL（可选）
            **kwargs: 其他参数
            
        Returns:
            提取结果字典
        """
        pass
    
    @abstractmethod
    def get_supported_extensions(self) -> List[str]:
        """
        获取支持的文件扩展名
        
        Returns:
            支持的文件扩展名列表
        """
        pass
    
    def get_llm_model_instance(self, provider: str, model: str) -> LargeLanguageModel:
        """
        获取LLM模型实例
        
        Args:
            provider: 模型供应商
            model: 模型名称
            
        Returns:
            LLM模型实例
        """
        return self.model_provider_factory.get_model_type_instance(provider, ModelType.LLM)
    
    def get_speech2text_model_instance(self, provider: str, model: str) -> Speech2TextModel:
        """
        获取语音转文本模型实例
        
        Args:
            provider: 模型供应商
            model: 模型名称
            
        Returns:
            语音转文本模型实例
        """
        return self.model_provider_factory.get_model_type_instance(provider, ModelType.SPEECH2TEXT)
    
    def format_image_prompt(self, image_data: str, prompt: str = None) -> List[PromptMessage]:
        """
        格式化图片提示信息
        
        Args:
            image_data: 图片数据（base64或URL）
            prompt: 提示文本
            
        Returns:
            提示消息列表
        """
        messages = []
        
        # 添加图片内容
        image_content = ImagePromptMessageContent(data=image_data)
        messages.append(PromptMessage(content=[image_content]))
        
        # 添加文本提示
        if prompt:
            text_content = TextPromptMessageContent(data=prompt)
            messages.append(PromptMessage(content=[text_content]))
        else:
            # 默认提示
            default_prompt = "请详细描述这张图片的内容，包括图片中的文字、物体、场景等信息。"
            text_content = TextPromptMessageContent(data=default_prompt)
            messages.append(PromptMessage(content=[text_content]))
            
        return messages
    
    def format_video_prompt(self, audio_transcription: str, prompt: str = None) -> List[PromptMessage]:
        """
        格式化视频提示信息
        
        Args:
            audio_transcription: 音频转文本结果
            prompt: 提示文本
            
        Returns:
            提示消息列表
        """
        messages = []
        
        # 添加音频转文本内容
        if audio_transcription:
            text_content = TextPromptMessageContent(data=f"视频音频转文本内容：{audio_transcription}")
            messages.append(PromptMessage(content=[text_content]))
        
        # 添加文本提示
        if prompt:
            text_content = TextPromptMessageContent(data=prompt)
            messages.append(PromptMessage(content=[text_content]))
        else:
            # 默认提示
            default_prompt = "请根据音频转文本内容，生成详细的视频描述，包括视频的主题、内容要点等。"
            text_content = TextPromptMessageContent(data=default_prompt)
            messages.append(PromptMessage(content=[text_content]))
            
        return messages
    
    def generate_structured_text(self, content_type: str, **kwargs) -> str:
        """
        生成结构化文本
        
        Args:
            content_type: 内容类型（'image' 或 'video'）
            **kwargs: 内容参数
            
        Returns:
            结构化文本
        """
        if content_type == 'image':
            return self._generate_image_text(**kwargs)
        elif content_type == 'video':
            return self._generate_video_text(**kwargs)
        else:
            raise ValueError(f"Unsupported content type: {content_type}")
    
    def _generate_image_text(self, **kwargs) -> str:
        """
        生成图片结构化文本
        """
        image_url = kwargs.get('image_url', '')
        image_description = kwargs.get('image_description', '')
        image_type = kwargs.get('image_type', '')
        file_size = kwargs.get('file_size', '')
        upload_time = kwargs.get('upload_time', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        text = f"""[图片描述]
图片URL: {image_url}
图片内容: {image_description}
图片类型: {image_type}
文件大小: {file_size}
上传时间: {upload_time}"""
        
        return text
    
    def _generate_video_text(self, **kwargs) -> str:
        """
        生成视频结构化文本
        """
        video_url = kwargs.get('video_url', '')
        video_title = kwargs.get('video_title', '')
        duration = kwargs.get('duration', '')
        audio_transcription = kwargs.get('audio_transcription', '')
        video_description = kwargs.get('video_description', '')
        file_size = kwargs.get('file_size', '')
        upload_time = kwargs.get('upload_time', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        text = f"""[视频描述]
视频URL: {video_url}
视频标题: {video_title}
视频时长: {duration}
音频转文本: {audio_transcription}
视频描述: {video_description}
文件大小: {file_size}
上传时间: {upload_time}"""
        
        return text
    
    def log_processing_info(self, content_type: str, file_path: str, processing_time: float, **kwargs):
        """
        记录处理信息
        
        Args:
            content_type: 内容类型
            file_path: 文件路径
            processing_time: 处理时间
            **kwargs: 其他信息
        """
        logger.info(
            f"Multimodal processing completed - Type: {content_type}, "
            f"File: {file_path}, Time: {processing_time:.2f}s, "
            f"Additional info: {kwargs}"
        ) 