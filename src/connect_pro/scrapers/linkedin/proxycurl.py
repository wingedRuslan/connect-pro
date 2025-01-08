from typing import Dict, Optional

import requests

from connect_pro.config.settings import settings


class LinkedInClient:
    """Client for interacting with LinkedIn API via ProxyCurl."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.PROXYCURL_API_KEY
        self.api_endpoint = "https://nubela.co/proxycurl/api/v2/linkedin"

    def get_profile(self, linkedin_profile_url: str, mock: bool = False) -> Dict:
        """Fetch LinkedIn profile data."""
        if mock:
            return self._get_mock_profile()

        headers = {"Authorization": f"Bearer {self.api_key}"}
        response = requests.get(
            self.api_endpoint,
            params={"url": linkedin_profile_url},
            headers=headers,
            timeout=10,
        )
        response.raise_for_status()
        return self._clean_response(response.json())

    def _get_mock_profile(self) -> Dict:
        """Get mock profile data for testing."""
        mock_url = "https://gist.githubusercontent.com/wingedRuslan/11dc8d754273d853c39a14cb2be86d85/raw/b5e61b0defad5ff07317ad37fa22b1247fdfc1c1/ruslan-yermak-linkedin.json"
        response = requests.get(mock_url, timeout=10)
        response.raise_for_status()
        return self._clean_response(response.json())

    @staticmethod
    def _clean_response(data: Dict) -> Dict:
        """Clean the API response data."""

        # Remove empty and excluded fields
        excluded_fields = ["people_also_viewed"]
        cleaned_data = {
            k: v
            for k, v in data.items()
            if v not in ([], "", "None", None)
            and k not in excluded_fields
            and "url" not in k.lower()
        }

        # Clean nested fields
        nested_fields = [
            "experiences",
            "education",
            "volunteer_work",
            "certifications",
            "groups",
        ]
        for field in nested_fields:
            if field in cleaned_data and isinstance(cleaned_data[field], list):
                cleaned_data[field] = [
                    {
                        k: v
                        for k, v in item.items()
                        if v not in ([], "", "None", None) and "url" not in k.lower()
                    }
                    for item in cleaned_data[field]
                ]

        return cleaned_data
