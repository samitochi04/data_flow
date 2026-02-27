-- ============================================================================
-- USERS TABLE
-- ============================================================================
-- Base table for application users with authentication fields
-- This is the foundation for author_profiles and all user-related data

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'admin',
    is_active BOOLEAN NOT NULL DEFAULT true,
    last_login_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Index on email for faster lookups during authentication
-- CREATE INDEX idx_users_email ON users(email); # psql does it automatically no need to create it.

-- Index on is_active for user filtering
-- CREATE INDEX idx_users_is_active ON users(is_active);

-- ============================================================================
-- CATEGORIES TABLE
-- ============================================================================
-- Table for blog posts topic categories
-- Supports nested categories through parent_id self-reference

CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) NOT NULL UNIQUE,
    description TEXT NOT NULL,
    parent_id INTEGER REFERENCES categories(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- TOPIC_CLUSTERS TABLE
-- ============================================================================
-- Table for blog posts topic cluster as main guide
-- pillar_post is a forward reference to blog_posts(id) - will be added when blog_posts table is created

CREATE TABLE IF NOT EXISTS topic_clusters (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) NOT NULL UNIQUE,
    pillar_post INTEGER,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- MEDIA TABLE
-- ============================================================================
-- Images and media files

CREATE TABLE IF NOT EXISTS media (
    id SERIAL PRIMARY KEY,
    url VARCHAR(255) NOT NULL UNIQUE,
    type VARCHAR(255) NOT NULL,
    cdn_url VARCHAR(255) NOT NULL UNIQUE,
    alt_text TEXT NOT NULL,
    caption TEXT,
    mime_type VARCHAR(255) NOT NULL,
    size_bytes BIGINT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- TAGS TABLE
-- ============================================================================
-- Posts tags for content classification and filtering

CREATE TABLE IF NOT EXISTS tags (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- NEWSLETTER_SUBSCRIBERS TABLE
-- ============================================================================
-- Newsletter subscriptions tracking

CREATE TABLE IF NOT EXISTS newsletter_subscribers (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    source_page VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- AUTHOR_PROFILES TABLE
-- ============================================================================
-- Extended user profiles for content creators/authors
-- One-to-one relationship with users table

CREATE TABLE IF NOT EXISTS author_profiles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    bio TEXT,
    avatar_url VARCHAR(255),
    linkedin_url VARCHAR(255),
    expertise_topics TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- BLOG_POSTS TABLE
-- ============================================================================
-- Main blog posts table with comprehensive content and SEO fields
-- Dependencies: users (author), categories, topic_clusters, media

CREATE TABLE IF NOT EXISTS blog_posts (
    id SERIAL PRIMARY KEY,
    author_id INTEGER NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    category_id INTEGER NOT NULL REFERENCES categories(id) ON DELETE RESTRICT,
    topic_cluster_id INTEGER REFERENCES topic_clusters(id) ON DELETE SET NULL,
    pillar_post_id INTEGER REFERENCES blog_posts(id) ON DELETE SET NULL,
    featured_image_id INTEGER REFERENCES media(id) ON DELETE SET NULL,
    og_image_id INTEGER REFERENCES media(id) ON DELETE SET NULL,
    
    -- Basic content fields
    title VARCHAR(255) NOT NULL,
    slug VARCHAR(255) NOT NULL UNIQUE,
    excerpt TEXT,
    content_markdown TEXT NOT NULL,
    content_html TEXT NOT NULL,
    
    -- Featured image metadata
    featured_image_alt VARCHAR(255),
    featured_image_caption TEXT,
    
    -- Open Graph (Social share) fields
    og_title VARCHAR(255),
    og_description TEXT,
    
    -- Twitter card fields
    twitter_title VARCHAR(255),
    twitter_description TEXT,
    twitter_card_type VARCHAR(50),
    
    -- SEO fields
    meta_title VARCHAR(255),
    meta_description TEXT,
    focus_keyword VARCHAR(255),
    content_language VARCHAR(10) NOT NULL DEFAULT 'en',
    geo_target_country VARCHAR(2),
    
    -- Content metadata
    status VARCHAR(50) NOT NULL DEFAULT 'draft',
    reading_time_minutes INTEGER,
    word_count INTEGER,
    table_of_contents_enabled BOOLEAN DEFAULT true,
    ai_generated_flag BOOLEAN DEFAULT false,
    content_version INTEGER DEFAULT 1,
    last_updated_reason TEXT,
    
    -- Publishing fields
    published_at TIMESTAMP WITH TIME ZONE,
    scheduled_at TIMESTAMP WITH TIME ZONE,
    last_reviewed_at TIMESTAMP WITH TIME ZONE,
    
    -- Statistics (denormalized for performance)
    view_count INTEGER DEFAULT 0,
    like_count INTEGER DEFAULT 0,
    comment_count INTEGER DEFAULT 0,
    share_count INTEGER DEFAULT 0,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- POST_TAGS TABLE
-- ============================================================================
-- Junction table for many-to-many relationship between blog_posts and tags

CREATE TABLE IF NOT EXISTS post_tags (
    post_id INTEGER NOT NULL REFERENCES blog_posts(id) ON DELETE CASCADE,
    tag_id INTEGER NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (post_id, tag_id)
);

-- ============================================================================
-- COMMENTS TABLE
-- ============================================================================
-- Blog post comments with nested reply support (parent_id for nested threads)
-- Many-to-many: many comments per post, many replies per comment

CREATE TABLE IF NOT EXISTS comments (
    id SERIAL PRIMARY KEY,
    post_id INTEGER NOT NULL REFERENCES blog_posts(id) ON DELETE CASCADE,
    parent_id INTEGER REFERENCES comments(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    is_approved BOOLEAN DEFAULT false,
    like_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_comments_is_approved ON comments(is_approved);

-- ============================================================================
-- LIKES TABLE
-- ============================================================================
-- Likes can be on either blog_posts or comments (one must be set, other NULL)
-- Uses fingerprint_hash to track unique users without requiring auth

CREATE TABLE IF NOT EXISTS likes (
    id SERIAL PRIMARY KEY,
    post_id INTEGER REFERENCES blog_posts(id) ON DELETE CASCADE,
    comment_id INTEGER REFERENCES comments(id) ON DELETE CASCADE,
    fingerprint_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_like_target CHECK (
        (post_id IS NOT NULL AND comment_id IS NULL) OR
        (post_id IS NULL AND comment_id IS NOT NULL)
    ),
    CONSTRAINT unique_post_like UNIQUE (post_id, fingerprint_hash),
    CONSTRAINT unique_comment_like UNIQUE (comment_id, fingerprint_hash)
);

-- ============================================================================
-- REDIRECTS TABLE
-- ============================================================================
-- URL redirects for SEO - tracks old slugs to their new locations
-- Supports multiple redirect types (301 permanent, 302 temporary, etc)

CREATE TABLE IF NOT EXISTS redirects (
    id SERIAL PRIMARY KEY,
    old_slug VARCHAR(255) NOT NULL UNIQUE,
    new_slug VARCHAR(255) NOT NULL,
    redirect_type INTEGER NOT NULL DEFAULT 301,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- POST_ANALYTICS TABLE
-- ============================================================================
-- Aggregated analytics per post, calculated from post_views data
-- avg_time: average session duration in seconds
-- bounce_rate: percentage of users who left without interacting (scale 0-100)
-- last_calculated_at: timestamp when aggregates were last computed
-- This is updated by a backend scheduled job processing post_views records

CREATE TABLE IF NOT EXISTS post_analytics (
    post_id INTEGER PRIMARY KEY REFERENCES blog_posts(id) ON DELETE CASCADE,
    avg_time DECIMAL(10,2) DEFAULT 0,
    bounce_rate DECIMAL(5,2) DEFAULT 0,
    total_views INTEGER DEFAULT 0,
    last_calculated_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- POST_VIEWS TABLE
-- ============================================================================
-- Individual page view records tracked with fingerprint for anonymous users
-- duration_seconds: time spent on page
-- is_bounce: true if user left < 10 seconds without interaction
-- Data source for real-time analytics and post_analytics aggregation

CREATE TABLE IF NOT EXISTS post_views (
    id SERIAL PRIMARY KEY,
    post_id INTEGER NOT NULL REFERENCES blog_posts(id) ON DELETE CASCADE,
    fingerprint_hash VARCHAR(255) NOT NULL,
    referrer_url VARCHAR(255),
    user_agent VARCHAR(255),
    country_code VARCHAR(2),
    device_type VARCHAR(50),
    is_bounce BOOLEAN DEFAULT false,
    duration_seconds INTEGER NOT NULL,
    started_at TIMESTAMP WITH TIME ZONE NOT NULL,
    ended_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for analytics queries and aggregation
CREATE INDEX IF NOT EXISTS idx_post_views_post_id ON post_views(post_id);
CREATE INDEX IF NOT EXISTS idx_post_views_created_at ON post_views(created_at);
CREATE INDEX IF NOT EXISTS idx_post_views_fingerprint ON post_views(fingerprint_hash);
CREATE INDEX IF NOT EXISTS idx_post_views_post_created ON post_views(post_id, created_at);