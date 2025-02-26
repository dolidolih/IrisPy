import json
from typing import Any, Optional

def load_json_string(json_string: Optional[str]) -> Optional[Any]:
    if json_string is None:
        return None
    try:
        return json.loads(json_string)
    except json.JSONDecodeError:
        print(f"Warning: Could not decode JSON string: {json_string}")
        return json_string