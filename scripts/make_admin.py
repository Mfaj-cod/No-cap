#!/usr/bin/env python
import sys
sys.path.insert(0, '.')

from src.db import get_user_by_email, create_user, get_connection
from src.security import hash_password

email = 'fajalmoaj@gmail.com'
user = get_user_by_email(email)

if user:
    print(f"User exists: {user.get('name')} ({user.get('role')})")
    # Update to admin role if not already
    conn = get_connection()
    conn.execute("UPDATE users SET role = 'admin' WHERE email = ?", (email,))
    conn.commit()
    conn.close()
    print(f"Updated {email} to admin role")
else:
    # Create new admin user
    create_user('Admin', email, hash_password('admin123'), 'admin')
    print(f"Created admin user: {email}")
    print("Default password: admin123 (please change after login)")
