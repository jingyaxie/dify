import pytest
from unittest.mock import Mock, patch
from services.multimodal_config_service import MultimodalConfigService
from models.dataset import MultimodalConfig

class TestMultimodalConfigService:
    
    def test_get_config_success(self):
        """测试成功获取配置"""
        with patch('services.multimodal_config_service.MultimodalConfig') as mock_model:
            mock_config = Mock()
            mock_config.to_dict.return_value = {
                'id': 'test-id',
                'tenant_id': 'test-tenant',
                'dataset_id': 'test-dataset',
                'enabled': True
            }
            mock_model.query.filter_by.return_value.first.return_value = mock_config
            
            result = MultimodalConfigService.get_config('test-tenant', 'test-dataset')
            
            assert result is not None
            assert result.to_dict()['enabled'] is True
    
    def test_get_config_not_found(self):
        """测试配置不存在"""
        with patch('services.multimodal_config_service.MultimodalConfig') as mock_model:
            mock_model.query.filter_by.return_value.first.return_value = None
            
            result = MultimodalConfigService.get_config('test-tenant', 'test-dataset')
            
            assert result is None
    
    def test_update_config_create_new(self):
        """测试更新配置时创建新配置"""
        with patch('services.multimodal_config_service.MultimodalConfig') as mock_model:
            mock_model.query.filter_by.return_value.first.return_value = None
            
            with patch('services.multimodal_config_service.db') as mock_db:
                mock_config = Mock()
                mock_model.return_value = mock_config
                
                result = MultimodalConfigService.update_config(
                    'test-tenant', 'test-dataset', 
                    {'enabled': True, 'image_model_provider': 'openai'}
                )
                
                assert result is not None
                mock_db.session.add.assert_called_once()
                mock_db.session.commit.assert_called_once()
    
    def test_update_config_existing(self):
        """测试更新现有配置"""
        with patch('services.multimodal_config_service.MultimodalConfig') as mock_model:
            mock_config = Mock()
            mock_model.query.filter_by.return_value.first.return_value = mock_config
            
            with patch('services.multimodal_config_service.db') as mock_db:
                result = MultimodalConfigService.update_config(
                    'test-tenant', 'test-dataset', 
                    {'enabled': False}
                )
                
                assert result is not None
                mock_db.session.commit.assert_called_once()
    
    def test_create_config_success(self):
        """测试成功创建配置"""
        with patch('services.multimodal_config_service.MultimodalConfig') as mock_model:
            mock_config = Mock()
            mock_model.return_value = mock_config
            
            with patch('services.multimodal_config_service.db') as mock_db:
                result = MultimodalConfigService.create_config(
                    'test-tenant', 'test-dataset',
                    {'enabled': True, 'image_model_provider': 'openai'}
                )
                
                assert result is not None
                mock_db.session.add.assert_called_once()
                mock_db.session.commit.assert_called_once()
