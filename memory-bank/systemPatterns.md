# System Patterns

## Architecture Overview

### Core Components
1. Email Processing Pipeline
   - GmailClient (gmail.py)
   - EmailProcessor (email_processor.py)
   - EmailClassifier (email_classifier.py)
   - LlamaAnalyzer (llama_analyzer.py)
   - DeepseekAnalyzer (deepseek_analyzer.py)
   - ResponseGenerator (email_writer.py)

2. Three-Stage Analysis System
   - Stage 1: Initial Meeting Classification (LlamaAnalyzer)
   - Stage 2: Detailed Content Analysis (DeepseekAnalyzer)
   - Stage 3: Final Decision Making (LlamaAnalyzer)

3. Data Management
   - SecureStorage (secure_storage.py)
   - WeeklyRollingHistory
   - StructuredDataStorage
   - BackupManager

## Design Patterns

### Singleton Pattern
- Used in GroqClientWrapper
- Manages single API client instance for Groq
- Centralizes API key handling for Groq

### Factory Pattern
- Used for analyzer creation (LlamaAnalyzer and DeepseekAnalyzer)
- Configurable analyzer selection based on analysis stage

### Strategy Pattern
- Implemented in email processing and response generation
- Flexible analysis strategies for different email types
- Configurable response templates

### Observer Pattern
- Email monitoring system
- Event-driven processing
- Asynchronous operations

### Chain of Responsibility
- Three-stage analysis pipeline
- Each stage can process or pass to the next

## Component Relationships

### Email Processing Flow
```
Gmail API → GmailClient
    ↓
EmailProcessor → EmailClassifier
    ↓
Stage 1: LlamaAnalyzer (Initial Classification)
    ↓
Stage 2: DeepseekAnalyzer (Detailed Analysis)
    ↓
Stage 3: LlamaAnalyzer (Final Decision)
    ↓
ResponseGenerator
    ↓
SecureStorage
```

### Analysis Flow
```
Unread Email
    ↓
Stage 1: Initial Classification (LlamaAnalyzer)
    ↓
Meeting-related? → Yes → Stage 2: Detailed Analysis (DeepseekAnalyzer)
    ↓
Stage 3: Final Decision (LlamaAnalyzer)
    ↓
Categorization (standard_response, needs_review, ignored)
    ↓
Processing Decision
```

## Technical Decisions

### Error Handling
- Single retry attempt with 3-second delay
- Comprehensive DEBUG level logging
- Metrics tracking
- Graceful degradation
- Robust API response validation
- Detailed error logging for troubleshooting

### Performance Optimization
- Batch processing (100 emails per cycle)
- Asynchronous processing
- Weekly rolling history for efficient deduplication
- Response time monitoring

### Data Management
- Structured JSON storage with confidence scores
- Weekly rolling history for deduplication
- Encrypted storage for processed emails and sensitive data
- Robust backup and recovery mechanisms

### Security
- OAuth2 authentication for Gmail integration
- Environment-based configuration
- API key protection
- Secure storage with encryption
- Regular security audits

## Implementation Patterns

### Batch Processing
```python
async def process_email_batch(batch_size: int = 100):
    # Fetch → Deduplicate → Process → Store
```

### Three-Stage Analysis
```python
async def analyze_email(email_content: str):
    # Stage 1: Initial Classification
    initial_classification = await llama_analyzer.classify(email_content)
    
    if initial_classification == "meeting_related":
        # Stage 2: Detailed Analysis
        detailed_analysis = await deepseek_analyzer.analyze(email_content)
        
        # Stage 3: Final Decision
        final_decision = await llama_analyzer.make_decision(detailed_analysis)
    else:
        final_decision = initial_classification
    
    return final_decision
```

### Response Generation
```python
def generate_response(email_category: str, parameters: dict):
    if email_category == "standard_response":
        return ResponseGenerator.generate_standard_response(parameters)
    elif email_category == "needs_review":
        return ResponseGenerator.flag_for_review(parameters)
    else:
        return None  # No response for ignored emails
```

### Secure Data Management
```python
class SecureStorage:
    def store_processed_email(email_id: str, analysis_result: dict):
        encrypted_data = self.encrypt(analysis_result)
        self.db.store(email_id, encrypted_data)
    
    def retrieve_processed_email(email_id: str) -> dict:
        encrypted_data = self.db.retrieve(email_id)
        return self.decrypt(encrypted_data)
```

This architecture ensures reliable and secure email management through a sophisticated three-stage analysis pipeline, robust error handling, and efficient data management practices.
