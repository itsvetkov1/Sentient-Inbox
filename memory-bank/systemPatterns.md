# System Patterns

## Architecture Overview

### Core Components
1. Email Processing Pipeline
   - GmailClient (gmail.py)
   - EmailProcessor (email_processor.py)
   - EmailClassifier (email_classifier.py)
   - EmailRouter (email_classifier.py)
   - LlamaAnalyzer (llama_analyzer.py)
   - DeepseekAnalyzer (deepseek_analyzer.py)
   - Topic-specific Agents (e.g., MeetingAgent)

2. Analysis System
   - Initial Analysis (LlamaAnalyzer)
   - Deep Analysis for Meeting Emails (DeepseekAnalyzer)
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
- Used in GroqClientWrapper
- Manages single API client instance for Groq
- Centralizes API key handling for Groq

### Factory Pattern
- Used for analyzer creation (LlamaAnalyzer and DeepseekAnalyzer)
- Configurable analyzer selection based on email type

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
LlamaAnalyzer (Initial Analysis)
    ↓
EmailRouter → Topic-specific Agent
    ↓
DeepseekAnalyzer (for meeting emails)
    ↓
SecureStorage
```

### Analysis Flow
```
Unread Email
    ↓
Initial Analysis (LlamaAnalyzer)
    ↓
Topic Detection → Pattern Matching
    ↓
Response Analysis → Agent Selection
    ↓
Deep Analysis (DeepseekAnalyzer for meeting emails)
    ↓
Processing Decision
```

## Technical Decisions

### Error Handling
- Exponential backoff retry
- Comprehensive logging
- Metrics tracking
- Graceful degradation
- Robust API response validation
- Detailed error logging for debugging
- Fallback mechanisms for unexpected API responses

#### API Response Handling (DeepseekAnalyzer)
```python
try:
    result = await response.json()
    if "choices" not in result or not result["choices"] or "message" not in result["choices"][0]:
        raise ValueError("Unexpected API response structure")
    
    content = result["choices"][0]["message"].get("content", "")
    if not content:
        raise ValueError("Empty content in API response")
    
    # Process content...
except Exception as e:
    logger.error(f"Error in DeepseekAnalyzer: {str(e)}", exc_info=True)
    return "flag_for_action", {"explanation": f"Error occurred during analysis, flagging for manual review. Error: {str(e)}"}
```

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
    # Fetch → Sort → Process → Deep Analyze (if meeting) → Respond
```

### Error Recovery
```python
async def process_with_retry():
    # Attempt → Retry → Backoff → Report
```

### Data Flow
```python
class MeetingSorter:
    # Parse → Extract → Process → Deep Analyze → Store
```

### Initial Analysis
```python
async def analyze_email(message_id: str, subject: str, content: str, sender: str, email_type: EmailTopic):
    # Analyze → Categorize → Determine Initial Action
```

### Deep Analysis
```python
async def analyze_meeting_email(email_content: str):
    # Deep Analyze → Refine Categorization → Determine Final Action
```

This architecture ensures reliable meeting coordination through robust email processing, deep analysis, and AI integration.
