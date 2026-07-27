"""Synchronous client for the unofficial Perplexity web protocol."""

import mimetypes
import random
import re
from typing import Any, Dict, Iterable, Iterator, Optional

from curl_cffi import CurlMime, requests

from .config import (
    API_BASE_URL,
    API_VERSION,
    DEFAULT_HEADERS,
    ENDPOINT_AUTH_SESSION,
    ENDPOINT_AUTH_SIGNIN,
    ENDPOINT_SSE_ASK,
    ENDPOINT_UPLOAD_URL,
    REQUEST_TIMEOUT,
)
from .emailnator import Emailnator
from .protocol import build_search_payload, file_size, parse_sse_event, validate_search


class Client:
    """Interact with Perplexity through the user's own web session."""

    def __init__(self, cookies: Optional[dict] = None):
        cookies = dict(cookies or {})
        self.session = requests.Session(
            headers=DEFAULT_HEADERS.copy(),
            cookies=cookies,
            impersonate="chrome",
        )
        self.own = bool(cookies)
        self.copilot = float("inf") if cookies else 0
        self.file_upload = float("inf") if cookies else 0
        self.signin_regex = re.compile(
            r'"(https://www\.perplexity\.ai/api/auth/callback/email\?callbackUrl=.*?)"'
        )
        self.timestamp = format(random.getrandbits(32), "08x")
        self.session.get(ENDPOINT_AUTH_SESSION, timeout=REQUEST_TIMEOUT)

    def create_account(self, cookies):
        """Create an account with the existing Emailnator workflow."""

        while True:
            try:
                emailnator_cli = Emailnator(cookies)
                response = self.session.post(
                    ENDPOINT_AUTH_SIGNIN,
                    data={
                        "email": emailnator_cli.email,
                        "csrfToken": self.session.cookies.get_dict()[
                            "next-auth.csrf-token"
                        ].split("%")[0],
                        "callbackUrl": f"{API_BASE_URL}/",
                        "json": "true",
                    },
                    timeout=REQUEST_TIMEOUT,
                )
                if response.ok:
                    new_messages = emailnator_cli.reload(
                        wait_for=lambda message: message["subject"] == "Sign in to Perplexity",
                        timeout=20,
                    )
                    if new_messages:
                        break
                else:
                    print("Perplexity account creating error:", response)
            except Exception:
                pass

        message = emailnator_cli.get(
            func=lambda item: item["subject"] == "Sign in to Perplexity"
        )
        match = self.signin_regex.search(emailnator_cli.open(message["messageID"]))
        if not match:
            raise RuntimeError("Perplexity sign-in link was not found in the email")

        self.session.get(match.group(1), timeout=REQUEST_TIMEOUT)
        self.copilot = 5
        self.file_upload = 10
        return True

    def _upload_files(self, files: Dict[str, Any]) -> list[str]:
        uploaded_files = []
        for filename, data in files.items():
            content_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"
            upload_info_response = self.session.post(
                ENDPOINT_UPLOAD_URL,
                params={"version": API_VERSION, "source": "default"},
                json={
                    "content_type": content_type,
                    "file_size": file_size(data),
                    "filename": filename,
                    "force_image": False,
                    "source": "default",
                },
                timeout=REQUEST_TIMEOUT,
            )
            if not upload_info_response.ok:
                raise RuntimeError(
                    f"Upload URL request failed with status {upload_info_response.status_code}"
                )
            upload_info = upload_info_response.json()

            multipart = CurlMime()
            for key, value in upload_info["fields"].items():
                multipart.addpart(name=key, data=value)
            multipart.addpart(
                name="file",
                content_type=content_type,
                filename=filename,
                data=data,
            )

            upload_response = self.session.post(
                upload_info["s3_bucket_url"],
                multipart=multipart,
                timeout=REQUEST_TIMEOUT,
            )
            if not upload_response.ok:
                raise RuntimeError(
                    f"File upload failed with status {upload_response.status_code}"
                )

            object_url = upload_info["s3_object_url"]
            if "image/upload" in object_url:
                secure_url = upload_response.json()["secure_url"]
                object_url = re.sub(
                    r"/private/s--.*?--/v\d+/user_uploads/",
                    "/private/user_uploads/",
                    secure_url,
                )
            uploaded_files.append(object_url)

        return uploaded_files

    @staticmethod
    def _iter_messages(response) -> Iterator[dict]:
        for raw_event in response.iter_lines(delimiter=b"\r\n\r\n"):
            event_name, payload = parse_sse_event(raw_event)
            if event_name == "end_of_stream":
                break
            if payload is not None:
                yield payload

    def search(
        self,
        query: str,
        mode: str = "auto",
        model: Optional[str] = None,
        sources: Optional[Iterable[str]] = None,
        files: Optional[Dict[str, Any]] = None,
        stream: bool = False,
        language: str = "en-US",
        follow_up: Optional[dict] = None,
        incognito: bool = False,
    ):
        sources = list(sources or ["web"])
        files = dict(files or {})
        validate_search(mode, model, sources)

        if mode in ("pro", "reasoning", "deep research") and self.copilot <= 0:
            raise RuntimeError("No enhanced queries remain for this session")
        if files and self.file_upload - len(files) < 0:
            raise RuntimeError("File upload limit exceeded")

        uploaded_files = self._upload_files(files) if files else []
        payload = build_search_payload(
            query,
            mode=mode,
            model=model,
            sources=sources,
            uploaded_files=uploaded_files,
            follow_up=follow_up,
            language=language,
            incognito=incognito,
        )

        response = self.session.post(
            ENDPOINT_SSE_ASK,
            json=payload,
            stream=True,
            timeout=REQUEST_TIMEOUT,
        )
        if not response.ok:
            raise RuntimeError(
                f"Perplexity request failed with status {response.status_code}"
            )

        if mode in ("pro", "reasoning", "deep research"):
            self.copilot -= 1
        if files:
            self.file_upload -= len(files)

        messages = self._iter_messages(response)
        if stream:
            return messages

        last_message = {}
        for last_message in messages:
            pass
        return last_message
