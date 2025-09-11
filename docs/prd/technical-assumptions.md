# Technical Assumptions

## Repository Structure: Monorepo

The project will use a monorepo structure to manage both frontend and backend code in a single repository, enabling shared tooling, consistent dependencies, and simplified deployment processes.

## Service Architecture

**Frontend:** Next.js with TypeScript for full-stack React development, providing server-side rendering, API routes, and modern development practices with component-based architecture.

**Backend:** Python with FastAPI for high-performance API development, providing RESTful endpoints for resume processing, user management, and consultation requests with automatic API documentation.

**Database:** AWS RDS (PostgreSQL) for structured data storage including user information, consultation requests, and analytics.

**File Storage:** AWS S3 for resume file storage with appropriate security and retention policies.

**AI Integration:** AWS Bedrock for resume analysis and improvement suggestions, enhanced with LangChain for AI workflow orchestration and Strand Agents for agentic AI capabilities.

**Deployment:** Docker containers with AWS ECS for production deployment, supporting both local development and cloud scaling.

## Testing Requirements

**Frontend Testing:** Jest and React Testing Library for Next.js component testing with 80%+ code coverage.

**Backend Testing:** Pytest for Python/FastAPI unit tests and integration tests with 80%+ code coverage.

**API Testing:** FastAPI's built-in testing capabilities and pytest for endpoint testing and database integration tests.

**End-to-End Testing:** Playwright for critical user journeys including resume upload, analysis, and download.

**Manual Testing:** User acceptance testing for consultation request workflows and edge cases.

## Additional Technical Assumptions and Requests

- **Environment Management:** Separate development, staging, and production environments
- **CI/CD Pipeline:** GitHub Actions for automated testing and deployment
- **Monitoring:** AWS CloudWatch for application monitoring and error tracking
- **Security:** HTTPS enforcement, input validation, and secure file handling
- **Performance:** CDN integration for static assets and optimized image delivery
- **Analytics:** Google Analytics or similar for user behavior tracking
- **AI Workflow:** LangChain for orchestrating AI analysis workflows and prompt management
- **Agentic AI:** Strand Agents for implementing agentic AI behaviors and autonomous task execution
- **API Documentation:** FastAPI automatic OpenAPI/Swagger documentation generation
- **Python Dependencies:** Poetry or pipenv for Python dependency management
- **Frontend Build:** Next.js build optimization and static generation where applicable
- **Containerization:** Docker for local development and production deployment
- **Orchestration:** AWS ECS for container orchestration and scaling
- **Authentication:** Clerk for user profile authentication and session management (Phase 2)
- **Unified Deployment:** Single Docker container with Next.js frontend and FastAPI backend
- **Phase 1 Scope:** No authentication required - users can try analysis without signup
