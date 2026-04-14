import cloudinary
import cloudinary.uploader
from werkzeug.exceptions import UnsupportedMediaType

ALLOWED_MIMES = {'image/jpeg', 'image/png', 'image/webp'}

MAGIC_BYTES = {
    'image/jpeg': [b'\xff\xd8\xff'],
    'image/png': [b'\x89PNG\r\n\x1a\n'],
    'image/webp': [b'RIFF'],  # followed by 4 bytes size, then 'WEBP'
}


def _validate_image_bytes(file_storage) -> None:
    mimetype = file_storage.mimetype
    if mimetype not in ALLOWED_MIMES:
        raise UnsupportedMediaType(f'Unsupported mime type: {mimetype}')

    file_storage.seek(0)
    head = file_storage.read(12)
    file_storage.seek(0)

    if mimetype == 'image/webp':
        ok = head.startswith(b'RIFF') and head[8:12] == b'WEBP'
    else:
        ok = any(head.startswith(sig) for sig in MAGIC_BYTES[mimetype])

    if not ok:
        raise UnsupportedMediaType('File bytes do not match declared mime type')


def upload_image(file_storage) -> dict:
    _validate_image_bytes(file_storage)
    result = cloudinary.uploader.upload(
        file_storage,
        folder='ascaso-gallery',
        resource_type='image',
    )
    return {
        'url': result['secure_url'],
        'public_id': result['public_id'],
        'width': result.get('width'),
        'height': result.get('height'),
        'format': result.get('format'),
        'bytes': result.get('bytes'),
    }
