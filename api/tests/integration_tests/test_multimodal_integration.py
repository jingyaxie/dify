import pytest
from unittest.mock import Mock, patch, MagicMock
from core.rag.extractor.extract_processor import ExtractProcessor
from core.rag.extractor.entity.extract_setting import ExtractSetting
from models.model import UploadFile

class TestMultimodalIntegration:
    
    def test_image_processing_with_multimodal_enabled(self):
        """测试启用多模态时的图片处理"""
        with patch('core.rag.extractor.extract_processor.MultimodalConfigService') as mock_service:
            # Mock配置服务返回启用状态
            mock_config = Mock()
            mock_config.enabled = True
            mock_service.get_config.return_value = mock_config
            
            # Mock图片提取器
            with patch('core.rag.extractor.extract_processor.MultimodalImageExtractor') as mock_extractor:
                mock_documents = [Mock()]
                mock_extractor.return_value.extract.return_value = mock_documents
                
                # 创建测试数据
                upload_file = Mock()
                upload_file.tenant_id = 'test-tenant'
                upload_file.dataset_id = 'test-dataset'
                upload_file.key = 'test.jpg'
                
                extract_setting = ExtractSetting(
                    datasource_type="upload_file",
                    upload_file=upload_file,
                    document_model="text_model"
                )
                
                # 执行提取
                result = ExtractProcessor.extract(extract_setting)
                
                # 验证调用了多模态提取器
                mock_extractor.assert_called_once_with('test-tenant')
                assert result == mock_documents
    
    def test_image_processing_with_multimodal_disabled(self):
        """测试禁用多模态时的图片处理"""
        with patch('core.rag.extractor.extract_processor.MultimodalConfigService') as mock_service:
            # Mock配置服务返回禁用状态
            mock_config = Mock()
            mock_config.enabled = False
            mock_service.get_config.return_value = mock_config
            
            # Mock文本提取器
            with patch('core.rag.extractor.extract_processor.TextExtractor') as mock_extractor:
                mock_documents = [Mock()]
                mock_extractor.return_value.extract.return_value = mock_documents
                
                # 创建测试数据
                upload_file = Mock()
                upload_file.tenant_id = 'test-tenant'
                upload_file.dataset_id = 'test-dataset'
                upload_file.key = 'test.jpg'
                
                extract_setting = ExtractSetting(
                    datasource_type="upload_file",
                    upload_file=upload_file,
                    document_model="text_model"
                )
                
                # 执行提取
                result = ExtractProcessor.extract(extract_setting)
                
                # 验证调用了文本提取器而不是多模态提取器
                mock_extractor.assert_called_once()
                assert result == mock_documents
    
    def test_video_processing_with_multimodal_enabled(self):
        """测试启用多模态时的视频处理"""
        with patch('core.rag.extractor.extract_processor.MultimodalConfigService') as mock_service:
            # Mock配置服务返回启用状态
            mock_config = Mock()
            mock_config.enabled = True
            mock_service.get_config.return_value = mock_config
            
            # Mock视频提取器
            with patch('core.rag.extractor.extract_processor.MultimodalVideoExtractor') as mock_extractor:
                mock_documents = [Mock()]
                mock_extractor.return_value.extract.return_value = mock_documents
                
                # 创建测试数据
                upload_file = Mock()
                upload_file.tenant_id = 'test-tenant'
                upload_file.dataset_id = 'test-dataset'
                upload_file.key = 'test.mp4'
                
                extract_setting = ExtractSetting(
                    datasource_type="upload_file",
                    upload_file=upload_file,
                    document_model="text_model"
                )
                
                # 执行提取
                result = ExtractProcessor.extract(extract_setting)
                
                # 验证调用了多模态提取器
                mock_extractor.assert_called_once_with('test-tenant')
                assert result == mock_documents
    
    def test_non_multimodal_file_processing(self):
        """测试非多模态文件处理（PDF等）"""
        with patch('core.rag.extractor.extract_processor.MultimodalConfigService') as mock_service:
            # Mock配置服务返回启用状态
            mock_config = Mock()
            mock_config.enabled = True
            mock_service.get_config.return_value = mock_config
            
            # Mock PDF提取器
            with patch('core.rag.extractor.extract_processor.PdfExtractor') as mock_extractor:
                mock_documents = [Mock()]
                mock_extractor.return_value.extract.return_value = mock_documents
                
                # 创建测试数据
                upload_file = Mock()
                upload_file.tenant_id = 'test-tenant'
                upload_file.dataset_id = 'test-dataset'
                upload_file.key = 'test.pdf'
                
                extract_setting = ExtractSetting(
                    datasource_type="upload_file",
                    upload_file=upload_file,
                    document_model="text_model"
                )
                
                # 执行提取
                result = ExtractProcessor.extract(extract_setting)
                
                # 验证调用了PDF提取器而不是多模态提取器
                mock_extractor.assert_called_once()
                assert result == mock_documents
    
    def test_error_handling(self):
        """测试异常处理"""
        with patch('core.rag.extractor.extract_processor.MultimodalConfigService') as mock_service:
            # Mock配置服务抛出异常
            mock_service.get_config.side_effect = Exception("Database error")
            
            # 创建测试数据
            upload_file = Mock()
            upload_file.tenant_id = 'test-tenant'
            upload_file.dataset_id = 'test-dataset'
            upload_file.key = 'test.jpg'
            
            extract_setting = ExtractSetting(
                datasource_type="upload_file",
                upload_file=upload_file,
                document_model="text_model"
            )
            
            # 执行提取，应该回退到原有逻辑
            with patch('core.rag.extractor.extract_processor.TextExtractor') as mock_extractor:
                mock_documents = [Mock()]
                mock_extractor.return_value.extract.return_value = mock_documents
                
                result = ExtractProcessor.extract(extract_setting)
                
                # 验证调用了文本提取器
                mock_extractor.assert_called_once()
                assert result == mock_documents
