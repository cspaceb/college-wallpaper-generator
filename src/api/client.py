import os
import requests
from dotenv import load_dotenv

load_dotenv()

class CFBDClient:
    BASE_URL = "https://api.collegefootballdata.com"

    def __init__(self):
        self.api_key = os.getenv("CFBD_API_KEY")
        if not self.api_key:
            raise ValueError("CFBD_API_KEY not found in .env")

        self.headers = {
            "Authorization": f"Bearer {self.api_key}"
        }

    def get(self, endpoint, params=None):
        url = f"{self.BASE_URL}{endpoint}"
        response = requests.get(url, headers=self.headers, params=params)

        if response.status_code != 200:
            raise Exception(
                f"API error {response.status_code}: {response.text}"
            )

        return response.json()
