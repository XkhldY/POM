# BCareful Clerk Authentication Fullstack Architecture

## Introduction

This document outlines the complete fullstack architecture for integrating Clerk authentication into BCareful, including backend systems, frontend implementation, and their integration. It serves as the single source of truth for AI-driven development, ensuring consistency across the entire technology stack.

This unified approach combines what would traditionally be separate backend and frontend architecture documents, streamlining the development process for modern fullstack applications where these concerns are increasingly intertwined.

### Starter Template or Existing Project

**Decision:** This is a brownfield enhancement to an existing system. We'll integrate Clerk authentication while preserving all existing functionality.

### Change Log

| Date | Version | Description | Author |
|------|---------|-------------|---------|
| 2024-09-11 | 1.0 | Initial Clerk authentication architecture design | Winston (Architect) |

## High Level Architecture

### Technical Summary

The BCareful Clerk authentication integration follows a **brownfield enhancement pattern** that extends the existing Next.js 14 + FastAPI architecture with comprehensive authentication capabilities. The system maintains full backward compatibility with anonymous resume analysis while adding user registration, login, and session management through Clerk's JWT-based authentication.

### Platform and Infrastructure Choice

**Platform:** AWS (existing infrastructure)
**Key Services:** 
- Existing: RDS PostgreSQL, S3, ECS, CloudWatch
- New: Clerk Authentication Service (managed)
- Enhanced: JWT validation, webhook processing

**Deployment Host and Regions:** AWS ECS (existing), Clerk global CDN

### Repository Structure

**Structure:** Monorepo (existing)
**Monorepo Tool:** Existing structure with frontend/ and backend/ directories
**Package Organization:** 
- `frontend/` - Next.js application with Clerk integration
- `backend/` - FastAPI application with JWT validation
- Shared types and utilities as needed

### High Level Architecture Diagram

```mermaid
graph TB
    User[👤 User] --> Browser[🌐 Browser]
    Browser --> NextJS[⚛️ Next.js Frontend<br/>Clerk Provider]
    NextJS --> Clerk[🔐 Clerk Auth Service]
    NextJS --> FastAPI[🐍 FastAPI Backend<br/>JWT Validation]
    FastAPI --> PostgreSQL[(🗄️ PostgreSQL<br/>User Data)]
    FastAPI --> Redis[(⚡ Redis<br/>Sessions)]
    FastAPI --> S3[(📁 S3<br/>File Storage)]
    Clerk --> Webhook[📡 Webhook Handler]
    Webhook --> PostgreSQL
    FastAPI --> Celery[⚙️ Celery Workers<br/>Background Tasks]
    Celery --> PostgreSQL
```

### Architectural Patterns

- **JWT-Based Authentication:** Secure, stateless authentication using Clerk's JWT tokens
- **Optional Authentication Middleware:** Backend middleware that works for both authenticated and anonymous users
- **Webhook-Driven User Sync:** Real-time synchronization between Clerk and local database
- **Component-Based Frontend:** React components with Clerk integration
- **Repository Pattern:** Abstracted data access for user management
- **API Gateway Pattern:** Single entry point for all API calls with authentication

## Tech Stack

| Category | Technology | Version | Purpose | Rationale |
|----------|------------|---------|---------|-----------|
| Frontend Language | TypeScript | 5.3.3 | Type-safe frontend development | Existing choice, provides excellent type safety for Clerk integration |
| Frontend Framework | Next.js | 14.0.4 | React framework with SSR/SSG | Existing choice, excellent Clerk integration support |
| UI Component Library | Tailwind CSS | 3.3.6 | Utility-first CSS framework | Existing choice, consistent with current design system |
| State Management | Zustand | 4.4.7 | Lightweight state management | Existing choice, works well with Clerk auth state |
| Authentication | Clerk | 4.29.0 | Managed authentication service | Industry-leading auth solution with excellent Next.js integration |
| Backend Language | Python | 3.11 | Backend API development | Existing choice, excellent for FastAPI and JWT validation |
| Backend Framework | FastAPI | 0.104.1 | Modern Python web framework | Existing choice, excellent JWT support and async capabilities |
| API Style | REST | - | RESTful API design | Existing choice, simple and well-understood |
| Database | PostgreSQL | 15 | Primary data storage | Existing choice, excellent for user data and relationships |
| Cache | Redis | 7 | Session storage and caching | Existing choice, perfect for JWT token caching |
| File Storage | AWS S3 | - | Resume file storage | Existing choice, secure and scalable |
| Frontend Testing | Jest + RTL | 29.7.0 | Component and unit testing | Existing choice, excellent for testing auth components |
| Backend Testing | Pytest | 7.4.3 | Python testing framework | Existing choice, comprehensive testing capabilities |
| E2E Testing | Playwright | 1.40.1 | End-to-end testing | Existing choice, excellent for testing auth flows |
| Build Tool | uv | Latest | Python dependency management | Existing choice, faster than Poetry |
| Bundler | Webpack (Next.js) | Built-in | Frontend bundling | Existing choice, optimized for Next.js |
| IaC Tool | AWS CDK/CloudFormation | - | Infrastructure as code | Existing choice, leverages current AWS setup |
| CI/CD | GitHub Actions | - | Automated testing and deployment | Existing choice, already configured |
| Monitoring | AWS CloudWatch | - | Application monitoring | Existing choice, integrates with current infrastructure |
| Logging | Python logging + CloudWatch | - | Application logging | Existing choice, centralized logging solution |

