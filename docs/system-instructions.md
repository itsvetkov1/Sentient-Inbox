# Email Management System Development Instructions

## System Overview and Purpose
This automated email management system focuses on meeting coordination through Gmail integration. The system leverages a sophisticated AI-powered architecture using Groq, with specialized components designed for efficient email processing and response handling. The foundation includes secure storage encryption and Gmail integration with OAuth2 authentication.

## Core Architecture Implementation Flow
The system processes emails through a sophisticated three-stage analysis pipeline, utilizing both Llama and Deepseek models for comprehensive email understanding and decision-making.

### Stage 1: Initial Meeting Classification (Llama)
The first stage employs a Llama model to perform preliminary email classification with these key functions:
- Analysis of incoming email content to determine meeting-related information
- Binary classification (meeting-related or not)
- Processing of only new, unhandled emails using unique identifiers
- Maintenance of a weekly rolling history of processed email IDs for deduplication

### Stage 2: Detailed Content Analysis (Deepseek)
When an email is classified as meeting-related, the Deepseek R1 model performs a comprehensive content analysis that generates:

Detailed Analysis Output:
- A natural language summary of the email's key points
- Extracted meeting parameters with confidence scores
- Assessment of email complexity and clarity
- Identification of any missing or unclear information
- Reasoning about the email's context and requirements

This analysis is structured to include:
- Primary meeting details (date, time, location) with confidence scores
- Secondary information (agenda, participants, prerequisites)
- Potential complexities or ambiguities that need attention
- Initial recommendation based on completeness of information

### Stage 3: Final Decision Making (Llama)
The Llama model performs a critical final analysis by:
- Ingesting the complete Deepseek analysis output
- Reviewing the reasoning and extracted information
- Evaluating confidence scores and identified complexities
- Making a final categorization decision

The model assigns one of three final statuses:

1. "standard_response":
   - All required meeting details present with high confidence
   - No complex requirements or ambiguities identified
   - Clear, single-purpose meeting request
   - Will be marked with a star after automated response
   - Uses customizable response templates

2. "needs_review":
   - Complex meetings with multiple components
   - Presence of attachments requiring review
   - Unclear or incomplete critical information
   - Low confidence scores in key parameters
   - Will be left unread and starred

3. "ignored":
   - Confirmed non-meeting emails
   - No action required based on content
   - Remains unread, no further processing

## Email Processing Rules and Requirements

### Required Meeting Details
Standard response processing requires:
- Date (with validated format)
- Time (with clear specification)
- Location (physical or virtual meeting space)

### Standard Response Template
Template structure with parameter insertion:
"Thank you for your meeting request. I am pleased to confirm our meeting on {params['date']['value']} at {params['time']['value']} at {params['location']['value']}"

### Batch Processing Specifications
- Batch size: 100 emails per processing cycle
- Processing of only new, unhandled emails
- Weekly rolling history maintenance
- Deduplication checks before processing

### Error Handling and Retry Logic
- Single retry attempt with 3-second delay
- No retries for content parsing failures
- Comprehensive error reporting
- DEBUG level logging for all operations
- Input/output logging for troubleshooting

## System Evolution and Future Features

### High Priority Development
1. Agent coordination system implementation
2. Monitoring dashboard development
3. Agent configuration interface
4. Enhanced response template system

### Planned Feature Expansion
1. Auto-reminder System:
   - Independent service architecture
   - API endpoint accessibility
   - Frontend integration capability

2. Advanced Features:
   - Multi-agent architecture
   - Calendar integration with conflict detection
   - Frontend customization options
   - Template customization interface
   - Variable field insertion system
   - Processing rules configuration

### Lower Priority Enhancements
1. Timezone handling improvements
2. Advanced PII detection and handling
3. Performance metrics expansion

## Development Guidelines
Development priorities should focus on:
1. Core email processing pipeline implementation
2. Comprehensive logging system
3. Robust error handling mechanisms
4. Microservice-ready component design
5. Frontend integration preparation

The system should be developed with consideration for:
- Future distributed system architecture
- API endpoint development
- Frontend communication requirements
- Scalability and maintenance
- Security and data protection

This architecture ensures a robust, scalable system that can evolve while maintaining reliable email processing capabilities.