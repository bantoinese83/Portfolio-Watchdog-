"""
PostgreSQL database models and helper functions for Portfolio Watchdog.

This module defines the SQLAlchemy ORM models for Users and WatchlistItems,
and provides helper functions for database operations.
"""

import os
from datetime import datetime, timezone

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

# DATABASE_URL example:
# postgres://user:password@host:5432/portfolio_watchdog
# For development, you can use SQLite by setting: sqlite:///portfolio_watchdog.db
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///portfolio_watchdog.db")

# Use SQLite for development if no DATABASE_URL is set
# This allows the app to run without PostgreSQL setup
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL, connect_args={"check_same_thread": False}, future=True
    )
else:
    engine = create_engine(DATABASE_URL, future=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

Base = declarative_base()


class User(Base):
    """
    Basic user table mapped to authentication system.

    In this MVP, 'username' must match the username configured in streamlit-authenticator.
    This ensures that the authentication layer (streamlit-authenticator) and the database
    user records are synchronized.
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(64), unique=True, index=True, nullable=False)
    email = Column(String(256), unique=True, index=True, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # One-to-many relationship: one user can have many watchlist items
    watchlists = relationship(
        "WatchlistItem", back_populates="user", cascade="all, delete-orphan"
    )


class WatchlistItem(Base):
    """
    Simple watchlist: each row is a (user, ticker) pair.

    This table stores the ticker symbols that each user wants to monitor.
    The unique constraint on (user_id, ticker) prevents duplicate entries
    for the same ticker in a user's watchlist.
    """

    __tablename__ = "watchlist_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    ticker = Column(String(32), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Many-to-one relationship: many watchlist items belong to one user
    user = relationship("User", back_populates="watchlists")

    # Ensure each user can only have one entry per ticker
    __table_args__ = (UniqueConstraint("user_id", "ticker", name="uq_user_ticker"),)


def init_db() -> None:
    """
    Create all tables if they do not exist.

    Call this once at startup or via migration script.
    This is safe to call multiple times - it will not recreate existing tables.

    Raises:
        OperationalError: If database connection fails
    """
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        # Log error but don't crash - allows app to show helpful error message
        import logging

        logging.error(f"Database initialization failed: {e}")
        raise


def get_or_create_user(session, username: str, email: str | None = None) -> User:
    """
    Retrieve existing user by username or create a new one.

    This connects Streamlit-authenticator identity with the database record.
    When a user logs in for the first time, we create their database record
    automatically based on their authenticated username.

    Args:
        session: SQLAlchemy database session
        username: Username from streamlit-authenticator
        email: Optional email address

    Returns:
        User object (existing or newly created)
    """
    user = session.query(User).filter(User.username == username).one_or_none()
    if user is None:
        user = User(username=username, email=email)
        session.add(user)
        session.commit()
        session.refresh(user)
    return user


def add_ticker_to_watchlist(session, user: User, ticker: str) -> None:
    """
    Insert a ticker into the user's watchlist if not already present.

    The ticker is automatically converted to uppercase to ensure consistency.
    Duplicate entries are prevented by the unique constraint.

    Args:
        session: SQLAlchemy database session
        user: User object
        ticker: Stock ticker symbol (e.g., "TSLA")
    """
    ticker = ticker.upper().strip()
    existing = (
        session.query(WatchlistItem)
        .filter(WatchlistItem.user_id == user.id, WatchlistItem.ticker == ticker)
        .one_or_none()
    )
    if existing is None:
        item = WatchlistItem(user_id=user.id, ticker=ticker)
        session.add(item)
        session.commit()


def remove_ticker_from_watchlist(session, user: User, ticker: str) -> None:
    """
    Remove a ticker from user's watchlist if present.

    Args:
        session: SQLAlchemy database session
        user: User object
        ticker: Stock ticker symbol to remove
    """
    ticker = ticker.upper().strip()
    item = (
        session.query(WatchlistItem)
        .filter(WatchlistItem.user_id == user.id, WatchlistItem.ticker == ticker)
        .one_or_none()
    )
    if item:
        session.delete(item)
        session.commit()


def get_watchlist_for_user(session, user: User) -> list[str]:
    """
    Return a list of ticker symbols on the user's watchlist.

    Args:
        session: SQLAlchemy database session (unused but kept for API consistency)
        user: User object

    Returns:
        List of ticker symbols (uppercase strings)
    """
    return [item.ticker for item in user.watchlists]
