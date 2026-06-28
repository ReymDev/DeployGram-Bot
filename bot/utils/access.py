"""Helper functions for access control."""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models import Project, User
    from models.coowner import CoOwner
    from sqlalchemy.ext.asyncio import AsyncSession


async def check_project_access(
    project: Project | None,
    user: User,
    session: AsyncSession,
) -> bool:
    """
    Check if user has access to project (owner or coowner).
    
    Args:
        project: Project to check
        user: User to check access for
        session: Database session
        
    Returns:
        True if user is owner or coowner, False otherwise
    """
    if project is None:
        return False
    
    # Owner always has access
    if project.user_id == user.id:
        return True
    
    # Check if user is coowner
    from repositories.coowner import CoOwnerRepository
    coowner_repo = CoOwnerRepository(session)
    coowner = await coowner_repo.get_by_user_and_project(user.id, project.id)
    
    return coowner is not None


async def check_permission(
    project: Project | None,
    user: User,
    session: AsyncSession,
    permission: str,
) -> tuple[bool, CoOwner | None]:
    """
    Check if user has specific permission for a project.
    
    Args:
        project: Project to check
        user: User to check permission for
        session: Database session
        permission: Permission name (can_start_stop, can_view_logs, can_edit_files, can_manage_deps, can_view_settings)
        
    Returns:
        Tuple of (has_permission, coowner_object)
        - Owner always has all permissions
        - Coowner permissions depend on their settings
    """
    if project is None:
        return False, None
    
    # Owner always has full access
    if project.user_id == user.id:
        return True, None
    
    # Check coowner permissions
    from repositories.coowner import CoOwnerRepository
    coowner_repo = CoOwnerRepository(session)
    coowner = await coowner_repo.get_by_user_and_project(user.id, project.id)
    
    if coowner is None:
        return False, None
    
    # Check specific permission
    has_perm = getattr(coowner, permission, False)
    return has_perm, coowner
