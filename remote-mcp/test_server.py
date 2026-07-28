import importlib.util
from pathlib import Path


MODULE = Path(__file__).with_name("server.py")
spec = importlib.util.spec_from_file_location("remote_server", MODULE)
remote_server = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(remote_server)


def test_rejects_non_http_urls():
    for value in ("file:///etc/passwd", "javascript:alert(1)", "not-a-url"):
        try:
            remote_server._validate_url(value)
        except ValueError:
            pass
        else:
            raise AssertionError(value)


def test_rejects_private_ip_urls():
    for value in ("http://127.0.0.1/video", "http://10.0.0.2/video", "http://169.254.1.1/video"):
        try:
            remote_server._validate_url(value)
        except ValueError:
            pass
        else:
            raise AssertionError(value)

