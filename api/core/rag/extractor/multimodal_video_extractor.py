"""
视频多模态提取器
支持视频音频提取和文本生成
"""

import logging
import os
import time
from pathlib import Path
from typing import Optional, Dict, Any, List
import subprocess
import tempfile

from core.rag.extractor.multimodal_base_extractor import MultimodalBaseExtractor
from core.rag.models.document import Document
from core.model_runtime.entities.message_entities import PromptMessage
from core.model_runtime.entities.llm_entities import LLMResult

logger = logging.getLogger(__name__)


class MultimodalVideoExtractor(MultimodalBaseExtractor):
    """
    视频多模态提取器
    """
    
    def __init__(self, tenant_id: str):
        super().__init__(tenant_id)
        
    def get_supported_extensions(self) -> List[str]:
        """
        获取支持的视频文件扩展名
        
        Returns:
            支持的视频文件扩展名列表
        """
        return [".mp4", ".avi", ".mov", ".wmv", ".flv", ".webm", ".mkv"]
    
    def extract(self, file_path: str, file_url: Optional[str] = None, **kwargs) -> List[Document]:
        """
        提取视频内容
        
        Args:
            file_path: 视频文件路径
            file_url: 视频URL（可选）
            **kwargs: 其他参数
            
        Returns:
            文档列表
        """
        start_time = time.time()
        
        try:
            # 获取模型配置
            model_config = self._get_model_config()
            if not model_config:
                logger.warning("No speech-to-text model configured, using default text extractor")
                return self._fallback_to_text_extractor(file_path)
            
            # 提取视频音频
            audio_file = self._extract_audio_from_video(file_path)
            if not audio_file:
                logger.error(f"Failed to extract audio from video {file_path}")
                return self._fallback_to_text_extractor(file_path)
            
            # 音频转文本
            audio_transcription = self._transcribe_audio(audio_file, model_config)
            
            # 生成视频描述
            video_description = self._generate_video_description(audio_transcription, model_config)
            
            # 获取视频信息
            video_info = self._get_video_info(file_path)
            
            # 生成结构化文本
            structured_text = self.generate_structured_text('video', **{
                'video_url': file_url or file_path,
                'video_title': Path(file_path).stem,
                'duration': video_info.get('duration', 'Unknown'),
                'audio_transcription': audio_transcription,
                'video_description': video_description,
                'file_size': self._get_file_size(file_path),
                'upload_time': time.strftime('%Y-%m-%d %H:%M:%S')
            })
            
            # 创建文档
            document = Document(
                page_content=structured_text,
                metadata={
                    'source': file_path,
                    'type': 'video',
                    'multimodal_type': 'video',
                    'original_url': file_url,
                    'processed_content': audio_transcription,
                    'model_used': f"{model_config['provider']}/{model_config['model']}",
                    'processing_time': time.time() - start_time,
                    'video_duration': video_info.get('duration'),
                    'video_resolution': video_info.get('resolution')
                }
            )
            
            # 清理临时文件
            if audio_file and os.path.exists(audio_file):
                os.remove(audio_file)
            
            # 记录处理信息
            self.log_processing_info(
                'video', 
                file_path, 
                time.time() - start_time,
                model_used=f"{model_config['provider']}/{model_config['model']}",
                transcription_length=len(audio_transcription),
                duration=video_info.get('duration')
            )
            
            return [document]
            
        except Exception as e:
            logger.error(f"Error processing video {file_path}: {str(e)}")
            # 发生错误时回退到文本提取器
            return self._fallback_to_text_extractor(file_path)
    
    def _extract_audio_from_video(self, video_path: str) -> Optional[str]:
        """
        从视频中提取音频
        
        Args:
            video_path: 视频文件路径
            
        Returns:
            音频文件路径
        """
        try:
            # 创建临时音频文件
            audio_file = tempfile.mktemp(suffix='.wav')
            
            # 使用ffmpeg提取音频
            cmd = [
                'ffmpeg', '-i', video_path, 
                '-vn',  # 不包含视频
                '-acodec', 'pcm_s16le',  # 音频编码
                '-ar', '16000',  # 采样率
                '-ac', '1',  # 单声道
                '-y',  # 覆盖输出文件
                audio_file
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0 and os.path.exists(audio_file):
                return audio_file
            else:
                logger.error(f"FFmpeg error: {result.stderr}")
                return None
                
        except Exception as e:
            logger.error(f"Error extracting audio from video: {str(e)}")
            return None
    
    def _transcribe_audio(self, audio_file: str, model_config: Dict[str, str]) -> str:
        """
        音频转文本
        
        Args:
            audio_file: 音频文件路径
            model_config: 模型配置
            
        Returns:
            转文本结果
        """
        try:
            # 获取语音转文本模型实例
            model_instance = self.get_speech2text_model_instance(
                model_config['provider'], 
                model_config['model']
            )
            
            # 读取音频文件
            with open(audio_file, 'rb') as f:
                # 调用模型进行转文本
                result = model_instance.invoke(
                    model=model_config['model'],
                    credentials={},  # 凭据应该从配置中获取
                    file=f
                )
                
                return result
                
        except Exception as e:
            logger.error(f"Error transcribing audio: {str(e)}")
            return "音频转文本失败"
    
    def _generate_video_description(self, audio_transcription: str, model_config: Dict[str, str]) -> str:
        """
        生成视频描述
        
        Args:
            audio_transcription: 音频转文本结果
            model_config: 模型配置
            
        Returns:
            视频描述
        """
        try:
            # 获取LLM模型实例
            model_instance = self.get_llm_model_instance(
                model_config['provider'], 
                model_config['model']
            )
            
            # 格式化提示信息
            prompt_messages = self.format_video_prompt(
                audio_transcription,
                "请根据音频转文本内容，生成详细的视频描述，包括视频的主题、内容要点、说话者信息等。"
            )
            
            # 调用模型
            result = model_instance.invoke(
                model=model_config['model'],
                credentials={},  # 凭据应该从配置中获取
                prompt_messages=prompt_messages,
                model_parameters={
                    'temperature': 0.3,
                    'max_tokens': 500
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
            logger.error(f"Error generating video description: {str(e)}")
            return "视频描述生成失败"
    
    def _get_video_info(self, video_path: str) -> Dict[str, str]:
        """
        获取视频信息
        
        Args:
            video_path: 视频文件路径
            
        Returns:
            视频信息字典
        """
        try:
            # 使用ffprobe获取视频信息
            cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_format', '-show_streams', video_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                import json
                info = json.loads(result.stdout)
                
                # 提取时长
                duration = info.get('format', {}).get('duration', 'Unknown')
                if duration != 'Unknown':
                    duration = f"{float(duration):.1f}秒"
                
                # 提取分辨率
                video_stream = next((s for s in info.get('streams', []) if s.get('codec_type') == 'video'), None)
                resolution = 'Unknown'
                if video_stream:
                    width = video_stream.get('width', 'Unknown')
                    height = video_stream.get('height', 'Unknown')
                    if width != 'Unknown' and height != 'Unknown':
                        resolution = f"{width}x{height}"
                
                return {
                    'duration': duration,
                    'resolution': resolution
                }
            else:
                return {'duration': 'Unknown', 'resolution': 'Unknown'}
                
        except Exception as e:
            logger.error(f"Error getting video info: {str(e)}")
            return {'duration': 'Unknown', 'resolution': 'Unknown'}
    
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
                'model': 'qwen-audio'
            }
        except Exception:
            try:
                # 尝试获取OpenAI配置
                return {
                    'provider': 'openai',
                    'model': 'whisper-1'
                }
            except Exception:
                logger.warning("No speech-to-text model available")
                return None
    
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
                page_content=f"视频文件: {Path(file_path).name}",
                metadata={
                    'source': file_path,
                    'type': 'video',
                    'error': 'Processing failed'
                }
            )
            return [document]
