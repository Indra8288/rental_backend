from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.core.config import settings
from app.crud.user import get_by_username, create_user
from app.models.enums import Role

def main():
    init_db()
    db = SessionLocal()
    try:
        if get_by_username(db, settings.SEED_OWNER_USERNAME):
            print("Owner already exists")
            return
        u = create_user(
            db,
            user_name=settings.SEED_OWNER_USERNAME,
            password=settings.SEED_OWNER_PASSWORD,
            role=settings.SEED_OWNER_ROLE,
        )
        print(f"Created owner user: {u.user_name} role={u.role}")
    finally:
        db.close()

if __name__ == "__main__":
    main()
