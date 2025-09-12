# Frontend Architecture Stories

## Next.js Application Structure

### Project Structure

**Story:** Set up Next.js 14 application with App Router and TypeScript

```
apps/web/
├── src/
│   ├── app/                    # Next.js App Router
│   │   ├── layout.tsx          # Root layout
│   │   ├── page.tsx            # Landing page
│   │   ├── upload/
│   │   │   └── page.tsx        # Upload page
│   │   ├── analysis/
│   │   │   ├── page.tsx        # Analysis results
│   │   │   └── [id]/
│   │   │       └── page.tsx    # Specific analysis
│   │   ├── consultation/
│   │   │   └── page.tsx        # Consultation request
│   │   ├── thank-you/
│   │   │   └── page.tsx        # Thank you page
│   │   └── api/                # API routes
│   │       ├── upload/
│   │       │   └── route.ts
│   │       ├── analysis/
│   │       │   └── [id]/
│   │       │       └── route.ts
│   │       └── consultation/
│   │           └── route.ts
│   ├── components/             # React components
│   │   ├── ui/                 # Base UI components
│   │   │   ├── button.tsx
│   │   │   ├── input.tsx
│   │   │   ├── modal.tsx
│   │   │   ├── progress-bar.tsx
│   │   │   └── card.tsx
│   │   ├── layout/             # Layout components
│   │   │   ├── header.tsx
│   │   │   ├── footer.tsx
│   │   │   └── navigation.tsx
│   │   ├── forms/              # Form components
│   │   │   ├── file-upload.tsx
│   │   │   ├── consultation-form.tsx
│   │   │   └── feedback-form.tsx
│   │   ├── analysis/           # Analysis components
│   │   │   ├── analysis-progress.tsx
│   │   │   ├── results-display.tsx
│   │   │   ├── suggestion-card.tsx
│   │   │   └── score-display.tsx
│   │   └── landing/            # Landing page components
│   │       ├── hero-section.tsx
│   │       ├── how-it-works.tsx
│   │       ├── features.tsx
│   │       └── cta-section.tsx
│   ├── hooks/                  # Custom React hooks
│   │   ├── use-upload.ts
│   │   ├── use-analysis.ts
│   │   ├── use-session.ts
│   │   └── use-local-storage.ts
│   ├── lib/                    # Utilities and configurations
│   │   ├── api-client.ts       # API client setup
│   │   ├── utils.ts            # General utilities
│   │   ├── constants.ts        # App constants
│   │   └── validations.ts      # Form validation schemas
│   ├── stores/                 # State management
│   │   ├── upload-store.ts     # Upload state
│   │   ├── analysis-store.ts   # Analysis state
│   │   ├── session-store.ts    # Session state
│   │   └── ui-store.ts         # UI state
│   ├── styles/                 # Styling
│   │   ├── globals.css         # Global styles
│   │   └── components.css      # Component styles
│   └── types/                  # TypeScript types
│       ├── api.ts              # API response types
│       ├── analysis.ts         # Analysis types
│       └── ui.ts               # UI component types
├── public/                     # Static assets
│   ├── images/
│   ├── icons/
│   └── favicon.ico
├── tailwind.config.js          # Tailwind configuration
├── next.config.js              # Next.js configuration
├── tsconfig.json               # TypeScript configuration
└── package.json                # Dependencies
```

## Component Architecture

### Base UI Components

**Story:** Create reusable UI components with Tailwind CSS

```typescript
// src/components/ui/button.tsx
import React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/utils';

const buttonVariants = cva(
  'inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50',
  {
    variants: {
      variant: {
        default: 'bg-primary text-primary-foreground shadow hover:bg-primary/90',
        destructive: 'bg-destructive text-destructive-foreground shadow-sm hover:bg-destructive/90',
        outline: 'border border-input bg-background shadow-sm hover:bg-accent hover:text-accent-foreground',
        secondary: 'bg-secondary text-secondary-foreground shadow-sm hover:bg-secondary/80',
        ghost: 'hover:bg-accent hover:text-accent-foreground',
        link: 'text-primary underline-offset-4 hover:underline',
      },
      size: {
        default: 'h-9 px-4 py-2',
        sm: 'h-8 rounded-md px-3 text-xs',
        lg: 'h-10 rounded-md px-8',
        icon: 'h-9 w-9',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  }
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    return (
      <button
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    );
  }
);

Button.displayName = 'Button';

export { Button, buttonVariants };
```

