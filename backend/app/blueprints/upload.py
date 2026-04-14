from flask import Blueprint, jsonify, request
from marshmallow import ValidationError

from app.services.auth import admin_required
from app.services.cloudinary import upload_image

bp = Blueprint('upload', __name__, url_prefix='/api/upload')


@bp.post('')
@admin_required
def upload():
    file_storage = request.files.get('file')
    if file_storage is None:
        raise ValidationError({'file': ['Missing file in multipart/form-data']})
    result = upload_image(file_storage)
    return jsonify(result), 201
