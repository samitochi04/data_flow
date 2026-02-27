from app.core.database import Base  # noqa: F401

# Import all models here to register them with SQLAlchemy
from app.models.db.user_model import User # noqa: F401

# TODO: Add other models as they are created
# from app.models.db.post_model import Post
# from app.models.db.comment_model import Comment