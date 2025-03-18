# Ethical Data Collection and PostgreSQL Implementation Plan

## 1. Ethical Data Collection and Management

### 1.1 Principles for Ethical Data Collection
- **Transparency**: Clearly inform users about what data is being collected and how it will be used
- **Consent**: Obtain explicit consent before collecting conversation data
- **Purpose Limitation**: Only collect data necessary for stated purposes
- **Data Minimization**: Limit personal data collection to what's necessary
- **Security**: Implement strong security measures to protect user data
- **User Control**: Allow users to access, export, and delete their data
- **Anonymization**: Remove personally identifiable information when storing data for analysis

### 1.2 Implementation Steps for Ethical Data Collection

#### 1.2.1 Consent Management System
- Implement a consent banner/dialog when users first interact with the chatbot
- Store user consent preferences in the database
- Allow users to update their consent preferences at any time
- Implement different levels of consent (e.g., storage for service improvement, training, etc.)

#### 1.2.2 Privacy Notices
- Create clear privacy notices explaining:
  - What data is collected
  - How it's used
  - How long it's stored
  - Who has access to it
  - How users can access or delete their data
- Make privacy notices easily accessible from the chatbot interface

#### 1.2.3 Data Retention Policies
- Implement automatic data retention periods (e.g., 90 days for full conversations)
- Create a data lifecycle management system:
  - Active data: Full conversation with user details
  - Anonymized data: Conversations with PII removed
  - Aggregated data: Statistical information only
- Implement automatic deletion of data after retention period expires

#### 1.2.4 Data Anonymization Techniques
- Implement PII detection and removal:
  - Names, email addresses, phone numbers
  - Location data
  - Financial information
- Use techniques like:
  - Tokenization
  - Pseudonymization
  - Generalization

#### 1.2.5 User Data Access and Deletion
- Create API endpoints for users to:
  - View their conversation history
  - Export their data in a portable format
  - Request deletion of their data
- Implement verification mechanisms to ensure only authorized users can access data

## 2. PostgreSQL Migration Plan

### 2.1 Database Configuration Changes

#### 2.1.1 PostgreSQL Setup
- Install PostgreSQL and required dependencies
- Configure connection pooling for optimal performance
- Set up proper authentication and security

#### 2.1.2 Update Database Configuration
- Modify `backend/config/database.js` to use PostgreSQL instead of SQLite
- Implement environment variables for database configuration
- Create separate development and production database configurations

### 2.2 Database Schema Design