```typescript
// src/components/ui/progress-bar.tsx
import React from 'react';
import { cn } from '@/lib/utils';

interface ProgressBarProps {
  value: number;
  max?: number;
  className?: string;
  showPercentage?: boolean;
  size?: 'sm' | 'md' | 'lg';
  variant?: 'default' | 'success' | 'warning' | 'error';
}

const sizeVariants = {
  sm: 'h-2',
  md: 'h-3',
  lg: 'h-4',
};

const colorVariants = {
  default: 'bg-blue-500',
  success: 'bg-green-500',
  warning: 'bg-yellow-500',
  error: 'bg-red-500',
};

export const ProgressBar: React.FC<ProgressBarProps> = ({
  value,
  max = 100,
  className,
  showPercentage = false,
  size = 'md',
  variant = 'default',
}) => {
  const percentage = Math.min((value / max) * 100, 100);
  
  return (
    <div className={cn('w-full', className)}>
      <div className={cn(
        'w-full bg-gray-200 rounded-full overflow-hidden',
        sizeVariants[size]
      )}>
        <div
          className={cn(
            'h-full transition-all duration-300 ease-out rounded-full',
            colorVariants[variant]
          )}
          style={{ width: `${percentage}%` }}
        />
      </div>
      {showPercentage && (
        <div className="text-sm text-gray-600 mt-1">
          {Math.round(percentage)}%
        </div>
      )}
    </div>
  );
};
```

### File Upload Component

**Story:** Create drag-and-drop file upload with validation

```typescript
// src/components/forms/file-upload.tsx
import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, File, X, AlertCircle } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';

interface FileUploadProps {
  onFileSelect: (file: File) => void;
  onFileRemove: () => void;
  selectedFile: File | null;
  isUploading?: boolean;
  error?: string;
  className?: string;
}

const ACCEPTED_FILE_TYPES = {
  'application/pdf': ['.pdf'],
  'application/msword': ['.doc'],
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
  'text/plain': ['.txt'],
};

const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB

export const FileUpload: React.FC<FileUploadProps> = ({
  onFileSelect,
  onFileRemove,
  selectedFile,
  isUploading = false,
  error,
  className,
}) => {
  const [dragError, setDragError] = useState<string>('');

  const onDrop = useCallback(
    (acceptedFiles: File[], rejectedFiles: any[]) => {
      setDragError('');

      if (rejectedFiles.length > 0) {
        const rejection = rejectedFiles[0];
        if (rejection.errors.some((e: any) => e.code === 'file-too-large')) {
          setDragError('File size must be less than 10MB');
        } else if (rejection.errors.some((e: any) => e.code === 'file-invalid-type')) {
          setDragError('Please upload a PDF, DOC, DOCX, or TXT file');
        } else {
          setDragError('Invalid file. Please try again.');
        }
        return;
      }

      if (acceptedFiles.length > 0) {
        onFileSelect(acceptedFiles[0]);
      }
    },
    [onFileSelect]
  );

  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop,
    accept: ACCEPTED_FILE_TYPES,
    maxSize: MAX_FILE_SIZE,
    multiple: false,
    disabled: isUploading,
  });

  const displayError = error || dragError;

  return (
    <div className={cn('w-full', className)}>
      {!selectedFile ? (
        <div
          {...getRootProps()}
          className={cn(
            'border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors',
            isDragActive && !isDragReject && 'border-blue-500 bg-blue-50',
            isDragReject && 'border-red-500 bg-red-50',
            isUploading && 'opacity-50 cursor-not-allowed',
            !isDragActive && !isDragReject && 'border-gray-300 hover:border-gray-400'
          )}
        >
          <input {...getInputProps()} />
          <div className="flex flex-col items-center space-y-4">
            <Upload
              className={cn(
                'w-12 h-12',
                isDragActive && !isDragReject && 'text-blue-500',
                isDragReject && 'text-red-500',
                !isDragActive && !isDragReject && 'text-gray-400'
              )}
            />
            <div>
              <p className="text-lg font-medium text-gray-900">
                {isDragActive
                  ? isDragReject
                    ? 'Invalid file type'
                    : 'Drop your resume here'
                  : 'Upload your resume'}
              </p>
              <p className="text-sm text-gray-500 mt-1">
                Drag and drop or click to browse
              </p>
              <p className="text-xs text-gray-400 mt-2">
                Supports PDF, DOC, DOCX, TXT (max 10MB)
              </p>
            </div>
          </div>
        </div>
      ) : (
        <div className="border rounded-lg p-4 bg-gray-50">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <File className="w-8 h-8 text-blue-500" />
              <div>
                <p className="font-medium text-gray-900">{selectedFile.name}</p>
                <p className="text-sm text-gray-500">
                  {(selectedFile.size / 1024 / 1024).toFixed(1)} MB
                </p>
              </div>
            </div>
            {!isUploading && (
              <Button
                variant="ghost"
                size="icon"
                onClick={onFileRemove}
                className="text-gray-400 hover:text-red-500"
              >
                <X className="w-4 h-4" />
              </Button>
            )}
          </div>
        </div>
      )}

      {displayError && (
        <div className="mt-2 flex items-center space-x-2 text-red-600">
          <AlertCircle className="w-4 h-4" />
          <p className="text-sm">{displayError}</p>
        </div>
      )}
    </div>
  );
};
```

