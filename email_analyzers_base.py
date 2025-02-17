from dataclasses import dataclass
from typing import List, Dict, Optional
from email.message import Message

@dataclass
class EmailAnalysisResult:
    is_meeting: bool
    action_required: bool
    relevant_data: Dict[str, str]
    raw_email: Message

class BaseEmailAnalyzer:
    def analyze_email(self, email: Message) -> EmailAnalysisResult:
        raise NotImplementedError("Must implement analyze_email")
