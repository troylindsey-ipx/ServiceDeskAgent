# Token Tracking System

This document explains the token tracking system implemented for the LiveKit AI Service Desk Agent to monitor Azure OpenAI token usage across both transcriber and agent services.

## Overview

The token tracking system captures and stores token usage data from both Azure OpenAI services:
- **Transcriber Service**: Uses Azure OpenAI Whisper for speech-to-text
- **Agent Service**: Uses Azure OpenAI GPT-4o Realtime API for conversation

## Architecture

### Components

1. **Database Layer** (`db_token_usage.py`)
   - SQLite database for storing token usage records
   - Indexed tables for efficient querying
   - Session-based tracking with start/end timestamps

2. **Token Tracker Service** (`token_tracker.py`)
   - Centralized service for managing token tracking sessions
   - Coordinates between transcriber and agent services
   - Provides in-memory session management

3. **Service Integration**
   - **Agent Service** (`agent.py`): Tracks GPT-4o Realtime API usage
   - **Transcriber Service** (`transcriber.py`): Tracks Whisper STT usage

4. **Reporting Tools** (`view_token_usage.py`)
   - Command-line utility for viewing usage reports
   - JSON export capabilities
   - Session-specific analysis

## Database Schema

```sql
CREATE TABLE token_usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    user_name TEXT,
    service_type TEXT NOT NULL,        -- 'transcriber' or 'agent'
    model_name TEXT NOT NULL,          -- 'whisper' or 'gpt-4o-realtime'
    input_tokens INTEGER DEFAULT 0,
    output_tokens INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,
    session_start TIMESTAMP,
    session_end TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## How It Works

### Session Lifecycle

1. **Session Start**
   - User connects to LiveKit room
   - Token tracker creates unique session ID
   - Both services register with the tracker

2. **Token Tracking**
   - Each service reports token usage as it occurs
   - Database records are updated incrementally
   - In-memory counters track real-time usage

3. **Session End**
   - User disconnects or services shut down
   - Final token counts are recorded
   - Usage summary is generated and logged

### Token Estimation

- **Agent Service**: Attempts to extract actual token usage from Azure OpenAI responses
- **Transcriber Service**: Uses word-count estimation (approximation method)

## Usage

### Viewing Token Usage

```bash
# View summary for last 7 days
npm run token-usage

# View summary as JSON
npm run token-usage-json

# View specific session details
npm run token-session SESSION_ID

# View usage for specific time period
cd backend && python view_token_usage.py --days 30
```

### Command Line Options

```bash
python view_token_usage.py --help

Options:
  --summary          Show usage summary (default)
  --session ID       Show details for specific session
  --days N           Number of days to include (default: 7)
  --json             Output as JSON format
```

## Sample Output

### Usage Summary
```
============================================================
TOKEN USAGE SUMMARY
============================================================
Total Sessions: 15
Total Input Tokens: 12,450
Total Output Tokens: 8,320
Total Tokens: 20,770

BY SERVICE:
----------------------------------------

TRANSCRIBER SERVICE:
  Model: whisper
    Sessions: 15
    Input Tokens: 8,200
    Output Tokens: 3,100
    Total Tokens: 11,300
    Avg Tokens/Session: 753.33

AGENT SERVICE:
  Model: gpt-4o-realtime
    Sessions: 15
    Input Tokens: 4,250
    Output Tokens: 5,220
    Total Tokens: 9,470
    Avg Tokens/Session: 631.33
```

### Session Details
```
============================================================
SESSION DETAILS: support-room-john-doe_abc123def
============================================================

Service: TRANSCRIBER
Model: whisper
User: John Doe
Input Tokens: 547
Output Tokens: 206
Total Tokens: 753
Session Start: 2025-06-27 15:30:15
Session End: 2025-06-27 15:35:42

Service: AGENT
Model: gpt-4o-realtime
User: John Doe
Input Tokens: 283
Output Tokens: 348
Total Tokens: 631
Session Start: 2025-06-27 15:30:18
Session End: 2025-06-27 15:35:40

SESSION TOTALS:
Total Input Tokens: 830
Total Output Tokens: 554
Total Tokens: 1,384
```

## Integration Points

### Frontend Integration
- `LiveKitModal.jsx`: Handles disconnect events
- Automatic cleanup when users close the modal or disconnect

### Backend Integration
- Both services automatically start/end token tracking
- Graceful handling of service failures
- Cleanup of stale sessions

## Cost Analysis

To calculate costs, you can use Azure OpenAI pricing:

```python
# Example cost calculation (prices as of 2025)
WHISPER_COST_PER_1K_TOKENS = 0.006  # $0.006 per 1K tokens
GPT4O_INPUT_COST_PER_1K_TOKENS = 0.0025   # $0.0025 per 1K input tokens
GPT4O_OUTPUT_COST_PER_1K_TOKENS = 0.01    # $0.01 per 1K output tokens

def calculate_session_cost(usage_summary):
    total_cost = 0
    
    for service_type, service_data in usage_summary.get('services', {}).items():
        if service_type == 'transcriber':
            # Whisper pricing
            total_cost += (service_data['total_tokens'] / 1000) * WHISPER_COST_PER_1K_TOKENS
        elif service_type == 'agent':
            # GPT-4o pricing
            total_cost += (service_data['input_tokens'] / 1000) * GPT4O_INPUT_COST_PER_1K_TOKENS
            total_cost += (service_data['output_tokens'] / 1000) * GPT4O_OUTPUT_COST_PER_1K_TOKENS
    
    return total_cost
```

## Monitoring and Alerts

### Recommended Monitoring
- Daily token usage reports
- Cost threshold alerts
- Unusual usage pattern detection
- Service availability monitoring

### Log Files
- Token tracking events are logged to console
- Database operations are logged with timestamps
- Error conditions are captured and logged

## Troubleshooting

### Common Issues

1. **Missing Token Data**
   - Check if services are properly registering with token tracker
   - Verify database connectivity
   - Review service startup logs

2. **Inaccurate Token Counts**
   - Transcriber uses estimation - actual usage may vary
   - Agent token extraction depends on Azure OpenAI response format
   - Consider implementing more precise tracking methods

3. **Database Errors**
   - Check SQLite file permissions
   - Verify disk space availability
   - Review database initialization logs

### Debug Commands

```bash
# Check database contents
cd backend && python -c "from db_token_usage import token_db; print(token_db.get_usage_summary())"

# View active sessions
cd backend && python -c "from token_tracker import token_tracker; print(token_tracker.active_sessions)"

# Test database connection
cd backend && python check_db.py
```

## Future Enhancements

### Planned Features
- Real-time cost monitoring dashboard
- Email alerts for usage thresholds
- Integration with Azure Cost Management APIs
- More precise token counting methods
- Historical trend analysis
- User-specific usage reports

### API Integration
- RESTful API for token usage data
- Webhook notifications for high usage
- Integration with monitoring systems (Prometheus, Grafana)

## Security Considerations

- Token usage data contains user information
- Database should be secured with appropriate permissions
- Consider encryption for sensitive usage data
- Implement data retention policies
- Regular backup of usage data

## Performance Notes

- Database operations are optimized with indexes
- In-memory tracking reduces database load
- Batch updates for high-frequency operations
- Automatic cleanup of old records (future enhancement)
