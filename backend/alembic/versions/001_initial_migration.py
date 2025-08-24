"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('first_name', sa.String(length=50), nullable=False),
        sa.Column('last_name', sa.String(length=50), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('date_of_birth', sa.DateTime(), nullable=True),
        sa.Column('gender', sa.String(length=20), nullable=True),
        sa.Column('city', sa.String(length=100), nullable=True),
        sa.Column('state', sa.String(length=100), nullable=True),
        sa.Column('country', sa.String(length=100), nullable=True),
        sa.Column('timezone', sa.String(length=50), nullable=True),
        sa.Column('language', sa.String(length=5), nullable=False, server_default='en'),
        sa.Column('currency', sa.String(length=3), nullable=False, server_default='USD'),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('avatar_url', sa.String(length=500), nullable=True),
        sa.Column('social_links', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('notification_preferences', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_superuser', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('email_verified_at', sa.DateTime(), nullable=True),
        sa.Column('phone_verified_at', sa.DateTime(), nullable=True),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.Column('login_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('failed_login_attempts', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('account_locked_until', sa.DateTime(), nullable=True),
        sa.Column('verification_token', sa.String(length=255), nullable=True),
        sa.Column('password_reset_token', sa.String(length=255), nullable=True),
        sa.Column('verification_token_expires', sa.DateTime(), nullable=True),
        sa.Column('password_reset_token_expires', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)

    # Create companies table
    op.create_table('companies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('slug', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('website', sa.String(length=500), nullable=True),
        sa.Column('industry', sa.String(length=100), nullable=True),
        sa.Column('company_size', sa.String(length=50), nullable=True),
        sa.Column('founded_year', sa.Integer(), nullable=True),
        sa.Column('city', sa.String(length=100), nullable=True),
        sa.Column('state', sa.String(length=100), nullable=True),
        sa.Column('country', sa.String(length=100), nullable=True),
        sa.Column('logo_url', sa.String(length=500), nullable=True),
        sa.Column('banner_url', sa.String(length=500), nullable=True),
        sa.Column('mission_statement', sa.Text(), nullable=True),
        sa.Column('vision_statement', sa.Text(), nullable=True),
        sa.Column('linkedin_url', sa.String(length=500), nullable=True),
        sa.Column('twitter_url', sa.String(length=500), nullable=True),
        sa.Column('facebook_url', sa.String(length=500), nullable=True),
        sa.Column('instagram_url', sa.String(length=500), nullable=True),
        sa.Column('benefits', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('culture_tags', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('technologies', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('certifications', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('contact_email', sa.String(length=255), nullable=True),
        sa.Column('contact_phone', sa.String(length=20), nullable=True),
        sa.Column('contact_address', sa.Text(), nullable=True),
        sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_remote_friendly', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('seo_title', sa.String(length=200), nullable=True),
        sa.Column('seo_description', sa.Text(), nullable=True),
        sa.Column('seo_keywords', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('verified_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_companies_slug'), 'companies', ['slug'], unique=True)
    op.create_index(op.f('ix_companies_id'), 'companies', ['id'], unique=False)

    # Create profiles table
    op.create_table('profiles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=True),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('years_of_experience', sa.Integer(), nullable=True),
        sa.Column('city', sa.String(length=100), nullable=True),
        sa.Column('state', sa.String(length=100), nullable=True),
        sa.Column('country', sa.String(length=100), nullable=True),
        sa.Column('is_remote_available', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('skills', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('languages', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('education', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('experience', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('linkedin_url', sa.String(length=500), nullable=True),
        sa.Column('github_url', sa.String(length=500), nullable=True),
        sa.Column('portfolio_url', sa.String(length=500), nullable=True),
        sa.Column('salary_expectation_min', sa.Integer(), nullable=True),
        sa.Column('salary_expectation_max', sa.Integer(), nullable=True),
        sa.Column('preferred_work_types', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('preferred_industries', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('resume_url', sa.String(length=500), nullable=True),
        sa.Column('resume_filename', sa.String(length=255), nullable=True),
        sa.Column('resume_uploaded_at', sa.DateTime(), nullable=True),
        sa.Column('skills_vector', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('experience_vector', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('last_ai_analysis', sa.DateTime(), nullable=True),
        sa.Column('is_complete', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('profile_score', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_profiles_user_id'), 'profiles', ['user_id'], unique=True)
    op.create_index(op.f('ix_profiles_id'), 'profiles', ['id'], unique=False)

    # Create jobs table
    op.create_table('jobs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('slug', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=True),
        sa.Column('employer_id', sa.Integer(), nullable=True),
        sa.Column('job_type', sa.String(length=50), nullable=False),
        sa.Column('experience_level', sa.String(length=50), nullable=False),
        sa.Column('department', sa.String(length=100), nullable=True),
        sa.Column('industry', sa.String(length=100), nullable=True),
        sa.Column('city', sa.String(length=100), nullable=True),
        sa.Column('state', sa.String(length=100), nullable=True),
        sa.Column('country', sa.String(length=100), nullable=True),
        sa.Column('is_remote', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('remote_work_percentage', sa.Integer(), nullable=True),
        sa.Column('skills_required', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('skills_preferred', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('experience_years_min', sa.Integer(), nullable=True),
        sa.Column('experience_years_max', sa.Integer(), nullable=True),
        sa.Column('education_required', sa.String(length=100), nullable=True),
        sa.Column('certifications_required', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('salary_min', sa.Integer(), nullable=True),
        sa.Column('salary_max', sa.Integer(), nullable=True),
        sa.Column('salary_currency', sa.String(length=3), nullable=False, server_default='USD'),
        sa.Column('salary_period', sa.String(length=20), nullable=False, server_default='yearly'),
        sa.Column('benefits', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('application_deadline', sa.DateTime(), nullable=True),
        sa.Column('max_applications', sa.Integer(), nullable=True),
        sa.Column('application_instructions', sa.Text(), nullable=True),
        sa.Column('contact_email', sa.String(length=255), nullable=True),
        sa.Column('contact_phone', sa.String(length=20), nullable=True),
        sa.Column('application_url', sa.String(length=500), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='draft'),
        sa.Column('views_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('current_applications', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('skills_vector', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('requirements_vector', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('last_ai_analysis', sa.DateTime(), nullable=True),
        sa.Column('seo_title', sa.String(length=200), nullable=True),
        sa.Column('seo_description', sa.Text(), nullable=True),
        sa.Column('seo_keywords', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('published_at', sa.DateTime(), nullable=True),
        sa.Column('closed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
        sa.ForeignKeyConstraint(['employer_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_jobs_slug'), 'jobs', ['slug'], unique=True)
    op.create_index(op.f('ix_jobs_id'), 'jobs', ['id'], unique=False)
    op.create_index(op.f('ix_jobs_company_id'), 'jobs', ['company_id'], unique=False)
    op.create_index(op.f('ix_jobs_employer_id'), 'jobs', ['employer_id'], unique=False)

    # Create applications table
    op.create_table('applications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('job_id', sa.Integer(), nullable=False),
        sa.Column('applicant_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='submitted'),
        sa.Column('cover_letter', sa.Text(), nullable=True),
        sa.Column('resume_url', sa.String(length=500), nullable=True),
        sa.Column('expected_salary', sa.Integer(), nullable=True),
        sa.Column('earliest_start_date', sa.DateTime(), nullable=True),
        sa.Column('additional_questions', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('source', sa.String(length=100), nullable=True),
        sa.Column('referral_name', sa.String(length=100), nullable=True),
        sa.Column('is_remote_ok', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_relocation_ok', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('preferred_work_schedule', sa.String(length=50), nullable=True),
        sa.Column('portfolio_url', sa.String(length=500), nullable=True),
        sa.Column('linkedin_url', sa.String(length=500), nullable=True),
        sa.Column('github_url', sa.String(length=500), nullable=True),
        sa.Column('other_urls', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('ai_match_score', sa.Float(), nullable=True),
        sa.Column('skill_match_percentage', sa.Float(), nullable=True),
        sa.Column('experience_match_percentage', sa.Float(), nullable=True),
        sa.Column('ai_analysis', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('ai_recommendations', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('ai_risk_factors', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('is_favorite', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('tags', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('communication_history', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('interview_scheduled', sa.DateTime(), nullable=True),
        sa.Column('interview_type', sa.String(length=50), nullable=True),
        sa.Column('interview_location', sa.String(length=200), nullable=True),
        sa.Column('interview_notes', sa.Text(), nullable=True),
        sa.Column('offer_made', sa.DateTime(), nullable=True),
        sa.Column('offer_amount', sa.Integer(), nullable=True),
        sa.Column('offer_currency', sa.String(length=3), nullable=True),
        sa.Column('offer_status', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('status_updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['applicant_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['job_id'], ['jobs.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_applications_job_id'), 'applications', ['job_id'], unique=False)
    op.create_index(op.f('ix_applications_applicant_id'), 'applications', ['applicant_id'], unique=False)
    op.create_index(op.f('ix_applications_id'), 'applications', ['id'], unique=False)
    op.create_index(op.f('ix_applications_job_applicant'), 'applications', ['job_id', 'applicant_id'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_applications_job_applicant'), table_name='applications')
    op.drop_index(op.f('ix_applications_id'), table_name='applications')
    op.drop_index(op.f('ix_applications_applicant_id'), table_name='applications')
    op.drop_index(op.f('ix_applications_job_id'), table_name='applications')
    op.drop_table('applications')
    
    op.drop_index(op.f('ix_jobs_employer_id'), table_name='jobs')
    op.drop_index(op.f('ix_jobs_company_id'), table_name='jobs')
    op.drop_index(op.f('ix_jobs_id'), table_name='jobs')
    op.drop_index(op.f('ix_jobs_slug'), table_name='jobs')
    op.drop_table('jobs')
    
    op.drop_index(op.f('ix_profiles_id'), table_name='profiles')
    op.drop_index(op.f('ix_profiles_user_id'), table_name='profiles')
    op.drop_table('profiles')
    
    op.drop_index(op.f('ix_companies_id'), table_name='companies')
    op.drop_index(op.f('ix_companies_slug'), table_name='companies')
    op.drop_table('companies')
    
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')