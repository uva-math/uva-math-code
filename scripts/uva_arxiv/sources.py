"""arXiv source fetch and unpack helpers."""

from __future__ import annotations

import argparse
import gzip
import io
import re
import shutil
import sys
import tarfile
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, TextIO

try:
    from . import env
except ImportError:  # pragma: no cover - direct script execution
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from scripts.uva_arxiv import env


EPRINT_ENDPOINT = "https://arxiv.org/e-print"
DEFAULT_RETRIES = 2
DEFAULT_RATE_LIMIT_SECONDS = 3.0
MAX_SOURCE_RESPONSE_BYTES = 50_000_000
MAX_ARCHIVE_MEMBERS = 2_000
MAX_ARCHIVE_FILE_BYTES = 20_000_000
MAX_ARCHIVE_TOTAL_BYTES = 100_000_000
COPY_CHUNK_BYTES = 1_048_576
TEXT_EXTENSIONS = {
    ".aux",
    ".bbl",
    ".bib",
    ".cls",
    ".dtx",
    ".ins",
    ".ltx",
    ".md",
    ".sty",
    ".tex",
    ".txt",
}

HttpGet = Callable[[str], bytes]
Sleeper = Callable[[float], None]


class SourceFetchError(RuntimeError):
    """Raised when an arXiv source cannot be fetched or unpacked."""


@dataclass(frozen=True)
class SourceFetchResult:
    arxiv_id: str
    safe_id: str
    source_url: str
    target_dir: Path
    dry_run: bool
    status: str
    source_format: str
    files_written: tuple[str, ...]
    bytes_fetched: int = 0


class RateLimiter:
    """Small injectable rate limiter for arXiv e-print requests."""

    def __init__(
        self,
        seconds: float = DEFAULT_RATE_LIMIT_SECONDS,
        sleeper: Sleeper = time.sleep,
        now: Callable[[], float] = time.monotonic,
    ) -> None:
        self.seconds = max(0.0, seconds)
        self.sleeper = sleeper
        self.now = now
        self._last_request: float | None = None

    def wait(self) -> None:
        if self.seconds <= 0:
            self._last_request = self.now()
            return
        current = self.now()
        if self._last_request is not None:
            remaining = self.seconds - (current - self._last_request)
            if remaining > 0:
                self.sleeper(remaining)
                current = self.now()
        self._last_request = current


def normalize_arxiv_id(value: str) -> str:
    arxiv_id = value.strip()
    if not arxiv_id:
        raise SourceFetchError("arXiv ID is required")
    if arxiv_id.startswith("arXiv:"):
        arxiv_id = arxiv_id[len("arXiv:") :]
    for marker in ("/abs/", "/pdf/", "/e-print/"):
        if marker in arxiv_id:
            arxiv_id = arxiv_id.split(marker, 1)[1]
            break
    if arxiv_id.endswith(".pdf"):
        arxiv_id = arxiv_id[:-4]
    arxiv_id = strip_version(arxiv_id.strip("/"))
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._+/-]*", arxiv_id):
        raise SourceFetchError(f"unsafe arXiv ID: {value!r}")
    return arxiv_id


def strip_version(arxiv_id: str) -> str:
    stem, sep, version = arxiv_id.rpartition("v")
    if sep and version.isdigit() and stem:
        return stem
    return arxiv_id


def safe_source_dir_name(arxiv_id: str) -> str:
    normalized = normalize_arxiv_id(arxiv_id)
    safe = normalized.replace("/", "__")
    safe = re.sub(r"[^A-Za-z0-9._-]+", "_", safe).strip("._-")
    if not safe:
        raise SourceFetchError(f"arXiv ID has no safe directory name: {arxiv_id!r}")
    return safe


def source_dir_for_id(sources_root: Path, arxiv_id: str) -> Path:
    return Path(sources_root) / safe_source_dir_name(arxiv_id)


def eprint_url(arxiv_id: str, endpoint: str = EPRINT_ENDPOINT) -> str:
    quoted_id = urllib.parse.quote(normalize_arxiv_id(arxiv_id), safe="/.")
    return endpoint.rstrip("/") + "/" + quoted_id


def _check_payload_size(payload: bytes, limit: int = MAX_SOURCE_RESPONSE_BYTES) -> None:
    if len(payload) > limit:
        raise SourceFetchError(
            f"source response is too large: {len(payload)} bytes exceeds {limit}"
        )


def default_http_get(url: str, timeout: int = 45) -> bytes:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "uva-math-arxiv-phase1-source-fetch/0.1"},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = response.read(MAX_SOURCE_RESPONSE_BYTES + 1)
            _check_payload_size(payload)
            return payload
    except urllib.error.URLError as exc:
        raise SourceFetchError(f"request failed for {url}: {exc}") from exc


def _is_safe_member_name(name: str) -> bool:
    path = Path(name)
    return not path.is_absolute() and ".." not in path.parts and name.strip() not in {"", "."}


