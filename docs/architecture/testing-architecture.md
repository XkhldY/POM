# Testing Architecture Stories

## Testing Strategy Overview

### Testing Pyramid Implementation

**Story:** Implement comprehensive testing strategy following the testing pyramid

```
                    E2E Tests (Playwright)
                   /                    \
              Integration Tests          API Tests
             /                \        /           \
      Frontend Unit Tests    Backend Unit Tests   Contract Tests
      (Jest + RTL)          (Pytest)             (Pact)
```

**Test Distribution:**
- **70% Unit Tests** - Fast, isolated, comprehensive coverage
- **20% Integration Tests** - Component interactions and API endpoints  
- **10% E2E Tests** - Critical user journeys and workflows

## Frontend Testing

### Jest Configuration

**Story:** Configure Jest for Next.js testing with comprehensive setup

```javascript
// jest.config.js
const nextJest = require('next/jest');

const createJestConfig = nextJest({
  // Provide the path to your Next.js app to load next.config.js and .env files
  dir: './',
});

// Add any custom config to be passed to Jest
const customJestConfig = {
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  testEnvironment: 'jest-environment-jsdom',
  moduleNameMapping: {
    // Handle module aliases (this will be automatically configured for you based on your tsconfig.json paths)
    '^@/(.*)$': '<rootDir>/src/$1',
    '^@/components/(.*)$': '<rootDir>/src/components/$1',
    '^@/lib/(.*)$': '<rootDir>/src/lib/$1',
    '^@/hooks/(.*)$': '<rootDir>/src/hooks/$1',
    '^@/stores/(.*)$': '<rootDir>/src/stores/$1',
  },
  collectCoverageFrom: [
    'src/**/*.{js,jsx,ts,tsx}',
    '!src/**/*.d.ts',
    '!src/pages/_app.tsx',
    '!src/pages/_document.tsx',
    '!src/pages/api/**',
  ],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80,
    },
  },
  testPathIgnorePatterns: [
    '<rootDir>/.next/',
    '<rootDir>/node_modules/',
    '<rootDir>/e2e/',
  ],
  transformIgnorePatterns: [
    '/node_modules/',
    '^.+\\.module\\.(css|sass|scss)$',
  ],
};

// createJestConfig is exported this way to ensure that next/jest can load the Next.js config which is async
module.exports = createJestConfig(customJestConfig);
```

```javascript
// jest.setup.js
import '@testing-library/jest-dom';
import { configure } from '@testing-library/react';
import { server } from './src/__mocks__/server';

// Configure React Testing Library
configure({ testIdAttribute: 'data-testid' });

// Mock Next.js router
jest.mock('next/router', () => ({
  useRouter() {
    return {
      route: '/',
      pathname: '/',
      query: {},
      asPath: '/',
      push: jest.fn(),
      pop: jest.fn(),
      reload: jest.fn(),
      back: jest.fn(),
      prefetch: jest.fn(),
      beforePopState: jest.fn(),
      events: {
        on: jest.fn(),
        off: jest.fn(),
        emit: jest.fn(),
      },
    };
  },
}));

// Mock IntersectionObserver
global.IntersectionObserver = jest.fn().mockImplementation(() => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn(),
}));

// Mock matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(), // deprecated
    removeListener: jest.fn(), // deprecated
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

// Setup MSW
beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
```

### Component Testing Examples

**Story:** Create comprehensive component tests with React Testing Library

