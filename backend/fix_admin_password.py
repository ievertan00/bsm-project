import os
import sys

# Add the backend directory to the Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

from app import app
from models import db, User

def update_admin_password(new_password):
    """Finds the 'admin' user and updates their password."""
    with app.app_context():
        admin_user = User.query.filter_by(username='admin').first()

        if not admin_user:
            print("User 'admin' not found.")
            return

        print(f"Found user 'admin'. Updating password...")
        admin_user.set_password(new_password)
        db.session.add(admin_user)
        db.session.commit()
        print("Password for 'admin' has been updated successfully.")

# Set the new password here
new_admin_password = "1234"
update_admin_password(new_admin_password)
