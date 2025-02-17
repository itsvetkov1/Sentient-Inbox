# #!/usr/bin/env python3
# import os
# import sys
# import json
# from pathlib import Path

# def create_env_file():
#     """Create .env file with required variables."""
#     env_template = """# API Keys
# GROQ_API_KEY=your_groq_api_key_here
# OPENAI_API_KEY=your_openai_api_key_here

# # Gmail Configuration
# GMAIL_CREDENTIALS_FILE=client_secret.json
# GMAIL_TOKEN_FILE=token.json

# # Application Settings
# BATCH_SIZE=50
# PROCESSING_INTERVAL=300  # 5 minutes
# LOG_LEVEL=INFO

# # Performance Settings
# MAX_RETRIES=3
# REQUEST_TIMEOUT=30
# """
    
#     if not os.path.exists('.env'):
#         with open('.env', 'w') as f:
#             f.write(env_template)
#         print("Created .env file - please update with your actual credentials")

# def create_directory_structure():
#     """Create necessary directories."""
#     directories = [
#         'logs',
#         'data',
#         'data/cache',
#         'data/metrics'
#     ]
    
#     for directory in directories:
#         Path(directory).mkdir(parents=True, exist_ok=True)
#     print("Created directory structure")

# def initialize_json_files():
#     """Initialize JSON files with default structure."""
#     json_files = {
#         'data/metrics/groq_metrics.json': {
#             'requests': [],
#             'errors': [],
#             'performance': {
#                 'avg_response_time': 0,
#                 'total_requests': 0,
#                 'success_rate': 100
#             }
#         },
#         'data/cache/meeting_mails.json': {
#             'last_updated': None,
#             'meetings': []
#         },
#         'data/email_responses.json': {
#             'responses': []
#         }
#     }
    
#     for file_path, default_content in json_files.items():
#         if not os.path.exists(file_path):
#             with open(file_path, 'w') as f:
#                 json.dump(default_content, f, indent=2)
#     print("Initialized JSON files")

# def verify_dependencies():
#     """Verify and install required dependencies."""
#     try:
#         import pip
#         requirements = [
#             'groq',
#             'google-auth-oauthlib',
#             'google-auth-httplib2',
#             'google-api-python-client',
#             'python-dotenv',
#             'aiohttp',
#             'openai'
#         ]
        
#         for package in requirements:
#             try:
#                 __import__(package)
#             except ImportError:
#                 print(f"Installing {package}...")
#                 pip.main(['install', package])
        
#         print("All dependencies verified")
#         return True
#     except Exception as e:
#         print(f"Error verifying dependencies: {e}")
#         return False

# def main():
#     """Run setup process."""
#     print("Starting setup process...")
    
#     try:
#         create_env_file()
#         create_directory_structure()
#         initialize_json_files()
#         if verify_dependencies():
#             print("\nSetup completed successfully!")
#             print("\nNext steps:")
#             print("1. Update the .env file with your API keys")
#             print("2. Place your Gmail OAuth credentials in client_secret.json")
#             print("3. Run 'python main.py' to start the application")
#         else:
#             print("\nSetup failed - please check the error messages above")
#     except Exception as e:
#         print(f"\nSetup failed: {e}")
#         sys.exit(1)

# if __name__ == "__main__":
#     main()


# setup.py
import os
from pathlib import Path

def setup_directories():
    """Create required directory structure for the application."""
    directories = [
        'logs/meeting_analyzer/model_responses/archives',
        'data/secure',
        'data/metrics'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {directory}")

if __name__ == "__main__":
    setup_directories()