# DataFlow Database

## Step-by-Step Database Schema Creation Guide

Here's the complete order to create tables without dependency issues:

### **Phase 1: Independent Tables (No Dependencies)**
1. **users** - Base application users
2. **categories** - Blog post categories
3. **topic_clusters** - Topic grouping system
4. **media** - Images and media files
5. **tags** - Blog post tags
6. **newsletter_subscribers** - Newsletter system

### **Phase 2: Dependent Tables**
7. **author_profiles** - Depends on users
8. **blog_posts** - Depends on users, categories, topic_clusters, media
9. **post_tags** - Depends on blog_posts, tags (junction table)
10. **comments** - Depends on blog_posts
11. **likes** - Depends on blog_posts, comments
12. **redirects** - Independent, should be before post analytics
13. **post_analytics** - Depends on blog_posts
14. **post_views** - Depends on blog_posts

---

## Users Table - Implementation

### Table Details

| Field | Data Type | Constraints | Purpose |
|-------|-----------|-------------|---------|
| **id** | SERIAL | PRIMARY KEY | Auto-incrementing unique identifier |
| **name** | VARCHAR(255) | NOT NULL | User's full name |
| **email** | VARCHAR(255) | NOT NULL, UNIQUE | Email for login (unique constraint) |
| **password** | VARCHAR(255) | NOT NULL | Hashed password |
| **role** | VARCHAR(50) | DEFAULT 'user' | User role (e.g., admin, editor, user) |
| **is_active** | BOOLEAN | DEFAULT true | Account status flag |
| **last_login_at** | TIMESTAMP WITH TIME ZONE | NULL allowed | Track last login time |
| **created_at** | TIMESTAMP WITH TIME ZONE | DEFAULT CURRENT_TIMESTAMP | Account creation time |

---

## Managing Your Database

### **1. DELETE the Users Table from Docker Container**

```bash
# Open PostgreSQL CLI in Docker container
docker exec -it dataflow_db psql -U your_postgres_user -d your_database_name
i.e : docker exec -it dataflow_db psql -U dataflow_user -d dataflow

# Inside PostgreSQL prompt:
DROP TABLE IF EXISTS users;

# To verify it's deleted:
\dt  -- Lists all tables (users should not appear)

# Exit PostgreSQL:
\q
```

---

### **2. ADD the Users Table to Your Database**

```bash
# Option A: Using SQL file (RECOMMENDED)
docker exec -i dataflow_db psql -U your_postgres_user -d your_database_name < /path/to/schema.sql

# Option B: Direct command (if file is small)
docker exec -it dataflow_db psql -U your_postgres_user -d your_database_name -f /schema.sql

# Option C: Copy file into container first, then execute
docker cp schema.sql dataflow_db:/schema.sql
docker exec -it dataflow_db psql -U your_postgres_user -d your_database_name -f /schema.sql
```

**For your setup**, use:
```powershell
Get-Content .\dataflow-database\schema.sql | docker exec -i dataflow_db psql -U dataflow_user -d dataflow
```

---

### **3. TEST the Users Table**

#### **A. Connect to the Database**
```bash
docker exec -it dataflow_db psql -U postgres -d dataflow_db
```

#### **B. INSERT Test Data**
```sql
INSERT INTO users (name, email, password, role, is_active)
VALUES 
    ('John Doe', 'john@example.com', 'hashed_password_123', 'admin', true),
    ('Jane Smith', 'jane@example.com', 'hashed_password_456', 'editor', true),
    ('Bob Johnson', 'bob@example.com', 'hashed_password_789', 'admin', false);

-- Verify inserts
SELECT * FROM users;
```

#### **C. UPDATE Test Data**
```sql
-- Update a user's role
UPDATE users
SET role = 'editor'
WHERE email = 'bob@example.com';

-- Update last login
UPDATE users
SET last_login_at = CURRENT_TIMESTAMP
WHERE id = 1;

-- Verify updates
SELECT id, email, role, last_login_at FROM users;
```

#### **D. DELETE Test Data**
```sql
-- Delete a specific user
DELETE FROM users
WHERE email = 'bob@example.com';

-- Verify deletion
SELECT * FROM users;
```

