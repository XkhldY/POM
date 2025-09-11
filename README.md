# POM - The AI-Powered Resume Analysis Tool

POM is a web application designed to help users improve their resumes. It uses AI to analyze resume content and provide actionable suggestions for improvement. This project is a monorepo containing a Next.js frontend and a Python FastAPI backend.

## Getting Started

Follow these instructions to get the project set up and running on your local machine for development and testing purposes.

### Prerequisites

You will need the following software installed on your system:
- [Docker](https://www.docker.com/get-started) and [Docker Compose](https://docs.docker.com/compose/install/)
- [Node.js](https://nodejs.org/) (v20 or later)
- [Python](https://www.python.org/) (v3.11 or later)
- [Poetry](https://python-poetry.org/docs/#installation) for Python package management

### Setup

1.  **Clone the repository:**
    ```sh
    git clone <repository-url>
    cd pom-monorepo
    ```

2.  **Set up the environment variables:**
    Copy the example environment file and update it if necessary. For local development, the default values should work.
    ```sh
    cp .env.example .env
    ```

3.  **Install dependencies:**
    This project uses a monorepo structure. Install all dependencies from the root directory.
    ```sh
    npm install
    ```
    This will install both the root-level and frontend dependencies. For the backend, Poetry is used. The dependencies will be installed inside the Docker container, but you can install them locally if you wish to run the backend outside of Docker:
    ```sh
    cd backend
    poetry install
    cd ..
    ```

## Running the Application

The entire application stack (frontend, backend, database) can be run using Docker Compose.

From the root of the project, run:
```sh
docker-compose up --build
```
This will build the Docker images for the frontend and backend and start the services.

Once the services are running, you can access them at:
- **Frontend:** [http://localhost:3000](http://localhost:3000)
- **Backend API Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)

To stop the application, press `Ctrl+C` in the terminal where `docker-compose` is running, and then run:
```sh
docker-compose down
```

## Project Structure

This is a monorepo with the following structure:
- `frontend/`: Contains the Next.js frontend application.
- `backend/`: Contains the Python FastAPI backend application.
- `docs/`: Contains all project documentation, including epics and stories.
- `docker-compose.yml`: Orchestrates the local development environment.
- `.github/`: Contains GitHub Actions workflows for CI/CD.

## Technology Stack

- **Frontend:**
  - Next.js 14
  - React 18
  - TypeScript
  - Tailwind CSS
- **Backend:**
  - FastAPI
  - Python 3.11
  - PostgreSQL
  - SQLAlchemy
  - Celery
- **DevOps:**
  - Docker
  - GitHub Actions