## Data Models

### User Model

**Purpose:** Extended user model that integrates Clerk authentication data with local application data

**Key Attributes:**
- `clerk_id`: string - Unique Clerk user identifier
- `email`: string - User's email address from Clerk
- `name`: string - User's full name
- `first_name`: string - User's first name
- `last_name`: string - User's last name
- `image_url`: string - User's profile image URL from Clerk
- `is_active`: boolean - Whether user account is active
- `last_login`: datetime - Last login timestamp
- `created_at`: datetime - Account creation timestamp
- `updated_at`: datetime - Last update timestamp

**TypeScript Interface:**
```typescript
interface User {
  id: number;
  clerk_id: string;
  email: string;
  name?: string;
  first_name?: string;
  last_name?: string;
  image_url?: string;
  is_active: boolean;
  last_login?: Date;
  created_at: Date;
  updated_at: Date;
}
```

**Relationships:**
- One-to-many with Resume analyses
- One-to-many with Consultation requests

## API Specification

### REST API Specification

```yaml
openapi: 3.0.0
info:
  title: BCareful API
  version: 1.0.0
  description: AI-powered resume analysis API with Clerk authentication
servers:
  - url: http://localhost:8000/api/v1
    description: Development server
  - url: https://api.bcareful.com/api/v1
    description: Production server

paths:
  /auth/me:
    get:
      summary: Get current user
      security:
        - bearerAuth: []
      responses:
        '200':
          description: User information
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
        '401':
          description: Unauthorized
        '404':
          description: User not found

  /upload:
    post:
      summary: Upload resume file
      security:
        - bearerAuth: []
      requestBody:
        content:
          multipart/form-data:
            schema:
              type: object
              properties:
                file:
                  type: string
                  format: binary
      responses:
        '200':
          description: Upload successful
          content:
            application/json:
              schema:
                type: object
                properties:
                  upload_id:
                    type: string
                  status:
                    type: string

  /webhooks/clerk:
    post:
      summary: Clerk webhook endpoint
      requestBody:
        content:
          application/json:
            schema:
              type: object
      responses:
        '200':
          description: Webhook processed successfully

components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT

  schemas:
    User:
      type: object
      properties:
        id:
          type: integer
        clerk_id:
          type: string
        email:
          type: string
        name:
          type: string
        first_name:
          type: string
        last_name:
          type: string
        image_url:
          type: string
        is_active:
          type: boolean
        last_login:
          type: string
          format: date-time
        created_at:
          type: string
          format: date-time
        updated_at:
          type: string
          format: date-time
```

## Core Workflows

### User Authentication Flow

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant C as Clerk
    participant B as Backend
    participant D as Database

    U->>F: Click Sign In
    F->>C: Redirect to Clerk
    C->>U: Show auth form
    U->>C: Submit credentials
    C->>F: Return with JWT token
    F->>B: API call with JWT
    B->>C: Validate JWT
    C->>B: Return user data
    B->>D: Get/Create user record
    D->>B: Return user data
    B->>F: Return user info
    F->>U: Show authenticated state