#### **E. Verify Table Structure**
```sql
-- View table definition
\d users

-- View all indexes on the table
\di users*

-- View table statistics
SELECT COUNT(*) FROM users;
```

---

---

## Categories Table - Implementation

### Table Details

| Field | Data Type | Constraints | Purpose |
|-------|-----------|-------------|---------|
| **id** | SERIAL | PRIMARY KEY | Auto-incrementing unique identifier |
| **name** | VARCHAR(255) | NOT NULL | Category name |
| **slug** | VARCHAR(255) | NOT NULL, UNIQUE | URL-friendly identifier |
| **description** | TEXT | NOT NULL | Category description |
| **parent_id** | INTEGER | FK to categories(id), ON DELETE CASCADE | For nested/hierarchical categories |
| **created_at** | TIMESTAMP WITH TIME ZONE | DEFAULT CURRENT_TIMESTAMP | Category creation time |

**Note:** The `parent_id` field allows for recursive/nested categories (e.g., "Technology > Data Pipeline > Best Practices"). When a parent category is deleted, all child categories are also deleted due to `ON DELETE CASCADE`.

---

## Managing Categories Table

### **1. DELETE the Categories Table from Docker Container**

```bash
# Open PostgreSQL CLI in Docker container
docker exec -it dataflow_db psql -U dataflow_user -d dataflow

# Inside PostgreSQL prompt:
DROP TABLE IF EXISTS categories;

# To verify it's deleted:
\dt

# Exit PostgreSQL:
\q
```

---

### **2. ADD the Categories Table to Your Database**

```powershell
# Using the same schema.sql file
Get-Content .\dataflow-database\schema.sql | docker exec -i dataflow_db psql -U dataflow_user -d dataflow
```

---

### **3. TEST the Categories Table**

#### **A. Connect to the Database**
```bash
docker exec -it dataflow_db psql -U dataflow_user -d dataflow
```

#### **B. INSERT Test Data (Nested Categories)**
```sql
-- Create parent categories
INSERT INTO categories (name, slug, description)
VALUES 
    ('Technology', 'technology', 'All technology related posts'),
    ('Business', 'business', 'Business insights and news'),
    ('Lifestyle', 'lifestyle', 'Lifestyle tips and tricks');

-- Create child categories (nested under Technology)
INSERT INTO categories (name, slug, description, parent_id)
VALUES 
    ('Data Pipeline', 'data-pipeline', 'Data pipeline best practices', 1),
    ('Machine Learning', 'machine-learning', 'ML models and techniques', 1),
    ('Cloud Computing', 'cloud-computing', 'Cloud infrastructure', 1);

-- Verify inserts
SELECT * FROM categories;

-- View hierarchical structure
SELECT id, name, slug, parent_id, created_at 
FROM categories 
ORDER BY parent_id ASC NULLS FIRST;
```

#### **C. UPDATE Test Data**
```sql
-- Update a category description
UPDATE categories
SET description = 'Advanced data pipeline techniques and best practices'
WHERE slug = 'data-pipeline';

-- Verify update
SELECT * FROM categories WHERE slug = 'data-pipeline';
```

#### **D. DELETE Test Data**
```sql
-- Delete a child category
DELETE FROM categories
WHERE slug = 'machine-learning';

-- Verify deletion
SELECT * FROM categories WHERE parent_id = 1;

-- DELETE a parent category (will cascade delete children)
DELETE FROM categories
WHERE slug = 'technology';

-- Verify parent and children are deleted
SELECT * FROM categories;
```

#### **E. Verify Table Structure**
```sql
-- View table definition
\d categories

-- View all categories with parent info
SELECT 
    c.id, 
    c.name, 
    c.slug, 
    c.parent_id,
    p.name as parent_name,
    c.created_at
FROM categories c
LEFT JOIN categories p ON c.parent_id = p.id
ORDER BY c.parent_id ASC NULLS FIRST, c.name;

-- Count categories
SELECT COUNT(*) as total_categories FROM categories;
```

