# Story: Frontend Clerk Provider Setup

**Epic:** Clerk Authentication Integration  
**Priority:** High  
**Estimate:** 6 story points

## User Story

As a **user**,  
I want **to sign up and log in using Clerk authentication**,  
so that **I can access personalized features and save my resume analysis history**.

## Story Context

**Existing System Integration:**
- Integrates with: Next.js app router, existing Zustand state management, current UI components
- Technology: Next.js 14, React, Clerk SDK, TypeScript
- Follows pattern: Existing component structure and state management patterns
- Touch points: App layout, API client, protected routes, user state

## Acceptance Criteria

### Functional Requirements

1. **Clerk Provider Configuration:** Clerk provider configured in app layout with proper theming
2. **Authentication Components:** Sign-in and sign-up components implemented with Clerk UI
3. **User Management:** User button and profile management integrated
4. **Protected Routes:** Protected route component created for authenticated-only pages

### Integration Requirements

5. **Anonymous Flow Preservation:** Existing anonymous resume analysis flow remains accessible
6. **API Client Integration:** API client updated to include auth tokens in requests
7. **State Management:** User state integrated with existing Zustand store patterns

### Quality Requirements

8. **Cross-Device Compatibility:** Authentication flow works seamlessly across different devices
9. **Error Handling:** Error handling for auth failures implemented
10. **UI Consistency:** UI follows existing design patterns and styling

## Technical Notes

- **Integration Approach:** Wrap app with ClerkProvider, create auth components, update API client with token injection
- **Existing Pattern Reference:** Follow current component structure in `app/` directory
- **Key Constraints:** Must not break existing anonymous user experience

## Implementation Details

### Dependencies to Add
```json
{
  "dependencies": {
    "@clerk/nextjs": "^4.29.0",
    "@clerk/themes": "^1.7.0"
  }
}
```

### Next.js Configuration Updates
```javascript
const { withClerkMiddleware } = require('@clerk/nextjs');

module.exports = withClerkMiddleware({
  output: 'standalone',
  experimental: {
    appDir: true,
  },
  images: {
    domains: ['img.clerk.com'],
  },
  // ... existing config
});
```

### App Layout Integration
```tsx
import { ClerkProvider } from '@clerk/nextjs';
import { dark } from '@clerk/themes';

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <ClerkProvider
      appearance={{
        baseTheme: dark,
        variables: {
          colorPrimary: '#3b82f6',
        },
      }}
    >
      <html lang="en">
        <body className="__className_f367f3">
          {children}
        </body>
      </html>
    </ClerkProvider>
  );
}
```

### Authentication Components
```tsx
// SignInButton component
import { SignInButton as ClerkSignInButton } from '@clerk/nextjs';

export function SignInButton() {
  return (
    <ClerkSignInButton mode="modal">
      <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
        Sign In
      </button>
    </ClerkSignInButton>
  );
}

// ProtectedRoute component
import { useAuth } from '@clerk/nextjs';
import { useRouter } from 'next/navigation';

export function ProtectedRoute({ children, fallback }: ProtectedRouteProps) {
  const { isSignedIn, isLoaded } = useAuth();
  const router = useRouter();

  // Implementation details...
}
```

### API Client Updates
```typescript
import axios from 'axios';
import { useAuth } from '@clerk/nextjs';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || '/api',
  timeout: 30000,
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const { getToken } = useAuth();
  
  getToken().then((token) => {
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  });
  
  return config;
});
```

## Definition of Done

- [ ] Clerk provider configured in app layout
- [ ] Authentication components created (SignIn, UserButton, ProtectedRoute)
- [ ] API client updated with auth token handling
- [ ] Protected routes implemented
- [ ] User state management integrated
- [ ] Authentication flow tested end-to-end
- [ ] Existing anonymous flow verified unchanged
- [ ] Error handling implemented
- [ ] UI styling matches existing design
- [ ] Documentation updated

## Risk Assessment

- **Primary Risk:** Breaking existing anonymous user experience
- **Mitigation:** Maintain existing routes and flows, add authentication as optional layer
- **Rollback Plan:** Remove Clerk provider, revert API client changes, disable protected routes

## Dependencies

- Requires backend Clerk authentication integration (previous story)
- Depends on existing Next.js app structure
- Requires existing Zustand state management setup

## Testing Strategy

- End-to-end testing of authentication flow
- Regression testing of anonymous user flow
- Cross-browser compatibility testing
- Mobile responsiveness testing
- Error handling testing

## Environment Variables

```env
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/dashboard
NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL=/dashboard
```

---

*This story provides the frontend authentication interface while preserving the existing anonymous user experience, enabling users to choose between anonymous and authenticated usage.*
