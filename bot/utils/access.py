"""Helper functions for access control."""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models import Project, User
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