### Analysis Progress Component

**Story:** Create real-time analysis progress display

```typescript
// src/components/analysis/analysis-progress.tsx
import React, { useEffect, useState } from 'react';
import { CheckCircle, Clock, Cog, FileText, Sparkles } from 'lucide-react';
import { ProgressBar } from '@/components/ui/progress-bar';
import { cn } from '@/lib/utils';

interface AnalysisStep {
  id: string;
  title: string;
  description: string;
  icon: React.ReactNode;
  duration: number; // in seconds
}

interface AnalysisProgressProps {
  isAnalyzing: boolean;
  progress: number;
  currentStep?: string;
  onComplete?: () => void;
  className?: string;
}

const ANALYSIS_STEPS: AnalysisStep[] = [
  {
    id: 'upload',
    title: 'Processing Upload',
    description: 'Extracting text from your resume...',
    icon: <FileText className="w-5 h-5" />,
    duration: 3,
  },
  {
    id: 'analysis',
    title: 'AI Analysis',
    description: 'Analyzing ATS compatibility and content...',
    icon: <Sparkles className="w-5 h-5" />,
    duration: 15,
  },
  {
    id: 'suggestions',
    title: 'Generating Suggestions',
    description: 'Creating personalized improvement recommendations...',
    icon: <Cog className="w-5 h-5" />,
    duration: 7,
  },
  {
    id: 'complete',
    title: 'Analysis Complete',
    description: 'Your resume analysis is ready!',
    icon: <CheckCircle className="w-5 h-5" />,
    duration: 0,
  },
];

export const AnalysisProgress: React.FC<AnalysisProgressProps> = ({
  isAnalyzing,
  progress,
  currentStep = 'upload',
  onComplete,
  className,
}) => {
  const [timeElapsed, setTimeElapsed] = useState(0);
  const [estimatedTimeRemaining, setEstimatedTimeRemaining] = useState(25);

  useEffect(() => {
    if (!isAnalyzing) return;

    const interval = setInterval(() => {
      setTimeElapsed((prev) => prev + 1);
      
      // Calculate estimated time remaining based on progress
      if (progress > 0) {
        const totalEstimatedTime = (timeElapsed / progress) * 100;
        setEstimatedTimeRemaining(Math.max(0, Math.round(totalEstimatedTime - timeElapsed)));
      }
    }, 1000);

    return () => clearInterval(interval);
  }, [isAnalyzing, progress, timeElapsed]);

  useEffect(() => {
    if (progress >= 100 && onComplete) {
      setTimeout(onComplete, 1000);
    }
  }, [progress, onComplete]);

  const currentStepIndex = ANALYSIS_STEPS.findIndex(step => step.id === currentStep);
  const currentStepData = ANALYSIS_STEPS[currentStepIndex];

  return (
    <div className={cn('w-full max-w-2xl mx-auto', className)}>
      {/* Progress Header */}
      <div className="text-center mb-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Analyzing Your Resume
        </h2>
        <p className="text-gray-600">
          Our AI is reviewing your resume to provide personalized suggestions
        </p>
      </div>

      {/* Progress Bar */}
      <div className="mb-8">
        <ProgressBar
          value={progress}
          size="lg"
          variant={progress >= 100 ? 'success' : 'default'}
          showPercentage
          className="mb-4"
        />
        
        <div className="flex justify-between text-sm text-gray-500">
          <span>{timeElapsed}s elapsed</span>
          {estimatedTimeRemaining > 0 && (
            <span>~{estimatedTimeRemaining}s remaining</span>
          )}
        </div>
      </div>

      {/* Current Step Display */}
      {currentStepData && (
        <div className="bg-blue-50 rounded-lg p-6 mb-8">
          <div className="flex items-center space-x-4">
            <div className="flex-shrink-0">
              <div className="w-12 h-12 bg-blue-500 rounded-full flex items-center justify-center text-white">
                {progress >= 100 ? (
                  <CheckCircle className="w-6 h-6" />
                ) : (
                  <div className="animate-spin">
                    <Cog className="w-6 h-6" />
                  </div>
                )}
              </div>
            </div>
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-gray-900">
                {currentStepData.title}
              </h3>
              <p className="text-gray-600">
                {currentStepData.description}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Steps Timeline */}
      <div className="space-y-4">
        {ANALYSIS_STEPS.map((step, index) => {
          const isCompleted = index < currentStepIndex || progress >= 100;
          const isCurrent = index === currentStepIndex && progress < 100;
          const isPending = index > currentStepIndex;

          return (
            <div
              key={step.id}
              className={cn(
                'flex items-center space-x-4 p-3 rounded-lg transition-colors',
                isCompleted && 'bg-green-50',
                isCurrent && 'bg-blue-50',
                isPending && 'bg-gray-50'
              )}
            >
              <div
                className={cn(
                  'flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center',
                  isCompleted && 'bg-green-500 text-white',
                  isCurrent && 'bg-blue-500 text-white',
                  isPending && 'bg-gray-300 text-gray-500'
                )}
              >
                {isCompleted ? (
                  <CheckCircle className="w-4 h-4" />
                ) : isCurrent ? (
                  <Clock className="w-4 h-4" />
                ) : (
                  step.icon
                )}
              </div>
              <div className="flex-1">
                <h4
                  className={cn(
                    'font-medium',
                    isCompleted && 'text-green-900',
                    isCurrent && 'text-blue-900',
                    isPending && 'text-gray-500'
                  )}
                >
                  {step.title}
                </h4>
                <p
                  className={cn(
                    'text-sm',
                    isCompleted && 'text-green-700',
                    isCurrent && 'text-blue-700',
                    isPending && 'text-gray-400'
                  )}
                >
                  {step.description}
                </p>
              </div>
            </div>
          );
        })}
      </div>

      {/* Completion Message */}
      {progress >= 100 && (
        <div className="mt-8 text-center">
          <div className="inline-flex items-center space-x-2 text-green-600 bg-green-50 px-4 py-2 rounded-full">
            <CheckCircle className="w-5 h-5" />
            <span className="font-medium">Analysis Complete!</span>
          </div>
        </div>
      )}
    </div>
  );
};
```