---

---

## Topic_Clusters Table - Implementation

### Table Details

| Field | Data Type | Constraints | Purpose |
|-------|-----------|-------------|---------|
| **id** | SERIAL | PRIMARY KEY | Auto-incrementing unique identifier |
| **name** | VARCHAR(255) | NOT NULL | Cluster name |
| **slug** | VARCHAR(255) | NOT NULL, UNIQUE | URL-friendly identifier |
| **pillar_post** | INTEGER | Nullable | Forward reference to blog_posts(id) - main guide post |
| **created_at** | TIMESTAMP WITH TIME ZONE | DEFAULT CURRENT_TIMESTAMP | Cluster creation time |

**Note:** `pillar_post` is a forward reference to the `blog_posts` table (created in Phase 2). It identifies the main pillar/guide post for this topic cluster.

---

## Managing Topic_Clusters Table

### **1. DELETE the Topic_Clusters Table**

```bash
docker exec -it dataflow_db psql -U dataflow_user -d dataflow

# Inside PostgreSQL prompt:
DROP TABLE IF EXISTS topic_clusters;
\q
```

---

### **2. ADD the Topic_Clusters Table**

```powershell
Get-Content .\dataflow-database\schema.sql | docker exec -i dataflow_db psql -U dataflow_user -d dataflow
```

---

### **3. TEST the Topic_Clusters Table**

#### **A. Connect to the Database**
```bash
docker exec -it dataflow_db psql -U dataflow_user -d dataflow
```

#### **B. INSERT Test Data**
```sql
INSERT INTO topic_clusters (name, slug)
VALUES 
    ('Data Engineering', 'data-engineering'),
    ('Machine Learning Ops', 'ml-ops'),
    ('Cloud Architecture', 'cloud-architecture');

-- Verify inserts
SELECT * FROM topic_clusters;
```

#### **C. UPDATE Test Data**
```sql
-- Update a cluster name
UPDATE topic_clusters
SET name = 'Advanced Data Engineering'
WHERE slug = 'data-engineering';

-- Verify update
SELECT * FROM topic_clusters WHERE slug = 'data-engineering';
```

#### **D. DELETE Test Data**
```sql
DELETE FROM topic_clusters
WHERE slug = 'ml-ops';

-- Verify deletion
SELECT COUNT(*) as total_clusters FROM topic_clusters;
```

#### **E. Verify Table Structure**
```sql
\d topic_clusters
SELECT * FROM topic_clusters ORDER BY created_at DESC;
```

---

## Media Table - Implementation

### Table Details

| Field | Data Type | Constraints | Purpose |
|-------|-----------|-------------|---------|
| **id** | SERIAL | PRIMARY KEY | Auto-incrementing unique identifier |
| **url** | VARCHAR(255) | NOT NULL, UNIQUE | Original upload URL |
| **type** | VARCHAR(255) | NOT NULL | Media type (image, video, document, etc.) |
| **cdn_url** | VARCHAR(255) | NOT NULL, UNIQUE | Optimized CDN delivery URL |
| **alt_text** | TEXT | NOT NULL | SEO-friendly alt text |
| **caption** | TEXT | Nullable | Image caption or description |
| **mime_type** | VARCHAR(255) | NOT NULL | File MIME type (image/jpeg, video/mp4, etc.) |
| **size_bytes** | BIGINT | NOT NULL | File size in bytes |
| **created_at** | TIMESTAMP WITH TIME ZONE | DEFAULT CURRENT_TIMESTAMP | Upload time |

---

## Managing Media Table

### **1. DELETE the Media Table**

```bash
docker exec -it dataflow_db psql -U dataflow_user -d dataflow

# Inside PostgreSQL prompt:
DROP TABLE IF EXISTS media;
\q
```

---

### **2. ADD the Media Table**

```powershell
Get-Content .\dataflow-database\schema.sql | docker exec -i dataflow_db psql -U dataflow_user -d dataflow
```

---

### **3. TEST the Media Table**

#### **A. Connect to the Database**
```bash
docker exec -it dataflow_db psql -U dataflow_user -d dataflow
```

