# Phase 4 — Courses & Memberships

> **Goal**: Build the course builder, membership portal, video hosting, paywalls, drip content, quizzes, certificates, and community features. After this phase, users can sell online courses and run membership communities.

## Status: NOT STARTED

## Dependencies
- Phase 0 (Foundation) — auth, storage
- Phase 2 (Dashboard) — UI, media library
- Phase 3 (Email) — email sequences for drip, welcome emails
- Phase 6 (Payments) — paywalls (partial dependency; can build course structure first, add payments when ready)

## Checklist

### Course Builder
- [ ] Course data model: title, description, image, price, status, instructor
- [ ] Module structure: course → sections → lessons (3-level hierarchy)
- [ ] Lesson types:
  - [ ] Video lesson (upload to S3, stream via CloudFront with signed URLs)
  - [ ] Text/article lesson (rich text editor, same as page editor)
  - [ ] Audio lesson (S3 upload + player)
  - [ ] PDF/download lesson (gated file download)
  - [ ] Quiz lesson (see quiz builder below)
  - [ ] Assignment lesson (student submission)
  - [ ] Live session placeholder (Zoom/Meet link + date)
- [ ] Course editor: drag-drop reorder sections/lessons
- [ ] Course settings: pricing (free/paid/subscription), enrollment (open/invite/password), visibility
- [ ] Course landing page (auto-generated, uses template system)
- [ ] Free preview/teaser: mark specific lessons as free
- [ ] Course thumbnail + promotional video

### Video Hosting
- [ ] Upload to S3 with progress indicator
- [ ] Transcoding pipeline (Lambda or MediaConvert): generate multiple resolutions (480p, 720p, 1080p)
- [ ] HLS streaming via CloudFront (adaptive bitrate)
- [ ] Signed URLs (prevent hotlinking / unauthorized access)
- [ ] Custom video player:
  - [ ] Playback speed control (0.5x - 2x)
  - [ ] Quality selector
  - [ ] Auto-generated captions (Whisper/Deepgram)
  - [ ] Manual caption upload (SRT/VTT)
  - [ ] Bookmarks (save timestamp with note)
  - [ ] Progress tracking (resume where left off)
  - [ ] Keyboard shortcuts
- [ ] Video analytics: total views, average watch time, completion rate, drop-off points

### Quiz / Assessment Builder
- [ ] Question types: multiple choice, true/false, free text, multi-select
- [ ] Question bank per course (reusable across lessons)
- [ ] Quiz settings: pass score, retakes allowed, time limit, randomize questions
- [ ] Auto-grading for MCQ/T-F/multi-select
- [ ] Manual grading for free text (instructor review queue)
- [ ] Quiz results: per-student scores, class average, question-level analytics
- [ ] Quiz as lesson gating: must pass quiz to unlock next section

### Drip Content
- [ ] Schedule-based drip: release sections X days after enrollment
- [ ] Date-based drip: release on specific dates (for cohorts)
- [ ] Completion-based drip: unlock next section after completing current
- [ ] Drip notification: email student when new content unlocks (ties to Email system)

### Certificates
- [ ] Certificate template designer (simple: course name, student name, date, instructor, unique ID)
- [ ] Auto-issue on course completion (all required lessons + passing all quizzes)
- [ ] Manual issue by instructor
- [ ] PDF generation (server-side)
- [ ] Unique verification URL: agentbloom.com/verify/[certificate-id]
- [ ] Certificate display on student profile

### Assignments
- [ ] Assignment creation: instructions, due date, file types accepted
- [ ] Student submission: text + file upload
- [ ] Instructor review panel: view submissions, grade (pass/fail or score), feedback
- [ ] Late submission handling: warn but allow (configurable)
- [ ] Notification: student notified on grade/feedback

