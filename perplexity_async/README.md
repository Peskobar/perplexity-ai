# perplexity_async

Asynchronous client for Perplexity AI with disposable email support. It mirrors the synchronous `perplexity` package but uses `curl_cffi` in async mode.

```
from perplexity_async import Client

async def main():
    cli = await Client()
    await cli.create_account([...])
```

