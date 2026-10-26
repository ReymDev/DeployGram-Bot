from __future__ import annotations

import io
import os
import stat
import zipfile
from pathlib import Path, PurePosixPath
from typing import BinaryIO, Union

ZipSource = Union[str, os.PathLike[str], bytes, bytearray, BinaryIO]

MAX_ARCHIVE_FILES = 20_000
MAX_ARCHIVE_SIZE = 500 * 1024 * 1024
MAX_ARCHIVE_MEMBER_SIZE = 200 * 1024 * 1024
MAX_COMPRESSION_RATIO = 200


class ArchiveError(ValueError):
    """Raised when an archive is invalid or unsafe to extract."""


def _read_source(source: ZipSource) -> Union[str, os.PathLike[str], bytes]:
    if isinstance(source, (bytes, bytearray)):
        return bytes(source)
    if hasattr(source, "read"):
        data = source.read()
        if not isinstance(data, (bytes, bytearray)):
            raise ArchiveError("Ожидался бинарный ZIP-архив")
        return bytes(data)
    return source


def _open_zip(source: ZipSource) -> zipfile.ZipFile:
    prepared = _read_source(source)
    if isinstance(prepared, (bytes, bytearray)):
        return zipfile.ZipFile(io.BytesIO(prepared), "r")
    return zipfile.ZipFile(prepared, "r")


def _normalized_member_name(name: str) -> str:
    name = (name or "").replace("\\", "/")
    if not name or name.startswith("/"):
        raise ArchiveError("Абсолютные пути в архиве запрещены")
    if any(ord(ch) < 32 for ch in name):
        raise ArchiveError(f"Некорректное имя файла в архиве: {name!r}")
    pure = PurePosixPath(name)
    if pure.is_absolute() or any(part in ("..", "") for part in pure.parts):
        raise ArchiveError(f"Небезопасный путь в архиве: {name}")
    if any(":" in part for part in pure.parts):
        raise ArchiveError(f"Небезопасный путь в архиве: {name}")
    return pure.as_posix()


def _is_symlink(info: zipfile.ZipInfo) -> bool:
    mode = info.external_attr >> 16
    return stat.S_ISLNK(mode)


def validate_zip(
    source: ZipSource,
    *,
    max_files: int = MAX_ARCHIVE_FILES,
    max_total_size: int = MAX_ARCHIVE_SIZE,
    max_member_size: int = MAX_ARCHIVE_MEMBER_SIZE,
) -> list[zipfile.ZipInfo]:
    """Validate every archive member before anything is written to disk."""
    try:
        zf = _open_zip(source)
    except zipfile.BadZipFile as exc:
        raise ArchiveError("Невалидный ZIP-архив") from exc

    with zf:
        infos = zf.infolist()
        if len(infos) > max_files:
            raise ArchiveError("В архиве слишком много файлов")

        total_size = 0
        for info in infos:
            name = _normalized_member_name(info.filename)
            if _is_symlink(info):
                raise ArchiveError(f"Символические ссылки в архиве запрещены: {name}")
            if info.file_size > max_member_size:
                raise ArchiveError(f"Файл слишком большой: {name}")
            total_size += info.file_size
            if total_size > max_total_size:
                raise ArchiveError("Распакованный архив слишком большой")
            if (
                info.file_size > 10 * 1024 * 1024
                and info.compress_size > 0
                and info.file_size / info.compress_size > MAX_COMPRESSION_RATIO * 5
            ):
                raise ArchiveError("Подозрительная степень сжатия архива (zip bomb)")
        return infos


def safe_extract_zip(
    source: ZipSource,
    destination: str | os.PathLike[str],
    *,
    max_files: int = MAX_ARCHIVE_FILES,
    max_total_size: int = MAX_ARCHIVE_SIZE,
    max_member_size: int = MAX_ARCHIVE_MEMBER_SIZE,
) -> None:
    """Safely extract a ZIP archive, rejecting traversal, symlinks and zip bombs."""
    dest = Path(destination).resolve()
    dest.mkdir(parents=True, exist_ok=True)
    dest_str = str(dest)

    prepared = _read_source(source)
    infos = validate_zip(
        prepared,
        max_files=max_files,
        max_total_size=max_total_size,
        max_member_size=max_member_size,
    )

    zf = _open_zip(prepared)
    with zf:
        for info in infos:
            name = _normalized_member_name(info.filename)
            target = (dest / PurePosixPath(name)).resolve()
            try:
                common = os.path.commonpath([dest_str, str(target)])
            except ValueError as exc:
                raise ArchiveError(f"Небезопасный путь в архиве: {name}") from exc
            if common != dest_str:
                raise ArchiveError(f"Небезопасный путь в архиве: {name}")
            if info.is_dir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            try:
                with zf.open(info, "r") as src, open(target, "wb") as out:
                    while True:
                        chunk = src.read(1024 * 1024)
                        if not chunk:
                            break
                        out.write(chunk)
            except (RuntimeError, zipfile.BadZipFile, OSError) as exc:
                raise ArchiveError(f"?? ??????? ??????????? {name}") from exc
