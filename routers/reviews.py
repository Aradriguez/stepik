from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update, func
from sqlalchemy.orm import Session

from stepik.models.reviews import Review as ReviewModel
from stepik.models.categories import Category as CategoryModel
from stepik.models.products import Product as ProductModel
from stepik.schemas import Review as ReviewSchema, ReviewCreate
from stepik.db_depends import get_db, get_async_db
from sqlalchemy.ext.asyncio import AsyncSession

from stepik.models.users import User as UserModel
from stepik.auth import get_current_seller, get_current_buyer, get_current_user


# Создаём маршрутизатор для товаров
router = APIRouter(
    prefix="/reviews",
    tags=["reviews"],
)


@router.get("/", response_model=list[ReviewSchema])
async def get_review(db: AsyncSession = Depends(get_async_db)):
    """
    Возвращает список всех активных отзывов.
    """
    result = await db.scalars(select(ReviewModel).where(ReviewModel.is_active == True))
    reviews_db = result.all()
    return reviews_db


#response_model=ReviewSchema,
@router.post("/",  status_code=status.HTTP_201_CREATED)
async def create_review(
    review: ReviewCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(get_current_buyer)
):
    """
    Создаёт новый отзыв, доступ только для buyer
    """

    # 1. Проверяем, что товар существует и активен
    product_result = await db.scalars(select(ProductModel).where(ProductModel.id == review.product_id, ProductModel.is_active == True))
    if not product_result.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found or inactive")

    # 2. Проверяем, что пользователь ещё не оставлял отзыв на этот товар
    review_result = await db.scalars(select(ReviewModel).where(ReviewModel.product_id == review.product_id, ReviewModel.user_id == current_user.id))
    if review_result.first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="You have already left a review for this product.")

    # 3. Создаём отзыв
    db_review = ReviewModel(**review.model_dump(), user_id=current_user.id)
    db.add(db_review)

    # 4. Отправляем INSERT в БД, но не коммитим (чтобы отзыв уже учитывался в AVG)
    await db.flush()

    # 5. Считаем средний рейтинг по этому товару среди активных отзывов
    avg_result = await db.execute(select(func.avg(ReviewModel.grade)).where(ReviewModel.product_id == review.product_id, ReviewModel.is_active == True,))
    avg_rating = avg_result.scalar() or 0.0

    # 6. Обновляем рейтинг товара
    await db.execute(update(ProductModel).where(ProductModel.id == review.product_id).values(rating=avg_rating))

    # 7. Фиксируем и отзыв, и новый рейтинг одним коммитом
    await db.commit()
    await db.refresh(db_review)

    return db_review


@router.delete("/{review_id}")
async def delete_product(
    review_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Выполняет мягкое удаление отзыва, доступно только для 'admin'.
    """

    review_db = await db.scalars(select(ReviewModel).where(ReviewModel.id == review_id, ReviewModel.is_active == True))

    review = review_db.first()
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found or inactive")
    if current_user.role != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    await db.execute(update(ReviewModel).where(ReviewModel.id == review_id).values(is_active=False))
    await db.flush()

    avg_result = await db.execute(select(func.avg(ReviewModel.grade)).where(ReviewModel.product_id == review.product_id, ReviewModel.is_active == True,))
    avg_rating = avg_result.scalar() or 0.0

    await db.execute(update(ProductModel).where(ProductModel.id == review.product_id).values(rating=avg_rating))

    await db.commit()
    await db.refresh(review)
    return {"message": "Review deleted"}