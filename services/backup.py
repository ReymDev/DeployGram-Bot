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
                            for file in files:
                                file_path = os.path.join(root, file)
                                arcname = os.path.relpath(file_path, project_dir)
                                zf.write(file_path, arcname)
                    return backup_file.stat().st_size
                except Exception as e:
                    logger.error("Failed to create backup for project %d: %s", project_id, e)
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

            with zipfile.ZipFile(matched_backup, "r") as zf:
                for member in zf.infolist():
                    target = (tmp_dir / member.filename).resolve()
                    if not str(target).startswith(str(tmp_dir.resolve())):
                        logger.warning("Zip slip in backup: %s", member.filename)
                        return False, "Бэкап повреждён"
                zf.extractall(tmp_dir)

            if project_dir.exists():
                shutil.rmtree(project_dir)
            tmp_dir.rename(project_dir)

            return True, "Бэкап восстановлен"
        except Exception as e:
            logger.error("Failed to restore backup %d: %s", backup_id, e)
            if tmp_dir.exists():
                shutil.rmtree(tmp_dir, ignore_errors=True)
            return False, "Ошибка восстановления"