### Student Experience
- [ ] Student dashboard: enrolled courses, progress overview, upcoming deadlines
- [ ] Course player: sidebar navigation (sections/lessons) + content area
- [ ] Progress tracking: visual progress bar, lesson completion checkmarks
- [ ] Notes: per-lesson note-taking (saved to student's account)
- [ ] Bookmarks: save important lessons for quick access
- [ ] Discussion per lesson (see Community below)
- [ ] Certificate downloads
- [ ] Profile: name, avatar, bio

### Membership Portal
- [ ] Membership tier management (from Members Area spec):
  - [ ] Create tiers: Free, Basic, Premium, etc.
  - [ ] Assign access rules per tier
  - [ ] Pricing: one-time or recurring (ties to Payments)
- [ ] Member login: magic link, Google OAuth, email/password
- [ ] Member portal: branded login page, member dashboard
- [ ] Protected content gating:
  - [ ] By tier: "Premium members only"
  - [ ] By purchase: "Buyers of Course X"
  - [ ] By tag: "VIP tagged contacts"
  - [ ] By date: "Members who joined before X"
- [ ] Member directory: optional, privacy-controlled (opt-in)
- [ ] Self-service billing: upgrade, downgrade, cancel (Stripe Customer Portal)
- [ ] Resource library: downloadable files per tier

### Community
- [ ] Activity feed (not traditional forums): posts, responses, reactions
- [ ] Per-course or global community spaces
- [ ] Post types: discussion, question (with "answered" marking), resource share
- [ ] Reactions: like, helpful, celebrate
- [ ] @mentions notification
- [ ] Pin/highlight posts (instructor)
- [ ] Media in posts: images, links
- [ ] Moderation: report, delete, ban user from community
- [ ] Threaded replies (1 level deep for simplicity)

### Engagement & Gamification (Optional per community)
- [ ] Points system: +5 lesson complete, +10 quiz pass, +2 community post
- [ ] Badges: "First Course Complete", "10 Lessons", "Quiz Master", etc.
- [ ] Streaks: consecutive days of activity
- [ ] Leaderboard: top learners this week/month
- [ ] Toggle on/off per course/community

### Agent Tools (Phase 4)
- [ ] `create_course` — Build course structure from description
- [ ] `add_lesson` — Add lesson to course/section
- [ ] `create_quiz` — Build quiz for lesson
- [ ] `generate_certificate` — Design certificate template
- [ ] `setup_membership` — Create membership tiers and access rules
- [ ] `configure_drip` — Set up drip schedule for course
- [ ] `generate_course_content` — AI-write lesson text content

### Database Schema (Phase 4 additions)
```sql
CREATE TABLE courses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    slug VARCHAR(255) NOT NULL,
    description TEXT,
    short_description TEXT,
    thumbnail_url TEXT,
    promo_video_url TEXT,
    instructor_name VARCHAR(255),
    instructor_bio TEXT,
    price DECIMAL(10,2) DEFAULT 0,
    currency VARCHAR(3) DEFAULT 'USD',
    pricing_type VARCHAR(50) DEFAULT 'free', -- free, one_time, subscription
    subscription_interval VARCHAR(20), -- monthly, yearly
    enrollment_type VARCHAR(50) DEFAULT 'open', -- open, invite, password
    enrollment_password VARCHAR(255),
    status VARCHAR(50) DEFAULT 'draft', -- draft, published, archived
    settings JSONB DEFAULT '{}',
    enrolled_count INTEGER DEFAULT 0,
    completion_count INTEGER DEFAULT 0,
    rating DECIMAL(3,2) DEFAULT 0,
    landing_page_id UUID REFERENCES pages(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    published_at TIMESTAMPTZ,
    UNIQUE(org_id, slug)
);

CREATE TABLE course_sections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    course_id UUID REFERENCES courses(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    sort_order INTEGER NOT NULL DEFAULT 0,
    drip_type VARCHAR(50), -- none, days_after_enrollment, specific_date, completion_based
    drip_value JSONB, -- {days: 7} or {date: "2026-03-01"} or {requires_section_id: "..."}
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE lessons (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    section_id UUID REFERENCES course_sections(id) ON DELETE CASCADE,
    course_id UUID REFERENCES courses(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    lesson_type VARCHAR(50) NOT NULL, -- video, text, audio, download, quiz, assignment, live
    content TEXT, -- for text lessons (HTML)
    video_url TEXT, -- S3/CloudFront URL
    video_duration INTEGER, -- seconds
    audio_url TEXT,
    download_url TEXT,
    download_filename VARCHAR(255),
    live_url TEXT, -- Zoom/Meet link
    live_date TIMESTAMPTZ,
    is_free_preview BOOLEAN DEFAULT FALSE,
    is_required BOOLEAN DEFAULT TRUE,
    sort_order INTEGER NOT NULL DEFAULT 0,
    estimated_duration INTEGER, -- minutes
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE quizzes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lesson_id UUID REFERENCES lessons(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    pass_score INTEGER DEFAULT 70, -- percentage
    max_retakes INTEGER DEFAULT 3, -- -1 for unlimited
    time_limit INTEGER, -- minutes, null for no limit
    randomize_questions BOOLEAN DEFAULT FALSE,
    show_answers_after BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE quiz_questions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    quiz_id UUID REFERENCES quizzes(id) ON DELETE CASCADE,
    question_type VARCHAR(50) NOT NULL, -- multiple_choice, true_false, free_text, multi_select
    question_text TEXT NOT NULL,
    options JSONB, -- [{text, is_correct}] for MCQ
    correct_answer TEXT, -- for free text (keyword match)
    points INTEGER DEFAULT 1,
    explanation TEXT, -- shown after answering
    sort_order INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE enrollments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    course_id UUID REFERENCES courses(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    status VARCHAR(50) DEFAULT 'active', -- active, completed, paused, refunded
    enrolled_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    progress_pct DECIMAL(5,2) DEFAULT 0,
    last_lesson_id UUID REFERENCES lessons(id),
    payment_id UUID, -- reference to payment record
    UNIQUE(course_id, user_id)
);

CREATE TABLE lesson_progress (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    enrollment_id UUID REFERENCES enrollments(id) ON DELETE CASCADE,
    lesson_id UUID REFERENCES lessons(id) ON DELETE CASCADE,
    status VARCHAR(50) DEFAULT 'not_started', -- not_started, in_progress, completed
    video_progress INTEGER DEFAULT 0, -- seconds watched
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(enrollment_id, lesson_id)
);

CREATE TABLE quiz_attempts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    quiz_id UUID REFERENCES quizzes(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    score INTEGER NOT NULL,
    max_score INTEGER NOT NULL,
    passed BOOLEAN NOT NULL,
    answers JSONB NOT NULL, -- [{question_id, answer, is_correct}]
    time_taken INTEGER, -- seconds
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE assignments_submissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lesson_id UUID REFERENCES lessons(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    content TEXT,
    file_url TEXT,
    file_name VARCHAR(255),
    grade VARCHAR(50), -- pass, fail, or numeric
    feedback TEXT,
    graded_by UUID REFERENCES users(id),
    graded_at TIMESTAMPTZ,
    submitted_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE certificates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    course_id UUID REFERENCES courses(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    certificate_number VARCHAR(50) UNIQUE NOT NULL,
    template_config JSONB DEFAULT '{}',
    pdf_url TEXT,
    issued_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(course_id, user_id)
);

CREATE TABLE membership_tiers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) DEFAULT 0,
    currency VARCHAR(3) DEFAULT 'USD',
    billing_interval VARCHAR(20), -- monthly, yearly, one_time
    features JSONB DEFAULT '[]', -- list of feature descriptions
    access_rules JSONB DEFAULT '{}', -- {courses: [...], pages: [...], resources: [...]}
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    stripe_price_id VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(org_id, slug)
);

CREATE TABLE memberships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tier_id UUID REFERENCES membership_tiers(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    status VARCHAR(50) DEFAULT 'active', -- active, past_due, cancelled, expired
    stripe_subscription_id VARCHAR(255),
    current_period_start TIMESTAMPTZ,
    current_period_end TIMESTAMPTZ,
    cancelled_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(tier_id, user_id)
);

CREATE TABLE community_spaces (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    course_id UUID REFERENCES courses(id), -- null = global community
    name VARCHAR(255) NOT NULL,
    description TEXT,
    access_type VARCHAR(50) DEFAULT 'members', -- public, members, tier_based
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE community_posts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    space_id UUID REFERENCES community_spaces(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    parent_id UUID REFERENCES community_posts(id), -- null = top-level
    post_type VARCHAR(50) DEFAULT 'discussion', -- discussion, question, resource
    title VARCHAR(255),
    content TEXT NOT NULL,
    is_pinned BOOLEAN DEFAULT FALSE,
    is_answered BOOLEAN DEFAULT FALSE, -- for questions
    reaction_counts JSONB DEFAULT '{"like":0,"helpful":0,"celebrate":0}',
    reply_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE community_reactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    post_id UUID REFERENCES community_posts(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    reaction_type VARCHAR(50) NOT NULL, -- like, helpful, celebrate
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(post_id, user_id, reaction_type)
);

CREATE TABLE student_notes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    lesson_id UUID REFERENCES lessons(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    timestamp INTEGER, -- video timestamp in seconds (optional)
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE student_bookmarks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    lesson_id UUID REFERENCES lessons(id) ON DELETE CASCADE,
    video_timestamp INTEGER,
    note VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Gamification (optional, toggle per community)
CREATE TABLE badges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    icon_url TEXT,
    criteria JSONB NOT NULL, -- {type: "lessons_completed", count: 10}
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE user_badges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    badge_id UUID REFERENCES badges(id) ON DELETE CASCADE,
    earned_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, badge_id)
);

CREATE TABLE user_points (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    total_points INTEGER DEFAULT 0,
    current_streak INTEGER DEFAULT 0,
    longest_streak INTEGER DEFAULT 0,
    last_activity_date DATE,
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, org_id)
);
```

## Acceptance Criteria
- [ ] Creator can build a multi-section, multi-lesson course
- [ ] Video uploads process and stream via CloudFront with custom player
- [ ] Auto-captions generated for uploaded videos
- [ ] Drip content releases on schedule / after completion
- [ ] Quizzes with auto-grading work correctly
- [ ] Students see progress tracking and can resume where they left off
- [ ] Certificates auto-issue on completion, verifiable via URL
- [ ] Membership tiers control access to content
- [ ] Member portal shows enrolled courses, progress, billing
- [ ] Community spaces support posts, replies, reactions
- [ ] Agent can create courses and configure memberships via commands
- [ ] Student/member experience is mobile-friendly

## Known Risks
- Video transcoding costs: AWS MediaConvert charges per minute. Budget for this.
- Storage costs: Video files are large. Implement storage limits per plan tier.
- Caption quality: Auto-generated captions need review option. Quality varies by audio clarity.
- Community moderation: Need reporting and moderation tools from day one to prevent abuse.

## What's Next
Phase 5 (Calendar) and/or Phase 6 (Payments) — both can be developed in parallel.