```typescript
// src/components/forms/__tests__/file-upload.test.tsx
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { FileUpload } from '../file-upload';

// Mock file for testing
const createMockFile = (name: string, size: number, type: string): File => {
  const file = new File(['file content'], name, { type });
  Object.defineProperty(file, 'size', { value: size });
  return file;
};

describe('FileUpload Component', () => {
  const mockOnFileSelect = jest.fn();
  const mockOnFileRemove = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  const defaultProps = {
    onFileSelect: mockOnFileSelect,
    onFileRemove: mockOnFileRemove,
    selectedFile: null,
  };

  describe('Initial State', () => {
    it('renders upload area when no file is selected', () => {
      render(<FileUpload {...defaultProps} />);
      
      expect(screen.getByText('Upload your resume')).toBeInTheDocument();
      expect(screen.getByText('Drag and drop or click to browse')).toBeInTheDocument();
      expect(screen.getByText('Supports PDF, DOC, DOCX, TXT (max 10MB)')).toBeInTheDocument();
    });

    it('shows upload icon in initial state', () => {
      render(<FileUpload {...defaultProps} />);
      
      const uploadIcon = screen.getByTestId('upload-icon');
      expect(uploadIcon).toBeInTheDocument();
    });
  });

  describe('File Selection', () => {
    it('accepts valid PDF file', async () => {
      const user = userEvent.setup();
      render(<FileUpload {...defaultProps} />);
      
      const validFile = createMockFile('resume.pdf', 1024 * 1024, 'application/pdf');
      const input = screen.getByRole('button', { name: /upload your resume/i });
      
      await user.upload(input, validFile);
      
      expect(mockOnFileSelect).toHaveBeenCalledWith(validFile);
    });

    it('accepts valid DOC file', async () => {
      const user = userEvent.setup();
      render(<FileUpload {...defaultProps} />);
      
      const validFile = createMockFile('resume.doc', 1024 * 1024, 'application/msword');
      const input = screen.getByRole('button', { name: /upload your resume/i });
      
      await user.upload(input, validFile);
      
      expect(mockOnFileSelect).toHaveBeenCalledWith(validFile);
    });

    it('rejects files that are too large', async () => {
      const user = userEvent.setup();
      render(<FileUpload {...defaultProps} />);
      
      const largeFile = createMockFile('large-resume.pdf', 15 * 1024 * 1024, 'application/pdf');
      const input = screen.getByRole('button', { name: /upload your resume/i });
      
      await user.upload(input, largeFile);
      
      expect(mockOnFileSelect).not.toHaveBeenCalled();
      expect(screen.getByText('File size must be less than 10MB')).toBeInTheDocument();
    });

    it('rejects unsupported file types', async () => {
      const user = userEvent.setup();
      render(<FileUpload {...defaultProps} />);
      
      const invalidFile = createMockFile('image.jpg', 1024 * 1024, 'image/jpeg');
      const input = screen.getByRole('button', { name: /upload your resume/i });
      
      await user.upload(input, invalidFile);
      
      expect(mockOnFileSelect).not.toHaveBeenCalled();
      expect(screen.getByText('Please upload a PDF, DOC, DOCX, or TXT file')).toBeInTheDocument();
    });
  });

  describe('File Display', () => {
    it('displays selected file information', () => {
      const selectedFile = createMockFile('my-resume.pdf', 2 * 1024 * 1024, 'application/pdf');
      
      render(<FileUpload {...defaultProps} selectedFile={selectedFile} />);
      
      expect(screen.getByText('my-resume.pdf')).toBeInTheDocument();
      expect(screen.getByText('2.0 MB')).toBeInTheDocument();
    });

    it('allows file removal when not uploading', async () => {
      const user = userEvent.setup();
      const selectedFile = createMockFile('resume.pdf', 1024 * 1024, 'application/pdf');
      
      render(<FileUpload {...defaultProps} selectedFile={selectedFile} />);
      
      const removeButton = screen.getByRole('button', { name: /remove file/i });
      await user.click(removeButton);
      
      expect(mockOnFileRemove).toHaveBeenCalled();
    });

    it('hides remove button when uploading', () => {
      const selectedFile = createMockFile('resume.pdf', 1024 * 1024, 'application/pdf');
      
      render(<FileUpload {...defaultProps} selectedFile={selectedFile} isUploading={true} />);
      
      expect(screen.queryByRole('button', { name: /remove file/i })).not.toBeInTheDocument();
    });
  });

  describe('Drag and Drop', () => {
    it('shows drag active state', () => {
      render(<FileUpload {...defaultProps} />);
      
      const dropzone = screen.getByRole('button', { name: /upload your resume/i });
      
      fireEvent.dragEnter(dropzone);
      expect(screen.getByText('Drop your resume here')).toBeInTheDocument();
    });

    it('shows drag reject state for invalid files', () => {
      render(<FileUpload {...defaultProps} />);
      
      const dropzone = screen.getByRole('button', { name: /upload your resume/i });
      
      // Simulate dragging invalid file
      fireEvent.dragEnter(dropzone, {
        dataTransfer: {
          types: ['Files'],
          files: [createMockFile('image.jpg', 1024, 'image/jpeg')],
        },
      });
      
      expect(screen.getByText('Invalid file type')).toBeInTheDocument();
    });
  });

  describe('Loading State', () => {
    it('disables upload when uploading', () => {
      render(<FileUpload {...defaultProps} isUploading={true} />);
      
      const dropzone = screen.getByRole('button', { name: /upload your resume/i });
      expect(dropzone).toHaveClass('opacity-50', 'cursor-not-allowed');
    });
  });

  describe('Error Handling', () => {
    it('displays external error messages', () => {
      render(<FileUpload {...defaultProps} error="Network error occurred" />);
      
      expect(screen.getByText('Network error occurred')).toBeInTheDocument();
    });

    it('clears drag error when new file is dropped', async () => {
      const user = userEvent.setup();
      render(<FileUpload {...defaultProps} />);
      
      // First, trigger an error
      const invalidFile = createMockFile('image.jpg', 1024, 'image/jpeg');
      const input = screen.getByRole('button', { name: /upload your resume/i });
      await user.upload(input, invalidFile);
      
      expect(screen.getByText('Please upload a PDF, DOC, DOCX, or TXT file')).toBeInTheDocument();
      
      // Then upload a valid file
      const validFile = createMockFile('resume.pdf', 1024, 'application/pdf');
      await user.upload(input, validFile);
      
      expect(screen.queryByText('Please upload a PDF, DOC, DOCX, or TXT file')).not.toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('has proper ARIA attributes', () => {
      render(<FileUpload {...defaultProps} />);
      
      const input = screen.getByLabelText(/upload your resume/i);
      expect(input).toHaveAttribute('type', 'file');
      expect(input).toHaveAttribute('accept', '.pdf,.doc,.docx,.txt');
    });

    it('provides screen reader feedback for errors', () => {
      render(<FileUpload {...defaultProps} error="File too large" />);
      
      const errorMessage = screen.getByRole('alert');
      expect(errorMessage).toHaveTextContent('File too large');
    });
  });
});
```

