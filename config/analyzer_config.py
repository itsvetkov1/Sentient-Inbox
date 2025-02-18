# config/analyzer_config.py
ANALYZER_CONFIG = {
    "default_analyzer": {
        "model": {
            "name": "llama-3.3-70b-versatile",
            "temperature": 0.3,
            "max_tokens": 2000
        },
    },
    "meeting_analyzer": {
        "model": {
            "name": "llama-3.3-70b-versatile",
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
            "name": "deepseek-reasoner",
            "temperature": 0.3,
            "max_tokens": 5000,
            "api_endpoint": "https://api.deepseek.com/v1",
            "api_key": "${DEEPSEEK_API_KEY}"
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
