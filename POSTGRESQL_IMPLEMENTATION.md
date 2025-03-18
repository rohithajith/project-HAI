# PostgreSQL Implementation and Ethical Data Collection

This document provides instructions for setting up and using the PostgreSQL database and ethical data collection features for the hotel management system.

## Table of Contents

1. [Overview](#overview)
2. [PostgreSQL Setup](#postgresql-setup)
3. [Database Migration](#database-migration)
4. [Ethical Data Collection](#ethical-data-collection)
5. [Data Anonymization](#data-anonymization)
6. [Data Retention](#data-retention)
7. [Conversation History Storage](#conversation-history-storage)
8. [Monitoring and Reporting](#monitoring-and-reporting)

## Overview

The hotel management system has been updated to use PostgreSQL for data storage and includes features for ethical data collection, particularly for conversations with the AI assistant. This implementation follows best practices for data privacy and security.

## PostgreSQL Setup

### Prerequisites

- PostgreSQL 12 or higher
- Node.js 14 or higher
- npm 6 or higher

### Installation

1. Install PostgreSQL:
   - Windows: Download and install from [postgresql.org](https://www.postgresql.org/download/windows/)
   - macOS: `brew install postgresql`
   - Linux: `sudo apt-get install postgresql`

2. Create a database:
   ```bash
   psql -U postgres
   CREATE DATABASE hotel_management;
   \q
   ```

3. Update environment variables:
   The `.env` file in the backend directory contains PostgreSQL configuration:
   ```
   PGUSER=postgres
   PGHOST=localhost
   PGDATABASE=hotel_management
   PGPASSWORD=postgres
   PGPORT=5432
   ```
   Update these values according to your PostgreSQL setup.

4. Install required npm packages:
   ```bash
   cd backend
   npm install pg pg-hstore
   ```

### Initialize Database Schema

Run the initialization script to create the necessary tables:

```bash
cd backend
node scripts/init_postgres_db.js
```

This script creates:
- User authentication tables (users, roles, permissions)
- Conversation history tables (sessions, messages, metrics)
- Data consent tables

## Database Migration

If you're migrating from SQLite to PostgreSQL, use the migration script:

```bash
cd backend
node scripts/migrate_sqlite_to_postgres.js
```

This script:
1. Extracts data from the SQLite database
2. Transforms it to match the PostgreSQL schema
3. Loads it into the PostgreSQL database

## Ethical Data Collection

### Consent Management

The system implements a comprehensive consent management system:

1. **User Consent Levels**:
   - Service Improvement: Allow data collection to improve the AI assistant
   - Model Training: Allow anonymized data to be used for training models
   - Analytics: Allow usage pattern analysis
   - Marketing: Allow personalized marketing based on preferences

2. **Consent Storage**:
   Consent preferences are stored in the `data_consent` table:
   ```sql
   SELECT * FROM data_consent WHERE user_id = [user_id];
   ```

3. **Consent UI**:
   - Users are prompted for consent when first using the chatbot
   - A consent management interface allows users to update preferences
   - Users can access this via the settings icon in the chatbot interface

### Privacy Notices

The system includes clear privacy notices explaining:
- What data is collected
- How it's used
- How long it's stored
- Who has access to it
- How users can access or delete their data

## Data Anonymization

The system automatically anonymizes conversation data after a specified period:

1. **Anonymization Process**:
   Run the anonymization script:
   ```bash
   cd backend
   node scripts/anonymize_conversations.js
   ```

2. **Anonymization Settings**:
   Configure in `.env`:
   ```
   ANONYMIZE_AFTER_DAYS=30
   ```

3. **What Gets Anonymized**:
   - Personal identifiers (names, emails, phone numbers)
   - Location information
   - Room numbers
   - Financial information
   - IP addresses and device information

4. **Scheduling Anonymization**:
   Set up a cron job to run the script regularly:
   ```
   0 2 * * * cd /path/to/backend && node scripts/anonymize_conversations.js >> /var/log/anonymize.log 2>&1
   ```

## Data Retention

The system implements automatic data deletion after the retention period:

1. **Retention Process**:
   Run the deletion script:
   ```bash
   cd backend
   node scripts/delete_old_conversations.js
   ```

2. **Retention Settings**:
   Configure in `.env`:
   ```
   DATA_RETENTION_DAYS=90
   ```

3. **Scheduling Deletion**:
   Set up a cron job to run the script regularly:
   ```
   0 3 * * * cd /path/to/backend && node scripts/delete_old_conversations.js >> /var/log/delete_conversations.log 2>&1
   ```

## Conversation History Storage

### Storage Flow

1. **User sends message**:
   - System checks for user consent
   - Creates or retrieves conversation session
   - Stores user message if consent given

2. **AI processes message**:
   - Generates response
   - Collects metrics (tokens, latency)
   - Detects and redacts PII in response

3. **System stores response**:
   - Stores AI response if consent given
   - Stores metrics for analysis

### Accessing Conversation History

Users can access their conversation history through the UI or API:

- **UI**: Via the chatbot interface settings
- **API**: `GET /api/chatbot/history`

### Deleting Conversation History

Users can delete their conversation history:

- **UI**: Via the chatbot interface settings
- **API**: `DELETE /api/chatbot/history`

## Monitoring and Reporting

### Usage Monitoring

The system collects anonymized usage metrics:

- Number of conversations
- Average conversation length
- Common topics
- Response latency

### Compliance Reporting

Generate compliance reports:

```bash
cd backend
node scripts/generate_compliance_report.js
```

This creates a report showing:
- Number of users who have given consent
- Number of anonymized conversations
- Number of deleted conversations
- Data retention compliance status

### Audit Logging

All data access and management actions are logged:
- Who accessed what data
- When data was anonymized
- When data was deleted

Access logs:
```sql
SELECT * FROM audit_logs WHERE action = 'data_access' ORDER BY timestamp DESC;