"""
Helper script to generate hashed passwords for streamlit-authenticator.

Usage:
    python generate_password_hash.py

This script will prompt you for a password and generate a bcrypt hash
that can be used in config.yaml for authentication.
"""

import streamlit_authenticator as stauth
import getpass


def main():
    """
    Generate a hashed password for use in config.yaml.
    """
    print("=" * 60)
    print("Password Hash Generator for Portfolio Watchdog")
    print("=" * 60)
    print()

    # Get password from user (hidden input)
    password = getpass.getpass("Enter password to hash: ")

    if not password:
        print("Error: Password cannot be empty.")
        return

    # Confirm password
    password_confirm = getpass.getpass("Confirm password: ")

    if password != password_confirm:
        print("Error: Passwords do not match.")
        return

    # Generate hash
    try:
        hasher = stauth.Hasher([password])
        hashed = hasher.generate()
        hash_string = hashed[0]

        print()
        print("=" * 60)
        print("SUCCESS! Copy the hash below to your config.yaml:")
        print("=" * 60)
        print()
        print(f'password: "{hash_string}"')
        print()
        print("=" * 60)
        print("Example config.yaml entry:")
        print("=" * 60)
        print()
        print("credentials:")
        print("  usernames:")
        print("    your_username:")
        print("      email: your@email.com")
        print("      name: Your Name")
        print(f'      password: "{hash_string}"')
        print()

    except Exception as e:
        print(f"Error generating hash: {e}")


if __name__ == "__main__":
    main()