```

## Database Schema

```sql
-- Users table (extended for Clerk integration)
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    clerk_id VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    image_url VARCHAR(500),
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Resume uploads table
CREATE TABLE resumes (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    file_path VARCHAR(500) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_size INTEGER NOT NULL,
    upload_status VARCHAR(50) DEFAULT 'pending',
    analysis_status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Analysis results table
CREATE TABLE analyses (
    id SERIAL PRIMARY KEY,
    resume_id INTEGER REFERENCES resumes(id) ON DELETE CASCADE,
    analysis_result JSONB NOT NULL,
    suggestions JSONB NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_users_clerk_id ON users(clerk_id);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_resumes_user_id ON resumes(user_id);
CREATE INDEX idx_analyses_resume_id ON analyses(resume_id);
```

## Frontend Architecture

### Component Organization
```
frontend/
├── app/
│   ├── layout.tsx                 # ClerkProvider wrapper
│   ├── page.tsx                   # Landing page
│   ├── dashboard/
│   │   └── page.tsx              # Protected dashboard
│   └── api/
│       └── auth/
│           └── route.ts          # Auth API routes
├── components/
│   ├── auth/
│   │   ├── SignInButton.tsx      # Clerk sign-in button
│   │   ├── UserButton.tsx        # Clerk user button
│   │   ├── ProtectedRoute.tsx    # Route protection
│   │   └── AuthProvider.tsx      # Auth context provider
│   ├── upload/
│   │   └── ResumeUpload.tsx      # File upload component
│   └── ui/
│       └── Button.tsx            # Reusable button component
├── lib/
│   ├── auth.ts                   # Auth utilities
│   ├── api.ts                    # API client with auth
│   └── types.ts                  # TypeScript interfaces
└── hooks/
    ├── useAuth.ts                # Auth state hook
    └── useApi.ts                 # API client hook
```

### API Client Setup
```typescript
import axios from 'axios';
import { useAuth } from '@clerk/nextjs';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || '/api',
  timeout: 30000,
});

// Add auth token to requests
api.interceptors.request.use(async (config) => {
  const { getToken } = useAuth();
  const token = await getToken();
  
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  
  return config;
});

export default api;
```

## Backend Architecture

### Service Architecture
```
backend/
├── app/
│   ├── main.py                   # FastAPI application
│   ├── core/
│   │   ├── config.py             # Configuration
│   │   ├── auth.py               # Auth middleware
│   │   └── database.py           # Database connection
│   ├── models/
│   │   ├── user.py               # User model
│   │   ├── resume.py             # Resume model
│   │   └── analysis.py           # Analysis model
│   ├── api/
│   │   └── v1/
│   │       ├── auth.py           # Auth endpoints
│   │       ├── upload.py         # Upload endpoints
│   │       ├── analysis.py       # Analysis endpoints
│   │       └── webhooks.py       # Webhook endpoints
│   ├── services/
│   │   ├── auth_service.py       # Auth business logic
│   │   ├── user_service.py       # User management
│   │   └── file_service.py       # File handling
│   └── tasks/
│       ├── user_tasks.py         # User sync tasks
│       └── analysis_tasks.py     # Analysis tasks
```

### Auth Middleware
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from typing import Optional
from app.core.config import settings
from app.models.user import User
from app.core.database import get_db
from sqlalchemy.orm import Session

security = HTTPBearer(auto_error=False)

async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Get current user if authenticated, None otherwise"""
    
    if not credentials:
        return None
    
    try:
        # Verify JWT token from Clerk
        payload = jwt.decode(
            credentials.credentials,
            settings.CLERK_JWT_SECRET,
            algorithms=["RS256"]
        )
        
        clerk_id = payload.get("sub")
        if not clerk_id:
            return None
        
        # Get or create user
        user_repo = UserRepository(db)
        user = user_repo.get_by_clerk_id(clerk_id)
        
        if not user:
            # Create user from Clerk data
            user = user_repo.create_from_clerk(payload)
        
        return user
        
    except JWTError:
        return None
    except Exception as e:
        logger.error(f"Auth error: {str(e)}")
        return None

async def get_current_user_required(
    current_user: Optional[User] = Depends(get_current_user_optional)
) -> User:
    """Require authenticated user"""
    
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return current_user
```

## Development Workflow

### Local Development Setup

#### Prerequisites
```bash
# Required software
node >= 18.0.0
python >= 3.11
docker >= 20.0.0
docker-compose >= 2.0.0
uv >= 0.1.0
```

#### Initial Setup
```bash
# Clone repository
git clone <repository-url>
cd BCareful

# Install dependencies
npm install
cd backend && uv sync
cd ../frontend && npm install

# Set up environment variables
cp .env.example .env
# Edit .env with your Clerk keys

# Start development environment
docker-compose up -d postgres redis
npm run dev
```

### Environment Configuration

#### Required Environment Variables
```bash
# Frontend (.env.local)
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/dashboard
NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL=/dashboard
NEXT_PUBLIC_API_URL=http://localhost:8000

# Backend (.env)
CLERK_SECRET_KEY=sk_test_...
CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_JWT_SECRET=your-jwt-secret
CLERK_WEBHOOK_SECRET=whsec_...
DATABASE_URL=postgresql://user:pass@localhost:5432/bcareful
REDIS_URL=redis://localhost:6379/0
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
S3_BUCKET_NAME=bcareful-resumes

# Shared
ENVIRONMENT=development
DEBUG=true
```

