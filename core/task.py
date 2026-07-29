from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass
class Task:
    """
    يمثل أي مهمة داخل النظام.
    """

    task_type: str

    command: str

    data: Dict[str, Any] = field(default_factory=dict)