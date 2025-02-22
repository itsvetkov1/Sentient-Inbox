# Technical Context

## Technologies Used

### Core Technologies
- Python 3.x (with asyncio)
- Gmail API
- Groq API (for Llama model integration)
- Deepseek API (for Deepseek R1 model integration)
- JSON for structured data storage and communication

### Key Dependencies
- groq-sdk: Groq API integration for Llama model
- deepseek-sdk: Deepseek API integration for Deepseek R1 model
- google-api-python-client: Gmail API access
- python-dotenv: Environment management
- typing-extensions: Type hints support
- pathlib: Path manipulation
- logging: Comprehensive DEBUG level logging
- pydantic: Data validation and settings management

## Development Setup

### Environment Configuration
1. Required Environment Variables:
   - GROQ_API_KEY
   - DEEPSEEK_API_KEY
   - Gmail OAuth credentials
   
2. Directory Structure:
```
sentient-inbox/
├── data/
│   ├── secure/          # Encrypted data storage
│   ├── cache/           # Weekly rolling history
│   └── metrics/         # Performance metrics
├── docs/                # Documentation
├── groq_integration/    # Llama model integration
├── deepseek_integration/# Deepseek R1 model integration
├── logs/                # System logs
└── memory-bank/         # System memory
```

3. File Organization:
   - main.py: Entry point
   - email_processor.py: Three-stage email processing pipeline
   - email_classifier.py: Initial classification (Llama)
   - deepseek_analyzer.py: Detailed content analysis
   - llama_analyzer.py: Final decision making
   - email_writer.py: Response generation
   - secure_storage.py: Encrypted data management

## Technical Constraints

### API Limitations
- Groq API rate limits
- Deepseek API rate limits
- Gmail API quotas
- Response time requirements
- Token limits for model inputs

### Performance Requirements
- Batch processing of 100 emails per cycle
- Efficient three-stage analysis pipeline
- Quick response generation for standard responses
- Reliable error recovery with single retry and 3-second delay

### Security Requirements
- OAuth2 authentication for Gmail integration
- Secure API key storage for Groq and Deepseek
- Encrypted storage for processed emails and sensitive data
- Safe credential handling
- Regular security audits

## Development Practices

### Code Standards
- Type hints usage
- PEP 8 compliance
- Async/await patterns for efficient processing
- Comprehensive error handling with detailed logging

### Logging System
- DEBUG level logging for all operations
- File-based logging with rotation
- Structured log format for easy parsing
- Comprehensive error and exception logging

### Error Handling
- Single retry attempt with 3-second delay
- Graceful degradation for persistent issues
- Detailed error reporting for future frontend integration
- No retries for content parsing failures

### Testing Requirements
- Unit tests for each stage of the analysis pipeline
- Integration testing for end-to-end email processing
- Stress testing for system stability under high load
- Error scenario coverage
- Performance monitoring and optimization

## Monitoring & Metrics

### Performance Tracking
- Response times for each stage of the pipeline
- Success rates for email classification and processing
- Error frequency and types
- API usage for Groq and Deepseek
- Batch processing efficiency

### Data Management
- Structured JSON storage with confidence scores
- Weekly rolling history for efficient deduplication
- Encrypted storage for processed emails and sensitive data
- Robust backup and recovery mechanisms
- Metrics collection for pipeline performance analysis

This technical context ensures a robust, scalable, and secure implementation of the three-stage email analysis pipeline, integrating multiple AI models for comprehensive email processing.
