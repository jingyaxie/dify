"""add multimodal fields

Revision ID: multimodal_fields_001
Revises: fecff1c3da27
Create Date: 2024-12-19 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'multimodal_fields_001'
down_revision = 'fecff1c3da27'
branch_labels = None
depends_on = None


def upgrade():
    # 添加多模态字段到documents表
    op.add_column('documents', sa.Column('multimodal_type', sa.String(20), nullable=True))
    op.add_column('documents', sa.Column('original_url', sa.Text(), nullable=True))
    op.add_column('documents', sa.Column('processed_content', sa.Text(), nullable=True))
    op.add_column('documents', sa.Column('model_used', sa.String(100), nullable=True))
    op.add_column('documents', sa.Column('processing_time', sa.Float(), nullable=True))
    
    # 创建multimodal_configs表
    op.create_table('multimodal_configs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('dataset_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('image_model_provider', sa.String(50), nullable=True),
        sa.Column('image_model_name', sa.String(100), nullable=True),
        sa.Column('video_model_provider', sa.String(50), nullable=True),
        sa.Column('video_model_name', sa.String(100), nullable=True),
        sa.Column('enabled', sa.Boolean(), default=True, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP(0)'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP(0)'), nullable=True),
        sa.PrimaryKeyConstraint('id', name='multimodal_config_pkey'),
        sa.Index('multimodal_config_tenant_idx', 'tenant_id'),
        sa.Index('multimodal_config_dataset_idx', 'dataset_id')
    )


def downgrade():
    # 删除multimodal_configs表
    op.drop_table('multimodal_configs')
    
    # 删除documents表中的多模态字段
    op.drop_column('documents', 'processing_time')
    op.drop_column('documents', 'model_used')
    op.drop_column('documents', 'processed_content')
    op.drop_column('documents', 'original_url')
    op.drop_column('documents', 'multimodal_type')
