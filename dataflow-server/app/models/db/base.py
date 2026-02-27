from app.core.database import Base  # noqa: F401

# Import all models here to register them with SQLAlchemy
from app.models.db.user_model import User  # noqa: F401
from app.models.db.category_model import Category  # noqa: F401
from app.models.db.topic_cluster_model import TopicCluster  # noqa: F401
from app.models.db.media_model import Media  # noqa: F401
from app.models.db.tag_model import Tag  # noqa: F401
from app.models.db.newsletter_subscriber_model import NewsletterSubscriber  # noqa: F401
from app.models.db.author_profile_model import AuthorProfile  # noqa: F401
from app.models.db.blog_post_model import BlogPost  # noqa: F401
from app.models.db.post_tag_model import PostTag  # noqa: F401
from app.models.db.comment_model import Comment  # noqa: F401
from app.models.db.like_model import Like  # noqa: F401
from app.models.db.post_analytic_model import PostAnalytic  # noqa: F401
from app.models.db.post_view_model import PostView  # noqa: F401
from app.models.db.redirect_model import Redirect  # noqa: F401