"""
Simple data structure map for PostgreSQL schema.

This file is not executed by the app but documents the tables,
columns, and relationships for maintainers and developers.

It provides a clear reference for understanding the database structure
without needing to examine the SQLAlchemy models directly.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass
class UserSchema:
    """
    Represents a row in the 'users' table.

    This table stores basic user information and links to the authentication
    system (streamlit-authenticator). Each user can have multiple watchlist items.

    Columns:
    - id: Primary key integer (auto-incrementing)
    - username: Unique username (aligned with streamlit-authenticator config)
      This must match the username in config.yaml for authentication to work.
    - email: Optional unique email address
    - created_at: Timestamp for when the user record was created

    Relationships:
    - watchlists: One-to-many relationship to WatchlistItemSchema
      When a user is deleted, all their watchlist items are cascade deleted.

    Indexes:
    - Primary key on 'id'
    - Unique index on 'username'
    - Unique index on 'email' (nullable)
    """

    id: int
    username: str
    email: str | None
    created_at: datetime
    watchlists: List["WatchlistItemSchema"]


@dataclass
class WatchlistItemSchema:
    """
    Represents a row in the 'watchlist_items' table.

    This table stores the ticker symbols that each user wants to monitor.
    Each row represents a single ticker in a user's watchlist.

    Columns:
    - id: Primary key integer (auto-incrementing)
    - user_id: Foreign key referencing users.id
      This links the watchlist item to its owner.
    - ticker: Uppercase symbol of the asset (e.g., "TSLA", "AAPL")
      Stored as uppercase string for consistency.
    - created_at: Timestamp when the asset was added to the watchlist

    Constraints:
    - (user_id, ticker) pair is unique to prevent duplicates
      This ensures a user cannot add the same ticker twice.
    - Foreign key constraint with CASCADE delete: if user is deleted,
      all their watchlist items are automatically deleted.

    Relationships:
    - user: Many-to-one relationship to UserSchema
      Each watchlist item belongs to exactly one user.

    Example Usage:
        user = User(id=1, username="demo_user", email="demo@example.com")
        item = WatchlistItem(id=1, user_id=1, ticker="TSLA")
        # This means user "demo_user" has TSLA in their watchlist
    """

    id: int
    user_id: int
    ticker: str
    created_at: datetime


# Database Schema Diagram (Text Representation)
"""
┌─────────────────┐
│     users       │
├─────────────────┤
│ id (PK)         │
│ username (UK)   │
│ email (UK)      │
│ created_at      │
└────────┬────────┘
         │
         │ 1:N
         │
         ▼
┌─────────────────┐
│ watchlist_items │
├─────────────────┤
│ id (PK)         │
│ user_id (FK)    │──┐
│ ticker          │  │
│ created_at      │  │
│                 │  │
│ (user_id,       │  │
│  ticker) (UK)   │  │
└─────────────────┘  │
                     │
                     │ References
                     │
                     └── users.id
"""
