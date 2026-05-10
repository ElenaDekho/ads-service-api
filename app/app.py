from typing import Annotated, Optional, List
from fastapi import FastAPI, Depends, Query, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import models
import schemas
from dependencies import get_db_session
from lifespan import lifespan
from services import get_item, search_items
from auth import get_current_user, check_password, create_token, hash_password
from datetime import datetime, timedelta
import uuid

app = FastAPI(
    title="Ads Service",
    description="Service for buying/selling ads",
    version="0.0.1",
    lifespan=lifespan,
)

SessionDep = Annotated[AsyncSession, Depends(get_db_session)]


@app.post("/advertisement", response_model=schemas.CreateAdResponse, status_code=201, summary="Создать объявление")
async def create_ad(
        ad_data: schemas.CreateAdRequest,
        session: SessionDep,
        x_token: Optional[str] = Header(None, alias="x-token")
):
    # 1. Проверяем токен и получаем пользователя. Если нет токена - 401
    if not x_token:
        raise HTTPException(status_code=401, detail="Token required")

    from auth import get_current_user
    current_user = await get_current_user(x_token, session)

    # 2. Создаём объявление от имени авторизованного пользователя
    new_ad = models.Advertisement(
        title=ad_data.title,
        description=ad_data.description,
        price=ad_data.price,
        author=current_user.username,
        user_id=current_user.id
    )
    session.add(new_ad)
    await session.commit()
    await session.refresh(new_ad)
    return schemas.CreateAdResponse(id=new_ad.id)


@app.get("/advertisement/{item_id}", response_model=schemas.GetAdResponse, summary="Получить объявление по ID")
async def get_ad(
        item_id: int,
        session: SessionDep
):
    ad = await get_item(session, models.Advertisement, item_id)
    return schemas.GetAdResponse(**ad.to_dict())


@app.patch("/advertisement/{item_id}", response_model=schemas.UpdateAdResponse, summary="Обновить объявление")
async def update_ad(
        item_id: int,
        update_data: schemas.UpdateAdRequest,
        session: SessionDep,
        current_user: models.User = Depends(get_current_user)
):
    stmt = select(models.Advertisement).where(models.Advertisement.id == item_id)
    ad = await session.scalar(stmt)
    # Администратор может всё, обычный пользователь — только свои объявления
    if not ad:
        raise HTTPException(status_code=404, detail="Advertisement not found")

    if current_user.group != "admin" and ad.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    update_dict = update_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(ad, key, value)

    await session.commit()
    await session.refresh(ad)
    return schemas.UpdateAdResponse(**ad.to_dict())


@app.delete("/advertisement/{item_id}", response_model=schemas.OKResponse, summary="Удалить объявление")
async def delete_ad(
        item_id: int,
        session: SessionDep,
        current_user: models.User = Depends(get_current_user)
):
    stmt = select(models.Advertisement).where(models.Advertisement.id == item_id)
    ad = await session.scalar(stmt)
    # Администратор может всё, обычный пользователь — только свои объявления
    if not ad:
        raise HTTPException(status_code=404, detail="Advertisement not found")

    if current_user.group != "admin" and ad.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    await session.delete(ad)
    await session.commit()
    return schemas.OKResponse()


@app.get("/advertisement", response_model=list[schemas.GetAdResponse], summary="Поиск объявлений")
async def search_ads(
        session: SessionDep,
        title: Optional[str] = Query(None),
        price_min: Optional[float] = Query(None),
        price_max: Optional[float] = Query(None)
):
    ads = await search_items(session, models.Advertisement, title, price_min, price_max)
    return [schemas.GetAdResponse(**ad.to_dict()) for ad in ads]


@app.post("/login", response_model=schemas.LoginResponse, summary="Авторизация")
async def login(
        login_data: schemas.LoginRequest,
        session: SessionDep
):
    stmt = select(models.User).where(models.User.username == login_data.username)
    user = await session.scalar(stmt)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    if not check_password(login_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token_obj = await create_token(session, user.id, ttl_hours=48)
    return schemas.LoginResponse(token=token_obj.token)


@app.post("/user", response_model=schemas.CreateUserResponse, status_code=201, summary="Создать пользователя")
async def create_user(
        user_data: schemas.CreateUserRequest,
        session: SessionDep
):
    hashed_password = hash_password(user_data.password)

    new_user = models.User(
        username=user_data.username,
        password=hashed_password,
        group=user_data.group
    )
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return schemas.CreateUserResponse(id=new_user.id)


@app.get("/user/{user_id}", response_model=schemas.GetUserResponse, summary="Получить пользователя по ID")
async def get_user(
        user_id: int,
        session: SessionDep
):
    stmt = select(models.User).where(models.User.id == user_id)
    user = await session.scalar(stmt)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return schemas.GetUserResponse(
        id=user.id,
        username=user.username,
        group=user.group,
        created_at=user.created_at
    )


@app.patch("/user/{user_id}", response_model=schemas.CreateUserResponse, summary="Обновить пользователя")
async def update_user(
    user_id: int,
    user_data: schemas.UpdateUserRequest,
    session: SessionDep,
    current_user: models.User = Depends(get_current_user)
):
    if current_user.group != "admin" and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    stmt = select(models.User).where(models.User.id == user_id)
    user = await session.scalar(stmt)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user_data.username is not None:
        user.username = user_data.username
    if user_data.password is not None:
        user.password = hash_password(user_data.password)
    if user_data.group is not None:
        if current_user.group != "admin":
            raise HTTPException(status_code=403, detail="Only admin can change group")
        user.group = user_data.group

    await session.commit()
    await session.refresh(user)
    return schemas.CreateUserResponse(id=user.id)


@app.delete("/user/{user_id}", response_model=schemas.OKResponse, summary="Удалить пользователя")
async def delete_user(
    user_id: int,
    session: SessionDep,
    current_user: models.User = Depends(get_current_user)
):
    if current_user.group != "admin" and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    stmt = select(models.User).where(models.User.id == user_id)
    user = await session.scalar(stmt)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    await session.delete(user)
    await session.commit()
    return schemas.OKResponse()