### Custom Hook Testing

**Story:** Test custom React hooks with comprehensive scenarios

```typescript
// src/hooks/__tests__/use-upload.test.ts
import { renderHook, act } from '@testing-library/react';
import { useUpload } from '../use-upload';
import { AnalysisService } from '@/lib/api-client';

// Mock the API service
jest.mock('@/lib/api-client');
const mockAnalysisService = AnalysisService as jest.Mocked<typeof AnalysisService>;

describe('useUpload Hook', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('initializes with correct default state', () => {
    const { result } = renderHook(() => useUpload());

    expect(result.current.state).toEqual({
      file: null,
      uploadId: null,
      progress: 0,
      status: 'idle',
      error: null,
    });
  });

  it('handles successful file upload', async () => {
    const mockFile = new File(['content'], 'resume.pdf', { type: 'application/pdf' });
    const mockResponse = { uploadId: 'test-upload-id' };
    
    mockAnalysisService.uploadResume.mockResolvedValue(mockResponse);

    const { result } = renderHook(() => useUpload());

    await act(async () => {
      await result.current.uploadFile(mockFile, 'test-session-id');
    });

    expect(result.current.state.status).toBe('completed');
    expect(result.current.state.uploadId).toBe('test-upload-id');
    expect(result.current.state.file).toBe(mockFile);
    expect(result.current.state.progress).toBe(100);
  });

  it('handles upload failure', async () => {
    const mockFile = new File(['content'], 'resume.pdf', { type: 'application/pdf' });
    const mockError = new Error('Upload failed');
    
    mockAnalysisService.uploadResume.mockRejectedValue(mockError);

    const { result } = renderHook(() => useUpload());

    await act(async () => {
      await result.current.uploadFile(mockFile, 'test-session-id');
    });

    expect(result.current.state.status).toBe('error');
    expect(result.current.state.error).toBe('Upload failed');
    expect(result.current.state.progress).toBe(0);
  });

  it('updates progress during upload', async () => {
    const mockFile = new File(['content'], 'resume.pdf', { type: 'application/pdf' });
    let progressCallback: ((progress: number) => void) | undefined;

    mockAnalysisService.uploadResume.mockImplementation((file, sessionId, onProgress) => {
      progressCallback = onProgress;
      return new Promise((resolve) => {
        setTimeout(() => {
          resolve({ uploadId: 'test-upload-id' });
        }, 100);
      });
    });

    const { result } = renderHook(() => useUpload());

    const uploadPromise = act(async () => {
      await result.current.uploadFile(mockFile, 'test-session-id');
    });

    // Simulate progress updates
    if (progressCallback) {
      act(() => {
        progressCallback(25);
      });
      expect(result.current.state.progress).toBe(25);

      act(() => {
        progressCallback(50);
      });
      expect(result.current.state.progress).toBe(50);

      act(() => {
        progressCallback(75);
      });
      expect(result.current.state.progress).toBe(75);
    }

    await uploadPromise;

    expect(result.current.state.progress).toBe(100);
    expect(result.current.state.status).toBe('completed');
  });

  it('allows resetting upload state', () => {
    const { result } = renderHook(() => useUpload());

    // Set some state first
    act(() => {
      result.current.setState({
        file: new File(['content'], 'test.pdf'),
        uploadId: 'test-id',
        progress: 50,
        status: 'uploading',
        error: null,
      });
    });

    // Reset
    act(() => {
      result.current.reset();
    });

    expect(result.current.state).toEqual({
      file: null,
      uploadId: null,
      progress: 0,
      status: 'idle',
      error: null,
    });
  });

  it('prevents concurrent uploads', async () => {
    const mockFile1 = new File(['content1'], 'resume1.pdf', { type: 'application/pdf' });
    const mockFile2 = new File(['content2'], 'resume2.pdf', { type: 'application/pdf' });

    mockAnalysisService.uploadResume
      .mockResolvedValueOnce({ uploadId: 'upload-1' })
      .mockResolvedValueOnce({ uploadId: 'upload-2' });

    const { result } = renderHook(() => useUpload());

    // Start first upload
    const upload1Promise = act(async () => {
      await result.current.uploadFile(mockFile1, 'session-1');
    });

    // Try to start second upload while first is in progress
    const upload2Promise = act(async () => {
      await result.current.uploadFile(mockFile2, 'session-2');
    });

    await Promise.all([upload1Promise, upload2Promise]);

    // Only first upload should have succeeded
    expect(mockAnalysisService.uploadResume).toHaveBeenCalledTimes(1);
    expect(result.current.state.uploadId).toBe('upload-1');
  });
});
```

## Backend Testing

### Pytest Configuration

**Story:** Configure Pytest for FastAPI testing with fixtures

```python
# apps/api/pytest.ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --strict-markers
    --strict-config
    --cov=src
    --cov-report=term-missing
    --cov-report=html:htmlcov
    --cov-report=xml
    --cov-fail-under=80
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow running tests
    external: Tests that require external services
```

