from __future__ import annotations

import asyncio
import logging
import os
import shutil
import uuid
import zipfile
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from bot.config import BASE_DIR
from models.backup import Backup
from services.archive import ArchiveError, safe_extract_zip
from repositories.backup import BackupRepository
from repositories.project import ProjectRepository

logger = logging.getLogger(__name__)


class BackupService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.backup_repo = BackupRepository(session)
        self.project_repo = ProjectRepository(session)

    def _get_backup_dir(self, project_id: int) -> Path:
        backup_dir = BASE_DIR / "data" / "backups" / str(project_id)
        backup_dir.mkdir(parents=True, exist_ok=True)
        return backup_dir

    async def create_backup(self, project_id: int, version_id: int | None = None, size: int = 0) -> Backup | None:
        project = await self.project_repo.get_by_id(project_id)
        if project is None:
            return None

        project_dir = BASE_DIR / "data" / "projects" / str(project_id)
        backup_dir = self._get_backup_dir(project_id)

        if project_dir.exists():
            backup_file = backup_dir / f"backup_{project_id}_{uuid.uuid4().hex[:8]}.zip"

            def _create():
                try:
                    with zipfile.ZipFile(backup_file, "w", zipfile.ZIP_DEFLATED) as zf:
                        for root, dirs, files in os.walk(project_dir):
                            dirs[:] = [
                                d for d in dirs
                                if d not in {".venv", "venv", "__pycache__", ".git"}
                                and not os.path.islink(os.path.join(root, d))
                            ]
                            for file in files:
                                file_path = os.path.join(root, file)
                                if os.path.islink(file_path):
                                    continue
                                arcname = os.path.relpath(file_path, project_dir)
                                zf.write(file_path, arcname)
                    return backup_file.stat().st_size
                except Exception as e:
                    logger.error("Failed to create backup for project %d: %s", project_id, e)
                    backup_file.unlink(missing_ok=True)
                    return 0

            size = await asyncio.to_thread(_create)

        return await self.backup_repo.create(
            project_id=project_id,
            version_id=version_id,
            size=size,
        )

    async def get_backups(self, project_id: int) -> list[Backup]:
        return await self.backup_repo.get_by_project_id(project_id)

    async def delete_backup(self, backup_id: int) -> bool:
        backup = await self.backup_repo.get_by_id(backup_id)
        if backup is None:
            return False

        backup_dir = self._get_backup_dir(backup.project_id)
        backup_files = list(backup_dir.glob("backup_*.zip"))
        if backup_files:
            backup_time = backup.created_at.timestamp() if backup.created_at else 0
            matched = min(
                backup_files, key=lambda f: abs(os.path.getctime(f) - backup_time)
            )
            try:
                matched.unlink(missing_ok=True)
            except OSError as e:
                logger.warning("Failed to delete backup file %s: %s", matched, e)

        return await self.backup_repo.delete(backup_id)

    async def restore_backup(self, backup_id: int) -> tuple[bool, str]:
        backup = await self.backup_repo.get_by_id(backup_id)
        if backup is None:
            return False, "Бэкап не найден"

        project = await self.project_repo.get_by_id(backup.project_id)
        if project is None:
            return False, "Проект не найден"

        backup_dir = self._get_backup_dir(backup.project_id)
        backup_files = list(backup_dir.glob("backup_*.zip"))

        if not backup_files:
            return False, "Файл бэкапа не найден"

        backup_time = backup.created_at.timestamp() if backup.created_at else 0
        matched_backup = min(backup_files, key=lambda f: abs(os.path.getctime(f) - backup_time))

        project_dir = BASE_DIR / "data" / "projects" / str(backup.project_id)
        tmp_dir = project_dir.parent / f"restore_tmp_{backup.project_id}"

        try:
            if tmp_dir.exists():
                shutil.rmtree(tmp_dir)
            tmp_dir.mkdir(parents=True, exist_ok=True)

            safe_extract_zip(matched_backup, tmp_dir)

            if project_dir.exists():
                shutil.rmtree(project_dir)
            tmp_dir.rename(project_dir)

            if hasattr(os, "geteuid") and os.geteuid() == 0:
                try:
                    os.chown(project_dir, 1000, 1000)
                    for root, dirs, files in os.walk(project_dir):
                        for name in dirs + files:
                            os.chown(os.path.join(root, name), 1000, 1000)
                except OSError as exc:
                    logger.warning("Failed to chown restored project: %s", exc)

            return True, "Бэкап восстановлен"
        except ArchiveError as e:
            logger.error("Unsafe backup %d: %s", backup_id, e)
            if tmp_dir.exists():
                shutil.rmtree(tmp_dir, ignore_errors=True)
            return False, "Бэкап повреждён"
        except Exception as e:
            logger.error("Failed to restore backup %d: %s", backup_id, e)
            if tmp_dir.exists():
                shutil.rmtree(tmp_dir, ignore_errors=True)
            return False, "Ошибка восстановления"