#### **B. INSERT Test Data**
```sql
INSERT INTO media (url, type, cdn_url, alt_text, mime_type, size_bytes)
VALUES 
    ('https://storage.example.com/image1.jpg', 'image', 'https://cdn.example.com/image1.jpg', 'Data pipeline diagram', 'image/jpeg', 256000),
    ('https://storage.example.com/video1.mp4', 'video', 'https://cdn.example.com/video1.mp4', 'ML tutorial video', 'video/mp4', 5242880),
    ('https://storage.example.com/doc1.pdf', 'document', 'https://cdn.example.com/doc1.pdf', 'Architecture guide PDF', 'application/pdf', 1024000);

-- Verify inserts
SELECT id, type, url, size_bytes FROM media;
```

#### **C. UPDATE Test Data**
```sql
-- Update media caption
UPDATE media
SET caption = 'Updated: Complete data pipeline architecture with error handling'
WHERE url = 'https://storage.example.com/image1.jpg';

-- Verify update
SELECT url, caption FROM media WHERE type = 'image';
```

#### **D. DELETE Test Data**
```sql
-- Delete a media file
DELETE FROM media
WHERE type = 'document';

-- Verify deletion
SELECT COUNT(*) as total_media FROM media;
```

#### **E. Verify Table Structure**
```sql
\d media

-- View media by type
SELECT type, COUNT(*) as count, SUM(size_bytes) as total_size 
FROM media 
GROUP BY type;

-- View all media with size in MB
SELECT id, type, url, size_bytes / 1048576.0 as size_mb 
FROM media 
ORDER BY created_at DESC;
```

---

## Tags Table - Implementation

### Table Details

| Field | Data Type | Constraints | Purpose |
|-------|-----------|-------------|---------|
| **id** | SERIAL | PRIMARY KEY | Auto-incrementing unique identifier |
| **name** | VARCHAR(255) | NOT NULL | Tag display name |
| **slug** | VARCHAR(255) | NOT NULL, UNIQUE | URL-friendly identifier |
| **created_at** | TIMESTAMP WITH TIME ZONE | DEFAULT CURRENT_TIMESTAMP | Tag creation time |

---

## Managing Tags Table

### **1. DELETE the Tags Table**

```bash
docker exec -it dataflow_db psql -U dataflow_user -d dataflow

# Inside PostgreSQL prompt:
DROP TABLE IF EXISTS tags;
\q
```

---

### **2. ADD the Tags Table**

```powershell
Get-Content .\dataflow-database\schema.sql | docker exec -i dataflow_db psql -U dataflow_user -d dataflow
```

---

### **3. TEST the Tags Table**

#### **A. Connect to the Database**
```bash
docker exec -it dataflow_db psql -U dataflow_user -d dataflow
```

#### **B. INSERT Test Data**
```sql
INSERT INTO tags (name, slug)
VALUES 
    ('Data Pipeline', 'data-pipeline'),
    ('Performance Optimization', 'performance-optimization'),
    ('Best Practices', 'best-practices'),
    ('Scalability', 'scalability'),
    ('Monitoring', 'monitoring');

-- Verify inserts
SELECT * FROM tags ORDER BY created_at;
```

#### **C. UPDATE Test Data**
```sql
-- Update tag name
UPDATE tags
SET name = 'Performance & Optimization'
WHERE slug = 'performance-optimization';

-- Verify update
SELECT * FROM tags WHERE slug = 'performance-optimization';
```

#### **D. DELETE Test Data**
```sql
-- Delete a tag
DELETE FROM tags
WHERE slug = 'monitoring';

-- Verify deletion
SELECT COUNT(*) as total_tags FROM tags;
```

#### **E. Verify Table Structure**
```sql
\d tags

-- List all tags
SELECT id, name, slug FROM tags ORDER BY name;

-- Count total tags
SELECT COUNT(*) as total_tags FROM tags;
```

---

## Newsletter_Subscribers Table - Implementation

### Table Details