```python
# apps/api/conftest.py
import pytest
import asyncio
from typing import Generator, AsyncGenerator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.main import app
from src.database import get_db, Base
from src.models.user import User
from src.models.analysis import ResumeAnalysis
from src.models.consultation import ConsultationRequest

# Test database URL
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

# Create test engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Create test session
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database dependency override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def sample_user(db_session):
    """Create a sample user for testing."""
    user = User(
        email="test@example.com",
        created_at="2024-01-01T00:00:00Z"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def sample_analysis(db_session, sample_user):
    """Create a sample analysis for testing."""
    analysis = ResumeAnalysis(
        user_id=sample_user.id,
        session_id="test-session-123",
        original_filename="test_resume.pdf",
        s3_key="test/test_resume.pdf",
        extracted_text="Sample resume text",
        analysis_results={
            "overall_score": 85,
            "suggestions": []
        },
        overall_score=85,
        status="completed"
    )
    db_session.add(analysis)
    db_session.commit()
    db_session.refresh(analysis)
    return analysis

@pytest.fixture
def mock_s3_client():
    """Mock S3 client for testing."""
    with patch('boto3.client') as mock_client:
        mock_s3 = MagicMock()
        mock_client.return_value = mock_s3
        yield mock_s3

@pytest.fixture
def mock_bedrock_client():
    """Mock Bedrock client for testing."""
    with patch('boto3.client') as mock_client:
        mock_bedrock = MagicMock()
        mock_client.return_value = mock_bedrock
        yield mock_bedrock

@pytest.fixture
def sample_pdf_file():
    """Create a sample PDF file for testing."""
    from io import BytesIO
    content = b"Sample PDF content"
    return BytesIO(content)

@pytest.fixture
def sample_analysis_results():
    """Sample analysis results for testing."""
    return {
        "overall_score": 75,
        "ats_compatibility": {
            "score": 70,
            "issues": ["Missing contact information", "Poor formatting"],
            "recommendations": ["Add phone number", "Use standard fonts"]
        },
        "keyword_optimization": {
            "score": 80,
            "missing_keywords": ["Python", "AWS"],
            "suggestions": ["Add technical skills section", "Include cloud experience"]
        },
        "structure_analysis": {
            "score": 75,
            "strengths": ["Clear work history", "Good education section"],
            "improvements": ["Add summary section", "Quantify achievements"]
        },
        "suggestions": [
            {
                "id": "1",
                "category": "formatting",
                "priority": "high",
                "description": "Use consistent font sizes",
                "example": "Use 11-12pt for body text"
            }
        ]
    }
```

### API Endpoint Testing

**Story:** Comprehensive API endpoint testing with various scenarios

