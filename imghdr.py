# imghdr.py - compatibility shim for Python 3.13+
# Minimal reimplementation for python-telegram-bot 13.x

def what(file, h=None):
    if h is None:
        with open(file, 'rb') as f:
            h = f.read(32)

    for test in tests:
        res = test(h, file)
        if res:
            return res
    return None

def test_jpeg(h, f):
    if h[6:10] in (b'JFIF', b'Exif'):
        return 'jpeg'

def test_png(h, f):
    if h.startswith(b'\211PNG\r\n\032\n'):
        return 'png'

def test_gif(h, f):
    if h[:6] in (b'GIF87a', b'GIF89a'):
        return 'gif'

def test_bmp(h, f):
    if h.startswith(b'BM'):
        return 'bmp'

def test_tiff(h, f):
    if h[:2] in (b'MM', b'II'):
        return 'tiff'

tests = [test_jpeg, test_png, test_gif, test_bmp, test_tiff]
