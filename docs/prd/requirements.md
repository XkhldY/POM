# Requirements

## Functional Requirements

**FR1:** The system shall accept resume uploads in PDF, DOC, and TXT formats with file size validation (max 10MB)

**FR2:** The system shall provide a multi-step wizard interface with 4 steps: Upload → Analysis → Results → Next Steps

**FR3:** The system shall use AWS Bedrock to analyze resumes and provide ATS optimization suggestions for tech roles

**FR4:** The system shall display real-time progress indicators during resume analysis with estimated completion time

**FR5:** The system shall generate specific, actionable improvement suggestions including ATS compatibility, keyword optimization, and formatting recommendations

**FR6:** The system shall allow users to download their improved resume in a unified template format to ensure consistent formatting and ATS compatibility

**FR7:** The system shall automatically extract email addresses from resume text, and only ask users for email if none is found in the resume

**FR8:** The system shall provide a consultation request form where users can specify their help needs and career goals

**FR9:** The system shall store consultation requests with user details, resume analysis results, and help requirements

**FR10:** The system shall provide responsive design that works on desktop and mobile devices

**FR11:** The system shall validate file uploads and provide clear error messages for unsupported formats or corrupted files

**FR12:** The system shall maintain user session state during the multi-step wizard process

**FR13:** The system shall provide feedback collection mechanism for users to rate improvement suggestions

**FR14:** The system shall provide a compelling landing page with clear value proposition, how it works explanation, and call-to-action

## Non-Functional Requirements

**NFR1:** The system shall process resume analysis within 2 minutes using AWS Bedrock integration

**NFR2:** The system shall maintain 99%+ uptime for the service during business hours

**NFR3:** The system shall handle concurrent users without performance degradation (target: 100 concurrent users)

**NFR4:** The system shall comply with GDPR requirements for data handling and user privacy

**NFR5:** The system shall encrypt resume files and user data both in transit and at rest

**NFR6:** The system shall use AWS free tier services where possible to minimize operational costs

**NFR7:** The system shall provide clear error handling and user-friendly error messages

**NFR8:** The system shall support file uploads up to 10MB with appropriate timeout handling

**NFR9:** The system shall maintain data retention policies for uploaded resumes (30 days) and user emails (indefinitely)

**NFR10:** The system shall provide analytics tracking for user engagement and conversion metrics
