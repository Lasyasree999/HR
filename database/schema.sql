-- ============================================================
-- HireGenius AI — MySQL Database Schema
-- ============================================================
-- Run this script to create the database and all tables.
-- Usage: mysql -u root -p < schema.sql
-- ============================================================

-- Create database
CREATE DATABASE IF NOT EXISTS hiregenius_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE hiregenius_db;

-- ============================================================
-- Table: users
-- Stores HR managers and admin accounts
-- ============================================================
CREATE TABLE IF NOT EXISTS users (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    username        VARCHAR(50)  NOT NULL UNIQUE,
    email           VARCHAR(255) NOT NULL UNIQUE,
    password_hash   VARCHAR(255) NOT NULL,
    full_name       VARCHAR(100) NOT NULL,
    role            ENUM('admin', 'hr_manager') NOT NULL DEFAULT 'hr_manager',
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    INDEX idx_users_email (email),
    INDEX idx_users_role (role)
) ENGINE=InnoDB;

-- ============================================================
-- Table: jobs
-- Stores job openings with descriptions and requirements
-- ============================================================
CREATE TABLE IF NOT EXISTS jobs (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    title           VARCHAR(200) NOT NULL,
    description     TEXT NOT NULL,
    required_skills TEXT,
    experience_range VARCHAR(50),
    department      VARCHAR(100),
    salary_range    VARCHAR(100),
    location        VARCHAR(200),
    status          ENUM('open', 'closed', 'on_hold') NOT NULL DEFAULT 'open',
    created_by      INT,
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_jobs_status (status),
    INDEX idx_jobs_department (department)
) ENGINE=InnoDB;

-- ============================================================
-- Table: candidates
-- Stores candidate information and AI-computed scores
-- ============================================================
CREATE TABLE IF NOT EXISTS candidates (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    name            VARCHAR(150) NOT NULL,
    email           VARCHAR(255) UNIQUE,
    phone           VARCHAR(30),
    summary         TEXT,
    match_score     FLOAT DEFAULT 0.0,
    status          ENUM('new', 'screening', 'interview', 'offered', 'hired', 'rejected')
                        NOT NULL DEFAULT 'new',
    job_id          INT,
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE SET NULL,
    INDEX idx_candidates_status (status),
    INDEX idx_candidates_job (job_id),
    INDEX idx_candidates_score (match_score DESC)
) ENGINE=InnoDB;

-- ============================================================
-- Table: resumes
-- Stores uploaded resume files and parsed content
-- ============================================================
CREATE TABLE IF NOT EXISTS resumes (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    candidate_id    INT NOT NULL,
    file_name       VARCHAR(255) NOT NULL,
    file_path       VARCHAR(500) NOT NULL,
    raw_text        LONGTEXT,
    parsed_data     JSON,
    is_embedded     BOOLEAN NOT NULL DEFAULT FALSE,
    uploaded_at     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (candidate_id) REFERENCES candidates(id) ON DELETE CASCADE,
    INDEX idx_resumes_candidate (candidate_id),
    INDEX idx_resumes_embedded (is_embedded)
) ENGINE=InnoDB;

-- ============================================================
-- Table: skills
-- Stores extracted candidate skills with proficiency levels
-- ============================================================
CREATE TABLE IF NOT EXISTS skills (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    candidate_id    INT NOT NULL,
    skill_name      VARCHAR(100) NOT NULL,
    proficiency     ENUM('beginner', 'intermediate', 'advanced', 'expert')
                        DEFAULT 'intermediate',
    years_experience INT DEFAULT 0,

    FOREIGN KEY (candidate_id) REFERENCES candidates(id) ON DELETE CASCADE,
    INDEX idx_skills_candidate (candidate_id),
    INDEX idx_skills_name (skill_name)
) ENGINE=InnoDB;

-- ============================================================
-- Table: interviews
-- Stores AI-generated interview questions and evaluations
-- ============================================================
CREATE TABLE IF NOT EXISTS interviews (
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    candidate_id        INT NOT NULL,
    job_id              INT NOT NULL,
    technical_questions JSON,
    hr_questions        JSON,
    scenario_questions  JSON,
    evaluation_criteria JSON,
    scoring_rubric      JSON,
    status              ENUM('pending', 'completed', 'cancelled')
                            NOT NULL DEFAULT 'pending',
    scheduled_at        DATETIME,
    created_at          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (candidate_id) REFERENCES candidates(id) ON DELETE CASCADE,
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE,
    INDEX idx_interviews_candidate (candidate_id),
    INDEX idx_interviews_job (job_id),
    INDEX idx_interviews_status (status)
) ENGINE=InnoDB;

-- ============================================================
-- Table: recommendations
-- Stores AI hiring recommendations for candidates
-- ============================================================
CREATE TABLE IF NOT EXISTS recommendations (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    candidate_id    INT NOT NULL,
    job_id          INT NOT NULL,
    decision        ENUM('strong_hire', 'hire', 'consider', 'reject') NOT NULL,
    reasoning       TEXT NOT NULL,
    confidence_score FLOAT DEFAULT 0.0,
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (candidate_id) REFERENCES candidates(id) ON DELETE CASCADE,
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE,
    INDEX idx_recommendations_candidate (candidate_id),
    INDEX idx_recommendations_decision (decision)
) ENGINE=InnoDB;

-- ============================================================
-- Table: emails
-- Stores AI-generated HR communication emails
-- ============================================================
CREATE TABLE IF NOT EXISTS emails (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    candidate_id    INT,
    email_type      ENUM('interview_invite', 'rejection', 'offer', 'followup', 'reminder')
                        NOT NULL,
    subject         VARCHAR(500) NOT NULL,
    body            TEXT NOT NULL,
    status          ENUM('draft', 'sent') NOT NULL DEFAULT 'draft',
    created_by      INT,
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (candidate_id) REFERENCES candidates(id) ON DELETE SET NULL,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_emails_candidate (candidate_id),
    INDEX idx_emails_type (email_type)
) ENGINE=InnoDB;

-- ============================================================
-- Table: policies
-- Stores HR policy documents for RAG-based Q&A
-- ============================================================
CREATE TABLE IF NOT EXISTS policies (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    title           VARCHAR(300) NOT NULL,
    file_name       VARCHAR(255),
    file_path       VARCHAR(500),
    content         LONGTEXT,
    is_embedded     BOOLEAN NOT NULL DEFAULT FALSE,
    uploaded_at     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_policies_embedded (is_embedded)
) ENGINE=InnoDB;

-- ============================================================
-- Table: analytics
-- Stores recruitment metrics and KPI data points
-- ============================================================
CREATE TABLE IF NOT EXISTS analytics (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    metric_name     VARCHAR(100) NOT NULL,
    metric_value    VARCHAR(255) NOT NULL,
    category        VARCHAR(100),
    job_id          INT,
    recorded_at     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE SET NULL,
    INDEX idx_analytics_metric (metric_name),
    INDEX idx_analytics_category (category)
) ENGINE=InnoDB;

-- ============================================================
-- Seed default admin user
-- Password: admin123 (bcrypt hashed)
-- ============================================================
INSERT INTO users (username, email, password_hash, full_name, role, is_active)
VALUES (
    'admin',
    'admin@hiregenius.ai',
    '$2b$12$LJ3m4ys3GZ8sKOYHnKL8eOFZm4w8K5yR0Q6j7JHjKvQXfL2xS1Wq.',
    'System Administrator',
    'admin',
    TRUE
) ON DUPLICATE KEY UPDATE username = username;
