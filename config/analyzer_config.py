# config/analyzer_config.py
ANALYZER_CONFIG = {
    "meeting_analyzer": {
        "model": {
            "name": "gpt-3.5-turbo",
            "temperature": 0.3,
            "max_tokens": 2000
        },
        "logging": {
            "base_dir": "logs/meeting_analyzer",
            "archive_retention_days": 30,
            "max_log_size_mb": 10,
            "backup_count": 5
        },
        "analysis": {
            "confidence_threshold": 0.7,
            "review_threshold": 0.5
        }
    },
    "deepseek_analyzer": {
        "model": {
            "name": "deepseek-r1",
            "temperature": 0.3,
            "max_tokens": 5000,
            "api_endpoint": "https://api.groq.com/openai/v1/chat/completions",
            "api_key": "your_groq_api_key_here"
        },
        "logging": {
            "base_dir": "logs/deepseek_analyzer",
            "archive_retention_days": 30,
            "max_log_size_mb": 10,
            "backup_count": 5
        },
        "analysis": {
            "confidence_threshold": 0.7,
            "review_threshold": 0.5
        }
    }
}
