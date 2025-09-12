# Story: Clerk Webhooks and User Sync

**Epic:** Clerk Authentication Integration  
**Priority:** Medium  
**Estimate:** 5 story points

## User Story

As a **system administrator**,  
I want **Clerk webhook events to sync user data with our database**,  
so that **user profiles stay synchronized and user lifecycle events are handled properly**.

## Story Context

**Existing System Integration:**
- Integrates with: FastAPI webhook endpoints, database models, existing user management
- Technology: FastAPI, SQLAlchemy, webhook validation, background tasks
- Follows pattern: Existing API endpoint structure and error handling
- Touch points: User model, webhook validation, database operations

## Acceptance Criteria

### Functional Requirements

1. **Webhook Endpoint:** Webhook endpoint created for Clerk user lifecycle events
2. **Signature Validation:** Webhook signature validation implemented for security
3. **Event Handling:** User creation, update, and deletion events handled properly
4. **Background Processing:** Background task processing for webhook events

### Integration Requirements

5. **API Structure Consistency:** Webhook endpoint follows existing API structure and error handling
6. **Data Integrity:** User data sync maintains referential integrity with existing models
7. **Performance Impact:** Webhook processing doesn't impact API performance

### Quality Requirements

8. **Security:** Webhook validation is secure and prevents unauthorized access
9. **Error Handling:** Error handling for webhook processing failures
10. **Monitoring:** Logging and monitoring for webhook events

## Technical Notes

- **Integration Approach:** Create webhook endpoint, implement signature validation, use Celery for background processing
- **Existing Pattern Reference:** Follow current API endpoint structure in `api/v1/endpoints/`
- **Key Constraints:** Webhook processing must be reliable and secure

## Implementation Details

### Webhook Endpoint Structure
```python
from fastapi import APIRouter, Request, HTTPException, Depends
from app.core.config import settings
import hmac
import hashlib
import json

router = APIRouter()

@router.post("/clerk")
async def clerk_webhook(request: Request):
    """Handle Clerk webhook events"""
    
    # Verify webhook signature
    signature = request.headers.get("svix-signature")
    if not signature:
        raise HTTPException(status_code=400, detail="Missing signature")
    
    body = await request.body()
    
    # Verify webhook signature
    # ... webhook verification logic
    
    event_data = await request.json()
    event_type = event_data.get("type")
    
    # Handle different event types
    if event_type == "user.created":
        await handle_user_created(event_data)
    elif event_type == "user.updated":
        await handle_user_updated(event_data)
    elif event_type == "user.deleted":
        await handle_user_deleted(event_data)
    
    return {"status": "success"}
```

### Event Handlers
```python
async def handle_user_created(event_data: dict):
    """Handle user creation event"""
    user_data = event_data.get("data", {})
    
    # Create background task for user creation
    from app.tasks.user import create_user_from_clerk
    create_user_from_clerk.delay(user_data)

async def handle_user_updated(event_data: dict):
    """Handle user update event"""
    user_data = event_data.get("data", {})
    
    # Create background task for user update
    from app.tasks.user import update_user_from_clerk
    update_user_from_clerk.delay(user_data)

async def handle_user_deleted(event_data: dict):
    """Handle user deletion event"""
    user_data = event_data.get("data", {})
    
    # Create background task for user deletion
    from app.tasks.user import delete_user_from_clerk
    delete_user_from_clerk.delay(user_data)
```

### Background Tasks
```python
# app/tasks/user.py
from celery import Celery
from app.core.database import get_db
from app.models.user import User
from sqlalchemy.orm import Session

@celery_app.task
def create_user_from_clerk(user_data: dict):
    """Create user from Clerk webhook data"""
    db = next(get_db())
    try:
        user = User(
            clerk_id=user_data.get("id"),
            email=user_data.get("email_addresses", [{}])[0].get("email_address"),
            name=user_data.get("full_name"),
            first_name=user_data.get("first_name"),
            last_name=user_data.get("last_name"),
            image_url=user_data.get("image_url"),
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

@celery_app.task
def update_user_from_clerk(user_data: dict):
    """Update user from Clerk webhook data"""
    db = next(get_db())
    try:
        user = db.query(User).filter(
            User.clerk_id == user_data.get("id")
        ).first()
        
        if user:
            user.email = user_data.get("email_addresses", [{}])[0].get("email_address")
            user.name = user_data.get("full_name")
            user.first_name = user_data.get("first_name")
            user.last_name = user_data.get("last_name")
            user.image_url = user_data.get("image_url")
            user.updated_at = datetime.utcnow()
            
            db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

@celery_app.task
def delete_user_from_clerk(user_data: dict):
    """Delete user from Clerk webhook data"""
    db = next(get_db())
    try:
        user = db.query(User).filter(
            User.clerk_id == user_data.get("id")
        ).first()
        
        if user:
            user.is_active = False
            user.updated_at = datetime.utcnow()
            db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()
```