| Field | Data Type | Constraints | Purpose |
|-------|-----------|-------------|---------|
| **id** | SERIAL | PRIMARY KEY | Auto-incrementing unique identifier |
| **email** | VARCHAR(255) | NOT NULL, UNIQUE | Subscriber email address |
| **source_page** | VARCHAR(255) | NOT NULL | Page where signup occurred |
| **created_at** | TIMESTAMP WITH TIME ZONE | DEFAULT CURRENT_TIMESTAMP | Subscription time |

---

## Managing Newsletter_Subscribers Table

### **1. DELETE the Newsletter_Subscribers Table**

```bash
docker exec -it dataflow_db psql -U dataflow_user -d dataflow

# Inside PostgreSQL prompt:
DROP TABLE IF EXISTS newsletter_subscribers;
\q
```

---

### **2. ADD the Newsletter_Subscribers Table**

```powershell
Get-Content .\dataflow-database\schema.sql | docker exec -i dataflow_db psql -U dataflow_user -d dataflow
```

---

### **3. TEST the Newsletter_Subscribers Table**

#### **A. Connect to the Database**
```bash
docker exec -it dataflow_db psql -U dataflow_user -d dataflow
```

#### **B. INSERT Test Data**
```sql
INSERT INTO newsletter_subscribers (email, source_page)
VALUES 
    ('alice@example.com', '/blog/data-pipeline'),
    ('bob@example.com', '/homepage'),
    ('charlie@example.com', '/blog/ml-ops'),
    ('diana@example.com', '/resources');

-- Verify inserts
SELECT * FROM newsletter_subscribers ORDER BY created_at DESC;
```

#### **C. UPDATE Test Data**
```sql
-- Note: Email is UNIQUE, so you can't update to an existing email
-- You can only update source_page if needed
-- In practice, newsletter management usually involves DELETE and INSERT instead

-- Verify current subscribers
SELECT COUNT(*) as total_subscribers FROM newsletter_subscribers;
```

#### **D. DELETE Test Data**
```sql
-- Unsubscribe a user
DELETE FROM newsletter_subscribers
WHERE email = 'bob@example.com';

-- Verify deletion
SELECT COUNT(*) as remaining_subscribers FROM newsletter_subscribers;
```

#### **E. Verify Table Structure & Statistics**
```sql
\d newsletter_subscribers

-- View all subscribers
SELECT id, email, source_page, created_at FROM newsletter_subscribers ORDER BY created_at DESC;

-- Stats by source_page
SELECT source_page, COUNT(*) as subscriber_count 
FROM newsletter_subscribers 
GROUP BY source_page 
ORDER BY subscriber_count DESC;

-- Check for duplicate emails (should be 0)
SELECT email, COUNT(*) 
FROM newsletter_subscribers 
GROUP BY email 
HAVING COUNT(*) > 1;
```

---

---

## Author_Profiles Table - Implementation

### Table Details

| Field | Data Type | Constraints | Purpose |
|-------|-----------|-------------|---------|
| **id** | SERIAL | PRIMARY KEY | Auto-incrementing unique identifier |
| **user_id** | INTEGER | NOT NULL, UNIQUE, FK to users(id), ON DELETE CASCADE | One-to-one relationship with users |
| **bio** | TEXT | Nullable | Author biography/description |
| **avatar_url** | VARCHAR(255) | Nullable | Profile picture URL |
| **linkedin_url** | VARCHAR(255) | Nullable | LinkedIn profile link |
| **expertise_topics** | TEXT | Nullable | Comma-separated list of expertise areas |
| **created_at** | TIMESTAMP WITH TIME ZONE | DEFAULT CURRENT_TIMESTAMP | Profile creation time |
| **updated_at** | TIMESTAMP WITH TIME ZONE | DEFAULT CURRENT_TIMESTAMP | Profile last update time |

**Note:** One-to-one relationship with users table. When a user is deleted, their author profile is automatically deleted (CASCADE).

---

## Blog_Posts Table - Implementation

### Table Details

