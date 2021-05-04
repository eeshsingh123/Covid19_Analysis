import json
import requests

from config import FLASK_HOST


def internal_request(port, method: str, data):
    try:
        result = requests.post(
            f"http://{FLASK_HOST}:{port}/{method}",
            data=json.dumps(data),
            headers={'Content-Type': 'application/json'}
        ).text

        result = json.loads(result)
        return result, True

    except json.JSONDecodeError:
        return "JSON decode error", False
    except Exception as e:
        return str(e), False
