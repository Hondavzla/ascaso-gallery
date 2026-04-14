import io
import pytest

# Sample magic-byte prefixes
JPEG = b'\xff\xd8\xff\xe0' + b'\x00' * 20
PNG = b'\x89PNG\r\n\x1a\n' + b'\x00' * 20
WEBP_RIFF = b'RIFF\x00\x00\x00\x00WEBP' + b'\x00' * 10
GIF = b'GIF89a' + b'\x00' * 20


class FakeFile:
    def __init__(self, data: bytes, mimetype: str, filename: str = 'f.jpg'):
        self.stream = io.BytesIO(data)
        self.mimetype = mimetype
        self.filename = filename

    def read(self, n=-1):
        return self.stream.read(n)

    def seek(self, pos, whence=0):
        return self.stream.seek(pos, whence)


def test_validates_jpeg():
    from app.services.cloudinary import _validate_image_bytes
    _validate_image_bytes(FakeFile(JPEG, 'image/jpeg'))  # no raise


def test_validates_png():
    from app.services.cloudinary import _validate_image_bytes
    _validate_image_bytes(FakeFile(PNG, 'image/png'))


def test_validates_webp():
    from app.services.cloudinary import _validate_image_bytes
    _validate_image_bytes(FakeFile(WEBP_RIFF, 'image/webp'))


def test_rejects_bad_mime():
    from app.services.cloudinary import _validate_image_bytes
    from werkzeug.exceptions import UnsupportedMediaType
    with pytest.raises(UnsupportedMediaType):
        _validate_image_bytes(FakeFile(JPEG, 'image/gif'))


def test_rejects_mime_magic_mismatch():
    from app.services.cloudinary import _validate_image_bytes
    from werkzeug.exceptions import UnsupportedMediaType
    with pytest.raises(UnsupportedMediaType):
        _validate_image_bytes(FakeFile(GIF, 'image/jpeg'))


def test_upload_image_calls_cloudinary(monkeypatch):
    from app.services import cloudinary as svc
    captured = {}

    def fake_upload(file, **kwargs):
        captured['called'] = True
        captured['kwargs'] = kwargs
        return {
            'secure_url': 'https://res.cloudinary.com/x/image.jpg',
            'public_id': 'ascaso-gallery/abc',
            'width': 800,
            'height': 600,
            'format': 'jpg',
            'bytes': 12345,
        }

    monkeypatch.setattr(svc.cloudinary.uploader, 'upload', fake_upload)
    result = svc.upload_image(FakeFile(JPEG, 'image/jpeg'))
    assert captured['called']
    assert captured['kwargs']['folder'] == 'ascaso-gallery'
    assert result['url'] == 'https://res.cloudinary.com/x/image.jpg'
    assert result['public_id'] == 'ascaso-gallery/abc'
    assert result['width'] == 800
