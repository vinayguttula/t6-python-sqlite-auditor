"""Models representing the output report structure."""
from typing import List, Dict, Any

class Blocker:
    def __init__(self, id: str, type: str, severity: str, description: str, policy_section: str):
        self.id = id
        self.type = type
        self.severity = severity
        self.description = description
        self.policy_section = policy_section

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "severity": self.severity,
            "description": self.description,
            "policy_section": self.policy_section
        }
