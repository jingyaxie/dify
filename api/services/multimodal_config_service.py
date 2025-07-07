from typing import Optional
from models.dataset import MultimodalConfig, db
from sqlalchemy.exc import SQLAlchemyError

class MultimodalConfigService:
    @staticmethod
    def get_config(tenant_id: str, dataset_id: str) -> Optional[MultimodalConfig]:
        try:
            return MultimodalConfig.query.filter_by(tenant_id=tenant_id, dataset_id=dataset_id).first()
        except SQLAlchemyError:
            db.session.rollback()
            return None

    @staticmethod
    def update_config(tenant_id: str, dataset_id: str, data: dict) -> Optional[MultimodalConfig]:
        try:
            config = MultimodalConfigService.get_config(tenant_id, dataset_id)
            if not config:
                config = MultimodalConfig(
                    tenant_id=tenant_id,
                    dataset_id=dataset_id
                )
                db.session.add(config)
            for key in ['image_model_provider', 'image_model_name', 'video_model_provider', 'video_model_name', 'enabled']:
                if key in data:
                    setattr(config, key, data[key])
            db.session.commit()
            return config
        except SQLAlchemyError:
            db.session.rollback()
            return None

    @staticmethod
    def create_config(tenant_id: str, dataset_id: str, data: dict) -> Optional[MultimodalConfig]:
        try:
            config = MultimodalConfig(
                tenant_id=tenant_id,
                dataset_id=dataset_id,
                image_model_provider=data.get('image_model_provider', 'openai'),
                image_model_name=data.get('image_model_name', 'gpt-4-vision-preview'),
                video_model_provider=data.get('video_model_provider', 'openai'),
                video_model_name=data.get('video_model_name', 'whisper-1'),
                enabled=data.get('enabled', True)
            )
            db.session.add(config)
            db.session.commit()
            return config
        except SQLAlchemyError:
            db.session.rollback()
            return None 