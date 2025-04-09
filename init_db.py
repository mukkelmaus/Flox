
from app.db.base import Base
from app.db.session import engine
from app.core.config import settings
from app.models.user import User
from sqlalchemy.orm import Session

def init_db():
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Create initial admin user
    db = Session(engine)
    try:
        user = db.query(User).filter(User.email == settings.FIRST_SUPERUSER_EMAIL).first()
        if not user:
            user = User(
                email=settings.FIRST_SUPERUSER_EMAIL,
                username=settings.FIRST_SUPERUSER,
                is_superuser=True,
            )
            user.set_password(settings.FIRST_SUPERUSER_PASSWORD)
            db.add(user)
            db.commit()
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
