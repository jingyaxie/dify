from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.multimodal_config_service import MultimodalConfigService
from models.dataset import db

bp = Blueprint('multimodal_config', __name__, url_prefix='/console/api/workspaces/current/datasets')

@bp.route('/<dataset_id>/multimodal-config', methods=['GET'])
@jwt_required()
def get_multimodal_config(dataset_id):
    tenant_id = get_jwt_identity().get('tenant_id')
    config = MultimodalConfigService.get_config(tenant_id, dataset_id)
    if not config:
        return jsonify({'data': None, 'message': 'Not found', 'code': 0}), 200
    return jsonify({'data': config.to_dict(), 'code': 0})

@bp.route('/<dataset_id>/multimodal-config', methods=['PUT'])
@jwt_required()
def update_multimodal_config(dataset_id):
    tenant_id = get_jwt_identity().get('tenant_id')
    data = request.get_json() or {}
    config = MultimodalConfigService.update_config(tenant_id, dataset_id, data)
    if not config:
        return jsonify({'message': 'Update failed', 'code': 1}), 400
    return jsonify({'data': config.to_dict(), 'code': 0}) 