def _write_file(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)


def _write_stream_bounded(path: Path, source: io.BufferedIOBase, expected_size: int) -> None:
    if expected_size < 0:
        raise SourceFetchError("archive member has unknown size")
    if expected_size > MAX_ARCHIVE_FILE_BYTES:
        raise SourceFetchError(
            f"archive member is too large: {expected_size} bytes exceeds {MAX_ARCHIVE_FILE_BYTES}"
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    remaining = expected_size
    with path.open("wb") as handle:
        while remaining:
            chunk = source.read(min(COPY_CHUNK_BYTES, remaining))
            if not chunk:
                raise SourceFetchError("archive member ended before its declared size")
            handle.write(chunk)
            remaining -= len(chunk)
        if source.read(1):
            raise SourceFetchError("archive member exceeded its declared size")


def _extract_tar(payload: bytes, target_dir: Path) -> tuple[str, tuple[str, ...]] | None:
    try:
        with tarfile.open(fileobj=io.BytesIO(payload), mode="r:*") as archive:
            members = archive.getmembers()
            if len(members) > MAX_ARCHIVE_MEMBERS:
                raise SourceFetchError(
                    f"archive has too many members: {len(members)} exceeds {MAX_ARCHIVE_MEMBERS}"
                )
            written: list[str] = []
            total_bytes = 0
            for member in members:
                if not _is_safe_member_name(member.name):
                    raise SourceFetchError(f"archive member has unsafe path: {member.name}")
                destination = target_dir / member.name
                if member.isdir():
                    destination.mkdir(parents=True, exist_ok=True)
                    continue
                if not member.isfile():
                    continue
                if member.size > MAX_ARCHIVE_FILE_BYTES:
                    raise SourceFetchError(
                        f"archive member {member.name} is too large: {member.size} bytes"
                    )
                total_bytes += member.size
                if total_bytes > MAX_ARCHIVE_TOTAL_BYTES:
                    raise SourceFetchError(
                        f"archive extraction is too large: {total_bytes} bytes exceeds {MAX_ARCHIVE_TOTAL_BYTES}"
                    )
                extracted = archive.extractfile(member)
                if extracted is None:
                    continue
                _write_stream_bounded(destination, extracted, member.size)
                written.append(str(Path(member.name)))
            if written:
                return ("tar", tuple(sorted(written)))
            raise SourceFetchError("archive contains no extractable regular files")
    except tarfile.TarError:
        return None


def _looks_like_pdf(payload: bytes) -> bool:
    return payload.startswith(b"%PDF")


def _looks_like_text(payload: bytes) -> bool:
    sample = payload[:4096]
    if b"\x00" in sample:
        return False
    try:
        sample.decode("utf-8")
        return True
    except UnicodeDecodeError:
        try:
            sample.decode("latin-1")
            return True
        except UnicodeDecodeError:
            return False


def _fallback_filename(payload: bytes) -> str:
    if _looks_like_pdf(payload):
        return "source.pdf"
    if _looks_like_text(payload):
        return "source.tex"
    return "source.bin"


def _decompress_gzip_bounded(payload: bytes) -> bytes | None:
    try:
        with gzip.GzipFile(fileobj=io.BytesIO(payload), mode="rb") as compressed:
            decompressed = compressed.read(MAX_ARCHIVE_TOTAL_BYTES + 1)
    except OSError:
        return None
    if len(decompressed) > MAX_ARCHIVE_TOTAL_BYTES:
        raise SourceFetchError(
            f"decompressed source is too large: {len(decompressed)} bytes exceeds {MAX_ARCHIVE_TOTAL_BYTES}"
        )
    return decompressed


def unpack_source_bytes(payload: bytes, target_dir: Path) -> tuple[str, tuple[str, ...]]:
    """Unpack an arXiv e-print payload into target_dir."""
    target_dir.mkdir(parents=True, exist_ok=True)

    tar_result = _extract_tar(payload, target_dir)
    if tar_result is not None:
        return tar_result

    decompressed = _decompress_gzip_bounded(payload)

    if decompressed is not None:
        tar_result = _extract_tar(decompressed, target_dir)
        if tar_result is not None:
            return tar_result
        filename = _fallback_filename(decompressed)
        _write_file(target_dir / filename, decompressed)
        return ("gzip", (filename,))

    filename = _fallback_filename(payload)
    _write_file(target_dir / filename, payload)
    if filename == "source.pdf":
        return ("pdf", (filename,))
    if Path(filename).suffix in TEXT_EXTENSIONS:
        return ("raw", (filename,))
    return ("binary", (filename,))


def fetch_source(
    config: env.UvaArxivConfig,
    arxiv_id: str,
    sources_dir: Path | None = None,
    dry_run: bool = False,
    force: bool = False,
    retries: int = DEFAULT_RETRIES,
    rate_limit_seconds: float = DEFAULT_RATE_LIMIT_SECONDS,
    endpoint: str = EPRINT_ENDPOINT,
    http_get: HttpGet | None = None,
    sleeper: Sleeper = time.sleep,
) -> SourceFetchResult:
    normalized_id = normalize_arxiv_id(arxiv_id)
    safe_id = safe_source_dir_name(normalized_id)
    source_url = eprint_url(normalized_id, endpoint)
    sources_root = Path(sources_dir or config.arxiv_sources_dir)
    target_dir = sources_root / safe_id

    existing_files = tuple(
        sorted(
            str(path.relative_to(target_dir))
            for path in target_dir.rglob("*")
            if path.is_file()
        )
    ) if target_dir.is_dir() else ()
    if dry_run:
        status = "exists" if existing_files else "would_fetch"
        return SourceFetchResult(
            arxiv_id=normalized_id,
            safe_id=safe_id,
            source_url=source_url,
            target_dir=target_dir,
            dry_run=True,
            status=status,
            source_format="none",
            files_written=existing_files,
        )
    if existing_files and not force:
        return SourceFetchResult(
            arxiv_id=normalized_id,
            safe_id=safe_id,
            source_url=source_url,
            target_dir=target_dir,
            dry_run=False,
            status="exists",
            source_format="existing",
            files_written=existing_files,
        )

    sources_root.mkdir(parents=True, exist_ok=True)
    getter = http_get or default_http_get
    limiter = RateLimiter(rate_limit_seconds, sleeper=sleeper)
    attempts = max(0, retries) + 1
    payload: bytes | None = None
    last_error: Exception | None = None
    for attempt in range(attempts):
        limiter.wait()
        try:
            payload = getter(source_url)
            _check_payload_size(payload)
            break
        except Exception as exc:  # noqa: BLE001 - keep retry hook generic.
            last_error = exc
            if attempt + 1 >= attempts:
                break
    if payload is None:
        raise SourceFetchError(f"failed to fetch {normalized_id}: {last_error}") from last_error

    temp_dir = Path(
        tempfile.mkdtemp(prefix=f".{safe_id}.", suffix=".tmp", dir=str(sources_root))
    )
    try:
        source_format, files_written = unpack_source_bytes(payload, temp_dir)
        if target_dir.exists():
            if not force:
                shutil.rmtree(temp_dir)
                return SourceFetchResult(
                    arxiv_id=normalized_id,
                    safe_id=safe_id,
                    source_url=source_url,
                    target_dir=target_dir,
                    dry_run=False,
                    status="exists",
                    source_format="existing",
                    files_written=existing_files,
                )
            shutil.rmtree(target_dir)
        temp_dir.rename(target_dir)
    except Exception:
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        raise

    return SourceFetchResult(
        arxiv_id=normalized_id,
        safe_id=safe_id,
        source_url=source_url,
        target_dir=target_dir,
        dry_run=False,
        status="fetched",
        source_format=source_format,
        files_written=files_written,
        bytes_fetched=len(payload),
    )


def print_fetch_result(result: SourceFetchResult, out: TextIO = sys.stdout) -> None:
    print(f"arxiv_id: {result.arxiv_id}", file=out)
    print(f"safe_id: {result.safe_id}", file=out)
    print(f"source_url: {result.source_url}", file=out)
    print(f"target_dir: {result.target_dir}", file=out)
    print(f"dry_run: {'true' if result.dry_run else 'false'}", file=out)
    print(f"status: {result.status}", file=out)
    print(f"source_format: {result.source_format}", file=out)
    print(f"bytes_fetched: {result.bytes_fetched}", file=out)
    print(f"files_written: {len(result.files_written)}", file=out)
    for path in result.files_written[:20]:
        print(f"file: {path}", file=out)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Fetch arXiv sources into the shared corpus.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    fetch = subparsers.add_parser("fetch", help="Fetch one arXiv source bundle.")
    fetch.add_argument("--id", required=True, dest="arxiv_id", help="arXiv ID to fetch.")
    fetch.add_argument("--dry-run", action="store_true", help="Print planned work without writing.")
    fetch.add_argument("--force", action="store_true", help="Replace an existing source directory.")
    fetch.add_argument("--sources-dir", type=Path, help="Override configured shared source corpus.")
    fetch.add_argument("--endpoint", default=EPRINT_ENDPOINT, help="Override arXiv e-print endpoint.")
    fetch.add_argument("--retries", type=int, default=DEFAULT_RETRIES)
    fetch.add_argument("--rate-limit", type=float, default=DEFAULT_RATE_LIMIT_SECONDS)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    config = env.load_config(ensure_dirs=True)

    if args.command == "fetch":
        result = fetch_source(
            config=config,
            arxiv_id=args.arxiv_id,
            sources_dir=args.sources_dir,
            dry_run=args.dry_run,
            force=args.force,
            retries=args.retries,
            rate_limit_seconds=args.rate_limit,
            endpoint=args.endpoint,
        )
        print_fetch_result(result)
        return 0
    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
