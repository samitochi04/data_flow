# Data FLow Server Structure

dataflow-server/
│
├── app/
│   ├── main.py
│
│   ├── core/
│   │   ├── config.py          # env + settings
│   │   ├── database.py        # DB engine + session
│   │   ├── security.py
│   │   └── logging.py
│
│   ├── api/
│   │   ├── routes/
|   |   |   ├── __init__.py
|   |   |   ├── user_routes.py
|   |   |   ├── auth_routes.py
│   │   │   ├── health_routes.py
│   │   │   ├── post_routes.py
│   │   │   └── comment_routes.py
│   │   │
│   │   └── controllers/
│   │       ├── __init__.py
│   │       ├── user_controller.py
│   │       ├── auth_controller.py
│   │       ├── post_controller.py
│   │       └── comment_controller.py
│
│   ├── services/
│   │   ├── __init__.py
│   │   ├── user_service.py
│   │   ├── auth_service.py
│   │   ├── post_service.py
│   │   └── comment_service.py
│
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── user_repository.py
│   │   ├── post_repository.py
│   │   └── comment_repository.py
│
│   ├── models/
|   |   ├── __init__.py
│   │   ├── db/
│   │   │   ├── base.py
│   │   │   ├── post_model.py
│   │   │   ├── comment_model.py
│   │   │   └── user_model.py
│   │   │
│   │   └── schemas/
│   │       ├── user_schema.py
│   │       ├── auth_schema.py
│   │       ├── post_schema.py
│   │       └── comment_schema.py
│
│   ├── middleware/
|   |   └── request_logger.py
│   └── utils/
│       ├── helpers.py
│       └── validators.py
│
├── migrations/                # Alembic later
│
├── tests/
|   ├── test_users.py
|   └── test_auth.py
│
├── .env
├── .env.example
├── Dockerfile
├── docker-compose.yml
└── requirements.txt


# Database ER Diagram

┌──────────────┐
│    users     │
├──────────────┤
│ id (PK)      │
│ name         │
│ email        │
│ password     │
│ role         │
│ is_active    │
│ last_login_at│
│ created_at   │
└──────┬───────┘
       │ 1
       │
       │ 1
┌──────▼──────────────┐
│  author_profiles    │
├─────────────────────┤
│ id (PK)             │
│ user_id (FK)        │
│ bio                 │
│ avatar_url          │
│ linkedin_url        │
│ expertise_topics    │
└─────────┬───────────┘
          │
          │ 1
          │
          │ N
┌─────────▼───────────────────┐
│       blog_posts            │
├─────────────────────────────┤
│ id (PK)                     │
│ author_id (FK)              │
│ category_id (FK)            │
│ topic_cluster_id (FK)       │ # group posts by topic
│ pillar_post_id (FK self)    │ # main guide post
│ featured_image_id (FK)      │
│ featured_image_alt          │
│ featured_image_caption      │
│ og_image_id                 │ # Share Details Starts
│ og_title                    │ -
│ og_description              │ -
│ twitter_title               │ -
│ twitter_description         │ -
│ twitter_card_type           │ # Share Details Ends
│ title                       │
│ slug                        │ # URL path (data-pipeline-best-practices)
│ content_html                │ # rendered article
│ content_markdown            │ # editor format
│ excerpt                     │ # Short summary
│ status                      │
│ published_at                │
│ scheduled_at                │
│ meta_title                  │ # search result title
│ meta_description            │ # search snippet
│ focus_keyword               │ # main keyword
│ reading_time_minutes        │
│ table_of_contents_enabled   │ # show TOC
│ last_reviewed_at            │ # Changes Review
│ content_version             │ -
│ last_updated_reason         │ -
│ content_language            │
│ geo_target_country          │
│ ai_generated_flag           │
│ word_count                  │
│ view_count                  │
│ like_count                  │
│ comment_count               │
│ share_count                 │
└───────┬─────────┬────────────┬────────────┬─────────────┐
        │         │            │            │
        │         │            │            │
        │         │            │            │
       N│        N│           N│           N│
        │         │            │            │
        │         │            │            │
┌───────▼───┐ ┌───▼────────┐ ┌─▼──────────┐ ┌─────────────────────┐
│ comments  │ │ post_tags  │ │ redirects  │ │ post_analytics      │
├───────────┤ ├────────────┤ ├────────────┤ ├─────────────────────┤
│ id (PK)   │ │ post_id FK │ │ id (PK)    │ │ post_id (PK)        │
│ post_id FK│ │ tag_id FK  │ │ old_slug   │ │ avg_time            │
│ parent_id │ └──────┬─────┘ │ new_slug   │ │ bounce_rate         │ # left <10s
│ name      │        │       │ type       │ | last_calculated_at  |
│ email     │        │       └────────────┘ └─────────────────────┘
│ content   │        │       redirect_type — 301 permanent
│ is_approved│       │
│ like_count│        │
│ created_at|        │
└─────┬─────┘        │
      │              │
     N│             N│
      │              │
┌─────▼─────┐   ┌────▼─────┐
│   likes   │   │   tags   │
├───────────┤   ├──────────┤
│ id (PK)   │   │ id (PK)  │
│ post_id FK│   │ name     │
│ comment FK│   │ slug     │
│ created_at|   └──────────┘
| fingerprint_hash|
└───────────┘


┌──────────────┐
│ categories   │
├──────────────┤
│ id (PK)      │
│ name         │
│ slug         │
│ description  │
│ parent_id FK │
└──────┬───────┘
       │ 1
       │
       │ N
       ▼
  blog_posts


┌──────────────┐
│topic_clusters│
├──────────────┤
│ id (PK)      │
│ name         │
│ slug         │
│ pillar_post  │
└──────┬───────┘
       │ 1
       │
       │ N
       ▼
   blog_posts


┌──────────────┐
│    media     │
├──────────────┤
│ id (PK)      │
│ url          │
│ type         │
│ cdn_url      │ # optimized delivery
│ alt_text     │
│ caption      │
│ mime_type    │
│ size_bytes   │
│ created_at   │
└──────┬───────┘
       │
       │ N
       ▼
   blog_posts


┌──────────────────────┐
│newsletter_subscribers│
├──────────────────────┤
│ id (PK)              │
│ email                │
│ source_page          │
│ created_at           │
└──────────────────────┘


┌──────────────────────────┐
│       post_views         │
├──────────────────────────┤
│ id (PK)                  │
│ post_id (FK)             │
│ fingerprint_hash         │
│ started_at               │
│ ended_at                 │
│ duration_seconds         │
│ user_agent               │
│ referrer_url             │
│ country_code             │
│ device_type              │
│ is_bounce                │
└──────────────┬───────────┘
               │
               │ N
               │
               │ 1
               ▼
         blog_posts