## Security and Performance

### Security Requirements

**Frontend Security:**
- CSP Headers: `default-src 'self'; script-src 'self' 'unsafe-inline' https://clerk.com`
- XSS Prevention: React's built-in XSS protection, input sanitization
- Secure Storage: Clerk handles token storage securely

**Backend Security:**
- Input Validation: Pydantic models for all API inputs
- Rate Limiting: 100 requests/minute per IP
- CORS Policy: Allow specific origins only

**Authentication Security:**
- Token Storage: Clerk manages token storage and refresh
- Session Management: Stateless JWT-based authentication
- Password Policy: Managed by Clerk

### Performance Optimization

**Frontend Performance:**
- Bundle Size Target: <500KB initial bundle
- Loading Strategy: Code splitting, lazy loading
- Caching Strategy: Next.js built-in caching, React Query for API data

**Backend Performance:**
- Response Time Target: <200ms for API calls
- Database Optimization: Proper indexing, connection pooling
- Caching Strategy: Redis for session data, JWT validation caching

## Testing Strategy

### Testing Pyramid
```
E2E Tests (Playwright)
/        \
Integration Tests (API + DB)
/            \
Frontend Unit (Jest)  Backend Unit (Pytest)
```

### Test Organization

#### Frontend Tests
```
frontend/tests/
├── components/
│   ├── auth/
│   │   ├── SignInButton.test.tsx
│   │   └── ProtectedRoute.test.tsx
│   └── upload/
│       └── ResumeUpload.test.tsx
├── hooks/
│   ├── useAuth.test.ts
│   └── useApi.test.ts
└── lib/
    ├── auth.test.ts
    └── api.test.ts
```

#### Backend Tests
```
backend/tests/
├── api/
│   ├── test_auth.py
│   ├── test_upload.py
│   └── test_webhooks.py
├── services/
│   ├── test_auth_service.py
│   └── test_user_service.py
└── models/
    └── test_user.py
```

## Coding Standards

### Critical Fullstack Rules
- **Type Sharing:** Always define types in shared interfaces and import from there
- **API Calls:** Never make direct HTTP calls - use the service layer
- **Environment Variables:** Access only through config objects, never process.env directly
- **Error Handling:** All API routes must use the standard error handler
- **State Updates:** Never mutate state directly - use proper state management patterns
- **JWT Validation:** Always validate JWT tokens on the backend, never trust client-side tokens
- **User Context:** Always get user context from authentication middleware, never from client
- **File Uploads:** Always validate file types and sizes on the backend

### Naming Conventions

| Element | Frontend | Backend | Example |
|---------|----------|---------|---------|
| Components | PascalCase | - | `UserProfile.tsx` |
| Hooks | camelCase with 'use' | - | `useAuth.ts` |
| API Routes | - | kebab-case | `/api/user-profile` |
| Database Tables | - | snake_case | `user_profiles` |
| Services | PascalCase | PascalCase | `AuthService.ts` |
| Models | PascalCase | PascalCase | `User.ts` |

## Error Handling Strategy

### Error Response Format
```typescript
interface ApiError {
  error: {
    code: string;
    message: string;
    details?: Record<string, any>;
    timestamp: string;
    requestId: string;
  };
}
```

### Frontend Error Handling
```typescript
import { toast } from 'react-hot-toast';

export function handleApiError(error: any) {
  if (error.response?.status === 401) {
    // Redirect to sign-in
    window.location.href = '/sign-in';
  } else if (error.response?.status === 403) {
    toast.error('You do not have permission to perform this action');
  } else if (error.response?.status >= 500) {
    toast.error('Server error. Please try again later.');
  } else {
    toast.error(error.response?.data?.error?.message || 'An error occurred');
  }
}
```

## Monitoring and Observability

### Monitoring Stack
- **Frontend Monitoring:** Vercel Analytics + Sentry
- **Backend Monitoring:** AWS CloudWatch + Sentry
- **Error Tracking:** Sentry for both frontend and backend
- **Performance Monitoring:** AWS CloudWatch metrics + Vercel Analytics

### Key Metrics

**Frontend Metrics:**
- Core Web Vitals (LCP, FID, CLS)
- JavaScript errors
- API response times
- User interactions
- Authentication success/failure rates

**Backend Metrics:**
- Request rate
- Error rate
- Response time
- Database query performance
- JWT validation performance
- Webhook processing success rate

---

*This architecture document provides the complete technical foundation for integrating Clerk authentication into the BCareful application while maintaining backward compatibility and following best practices for security, performance, and maintainability.*
