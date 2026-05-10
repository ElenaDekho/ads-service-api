from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import models
import schemas


async def get_item(
        session: AsyncSession,
        orm_model: type[models.Advertisement],
        item_id: int
) -> models.Advertisement:
    stmt = select(orm_model).where(orm_model.id == item_id)
    result = await session.execute(stmt)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Advertisement with id {item_id} not found"
        )
    return item


async def search_items(
        session: AsyncSession,
        orm_model: type[models.Advertisement],
        title: str = None,
        price_min: float = None,
        price_max: float = None
) -> list[models.Advertisement]:
    stmt = select(orm_model)

    if title:
        stmt = stmt.where(orm_model.title.ilike(f"%{title}%"))
    if price_min is not None:
        stmt = stmt.where(orm_model.price >= price_min)
    if price_max is not None:
        stmt = stmt.where(orm_model.price <= price_max)

    result = await session.execute(stmt)
    return result.scalars().all()
