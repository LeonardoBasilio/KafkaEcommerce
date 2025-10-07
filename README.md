Este projeto é de estudos de Kafka e aplicações de microserviços, rodando com conceito de Docker.

## Melhoria sugerida para `GetResponseBody`

A função original podia ficar presa em um loop infinito quando a conexão falhava
indefinidamente e não distinguia o tratamento entre URLs e arquivos locais. O
exemplo abaixo ilustra uma versão mais robusta que adiciona limite de tentativas,
intervalo incremental entre as execuções e uso explícito de codificação ao
normalizar o HTML com o BeautifulSoup.

```python
import time
from pathlib import Path
import ssl
from urllib import error, request

from bs4 import BeautifulSoup


def get_response_body(
    dados: str,
    timeout: int = 30,
    max_retries: int = 3,
    cafile: str | None = None,
    allow_insecure_fallback: bool = False,
) -> str:
    path = Path(dados)
    if path.exists():
        return path.read_text(encoding="utf-8")

    last_error: Exception | None = None
    for attempt in range(1, max_retries + 1):
        try:
            if cafile:
                context = ssl.create_default_context(cafile=cafile)
            else:
                try:
                    import certifi
                except ModuleNotFoundError:
                    context = None
                else:
                    context = ssl.create_default_context(cafile=certifi.where())
            with request.urlopen(dados, timeout=timeout, context=context) as response:
                encoding = response.headers.get_content_charset() or "utf-8"
                html = response.read().decode(encoding, errors="replace")

            page_items = BeautifulSoup(html, "html.parser")
            return str(page_items)
        except (error.URLError, error.HTTPError, ValueError) as exc:
            last_error = exc
            if attempt < max_retries:
                time.sleep(attempt)
            reason = getattr(exc, "reason", None)
            reason_text = str(reason or exc)
            is_cert_failure = isinstance(reason, ssl.SSLCertVerificationError) or (
                isinstance(reason, ssl.SSLError)
                and "CERTIFICATE_VERIFY_FAILED" in reason_text.upper()
            )
            if allow_insecure_fallback and is_cert_failure:
                context = ssl._create_unverified_context()
                context.check_hostname = False
                with request.urlopen(dados, timeout=timeout, context=context) as response:
                    encoding = response.headers.get_content_charset() or "utf-8"
                    html = response.read().decode(encoding, errors="replace")

                return str(BeautifulSoup(html, "html.parser"))

    raise RuntimeError(f"Não foi possível obter o conteúdo de {dados!r}") from last_error
```

Outras melhorias recomendadas:

- Registrar logs para facilitar a observação de falhas de rede.
- Expor parâmetros como *parser*, tempo de *backoff* e contexto SSL para ajuste fino.
- Instalar o pacote [`certifi`](https://pypi.org/project/certifi/) para obter uma
  cadeia de certificados confiáveis multiplataforma quando o sistema operacional
  não disponibiliza *roots* atualizadas.
- Propagar exceções específicas quando apropriado, em vez de simplesmente
  silenciá-las.