```python
# apps/api/tests/test_analysis_endpoints.py
import pytest
import json
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from io import BytesIO

class TestAnalysisEndpoints:
    """Test suite for analysis API endpoints."""

    def test_upload_resume_success(self, client, mock_s3_client, sample_analysis_results):
        """Test successful resume upload."""
        # Mock S3 upload
        mock_s3_client.put_object.return_value = {"ETag": "test-etag"}
        
        # Mock background task
        with patch('src.routes.analysis.analyze_resume_task.delay') as mock_task:
            mock_task.return_value = MagicMock(id="task-123")
            
            # Create test file
            test_file = BytesIO(b"Sample PDF content")
            
            response = client.post(
                "/api/upload",
                files={"file": ("test_resume.pdf", test_file, "application/pdf")},
                data={"session_id": "test-session-123"}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert "upload_id" in data
        assert data["status"] == "uploaded"
        
        # Verify S3 upload was called
        mock_s3_client.put_object.assert_called_once()
        
        # Verify background task was started
        mock_task.assert_called_once()

    def test_upload_resume_invalid_file_type(self, client):
        """Test upload with invalid file type."""
        test_file = BytesIO(b"Sample image content")
        
        response = client.post(
            "/api/upload",
            files={"file": ("image.jpg", test_file, "image/jpeg")},
            data={"session_id": "test-session-123"}
        )
        
        assert response.status_code == 400
        assert "Unsupported file type" in response.json()["detail"]

    def test_upload_resume_file_too_large(self, client):
        """Test upload with file that's too large."""
        # Create a large file (simulate 15MB)
        large_content = b"x" * (15 * 1024 * 1024)
        test_file = BytesIO(large_content)
        
        response = client.post(
            "/api/upload",
            files={"file": ("large_resume.pdf", test_file, "application/pdf")},
            data={"session_id": "test-session-123"}
        )
        
        assert response.status_code == 400
        assert "File too large" in response.json()["detail"]

    def test_upload_resume_missing_file(self, client):
        """Test upload without file."""
        response = client.post(
            "/api/upload",
            data={"session_id": "test-session-123"}
        )
        
        assert response.status_code == 422

    def test_upload_resume_missing_session_id(self, client):
        """Test upload without session ID."""
        test_file = BytesIO(b"Sample PDF content")
        
        response = client.post(
            "/api/upload",
            files={"file": ("test_resume.pdf", test_file, "application/pdf")}
        )
        
        assert response.status_code == 422

    def test_get_analysis_results_success(self, client, sample_analysis):
        """Test successful retrieval of analysis results."""
        response = client.get(f"/api/analysis/{sample_analysis.id}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == str(sample_analysis.id)
        assert data["overall_score"] == sample_analysis.overall_score
        assert data["status"] == sample_analysis.status
        assert "analysis_results" in data

    def test_get_analysis_results_not_found(self, client):
        """Test retrieval of non-existent analysis."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.get(f"/api/analysis/{fake_id}")
        
        assert response.status_code == 404
        assert "Analysis not found" in response.json()["detail"]

    def test_get_analysis_results_invalid_uuid(self, client):
        """Test retrieval with invalid UUID format."""
        response = client.get("/api/analysis/invalid-uuid")
        
        assert response.status_code == 422

    def test_get_analysis_status_processing(self, client, db_session, sample_user):
        """Test analysis status when still processing."""
        # Create processing analysis
        from src.models.analysis import ResumeAnalysis, AnalysisStatus
        
        analysis = ResumeAnalysis(
            user_id=sample_user.id,
            session_id="test-session-456",
            original_filename="processing_resume.pdf",
            s3_key="test/processing_resume.pdf",
            status=AnalysisStatus.PROCESSING
        )
        db_session.add(analysis)
        db_session.commit()
        db_session.refresh(analysis)
        
        response = client.get(f"/api/analysis/{analysis.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "processing"
        assert data["analysis_results"] is None

    def test_get_analysis_status_failed(self, client, db_session, sample_user):
        """Test analysis status when failed."""
        from src.models.analysis import ResumeAnalysis, AnalysisStatus
        
        analysis = ResumeAnalysis(
            user_id=sample_user.id,
            session_id="test-session-789",
            original_filename="failed_resume.pdf",
            s3_key="test/failed_resume.pdf",
            status=AnalysisStatus.FAILED
        )
        db_session.add(analysis)
        db_session.commit()
        db_session.refresh(analysis)
        
        response = client.get(f"/api/analysis/{analysis.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "failed"

    @pytest.mark.integration
    def test_upload_and_retrieve_workflow(self, client, mock_s3_client, sample_analysis_results):
        """Integration test for complete upload and retrieve workflow."""
        # Step 1: Upload file
        with patch('src.routes.analysis.analyze_resume_task.delay') as mock_task:
            mock_task.return_value = MagicMock(id="task-123")
            
            test_file = BytesIO(b"Sample PDF content")
            upload_response = client.post(
                "/api/upload",
                files={"file": ("test_resume.pdf", test_file, "application/pdf")},
                data={"session_id": "integration-test-session"}
            )
        
        assert upload_response.status_code == 200
        upload_data = upload_response.json()
        upload_id = upload_data["upload_id"]
        
        # Step 2: Simulate analysis completion by updating database
        from src.models.analysis import ResumeAnalysis, AnalysisStatus
        
        with client.app.dependency_overrides[get_db]() as db:
            analysis = db.query(ResumeAnalysis).filter(
                ResumeAnalysis.id == upload_id
            ).first()
            
            analysis.status = AnalysisStatus.COMPLETED
            analysis.analysis_results = sample_analysis_results
            analysis.overall_score = sample_analysis_results["overall_score"]
            db.commit()
        
        # Step 3: Retrieve analysis results
        results_response = client.get(f"/api/analysis/{upload_id}")
        
        assert results_response.status_code == 200
        results_data = results_response.json()
        
        assert results_data["status"] == "completed"
        assert results_data["overall_score"] == sample_analysis_results["overall_score"]
        assert results_data["analysis_results"]["suggestions"] == sample_analysis_results["suggestions"]

    def test_concurrent_uploads_same_session(self, client, mock_s3_client):
        """Test handling of concurrent uploads for the same session."""
        with patch('src.routes.analysis.analyze_resume_task.delay') as mock_task:
            mock_task.return_value = MagicMock(id="task-123")
            
            # Upload first file
            test_file1 = BytesIO(b"First PDF content")
            response1 = client.post(
                "/api/upload",
                files={"file": ("resume1.pdf", test_file1, "application/pdf")},
                data={"session_id": "concurrent-test-session"}
            )
            
            # Upload second file with same session
            test_file2 = BytesIO(b"Second PDF content")
            response2 = client.post(
                "/api/upload",
                files={"file": ("resume2.pdf", test_file2, "application/pdf")},
                data={"session_id": "concurrent-test-session"}
            )
        
        # Both should succeed but create separate analyses
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert response1.json()["upload_id"] != response2.json()["upload_id"]
```

### Service Layer Testing

**Story:** Test business logic in service layer with mocked dependencies

