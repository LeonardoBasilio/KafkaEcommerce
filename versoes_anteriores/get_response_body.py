"""Ferramentas auxiliares para leitura de HTML em aplicações de ETL."""

from __future__ import annotations

import logging
import ssl
import time
from pathlib import Path
from typing import Union
from urllib import error, request

from bs4 import BeautifulSoup

try:  # pragma: no cover - dependência opcional
    import certifi
except ModuleNotFoundError:  # pragma: no cover - dependência opcional
    certifi = None


LOGGER = logging.getLogger(__name__)


def get_response_body(
    dados: Union[str, Path],
    *,
    timeout: int = 30,
    max_retries: int = 3,
    backoff_factor: float = 1.0,
    parser: str = "html.parser",
    ssl_context: ssl.SSLContext | None = None,
    cafile: Union[str, Path, None] = None,
    allow_insecure_fallback: bool = False,
) -> str:
    """Retorna o HTML normalizado para a URL ou caminho informado.

    A função trata tanto URLs quanto caminhos locais. Quando ``dados`` é um
    caminho, o arquivo é lido diretamente do disco. Para URLs, uma política de
    tentativas com ``max_retries`` é aplicada antes de propagar uma exceção.

    Parameters
    ----------
    dados:
        URL ou caminho do conteúdo.
    timeout:
        Tempo máximo (em segundos) para aguardar a resposta de cada tentativa.
    max_retries:
        Número máximo de tentativas antes de falhar.
    backoff_factor:
        Multiplicador aplicado ao tempo de espera entre tentativas.
    parser:
        Parser utilizado pelo BeautifulSoup.

    Returns
    -------
    str
        Representação HTML normalizada pelo BeautifulSoup.

    Raises
    ------
    RuntimeError
        Quando não é possível obter o conteúdo após as tentativas realizadas.
    """

    path = Path(dados)
    if path.exists():
        LOGGER.debug("Lendo conteúdo local de %s", path)
        return path.read_text(encoding="utf-8")

    last_error: Exception | None = None
    insecure_attempted = False

    def build_context(disable_verification: bool = False) -> ssl.SSLContext | None:
        if ssl_context is not None:
            return ssl_context
        if disable_verification:
            LOGGER.warning(
                "SSL desabilitado para %s por solicitação explícita.",
                dados,
            )
            insecure_context = ssl._create_unverified_context()
            insecure_context.check_hostname = False
            return insecure_context
        if cafile is not None:
            return ssl.create_default_context(cafile=str(cafile))
        if certifi is not None:
            return ssl.create_default_context(cafile=certifi.where())
        return None

    for attempt in range(1, max_retries + 1):
        try:
            LOGGER.debug("Tentativa %s de leitura remota de %s", attempt, dados)
            context = build_context(disable_verification=insecure_attempted)
            with request.urlopen(str(dados), timeout=timeout, context=context) as response:
                encoding = response.headers.get_content_charset() or "utf-8"
                html = response.read().decode(encoding, errors="replace")

            page_items = BeautifulSoup(html, parser)
            return str(page_items)
        except (error.URLError, error.HTTPError, ValueError) as exc:
            last_error = exc
            LOGGER.warning(
                "Falha ao obter HTML de %s na tentativa %s/%s: %s",
                dados,
                attempt,
                max_retries,
                exc,
            )
            reason = getattr(exc, "reason", None)
            reason_text = str(reason or exc)
            is_cert_failure = isinstance(reason, ssl.SSLCertVerificationError) or (
                isinstance(reason, ssl.SSLError)
                and "CERTIFICATE_VERIFY_FAILED" in reason_text.upper()
            )
            if allow_insecure_fallback and not insecure_attempted and is_cert_failure:
                LOGGER.warning(
                    "Nova tentativa para %s com verificação SSL desabilitada; considere "
                    "configurar um arquivo de certificados de confiança (cafile).",
                    dados,
                )
                insecure_attempted = True
                continue
            if attempt < max_retries:
                sleep_for = backoff_factor * attempt
                LOGGER.debug("Aguardando %s segundo(s) antes da nova tentativa", sleep_for)
                time.sleep(sleep_for)

    raise RuntimeError(f"Não foi possível obter o conteúdo de {dados!r}") from last_error


__all__ = ["get_response_body"]