| Field | Data Type | Constraints | Purpose |
|-------|-----------|-------------|---------|
| **id** | SERIAL | PRIMARY KEY | Auto-incrementing unique identifier |
| **author_id** | INTEGER | NOT NULL, FK to users(id), ON DELETE RESTRICT | Post author |
| **category_id** | INTEGER | NOT NULL, FK to categories(id), ON DELETE RESTRICT | Blog post category |
| **topic_cluster_id** | INTEGER | FK to topic_clusters(id), ON DELETE SET NULL | Topic grouping for pillar content |
| **pillar_post_id** | INTEGER | FK to blog_posts(id), ON DELETE SET NULL | Self-reference to main guide post |
| **featured_image_id** | INTEGER | FK to media(id), ON DELETE SET NULL | Main post image |
| **og_image_id** | INTEGER | FK to media(id), ON DELETE SET NULL | Open Graph share image |
| **title** | VARCHAR(255) | NOT NULL | Post title |
| **slug** | VARCHAR(255) | NOT NULL, UNIQUE | URL-friendly identifier |
| **excerpt** | TEXT | Nullable | Short summary |
| **content_markdown** | TEXT | NOT NULL | Raw markdown content |
| **content_html** | TEXT | NOT NULL | Rendered HTML content |
| **featured_image_alt** | VARCHAR(255) | Nullable | Alt text for featured image |
| **featured_image_caption** | TEXT | Nullable | Featured image caption |
| **og_title** | VARCHAR(255) | Nullable | Facebook share title |
| **og_description** | TEXT | Nullable | Facebook share description |
| **twitter_title** | VARCHAR(255) | Nullable | Twitter share title |
| **twitter_description** | TEXT | Nullable | Twitter share description |
| **twitter_card_type** | VARCHAR(50) | Nullable | Twitter card type (summary, large_image, etc) |
| **meta_title** | VARCHAR(255) | Nullable | SEO title for search results |
| **meta_description** | TEXT | Nullable | SEO snippet for search results |
| **focus_keyword** | VARCHAR(255) | Nullable | Primary SEO keyword |
| **content_language** | VARCHAR(10) | NOT NULL, DEFAULT 'en' | Post language code |
| **geo_target_country** | VARCHAR(2) | Nullable | Target country for geo-specific content |
| **status** | VARCHAR(50) | NOT NULL, DEFAULT 'draft' | draft, published, archived, or scheduled |
| **reading_time_minutes** | INTEGER | Nullable | Estimated reading time |
| **word_count** | INTEGER | Nullable | Total words in post |
| **table_of_contents_enabled** | BOOLEAN | DEFAULT true | Show table of contents |
| **ai_generated_flag** | BOOLEAN | DEFAULT false | Flag if AI-generated |
| **content_version** | INTEGER | DEFAULT 1 | Content version number |
| **last_updated_reason** | TEXT | Nullable | Reason for last update |
| **published_at** | TIMESTAMP WITH TIME ZONE | Nullable | Publication timestamp |
| **scheduled_at** | TIMESTAMP WITH TIME ZONE | Nullable | Scheduled publish time |
| **last_reviewed_at** | TIMESTAMP WITH TIME ZONE | Nullable | Last review/verification timestamp |
| **view_count** | INTEGER | DEFAULT 0 | Total page views (denormalized) |
| **like_count** | INTEGER | DEFAULT 0 | Total likes (denormalized) |
| **comment_count** | INTEGER | DEFAULT 0 | Total comments (denormalized) |
| **share_count** | INTEGER | DEFAULT 0 | Total shares (denormalized) |
| **created_at** | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Post creation time |
| **updated_at** | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Post last update time |

**Note:** Status values: `draft` (not published), `published` (live), `archived` (hidden), `scheduled` (pending auto-publish). Denormalized counts provide performance for homepage/listing queries.

---

## Post_Tags Table - Implementation

### Table Details

| Field | Data Type | Constraints | Purpose |
|-------|-----------|-------------|---------|
| **post_id** | INTEGER | NOT NULL, FK to blog_posts(id), ON DELETE CASCADE | Blog post |
| **tag_id** | INTEGER | NOT NULL, FK to tags(id), ON DELETE CASCADE | Tag identifier |
| **created_at** | TIMESTAMP WITH TIME ZONE | DEFAULT CURRENT_TIMESTAMP | Association creation time |

