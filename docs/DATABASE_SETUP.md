# Database Setup Guide

## Quick Start (SQLite - No Setup Required!)

The app **defaults to SQLite** for easy development. No database setup needed!

Just run:
```bash
streamlit run app.py
```

The database file `portfolio_watchdog.db` will be created automatically in your project directory.

## Database Options

### Option 1: SQLite (Default - Recommended for Development)

**Pros:**
- ✅ No setup required
- ✅ Works out of the box
- ✅ Perfect for development and testing
- ✅ Single file database
- ✅ No server needed

**Cons:**
- ⚠️ Not ideal for production with high concurrency
- ⚠️ Limited to single server deployment

**Usage:**
```bash
# No configuration needed - just run the app!
streamlit run app.py
```

The database file `portfolio_watchdog.db` will be created automatically.

### Option 2: PostgreSQL (Recommended for Production)

**Pros:**
- ✅ Production-ready
- ✅ Handles concurrent users
- ✅ Better performance at scale
- ✅ Advanced features

**Cons:**
- ⚠️ Requires PostgreSQL installation
- ⚠️ Needs configuration

**Setup Steps:**

1. **Install PostgreSQL** (if not already installed):
   ```bash
   # macOS
   brew install postgresql@15
   brew services start postgresql@15
   
   # Ubuntu/Debian
   sudo apt-get install postgresql postgresql-contrib
   sudo systemctl start postgresql
   ```

2. **Create Database and User**:
   ```sql
   -- Connect to PostgreSQL
   psql postgres
   
   -- Create database and user
   CREATE DATABASE portfolio_watchdog;
   CREATE USER watchdog_user WITH PASSWORD 'your_secure_password';
   GRANT ALL PRIVILEGES ON DATABASE portfolio_watchdog TO watchdog_user;
   \q
   ```

3. **Set Environment Variable**:
   ```bash
   # Linux/macOS
   export DATABASE_URL="postgresql://watchdog_user:your_secure_password@localhost:5432/portfolio_watchdog"
   
   # Windows (PowerShell)
   $env:DATABASE_URL="postgresql://watchdog_user:your_secure_password@localhost:5432/portfolio_watchdog"
   
   # Or create .env file
   echo 'DATABASE_URL=postgresql://watchdog_user:your_secure_password@localhost:5432/portfolio_watchdog' > .env
   ```

4. **Run the App**:
   ```bash
   streamlit run app.py
   ```

## Database Schema

The app automatically creates these tables:

### `users` Table
- `id` (Primary Key)
- `username` (Unique, indexed)
- `email` (Unique, nullable)
- `created_at` (Timestamp)

### `watchlist_items` Table
- `id` (Primary Key)
- `user_id` (Foreign Key → users.id)
- `ticker` (String, uppercase)
- `created_at` (Timestamp)
- Unique constraint on (`user_id`, `ticker`)

## Troubleshooting

### "role 'user' does not exist"
**Solution**: Use SQLite (default) or set proper DATABASE_URL:
```bash
export DATABASE_URL="sqlite:///portfolio_watchdog.db"
```

### "connection refused"
**Solution**: 
- Check if PostgreSQL is running: `brew services list` (macOS) or `sudo systemctl status postgresql` (Linux)
- Verify connection string format
- Check firewall settings

### "database does not exist"
**Solution**: Create the database:
```sql
CREATE DATABASE portfolio_watchdog;
```

### SQLite Lock Errors
**Solution**: 
- Ensure only one instance of the app is running
- For production, use PostgreSQL instead

## Migration from SQLite to PostgreSQL

1. Export data from SQLite (if needed):
   ```bash
   sqlite3 portfolio_watchdog.db .dump > backup.sql
   ```

2. Set DATABASE_URL to PostgreSQL:
   ```bash
   export DATABASE_URL="postgresql://user:pass@host:5432/portfolio_watchdog"
   ```

3. Run the app - tables will be created automatically

4. Import data if needed (manual process for this MVP)

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///portfolio_watchdog.db` | Database connection string |

**Connection String Formats:**
- SQLite: `sqlite:///portfolio_watchdog.db`
- PostgreSQL: `postgresql://user:password@host:port/database`
- Remote PostgreSQL: `postgresql://user:password@remote-host:5432/database`

## Best Practices

1. **Development**: Use SQLite (default) - no setup needed
2. **Production**: Use PostgreSQL for better performance and reliability
3. **Backup**: Regularly backup your database
4. **Security**: Never commit database files or connection strings to version control

## Notes

- Tables are created automatically on first run
- No migrations needed for this MVP
- Database file is gitignored (won't be committed)
- All database operations are handled automatically

