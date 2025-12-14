# Login Information

## Default Credentials

The `config.yaml` file has been created with the following default credentials:

**Username:** `admin`  
**Password:** `admin123`  
**Email:** `admin@portfolio-watchdog.com`

## ⚠️ Security Note

**IMPORTANT:** These are default credentials for development only!

For production use:
1. Change the password immediately
2. Use a strong, unique password
3. Update the cookie key to a random secret
4. Add additional users as needed

## Changing the Password

### Option 1: Using Python

```python
import bcrypt

password = b'your_new_password'
hashed = bcrypt.hashpw(password, bcrypt.gensalt())
print(hashed.decode())
```

Then update `config.yaml` with the new hash.

### Option 2: Using the Helper Script

```bash
python generate_password_hash.py
```

(Note: The script may need updating for the current streamlit-authenticator version)

## Adding More Users

Edit `config.yaml` and add entries under `credentials.usernames`:

```yaml
credentials:
  usernames:
    admin:
      email: admin@portfolio-watchdog.com
      name: Admin User
      password: "$2b$12$..."
    another_user:
      email: user@example.com
      name: Another User
      password: "$2b$12$..."
```

## Cookie Key

The cookie key is used for session management. For production, generate a new random key:

```python
import secrets
print(secrets.token_urlsafe(32))
```

Update the `cookie.key` value in `config.yaml`.

## Testing Login

1. Run the app: `streamlit run app.py`
2. Navigate to the login page
3. Enter:
   - Username: `admin`
   - Password: `admin123`

You should now be able to access the dashboard!

