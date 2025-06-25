import os
import sys
from types import SimpleNamespace

import pytest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from perplexity.client import Client

class DummyEmailnator:
    def __init__(self, cookies):
        self.email = "dummy@example.com"
    async def reload(self, *args, **kwargs):
        return [{"messageID": "1", "subject": "Sign in to Perplexity"}]
    def reload(self, *args, **kwargs):
        return [{"messageID": "1", "subject": "Sign in to Perplexity"}]
    def get(self, func):
        return {"messageID": "1", "subject": "Sign in to Perplexity"}
    async def open(self, msg_id):
        return '"https://www.perplexity.ai/api/auth/callback/email?callbackUrl=https://www.perplexity.ai/"'
    def open(self, msg_id):
        return '"https://www.perplexity.ai/api/auth/callback/email?callbackUrl=https://www.perplexity.ai/"'

class DummySession:
    class DummyCookies:
        def __init__(self):
            self.data = {"next-auth.csrf-token": "token%123"}
        def get_dict(self):
            return self.data

    def __init__(self):
        self.cookies = self.DummyCookies()
    def post(self, url, data=None, **kwargs):
        return SimpleNamespace(ok=True)
    def get(self, url, **kwargs):
        return SimpleNamespace(ok=True)

@pytest.fixture
def patched(monkeypatch):
    monkeypatch.setattr("perplexity.client.Emailnator", DummyEmailnator)
    monkeypatch.setattr("perplexity.client.requests.Session", lambda **kw: DummySession())
    return monkeypatch

def test_create_account_validation():
    c = Client()
    with pytest.raises(ValueError):
        c.create_account({"name": "foo"})

def test_create_account_success(patched):
    c = Client()
    import re
    c.signin_regex = re.compile(r'(https://.*)')
    cookies = {"domain": "example.com", "name": "foo", "value": "bar", "path": "/", "expires": 0}
    assert c.create_account(cookies)