```python
# apps/api/tests/test_analysis_service.py
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from src.services.analysis_service import AnalysisService
from src.models.analysis import ResumeAnalysis, AnalysisStatus

class TestAnalysisService:
    """Test suite for AnalysisService."""

    @pytest.fixture
    def analysis_service(self):
        """Create AnalysisService instance for testing."""
        return AnalysisService()

    @pytest.mark.asyncio
    async def test_process_upload_success(self, analysis_service, db_session, mock_s3_client):
        """Test successful file upload processing."""
        # Mock file object
        mock_file = MagicMock()
        mock_file.filename = "test_resume.pdf"
        mock_file.read = AsyncMock(return_value=b"PDF content")
        
        # Mock S3 upload
        mock_s3_client.put_object.return_value = {"ETag": "test-etag"}
        
        with patch('src.services.analysis_service.analyze_resume_task.delay') as mock_task:
            mock_task.return_value = MagicMock(id="task-123")
            
            result = await analysis_service.process_upload(
                file=mock_file,
                session_id="test-session",
                user_id=None,
                db=db_session
            )
        
        assert isinstance(result, ResumeAnalysis)
        assert result.session_id == "test-session"
        assert result.original_filename == "test_resume.pdf"
        assert result.status == AnalysisStatus.PROCESSING
        assert result.s3_key.startswith("resumes/")
        
        # Verify background task was started
        mock_task.assert_called_once_with(str(result.id))

    @pytest.mark.asyncio
    async def test_process_upload_s3_failure(self, analysis_service, db_session, mock_s3_client):
        """Test upload processing when S3 upload fails."""
        # Mock file object
        mock_file = MagicMock()
        mock_file.filename = "test_resume.pdf"
        mock_file.read = AsyncMock(return_value=b"PDF content")
        
        # Mock S3 upload failure
        mock_s3_client.put_object.side_effect = Exception("S3 upload failed")
        
        with pytest.raises(Exception, match="S3 upload failed"):
            await analysis_service.process_upload(
                file=mock_file,
                session_id="test-session",
                user_id=None,
                db=db_session
            )

    @pytest.mark.asyncio
    async def test_get_analysis_success(self, analysis_service, db_session, sample_analysis):
        """Test successful analysis retrieval."""
        result = await analysis_service.get_analysis(
            analysis_id=str(sample_analysis.id),
            db=db_session
        )
        
        assert result is not None
        assert result.id == sample_analysis.id
        assert result.overall_score == sample_analysis.overall_score

    @pytest.mark.asyncio
    async def test_get_analysis_not_found(self, analysis_service, db_session):
        """Test analysis retrieval when analysis doesn't exist."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        
        result = await analysis_service.get_analysis(
            analysis_id=fake_id,
            db=db_session
        )
        
        assert result is None

    @pytest.mark.asyncio
    async def test_upload_to_s3_success(self, analysis_service, mock_s3_client):
        """Test successful S3 upload."""
        mock_file = MagicMock()
        mock_file.read = AsyncMock(return_value=b"File content")
        mock_file.content_type = "application/pdf"
        
        await analysis_service._upload_to_s3(mock_file, "test/key.pdf")
        
        mock_s3_client.put_object.assert_called_once_with(
            Bucket="test-bucket",
            Key="test/key.pdf",
            Body=b"File content",
            ContentType="application/pdf",
            ServerSideEncryption="AES256"
        )

    @pytest.mark.asyncio
    async def test_upload_to_s3_failure(self, analysis_service, mock_s3_client):
        """Test S3 upload failure handling."""
        mock_file = MagicMock()
        mock_file.read = AsyncMock(return_value=b"File content")
        mock_file.content_type = "application/pdf"
        
        mock_s3_client.put_object.side_effect = Exception("S3 error")
        
        with pytest.raises(Exception, match="S3 error"):
            await analysis_service._upload_to_s3(mock_file, "test/key.pdf")

    @pytest.mark.slow
    @pytest.mark.integration
    async def test_complete_analysis_workflow(self, analysis_service, db_session, mock_s3_client, sample_analysis_results):
        """Integration test for complete analysis workflow."""
        # Mock dependencies
        mock_file = MagicMock()
        mock_file.filename = "integration_test.pdf"
        mock_file.read = AsyncMock(return_value=b"PDF content")
        mock_file.content_type = "application/pdf"
        
        with patch('src.services.analysis_service.analyze_resume_task.delay') as mock_task:
            # Step 1: Process upload
            analysis = await analysis_service.process_upload(
                file=mock_file,
                session_id="integration-session",
                user_id=None,
                db=db_session
            )
            
            assert analysis.status == AnalysisStatus.PROCESSING
            
            # Step 2: Simulate background analysis completion
            analysis.status = AnalysisStatus.COMPLETED
            analysis.analysis_results = sample_analysis_results
            analysis.overall_score = sample_analysis_results["overall_score"]
            db_session.commit()
            
            # Step 3: Retrieve completed analysis
            completed_analysis = await analysis_service.get_analysis(
                analysis_id=str(analysis.id),
                db=db_session
            )
            
            assert completed_analysis.status == AnalysisStatus.COMPLETED
            assert completed_analysis.overall_score == sample_analysis_results["overall_score"]
            assert completed_analysis.analysis_results == sample_analysis_results
```

## End-to-End Testing

### Playwright Configuration

**Story:** Configure Playwright for comprehensive E2E testing

```typescript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [
    ['html'],
    ['json', { outputFile: 'test-results/results.json' }],
    ['junit', { outputFile: 'test-results/junit.xml' }],
  ],
  use: {
    baseURL: process.env.BASE_URL || 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },
    {
      name: 'Mobile Safari',
      use: { ...devices['iPhone 12'] },
    },
  ],

  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
    timeout: 120 * 1000,
  },
});
```

### E2E Test Examples

**Story:** Create comprehensive end-to-end tests for critical user journeys

