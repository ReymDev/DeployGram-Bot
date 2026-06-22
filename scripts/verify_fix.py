#!/usr/bin/env python3
"""
Скрипт для проверки исправления ошибки с entry point.
Проверяет, что изменения применены корректно.
"""

import os
import sys
from pathlib import Path


def check_file_contains(filepath: Path, search_string: str, description: str) -> bool:
    """Проверяет, что файл содержит определенную строку."""
    if not filepath.exists():
        print(f"❌ Файл не найден: {filepath}")
        return False
    
    content = filepath.read_text(encoding="utf-8")
    if search_string in content:
        print(f"✅ {description}")
        return True
    else:
        print(f"❌ {description} - НЕ НАЙДЕНО")
        return False


def check_file_not_contains(filepath: Path, search_string: str, description: str) -> bool:
    """Проверяет, что файл НЕ содержит определенную строку."""
    if not filepath.exists():
        print(f"❌ Файл не найден: {filepath}")
        return False
    
    content = filepath.read_text(encoding="utf-8")
    if search_string not in content:
        print(f"✅ {description}")
        return True
    else:
        print(f"❌ {description} - НАЙДЕНО (нужно удалить)")
        return False


def main():
    """Главная функция проверки."""
    print("=" * 60)
    print("🔍 Проверка исправления ошибки entry point")
    print("=" * 60)
    print()
    
    # Определяем корневую директорию проекта
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    print(f"📁 Корневая директория: {project_root}")
    print()
    
    results = []
    
    # Проверка 1: agent/main.py - правильный путь
    print("📝 Проверка 1: agent/main.py")
    agent_main = project_root / "agent" / "main.py"
    results.append(check_file_contains(
        agent_main,
        'project_dir = self._get_project_dir(str(project_id))',
        "Используется _get_project_dir для получения пути"
    ))
    results.append(check_file_not_contains(
        agent_main,
        'project_dir = f"/data/projects/{project_id}"',
        "Старый неправильный путь удален"
    ))
    print()
    
    # Проверка 2: agent/main.py - логирование в upload_project
    print("📝 Проверка 2: Логирование в upload_project")
    results.append(check_file_contains(
        agent_main,
        'logger.info("Uploading project %s to %s", project_id, project_dir)',
        "Добавлено логирование загрузки проекта"
    ))
    results.append(check_file_contains(
        agent_main,
        'logger.info("Extracted files for project %s: %s"',
        "Добавлено логирование извлеченных файлов"
    ))
    print()
    
    # Проверка 3: agent/main.py - логирование в create_container
    print("📝 Проверка 3: Логирование в create_container")
    results.append(check_file_contains(
        agent_main,
        'logger.info(\n                "Creating container for project %s:',
        "Добавлено логирование создания контейнера"
    ))
    results.append(check_file_contains(
        agent_main,
        'logger.info("Container created successfully: %s", container_id)',
        "Добавлено логирование успешного создания"
    ))
    print()
    
    # Проверка 4: services/docker_manager.py - логирование
    print("📝 Проверка 4: services/docker_manager.py")
    docker_manager = project_root / "services" / "docker_manager.py"
    results.append(check_file_contains(
        docker_manager,
        'logger.info(\n                    "Mounting volume: host=%s -> container=/app',
        "Добавлено логирование монтирования volume"
    ))
    results.append(check_file_contains(
        docker_manager,
        'logger.info(\n                "Creating container %s: entry_point=%s',
        "Добавлено логирование параметров контейнера"
    ))
    results.append(check_file_contains(
        docker_manager,
        'logger.info("Container created successfully: %s", container.id)',
        "Добавлено логирование успешного создания контейнера"
    ))
    print()
    
    # Проверка 5: Документация
    print("📝 Проверка 5: Документация")
    bugfix_doc = project_root / "BUGFIX_ENTRY_POINT.md"
    deployment_doc = project_root / "DEPLOYMENT_GUIDE.md"
    structure_doc = project_root / "docs" / "PROJECT_STRUCTURE_GUIDE.md"
    changelog = project_root / "CHANGELOG.md"
    
    results.append(bugfix_doc.exists())
    print(f"{'✅' if bugfix_doc.exists() else '❌'} BUGFIX_ENTRY_POINT.md создан")
    
    results.append(deployment_doc.exists())
    print(f"{'✅' if deployment_doc.exists() else '❌'} DEPLOYMENT_GUIDE.md создан")
    
    results.append(structure_doc.exists())
    print(f"{'✅' if structure_doc.exists() else '❌'} docs/PROJECT_STRUCTURE_GUIDE.md создан")
    
    results.append(changelog.exists())
    print(f"{'✅' if changelog.exists() else '❌'} CHANGELOG.md создан")
    print()
    
    # Итоги
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    percentage = (passed / total * 100) if total > 0 else 0
    
    print(f"📊 Результаты: {passed}/{total} проверок пройдено ({percentage:.1f}%)")
    print("=" * 60)
    
    if passed == total:
        print("✅ Все проверки пройдены! Исправление применено корректно.")
        print()
        print("Следующие шаги:")
        print("1. Перезапустите сервисы: docker-compose restart")
        print("2. Проверьте логи: docker logs deploygram-agent")
        print("3. Протестируйте запуск проекта через бота")
        return 0
    else:
        print("❌ Некоторые проверки не пройдены.")
        print()
        print("Возможные причины:")
        print("- Изменения не были применены")
        print("- Файлы были изменены вручную")
        print("- Неправильная версия кода")
        print()
        print("Рекомендации:")
        print("- Проверьте git diff для просмотра изменений")
        print("- Убедитесь, что все изменения закоммичены")
        print("- Повторно примените исправления")
        return 1


if __name__ == "__main__":
    sys.exit(main())
