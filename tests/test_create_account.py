import os
import sys
import re
from unittest.mock import MagicMock, patch

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from perplexity.client import Client


def test_create_account_flow():
    cookies = [{"domain": "emailnator.com", "name": "XSRF-TOKEN", "value": "1", "path": "/", "expires": 1}]

    mock_session = MagicMock()
    mock_session.post.return_value.ok = True
    mock_session.get.return_value = None
    mock_session.cookies.get_dict.return_value = {"next-auth.csrf-token": "token%1"}

    mock_emailnator = MagicMock()
    mock_emailnator.email = "foo@example.com"
    mock_emailnator.reload.return_value = [{"subject": "Sign in to Perplexity"}]
    mock_emailnator.get.return_value = {"messageID": "42"}
    mock_emailnator.open.return_value = (
        '"https://www.perplexity.ai/api/auth/callback/email?callbackUrl=foo"'
    )

    import perplexity.client as client_mod
    with patch("perplexity.client.requests.Session", return_value=mock_session):
        with patch("perplexity.client.Emailnator", return_value=mock_emailnator):
            with patch.object(client_mod, "Logger", return_value=MagicMock(log=MagicMock()), create=True):
                client = Client()
                client.signin_regex = re.compile(r"(https://.*)")
                assert client.create_account(cookies) is True