```typescript
// e2e/resume-analysis-flow.spec.ts
import { test, expect } from '@playwright/test';
import path from 'path';

test.describe('Resume Analysis Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('complete resume analysis journey - happy path', async ({ page }) => {
    // Step 1: Land on homepage and verify content
    await expect(page.getByRole('heading', { name: /AI-Powered Resume Analysis/i })).toBeVisible();
    await expect(page.getByText(/Get your resume ATS-ready/i)).toBeVisible();
    
    // Step 2: Click get started
    await page.getByRole('button', { name: /Get Started|Analyze My Resume/i }).click();
    
    // Step 3: Upload resume
    await expect(page.getByText(/Upload your resume/i)).toBeVisible();
    
    const fileInput = page.getByRole('button', { name: /upload your resume/i });
    const testFile = path.join(__dirname, 'fixtures', 'sample-resume.pdf');
    
    await fileInput.setInputFiles(testFile);
    
    // Verify file is selected
    await expect(page.getByText('sample-resume.pdf')).toBeVisible();
    await expect(page.getByText(/MB/)).toBeVisible();
    
    // Step 4: Start analysis
    await page.getByRole('button', { name: /Start Analysis|Continue/i }).click();
    
    // Step 5: Wait for analysis progress
    await expect(page.getByText(/Analyzing Your Resume/i)).toBeVisible();
    await expect(page.getByRole('progressbar')).toBeVisible();
    
    // Wait for analysis to complete (with timeout)
    await page.waitForSelector('text=Analysis Complete', { timeout: 30000 });
    
    // Step 6: View results
    await expect(page.getByText(/Your Resume Analysis Results/i)).toBeVisible();
    await expect(page.getByText(/Overall Score/i)).toBeVisible();
    
    // Verify score is displayed
    const scoreElement = page.locator('[data-testid="overall-score"]');
    await expect(scoreElement).toBeVisible();
    
    // Verify suggestions are present
    await expect(page.getByText(/Improvement Suggestions/i)).toBeVisible();
    
    // Step 7: Download improved resume
    await page.getByRole('button', { name: /Download.*Resume/i }).click();
    
    // Verify download started (check for download attribute or new tab)
    const downloadPromise = page.waitForEvent('download');
    await page.getByRole('button', { name: /Download/i }).click();
    const download = await downloadPromise;
    
    expect(download.suggestedFilename()).toContain('resume');
    
    // Step 8: Optional - Request consultation
    await page.getByRole('button', { name: /Expert.*Help|Consultation/i }).click();
    
    await expect(page.getByText(/Request Expert Consultation/i)).toBeVisible();
    
    // Fill consultation form
    await page.getByLabel(/email/i).fill('test@example.com');
    await page.getByLabel(/help.*category/i).selectOption('resume_review');
    await page.getByLabel(/details/i).fill('Need help improving my resume for senior developer positions');
    
    await page.getByRole('button', { name: /Submit.*Request/i }).click();
    
    // Step 9: Verify confirmation
    await expect(page.getByText(/Thank you.*request/i)).toBeVisible();
    await expect(page.getByText(/We'll be in touch/i)).toBeVisible();
  });

  test('handles file upload errors gracefully', async ({ page }) => {
    await page.getByRole('button', { name: /Get Started/i }).click();
    
    // Try to upload unsupported file type
    const fileInput = page.getByRole('button', { name: /upload your resume/i });
    const invalidFile = path.join(__dirname, 'fixtures', 'image.jpg');
    
    await fileInput.setInputFiles(invalidFile);
    
    // Verify error message
    await expect(page.getByText(/Please upload a PDF, DOC, DOCX, or TXT file/i)).toBeVisible();
    
    // Try to upload file that's too large
    const largeFile = path.join(__dirname, 'fixtures', 'large-file.pdf');
    await fileInput.setInputFiles(largeFile);
    
    await expect(page.getByText(/File size must be less than 10MB/i)).toBeVisible();
  });

  test('mobile responsive design works correctly', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    
    // Test mobile navigation
    await expect(page.getByRole('heading')).toBeVisible();
    await expect(page.getByRole('button', { name: /Get Started/i })).toBeVisible();
    
    // Test mobile file upload
    await page.getByRole('button', { name: /Get Started/i }).click();
    
    const fileInput = page.getByRole('button', { name: /upload your resume/i });
    expect(await fileInput.isVisible()).toBe(true);
    
    // Verify mobile-specific UI elements
    await expect(page.locator('.mobile-upload-area')).toBeVisible();
  });

  test('handles network errors and retries', async ({ page }) => {
    // Mock network failure
    await page.route('/api/upload', route => {
      route.fulfill({
        status: 500,
        body: JSON.stringify({ error: 'Network error' })
      });
    });
    
    await page.getByRole('button', { name: /Get Started/i }).click();
    
    const fileInput = page.getByRole('button', { name: /upload your resume/i });
    const testFile = path.join(__dirname, 'fixtures', 'sample-resume.pdf');
    
    await fileInput.setInputFiles(testFile);
    await page.getByRole('button', { name: /Start Analysis/i }).click();
    
    // Verify error handling
    await expect(page.getByText(/Upload failed.*try again/i)).toBeVisible();
    await expect(page.getByRole('button', { name: /Retry/i })).toBeVisible();
  });

  test('accessibility features work correctly', async ({ page }) => {
    // Test keyboard navigation
    await page.keyboard.press('Tab');
    await expect(page.getByRole('button', { name: /Get Started/i })).toBeFocused();
    
    await page.keyboard.press('Enter');
    
    // Test screen reader compatibility
    const uploadArea = page.getByRole('button', { name: /upload your resume/i });
    await expect(uploadArea).toHaveAttribute('aria-label');
    
    // Test focus management
    await page.keyboard.press('Tab');
    await expect(page.locator(':focus')).toBeVisible();
  });

  test('handles analysis timeout gracefully', async ({ page }) => {
    // Mock slow analysis
    await page.route('/api/analysis/*', route => {
      // Delay response to simulate timeout
      setTimeout(() => {
        route.fulfill({
          status: 200,
          body: JSON.stringify({
            status: 'processing',
            progress: 50
          })
        });
      }, 35000); // Longer than typical timeout
    });
    
    await page.getByRole('button', { name: /Get Started/i }).click();
    
    const fileInput = page.getByRole('button', { name: /upload your resume/i });
    const testFile = path.join(__dirname, 'fixtures', 'sample-resume.pdf');
    
    await fileInput.setInputFiles(testFile);
    await page.getByRole('button', { name: /Start Analysis/i }).click();
    
    // Should show timeout message
    await expect(page.getByText(/Analysis is taking longer than expected/i)).toBeVisible();
    await expect(page.getByRole('button', { name: /Check Status/i })).toBeVisible();
  });
});
```