### Results Display Component

**Story:** Create comprehensive results display with suggestions

```typescript
// src/components/analysis/results-display.tsx
import React, { useState } from 'react';
import { 
  TrendingUp, 
  AlertTriangle, 
  CheckCircle, 
  ChevronDown, 
  ChevronRight, 
  Download,
  Star,
  Target,
  FileText
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { ProgressBar } from '@/components/ui/progress-bar';
import { cn } from '@/lib/utils';

interface Suggestion {
  id: string;
  category: 'formatting' | 'content' | 'keywords' | 'structure';
  priority: 'high' | 'medium' | 'low';
  description: string;
  example?: string;
  before?: string;
  after?: string;
}

interface AnalysisResults {
  overallScore: number;
  atsCompatibility: {
    score: number;
    issues: string[];
    recommendations: string[];
  };
  keywordOptimization: {
    score: number;
    missingKeywords: string[];
    suggestions: string[];
  };
  structureAnalysis: {
    score: number;
    strengths: string[];
    improvements: string[];
  };
  suggestions: Suggestion[];
}

interface ResultsDisplayProps {
  results: AnalysisResults;
  onDownload: () => void;
  onConsultationRequest: () => void;
  className?: string;
}

const categoryIcons = {
  formatting: <FileText className="w-5 h-5" />,
  content: <Star className="w-5 h-5" />,
  keywords: <Target className="w-5 h-5" />,
  structure: <TrendingUp className="w-5 h-5" />,
};

const categoryColors = {
  formatting: 'blue',
  content: 'purple',
  keywords: 'green',
  structure: 'orange',
};

const priorityColors = {
  high: 'red',
  medium: 'yellow',
  low: 'blue',
};

export const ResultsDisplay: React.FC<ResultsDisplayProps> = ({
  results,
  onDownload,
  onConsultationRequest,
  className,
}) => {
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set(['overview']));
  const [expandedSuggestions, setExpandedSuggestions] = useState<Set<string>>(new Set());

  const toggleSection = (sectionId: string) => {
    const newExpanded = new Set(expandedSections);
    if (newExpanded.has(sectionId)) {
      newExpanded.delete(sectionId);
    } else {
      newExpanded.add(sectionId);
    }
    setExpandedSections(newExpanded);
  };

  const toggleSuggestion = (suggestionId: string) => {
    const newExpanded = new Set(expandedSuggestions);
    if (newExpanded.has(suggestionId)) {
      newExpanded.delete(suggestionId);
    } else {
      newExpanded.add(suggestionId);
    }
    setExpandedSuggestions(newExpanded);
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'green';
    if (score >= 60) return 'yellow';
    return 'red';
  };

  const getScoreVariant = (score: number): 'success' | 'warning' | 'error' => {
    if (score >= 80) return 'success';
    if (score >= 60) return 'warning';
    return 'error';
  };

  const groupedSuggestions = results.suggestions.reduce((acc, suggestion) => {
    if (!acc[suggestion.category]) {
      acc[suggestion.category] = [];
    }
    acc[suggestion.category].push(suggestion);
    return acc;
  }, {} as Record<string, Suggestion[]>);

  return (
    <div className={cn('w-full max-w-4xl mx-auto space-y-6', className)}>
      {/* Header */}
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Your Resume Analysis Results
        </h1>
        <p className="text-gray-600">
          Here's how your resume performs and what you can improve
        </p>
      </div>

      {/* Overall Score */}
      <div className="bg-white rounded-lg border shadow-sm p-6">
        <div className="text-center">
          <div className="mb-4">
            <div className="inline-flex items-center justify-center w-24 h-24 rounded-full bg-gray-100 mb-4">
              <span className={cn(
                'text-3xl font-bold',
                `text-${getScoreColor(results.overallScore)}-600`
              )}>
                {results.overallScore}
              </span>
            </div>
            <h2 className="text-2xl font-bold text-gray-900">Overall Score</h2>
            <p className="text-gray-600 mt-1">
              {results.overallScore >= 80 
                ? 'Excellent! Your resume is well-optimized.'
                : results.overallScore >= 60
                ? 'Good foundation with room for improvement.'
                : 'Significant improvements needed for better results.'}
            </p>
          </div>
          
          <div className="flex justify-center space-x-4 mt-6">
            <Button onClick={onDownload} size="lg">
              <Download className="w-4 h-4 mr-2" />
              Download Improved Resume
            </Button>
            <Button 
              variant="outline" 
              onClick={onConsultationRequest}
              size="lg"
            >
              Get Expert Help
            </Button>
          </div>
        </div>
      </div>

      {/* Score Breakdown */}
      <div className="bg-white rounded-lg border shadow-sm">
        <div 
          className="p-6 cursor-pointer flex items-center justify-between"
          onClick={() => toggleSection('breakdown')}
        >
          <h3 className="text-lg font-semibold text-gray-900">Score Breakdown</h3>
          {expandedSections.has('breakdown') ? (
            <ChevronDown className="w-5 h-5 text-gray-500" />
          ) : (
            <ChevronRight className="w-5 h-5 text-gray-500" />
          )}
        </div>
        
        {expandedSections.has('breakdown') && (
          <div className="px-6 pb-6 space-y-6">
            {/* ATS Compatibility */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="font-medium text-gray-900">ATS Compatibility</span>
                <span className={cn(
                  'font-semibold',
                  `text-${getScoreColor(results.atsCompatibility.score)}-600`
                )}>
                  {results.atsCompatibility.score}/100
                </span>
              </div>
              <ProgressBar 
                value={results.atsCompatibility.score} 
                variant={getScoreVariant(results.atsCompatibility.score)}
                className="mb-2"
              />
              <p className="text-sm text-gray-600">
                How well your resume works with Applicant Tracking Systems
              </p>
            </div>

            {/* Keyword Optimization */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="font-medium text-gray-900">Keyword Optimization</span>
                <span className={cn(
                  'font-semibold',
                  `text-${getScoreColor(results.keywordOptimization.score)}-600`
                )}>
                  {results.keywordOptimization.score}/100
                </span>
              </div>
              <ProgressBar 
                value={results.keywordOptimization.score} 
                variant={getScoreVariant(results.keywordOptimization.score)}
                className="mb-2"
              />
              <p className="text-sm text-gray-600">
                Relevance of keywords for tech industry positions
              </p>
            </div>

            {/* Structure Analysis */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="font-medium text-gray-900">Structure & Format</span>
                <span className={cn(
                  'font-semibold',
                  `text-${getScoreColor(results.structureAnalysis.score)}-600`
                )}>
                  {results.structureAnalysis.score}/100
                </span>
              </div>
              <ProgressBar 
                value={results.structureAnalysis.score} 
                variant={getScoreVariant(results.structureAnalysis.score)}
                className="mb-2"
              />
              <p className="text-sm text-gray-600">
                Organization, formatting, and overall structure quality
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Improvement Suggestions */}
      <div className="bg-white rounded-lg border shadow-sm">
        <div className="p-6 border-b">
          <h3 className="text-lg font-semibold text-gray-900">
            Improvement Suggestions ({results.suggestions.length})
          </h3>
          <p className="text-gray-600 mt-1">
            Prioritized recommendations to enhance your resume
          </p>
        </div>

        <div className="divide-y">
          {Object.entries(groupedSuggestions).map(([category, suggestions]) => (
            <div key={category} className="p-6">
              <div className="flex items-center space-x-3 mb-4">
                <div className={cn(
                  'p-2 rounded-lg',
                  `bg-${categoryColors[category as keyof typeof categoryColors]}-100`
                )}>
                  {categoryIcons[category as keyof typeof categoryIcons]}
                </div>
                <div>
                  <h4 className="font-semibold text-gray-900 capitalize">
                    {category} ({suggestions.length})
                  </h4>
                  <p className="text-sm text-gray-600">
                    Improvements for better {category} optimization
                  </p>
                </div>
              </div>

              <div className="space-y-3">
                {suggestions.map((suggestion) => (
                  <div key={suggestion.id} className="border rounded-lg">
                    <div 
                      className="p-4 cursor-pointer flex items-center justify-between"
                      onClick={() => toggleSuggestion(suggestion.id)}
                    >
                      <div className="flex items-center space-x-3">
                        <div className={cn(
                          'w-2 h-2 rounded-full',
                          `bg-${priorityColors[suggestion.priority]}-500`
                        )} />
                        <span className="font-medium text-gray-900">
                          {suggestion.description}
                        </span>
                        <span className={cn(
                          'text-xs px-2 py-1 rounded-full',
                          suggestion.priority === 'high' && 'bg-red-100 text-red-700',
                          suggestion.priority === 'medium' && 'bg-yellow-100 text-yellow-700',
                          suggestion.priority === 'low' && 'bg-blue-100 text-blue-700'
                        )}>
                          {suggestion.priority} priority
                        </span>
                      </div>
                      {expandedSuggestions.has(suggestion.id) ? (
                        <ChevronDown className="w-4 h-4 text-gray-500" />
                      ) : (
                        <ChevronRight className="w-4 h-4 text-gray-500" />
                      )}
                    </div>

                    {expandedSuggestions.has(suggestion.id) && (
                      <div className="px-4 pb-4 border-t bg-gray-50">
                        {suggestion.example && (
                          <div className="mt-3">
                            <p className="text-sm font-medium text-gray-700 mb-1">
                              Example:
                            </p>
                            <p className="text-sm text-gray-600 bg-white p-2 rounded border">
                              {suggestion.example}
                            </p>
                          </div>
                        )}
                        
                        {suggestion.before && suggestion.after && (
                          <div className="mt-3 grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                              <p className="text-sm font-medium text-red-700 mb-1">
                                Before:
                              </p>
                              <p className="text-sm text-gray-600 bg-red-50 p-2 rounded border border-red-200">
                                {suggestion.before}
                              </p>
                            </div>
                            <div>
                              <p className="text-sm font-medium text-green-700 mb-1">
                                After:
                              </p>
                              <p className="text-sm text-gray-600 bg-green-50 p-2 rounded border border-green-200">
                                {suggestion.after}
                              </p>
                            </div>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Next Steps */}
      <div className="bg-blue-50 rounded-lg border border-blue-200 p-6">
        <h3 className="text-lg font-semibold text-blue-900 mb-4">
          Ready to Improve Your Resume?
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Button onClick={onDownload} className="w-full">
            <Download className="w-4 h-4 mr-2" />
            Download Optimized Resume
          </Button>
          <Button 
            variant="outline" 
            onClick={onConsultationRequest}
            className="w-full border-blue-300 text-blue-700 hover:bg-blue-100"
          >
            Schedule Expert Consultation
          </Button>
        </div>
        <p className="text-sm text-blue-700 mt-3 text-center">
          Get personalized guidance from career experts to maximize your job search success
        </p>
      </div>
    </div>
  );
};
```

This covers the comprehensive frontend architecture with:

1. **Modern Next.js 14 structure** with App Router
2. **Reusable UI components** with Tailwind CSS and class-variance-authority
3. **Advanced file upload** with drag-and-drop and validation
4. **Real-time progress tracking** with animated states
5. **Comprehensive results display** with expandable sections
6. **Responsive design** optimized for all devices
7. **Accessibility features** following WCAG AA standards
8. **TypeScript integration** for type safety

The frontend is designed to provide an excellent user experience while being maintainable and scalable.