**Primary Key:** Composite (post_id, tag_id) - ensures no duplicate tag associations per post.

**Note:** Junction table for many-to-many relationship. A post can have multiple tags, and a tag can be used on multiple posts.

---

## Comments Table - Implementation

### Table Details

| Field | Data Type | Constraints | Purpose |
|-------|-----------|-------------|---------|
| **id** | SERIAL | PRIMARY KEY | Auto-incrementing unique identifier |
| **post_id** | INTEGER | NOT NULL, FK to blog_posts(id), ON DELETE CASCADE | Associated blog post |
| **parent_id** | INTEGER | FK to comments(id), ON DELETE CASCADE | Parent comment for nested replies |
| **name** | VARCHAR(255) | NOT NULL | Commenter name |
| **email** | VARCHAR(255) | NOT NULL | Commenter email |
| **content** | TEXT | NOT NULL | Comment text |
| **is_approved** | BOOLEAN | DEFAULT false | Moderation status |
| **like_count** | INTEGER | DEFAULT 0 | Likes on this comment |
| **created_at** | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Comment creation time |
| **updated_at** | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Comment update time |

**Note:** Many-to-many relationship: many comments per post, many replies per comment. Nested threaded comments supported via parent_id (self-reference). Comments can optionally be moderated before display.

---

## Likes Table - Implementation

### Table Details

| Field | Data Type | Constraints | Purpose |
|-------|-----------|-------------|---------|
| **id** | SERIAL | PRIMARY KEY | Auto-incrementing unique identifier |
| **post_id** | INTEGER | FK to blog_posts(id), ON DELETE CASCADE | Liked blog post (NULL if comment liked) |
| **comment_id** | INTEGER | FK to comments(id), ON DELETE CASCADE | Liked comment (NULL if post liked) |
| **fingerprint_hash** | VARCHAR(255) | NOT NULL | Anonymous user fingerprint |
| **created_at** | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Like creation time |

**Constraints:** 
- `chk_like_target`: Ensures exactly one of post_id or comment_id is set
- `unique_post_like`: Only one like per fingerprint per post
- `unique_comment_like`: Only one like per fingerprint per comment

**Note:** Uses fingerprint_hash to track anonymous users without requiring authentication. Can like either posts OR comments, not both simultaneously. Duplicate likes prevented per user per target.

---

## Redirects Table - Implementation

### Table Details

| Field | Data Type | Constraints | Purpose |
|-------|-----------|-------------|---------|
| **id** | SERIAL | PRIMARY KEY | Auto-incrementing unique identifier |
| **old_slug** | VARCHAR(255) | NOT NULL, UNIQUE | Previous URL slug |
| **new_slug** | VARCHAR(255) | NOT NULL | Current URL slug |
| **redirect_type** | INTEGER | NOT NULL, DEFAULT 301 | HTTP redirect status code |
| **created_at** | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Redirect creation time |
| **updated_at** | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Redirect update time |

**Common HTTP Status Codes:**
- `301`: Permanent redirect (SEO preferred)
- `302`: Temporary redirect
- `307`: Temporary redirect (preserves POST method)
- `308`: Permanent redirect (preserves POST method)

**Note:** SEO-critical table. Old post URLs are tracked and redirected to preserve search rankings. Each old_slug is unique.

---

## Post_Analytics Table - Implementation

### Table Details

| Field | Data Type | Constraints | Purpose |
|-------|-----------|-------------|---------|
| **post_id** | INTEGER | PRIMARY KEY, FK to blog_posts(id), ON DELETE CASCADE | Associated blog post |
| **avg_time** | DECIMAL(10,2) | DEFAULT 0 | Average session duration (seconds) |
| **bounce_rate** | DECIMAL(5,2) | DEFAULT 0 | Bounce rate percentage (0-100) |
| **total_views** | INTEGER | DEFAULT 0 | Total unique view count |
| **last_calculated_at** | TIMESTAMP WITH TIME ZONE | Nullable | When aggregates were last updated |
| **created_at** | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Analytics record creation time |
| **updated_at** | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Analytics record update time |

