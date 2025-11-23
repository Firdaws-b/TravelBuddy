import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # adds src/
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))  # adds project root

from models.admin_model import AdminModel
from config.databse import admins_collection
import secrets


def create_admin(name: str):
    api_key = secrets.token_urlsafe(32)
    admin = AdminModel(name=name, api_key=api_key )
    save_admin_to_db(admin)
    print(f"Admin '{name}' created successfully!")
    print("Give this API key to the agency — keep it secret!")
    print(f"API Key Generated{api_key}")


def save_admin_to_db(admin):
    admins_collection.insert_one(admin.model_dump())

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python create_admin.py 'Agency Name'")
        sys.exit(1)
    agency_name = sys.argv[1]
    create_admin(agency_name)
