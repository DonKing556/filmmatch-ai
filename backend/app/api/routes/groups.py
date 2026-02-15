import secrets

from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_session_store
from app.core.exceptions import NotFoundError
from app.core.logging import get_logger
from app.core.redis import SessionStore
from app.db.models import Group, GroupMember, User
from app.db.session import get_db
from app.schemas.group import GroupCreate, GroupJoin, GroupMemberPreferences, GroupResponse

logger = get_logger("group_routes")

router = APIRouter(prefix="/groups", tags=["groups"])


def _generate_join_code() -> str:
    return secrets.token_urlsafe(6)[:8].upper()


@router.post("", response_model=GroupResponse)
async def create_group(
    request: GroupCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    group = Group(
        created_by=user.id,
        name=request.name,
        join_code=_generate_join_code(),
    )
    db.add(group)
    await db.flush()

    member = GroupMember(group_id=group.id, user_id=user.id)
    db.add(member)

    logger.info("group_created", group_id=str(group.id), creator=str(user.id))

    return GroupResponse(
        id=str(group.id),
        name=group.name,
        join_code=group.join_code,
        member_count=1,
        is_active=group.is_active,
        created_at=group.created_at.isoformat(),
    )


@router.post("/join", response_model=GroupResponse)
async def join_group(
    request: GroupJoin,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Group).where(
            Group.join_code == request.join_code.upper(),
            Group.is_active == True,
        )
    )
    group = result.scalar_one_or_none()
    if group is None:
        raise NotFoundError("Group", request.join_code)

    # Check if already a member
    existing = await db.execute(
        select(GroupMember).where(
            GroupMember.group_id == group.id,
            GroupMember.user_id == user.id,
        )
    )
    if existing.scalar_one_or_none() is None:
        member = GroupMember(group_id=group.id, user_id=user.id)
        db.add(member)

    count_result = await db.execute(
        select(func.count()).where(GroupMember.group_id == group.id)
    )
    member_count = count_result.scalar() or 0

    return GroupResponse(
        id=str(group.id),
        name=group.name,
        join_code=group.join_code,
        member_count=member_count,
        is_active=group.is_active,
        created_at=group.created_at.isoformat(),
    )


@router.get("/{group_id}", response_model=GroupResponse)
async def get_group(
    group_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Group).where(Group.id == group_id))
    group = result.scalar_one_or_none()
    if group is None:
        raise NotFoundError("Group", group_id)

    count_result = await db.execute(
        select(func.count()).where(GroupMember.group_id == group.id)
    )
    member_count = count_result.scalar() or 0

    return GroupResponse(
        id=str(group.id),
        name=group.name,
        join_code=group.join_code,
        member_count=member_count,
        is_active=group.is_active,
        created_at=group.created_at.isoformat(),
    )


@router.post("/{group_id}/preferences")
async def submit_preferences(
    group_id: str,
    request: GroupMemberPreferences,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(GroupMember).where(
            GroupMember.group_id == group_id,
            GroupMember.user_id == user.id,
        )
    )
    member = result.scalar_one_or_none()
    if member is None:
        raise NotFoundError("GroupMember", f"{group_id}/{user.id}")

    member.preferences = request.model_dump()
    return {"message": "Preferences submitted"}
