# Three-Stage Email Analysis Pipeline Specification

## Overview
The email analysis pipeline implements a sophisticated three-stage approach to email processing, utilizing both Llama and Deepseek R1 models. This architecture ensures accurate classification and handling of meeting-related emails through progressive levels of analysis and decision-making.

## Stage 1: Initial Meeting Classification (Llama Model)

### Purpose
The first stage serves as an initial filter to identify meeting-related content within incoming emails. This stage prevents unnecessary deep analysis of non-meeting emails, optimizing system resources and processing time.

### Input Processing
The Llama model receives the complete email content and applies initial classification logic to determine if the email contains meeting-related information. The system processes emails in batches of 100, examining only previously unprocessed emails.

### Classification Process
The model performs binary classification:
- Positive Classification: Email contains meeting-related content
- Negative Classification: Email contains no meeting-related content

### Duplicate Prevention
The system maintains a weekly rolling history of processed email IDs to prevent duplicate processing. Only unique identifiers are stored, without additional metadata or model outputs.

### Output
The stage produces a binary decision that determines whether the email proceeds to Stage 2 or exits the pipeline.

## Stage 2: Detailed Content Analysis (Deepseek R1 Model)

### Purpose
For emails classified as meeting-related, the Deepseek R1 model performs comprehensive content analysis to understand the context, requirements, and necessary actions.

### Input Processing
The model receives:
- Complete email content
- Context from Stage 1 classification

### Analysis Process
The Deepseek R1 model conducts an in-depth analysis to:
- Review full email content
- Identify key meeting parameters (date, time, location)
- Evaluate content complexity
- Assess completeness of information
- Identify presence of attachments
- Detect multiple requests or complex requirements

### Analysis Output
The model generates a detailed summary containing:
- Assessment of whether the email can be handled with a standard response
- Identification of missing critical information
- Recognition of complex scenarios requiring user attention
- Reasoning for its recommendations

## Stage 3: Final Classification (Llama Model - Second Pass)

### Purpose
The final stage processes Deepseek's analysis to make definitive decisions about email handling and categorization.

### Input Processing
The Llama model receives:
- Structured analysis from Deepseek R1
- Classification reasoning
- Identified parameters and complexities

### Classification Categories
The model assigns one of three final statuses:

1. "standard_response"
   Requirements:
   - All mandatory parameters present (date, time, location)
   - No attachments
   - Single, clear meeting request
   - No complex additional information
   Actions:
   - Email will be starred
   - Automatic response generated using template
   - Marked as read after response

2. "needs_review"
   Triggers:
   - Missing mandatory parameters
   - Presence of attachments
   - Multiple meeting requests
   - Complex additional information
   - Unclear or ambiguous content
   Actions:
   - Email remains unread
   - Email is starred
   - No automatic response generated

3. "ignored"
   Criteria:
   - Confirmed non-meeting content
   - No action required
   Actions:
   - Email remains unread
   - No further processing

### Special Case Handling
- Emails with both meeting content and other important information are classified as "needs_review"
- Any meeting-related email containing attachments automatically receives "needs_review" status
- Multiple meeting requests in a single email trigger "needs_review" classification

## Error Handling and Reliability

### Retry Mechanism
- Single retry attempt for failures
- 3-second delay between attempts
- No retries for content parsing failures
- Comprehensive error reporting for future frontend integration

### Logging Requirements
- DEBUG level logging maintained throughout the pipeline
- Complete input/output logging at each stage
- Special emphasis on model interactions and decisions
- Detailed error and exception logging

## Pipeline Integrity

### Data Flow Protection
- Secure data transmission between stages
- Validation of input/output at each stage
- Proper error propagation through the pipeline

### Process Verification
- Confirmation of successful stage completion before progression
- Validation of decision criteria at each stage
- Verification of required parameters before final classification

This pipeline design ensures thorough analysis of meeting-related emails while maintaining efficiency through progressive filtering and detailed examination of relevant content. The system's multi-stage approach combines the strengths of both Llama and Deepseek R1 models to provide accurate classification and appropriate handling of various email scenarios.