#### 2.2.1 User Authentication Tables
```sql
-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    user_type VARCHAR(50) NOT NULL, -- 'admin', 'staff', 'guest'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,
    phone VARCHAR(50),
    timezone VARCHAR(50) DEFAULT 'UTC',
    locale VARCHAR(10) DEFAULT 'en'
);

-- Roles table
CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT
);

-- Permissions table
CREATE TABLE permissions (
    id SERIAL PRIMARY KEY,
    resource VARCHAR(50) NOT NULL,
    action VARCHAR(50) NOT NULL,
    description TEXT,
    UNIQUE(resource, action)
);

-- User roles table
CREATE TABLE user_roles (
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role_id INTEGER NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, role_id)
);

-- Role permissions table
CREATE TABLE role_permissions (
    role_id INTEGER NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    permission_id INTEGER NOT NULL REFERENCES permissions(id) ON DELETE CASCADE,
    PRIMARY KEY (role_id, permission_id)
);

-- Refresh tokens table
CREATE TABLE refresh_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    revoked BOOLEAN DEFAULT FALSE,
    device_info TEXT
);

-- Password reset tokens table
CREATE TABLE password_reset_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    used BOOLEAN DEFAULT FALSE
);

-- User profiles tables
CREATE TABLE staff_profiles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL,
    department VARCHAR(100),
    employee_id VARCHAR(50) UNIQUE
);

CREATE TABLE guest_profiles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    room_number VARCHAR(50),
    check_in TIMESTAMP WITH TIME ZONE,
    check_out TIMESTAMP WITH TIME ZONE,
    preferences JSONB
);

-- Audit logs table
CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(50) NOT NULL,
    resource VARCHAR(50) NOT NULL,
    details JSONB,
    ip_address VARCHAR(50),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

#### 2.2.2 Conversation History Tables
```sql
-- Data consent table
CREATE TABLE data_consent (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    service_improvement BOOLEAN DEFAULT FALSE,
    model_training BOOLEAN DEFAULT FALSE,
    analytics BOOLEAN DEFAULT FALSE,
    marketing BOOLEAN DEFAULT FALSE,
    consent_given_at TIMESTAMP WITH TIME ZONE,
    last_updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Conversation sessions table
CREATE TABLE conversation_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    session_id UUID NOT NULL,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB,
    consent_obtained BOOLEAN DEFAULT FALSE,
    anonymized BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Conversation messages table
CREATE TABLE conversation_messages (
    id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES conversation_sessions(id) ON DELETE CASCADE,
    message_index INTEGER NOT NULL,
    role VARCHAR(20) NOT NULL, -- 'user', 'assistant', 'system'
    content TEXT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

-- LLM metrics table
CREATE TABLE llm_metrics (
    id SERIAL PRIMARY KEY,
    message_id INTEGER REFERENCES conversation_messages(id) ON DELETE CASCADE,
    model_name VARCHAR(100),
    tokens_input INTEGER,
    tokens_output INTEGER,
    latency_ms INTEGER,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

-- Create indexes for performance
CREATE INDEX idx_conversation_messages_session_id ON conversation_messages(session_id);
CREATE INDEX idx_conversation_sessions_user_id ON conversation_sessions(user_id);
CREATE INDEX idx_conversation_sessions_created_at ON conversation_sessions(created_at);
CREATE INDEX idx_llm_metrics_message_id ON llm_metrics(message_id);
```

### 2.3 Data Migration Strategy
1. Create PostgreSQL database and schema
2. Export data from SQLite database
3. Transform data to match PostgreSQL schema
4. Import data into PostgreSQL
5. Validate data integrity
6. Update application to use PostgreSQL

## 3. LLM Conversation History Storage Implementation

### 3.1 Modifications to Chatbot Controller

#### 3.1.1 Update `chatbotController.js`
- Add user authentication check
- Check and store user consent
- Create conversation session if not exists
- Store each message in the conversation
- Collect and store LLM metrics
- Implement anonymization for stored conversations

### 3.2 Conversation Storage Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  User sends │     │ Check user  │     │ Create/get  │
│   message   │────▶│   consent   │────▶│ conversation│
└─────────────┘     └─────────────┘     │   session   │
                                        └──────┬──────┘
                                               │
┌─────────────┐     ┌─────────────┐     ┌─────▼──────┐
│  Store LLM  │     │ Process LLM │     │ Store user │
│   metrics   │◀────│  response   │◀────│  message   │
└─────────────┘     └─────────────┘     └─────────────┘
       │                   │
       │             ┌─────▼──────┐
       └────────────▶│ Store LLM  │
                     │  response  │
                     └─────────────┘
```

### 3.3 Anonymization Process

1. **Real-time Anonymization**:
   - Detect and mask PII in messages before storage
   - Use regex patterns and NER models to identify PII
   - Replace PII with tokens or generic placeholders

2. **Batch Anonymization**:
   - Run periodic jobs to anonymize older conversations
   - Apply more thorough anonymization techniques
   - Mark conversations as anonymized in the database

3. **Deletion Process**:
   - Delete raw conversations after retention period
   - Keep anonymized data for longer periods
   - Implement complete deletion on user request

### 3.4 Modifications to Python LLM Script

#### 3.4.1 Update `local_model_chatbot.py`
- Add metrics collection (tokens, latency)
- Implement memory management for conversation context
- Add capability to return model metadata
- Implement PII detection in responses

## 4. Implementation Roadmap

### Phase 1: Database Migration (Week 1)
- Set up PostgreSQL
- Create database schema
- Update database configuration
- Test database connection

### Phase 2: Ethical Data Collection Framework (Week 2)
- Implement consent management
- Create privacy notices
- Develop user data access endpoints
- Test consent flow

### Phase 3: Conversation Storage (Week 3)
- Modify chatbot controller
- Implement conversation session management
- Add message storage functionality
- Test conversation storage

### Phase 4: LLM Enhancements (Week 4)
- Update Python LLM script
- Add metrics collection
- Implement PII detection
- Test end-to-end flow

### Phase 5: Analytics and Reporting (Week 5)
- Create analytics dashboard
- Implement reporting functionality
- Set up data retention jobs
- Final testing and deployment

## 5. Security and Compliance Considerations

### 5.1 Security Measures
- Encrypt sensitive data at rest
- Implement proper access controls
- Use parameterized queries to prevent SQL injection
- Regularly audit access to conversation data

### 5.2 Compliance Requirements
- GDPR compliance for EU users
- CCPA compliance for California users
- HIPAA compliance if handling health information
- Industry-specific regulations

### 5.3 Documentation Requirements
- Data Processing Impact Assessment
- Records of Processing Activities
- Data Flow Diagrams
- Security Controls Documentation