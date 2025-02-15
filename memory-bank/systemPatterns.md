# System Patterns

## Architecture Overview

### Core Components
1. Email Processing Pipeline
   - GmailClient (gmail.py)
   - EmailProcessor (email_processor.py)
   - EmailClassifier (email_classifier.py)
   - EmailRouter (email_classifier.py)
   - Topic-specific Agents (e.g., MeetingAgent)

2. Classification System
   - Topic Detection
   - Response Requirement Analysis
   - Pattern Matching
   - Agent Routing

3. Data Management
   - Secure Storage (secure_storage.py)
   - Backup Management
   - Record Tracking
   - Status Management

## Design Patterns

### Singleton Pattern
- Used in EnhancedGroqClient
- Manages single API client instance
- Centralizes API key handling

### Strategy Pattern
- Implemented in email processing
- Flexible meeting detection strategies
- Configurable response generation

### Observer Pattern
- Email monitoring system
- Event-driven processing
- Asynchronous operations

### Factory Pattern
- Client initialization
- Configuration management
- Resource creation

## Component Relationships

### Email Processing Flow
```
Gmail API → GmailClient
    ↓
EmailProcessor → EmailClassifier
    ↓
EmailRouter → Topic-specific Agent
    ↓
SecureStorage
```

### Classification Flow
```
Unread Email
    ↓
Topic Detection → Pattern Matching
    ↓
Response Analysis → Agent Selection
    ↓
Processing Decision
```

## Technical Decisions

### Error Handling
- Exponential backoff retry
- Comprehensive logging
- Metrics tracking
- Graceful degradation

### Performance Optimization
- Asynchronous processing
- Batch operations
- Caching strategy
- Response time monitoring

### Data Management
- Structured JSON storage
- Deduplication logic
- Metrics aggregation
- Cache management

### Security
- Environment-based configuration
- API key protection
- Secure storage practices
- Error message sanitization

## Implementation Patterns

### Async Processing
```python
async def process_new_emails():
    # Fetch → Sort → Process → Respond
```

### Error Recovery
```python
async def process_with_retry():
    # Attempt → Retry → Backoff → Report
```

### Data Flow
```python
class MeetingSorter:
    # Parse → Extract → Process → Store
```

This architecture ensures reliable meeting coordination through robust email processing and AI integration.
