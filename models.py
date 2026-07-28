"""
Database models — one class per table, SQLAlchemy's ORM style.

Each class attribute = a column. Each instance you create and commit = a row.
relationship() gives you Python-level navigation (product.price_points) without
writing a JOIN yourself — SQLAlchemy generates it.
"""

from datetime import datetime, timezone

from sqlalchemy import ForeignKey, String, Float, Boolean, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Every model inherits from this. SQLAlchemy uses it to track all your tables."""
    pass


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    url: Mapped[str] = mapped_column(String, unique=True)
    title: Mapped[str] = mapped_column(String)
    target_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    # None = no alert configured. A real value ("discord", "email", ...) means
    # alerts are on, sent via that channel. One field, no way to contradict itself.
    alert_type: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    # This isn't a column — it's a Python-side convenience so you can do
    # `product.price_points` and get a list of related PricePoint rows.
    price_points: Mapped[list["PricePoint"]] = relationship(
        back_populates="product", cascade="all, delete-orphan"
    )


class PricePoint(Base):
    __tablename__ = "price_points"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    price: Mapped[float] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String, default="NOK")
    # None = unknown/not reported (e.g. Prisjakt's AggregateOffer has no
    # single stock status across its 5 stores). True/False = actually known.
    in_stock: Mapped[bool | None] = mapped_column(Boolean, nullable=True, default=None)
    checked_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    product: Mapped["Product"] = relationship(back_populates="price_points")