### Webhook Signature Validation
```python
import hmac
import hashlib
import time

def verify_webhook_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Verify Clerk webhook signature"""
    try:
        # Parse signature header
        timestamp, signature_hash = signature.split(',')
        timestamp = timestamp.split('=')[1]
        signature_hash = signature_hash.split('=')[1]
        
        # Create expected signature
        signed_payload = f"{timestamp}.{payload.decode()}"
        expected_signature = hmac.new(
            secret.encode(),
            signed_payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Verify signature
        return hmac.compare_digest(signature_hash, expected_signature)
    except Exception:
        return False
```

## Definition of Done

- [x] Webhook endpoint created and configured
- [x] Signature validation implemented
- [x] User lifecycle event handlers created
- [x] Background task processing implemented
- [x] Error handling and logging added
- [x] Webhook security testing completed
- [x] User data sync verified end-to-end
- [x] Performance impact assessed
- [x] Documentation updated

## Risk Assessment

- **Primary Risk:** Webhook processing failures or data inconsistency
- **Mitigation:** Implement robust error handling, use background tasks, add monitoring
- **Rollback Plan:** Disable webhook endpoint, manual data sync if needed

## Dependencies

- Requires backend Clerk authentication integration (previous stories)
- Depends on existing Celery background task system
- Requires existing database and User model setup

## Testing Strategy

- Unit tests for webhook signature validation
- Integration tests for event handlers
- End-to-end testing of user lifecycle events
- Security testing for webhook endpoint
- Performance testing for background task processing

## Environment Variables

```env
CLERK_WEBHOOK_SECRET=whsec_...
```

## Monitoring and Logging

- Log all webhook events received
- Monitor webhook processing success/failure rates
- Alert on webhook processing failures
- Track user sync performance metrics

## Dev Agent Record

### Agent Model Used
Claude 3.5 Sonnet (via Cursor)

### Completion Notes List
- ✅ **Webhook Endpoint**: Created `/api/v1/webhooks/clerk` endpoint with proper signature validation
- ✅ **Signature Validation**: Implemented HMAC-SHA256 signature verification for webhook security
- ✅ **Event Handlers**: Created handlers for user.created, user.updated, and user.deleted events
- ✅ **Background Tasks**: Implemented Celery tasks for user creation, update, and deletion
- ✅ **Error Handling**: Added comprehensive error handling with retry logic and logging
- ✅ **Security Testing**: Verified webhook signature validation works correctly
- ✅ **End-to-End Testing**: Successfully tested webhook with valid signature (200 OK response)
- ✅ **Performance**: Background task processing ensures no impact on API performance

### File List
- `backend/app/api/v1/endpoints/webhooks.py` - Webhook endpoint with signature validation
- `backend/app/tasks/user.py` - Celery tasks for user lifecycle management
- `backend/app/core/celery.py` - Celery configuration
- `backend/app/api/v1/api.py` - Updated to include webhook router
- `backend/app/core/config.py` - Added CLERK_WEBHOOK_SECRET configuration
- `backend/tests/test_webhooks.py` - Unit tests for webhook functionality
- `backend/tests/test_user_tasks.py` - Unit tests for Celery tasks

### Change Log
| Date | Version | Description | Author |
|------|---------|-------------|---------|
| 2024-09-11 | 1.0 | Initial implementation of Clerk webhooks and user sync | James (Dev) |

### Status
Ready for Review

---

*This story ensures reliable synchronization between Clerk and the local database, maintaining data consistency and handling user lifecycle events properly.*