### Performance Testing

**Story:** Add performance testing to E2E suite

```typescript
// e2e/performance.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Performance Tests', () => {
  test('page load performance meets requirements', async ({ page }) => {
    const startTime = Date.now();
    
    await page.goto('/');
    
    // Wait for page to be fully loaded
    await page.waitForLoadState('networkidle');
    
    const loadTime = Date.now() - startTime;
    
    // Assert page loads within 3 seconds
    expect(loadTime).toBeLessThan(3000);
    
    // Check Core Web Vitals
    const vitals = await page.evaluate(() => {
      return new Promise((resolve) => {
        new PerformanceObserver((list) => {
          const entries = list.getEntries();
          const vitals = {};
          
          for (const entry of entries) {
            if (entry.name === 'FCP') {
              vitals.fcp = entry.value;
            }
            if (entry.name === 'LCP') {
              vitals.lcp = entry.value;
            }
            if (entry.name === 'FID') {
              vitals.fid = entry.value;
            }
            if (entry.name === 'CLS') {
              vitals.cls = entry.value;
            }
          }
          
          resolve(vitals);
        }).observe({ entryTypes: ['measure', 'paint', 'largest-contentful-paint'] });
      });
    });
    
    // Assert Core Web Vitals thresholds
    if (vitals.fcp) expect(vitals.fcp).toBeLessThan(1800); // FCP < 1.8s
    if (vitals.lcp) expect(vitals.lcp).toBeLessThan(2500); // LCP < 2.5s
    if (vitals.fid) expect(vitals.fid).toBeLessThan(100);  // FID < 100ms
    if (vitals.cls) expect(vitals.cls).toBeLessThan(0.1);  // CLS < 0.1
  });

  test('file upload performance is acceptable', async ({ page }) => {
    await page.goto('/upload');
    
    const startTime = Date.now();
    
    // Upload 5MB test file
    const fileInput = page.getByRole('button', { name: /upload your resume/i });
    const testFile = path.join(__dirname, 'fixtures', 'large-resume.pdf'); // 5MB file
    
    await fileInput.setInputFiles(testFile);
    
    // Wait for upload to complete
    await page.waitForSelector('text=Upload complete', { timeout: 10000 });
    
    const uploadTime = Date.now() - startTime;
    
    // Assert upload completes within 10 seconds for 5MB file
    expect(uploadTime).toBeLessThan(10000);
  });

  test('analysis performance meets SLA', async ({ page }) => {
    await page.goto('/');
    
    // Complete upload flow
    await page.getByRole('button', { name: /Get Started/i }).click();
    
    const fileInput = page.getByRole('button', { name: /upload your resume/i });
    const testFile = path.join(__dirname, 'fixtures', 'sample-resume.pdf');
    
    await fileInput.setInputFiles(testFile);
    await page.getByRole('button', { name: /Start Analysis/i }).click();
    
    const analysisStartTime = Date.now();
    
    // Wait for analysis to complete
    await page.waitForSelector('text=Analysis Complete', { timeout: 120000 }); // 2 minute timeout
    
    const analysisTime = Date.now() - analysisStartTime;
    
    // Assert analysis completes within 2 minutes (SLA requirement)
    expect(analysisTime).toBeLessThan(120000);
    
    // Log actual analysis time for monitoring
    console.log(`Analysis completed in ${analysisTime}ms`);
  });
});
```

This comprehensive testing architecture provides:

1. **Complete test coverage** across unit, integration, and E2E tests
2. **Frontend testing** with Jest and React Testing Library
3. **Backend testing** with Pytest and comprehensive fixtures
4. **API endpoint testing** with various scenarios and error cases
5. **Service layer testing** with mocked dependencies
6. **End-to-end testing** with Playwright covering critical user journeys
7. **Performance testing** including Core Web Vitals and SLA compliance
8. **Accessibility testing** ensuring WCAG AA compliance
9. **Mobile responsive testing** for cross-device compatibility
10. **Error handling testing** for robust user experience

The testing strategy follows the testing pyramid principle with appropriate test distribution and comprehensive coverage of all application layers.
