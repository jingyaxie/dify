"""enable multimodal by default

Revision ID: enable_multimodal_default_001
Revises: multimodal_fields_001
Create Date: 2024-12-19 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'enable_multimodal_default_001'
down_revision = 'multimodal_fields_001'
branch_labels = None
depends_on = None


def upgrade():
    # 更新现有配置，将enabled设为true
    op.execute("""
        UPDATE multimodal_configs 
        SET enabled = true 
        WHERE enabled IS NULL OR enabled = false
    """)
    
    # 为没有配置的数据集创建默认配置
    op.execute("""
        INSERT INTO multimodal_configs (tenant_id, dataset_id, enabled, image_model_provider, image_model_name, video_model_provider, video_model_name, created_at, updated_at)
        SELECT DISTINCT 
            d.tenant_id,
            d.id as dataset_id,
            true as enabled,
            'openai' as image_model_provider,
            'gpt-4-vision-preview' as image_model_name,
            'openai' as video_model_provider,
            'whisper-1' as video_model_name,
            CURRENT_TIMESTAMP as created_at,
            CURRENT_TIMESTAMP as updated_at
        FROM datasets d
        WHERE NOT EXISTS (
            SELECT 1 FROM multimodal_configs mc 
            WHERE mc.dataset_id = d.id
        )
    """)


def downgrade():
    # 将enabled设为false
    op.execute("""
        UPDATE multimodal_configs 
        SET enabled = false
    """) 