**Note:** One-to-one relationship with blog_posts. This table contains aggregated data calculated from post_views records. Updated by backend scheduled job (recommended every 5-15 minutes).

**IMPORTANT: Backend Processing Recommendation** (See section below)

---

## Post_Views Table - Implementation

### Table Details

| Field | Data Type | Constraints | Purpose |
|-------|-----------|-------------|---------|
| **id** | SERIAL | PRIMARY KEY | Auto-incrementing unique identifier |
| **post_id** | INTEGER | NOT NULL, FK to blog_posts(id), ON DELETE CASCADE | Blog post viewed |
| **fingerprint_hash** | VARCHAR(255) | NOT NULL | Anonymous user fingerprint |
| **referrer_url** | VARCHAR(255) | Nullable | Source URL (referrer header) |
| **user_agent** | VARCHAR(255) | Nullable | Browser/device user agent |
| **country_code** | VARCHAR(2) | Nullable | Detected country (ISO 3166-1 alpha-2) |
| **device_type** | VARCHAR(50) | Nullable | Device category (mobile, desktop, tablet) |
| **is_bounce** | BOOLEAN | DEFAULT false | True if session < 10 seconds, no interaction |
| **duration_seconds** | INTEGER | NOT NULL | Time spent on page |
| **started_at** | TIMESTAMP WITH TIME ZONE | NOT NULL | Session start time |
| **ended_at** | TIMESTAMP WITH TIME ZONE | Nullable | Session end time |
| **created_at** | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Record creation time |

**Note:** Many-to-many with blog_posts. Each row is an individual page view. Fingerprint_hash enables anonymous user tracking without PII. This is source data for post_analytics calculations.

---

## Post_Analytics: Database vs Backend Processing

### Recommendation: **Backend Processing with Scheduled Job** ✅

**Why NOT use database triggers/stored procedures:**

1. **Business Logic vs Data Integrity**: Analytics calculation is business logic, not data integrity constraint. Database triggers are best for enforcing constraints, not complex calculations.

2. **Flexibility & Maintainability**: Analytics formulas change frequently. Updating Python code is much easier than database functions/triggers.

3. **Testability**: Backend code is infinitely easier to test and debug than database triggers.

4. **Performance**: Complex aggregations on database can lock tables and impact read performance. Backend jobs can run during off-hours.

5. **Observability**: Scheduled jobs allow proper logging, error tracking, metrics collection, and alerting.

### Recommended Architecture:

**Technology Stack:**
- **Scheduler**: Celery + Redis (distributed tasks) OR APScheduler (simpler)
- **Frequency**: Every 5-15 minutes (real-time analytics not usually required)
- **Error Handling**: Retry logic, dead letter queue, monitoring

**Backend Implementation Pattern (Pseudocode):**

```python
@periodic_task.on_schedule(
    schedule=crontab(minute='*/5')  # Every 5 minutes
)
def calculate_post_analytics():
    """
    Aggregates post_views into post_analytics
    Called: every 5 minutes
    """
    posts = db.query(BlogPost).filter(
        BlogPost.published_at.isnot(None)
    ).all()
    
    for post in posts:
        views = db.query(PostView).filter(
            PostView.post_id == post.id,
            PostView.created_at > post.analytics.last_calculated_at
        ).all()
        
        if not views:
            continue
            
        # Calculate aggregates
        avg_time = sum(v.duration_seconds for v in views) / len(views)
        bounce_count = sum(1 for v in views if v.is_bounce)
        bounce_rate = (bounce_count / len(views)) * 100
        
        # Update post_analytics
        analytics = db.query(PostAnalytics).filter_by(
            post_id=post.id
        ).first()
        
        if not analytics:
            analytics = PostAnalytics(post_id=post.id)
            db.add(analytics)
        
        analytics.avg_time = avg_time
        analytics.bounce_rate = bounce_rate
        analytics.total_views = len(views)
        analytics.last_calculated_at = datetime.utcnow()
        
        db.commit()
```



