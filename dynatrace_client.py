import requests
import json
from datetime import datetime, timedelta
from config import DYNATRACE_BASE_URL, DYNATRACE_API_TOKEN

class DynatraceClient:
    def __init__(self):
        self.base_url = DYNATRACE_BASE_URL
        self.headers = {
            "Authorization": f"Api-Token {DYNATRACE_API_TOKEN}",
            "Content-Type": "application/json"
        }

    def get_recent_problems(self, hours_back=24):
        """
        Fetch recent problems from Dynatrace API
        """
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours_back)

        params = {
            "from": start_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "to": end_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "pageSize": 100
        }

        url = f"{self.base_url}/api/v2/problems"
        response = requests.get(url, headers=self.headers, params=params)

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to fetch problems: {response.status_code} - {response.text}")

    def get_problem_details(self, problem_id):
        """
        Get detailed information about a specific problem
        """
        url = f"{self.base_url}/api/v2/problems/{problem_id}"
        response = requests.get(url, headers=self.headers)

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to fetch problem details: {response.status_code} - {response.text}")

    def format_problem_for_llm(self, problem_data):
        """
        Format problem data for LLM analysis
        """
        problem = problem_data.get('problem', {})
        impacted_entities = problem_data.get('impactedEntities', [])
        root_cause = problem_data.get('rootCause', {})

        formatted_data = {
            "problem_id": problem.get('problemId'),
            "title": problem.get('title'),
            "status": problem.get('status'),
            "severity": problem.get('severityLevel'),
            "start_time": problem.get('startTime'),
            "end_time": problem.get('endTime'),
            "affected_entities": [
                {
                    "entity_id": entity.get('entityId'),
                    "entity_type": entity.get('entityType'),
                    "name": entity.get('name')
                } for entity in impacted_entities
            ],
            "root_cause": {
                "description": root_cause.get('description'),
                "entity_id": root_cause.get('entityId')
            },
            "tags": problem.get('tags', [])
        }

        return formatted_data