import requests
import json
from config import SERVICENOW_INSTANCE, SERVICENOW_USERNAME, SERVICENOW_PASSWORD, SERVICENOW_ASSIGNMENT_GROUP, SERVICENOW_CATEGORY, SERVICENOW_SUBCATEGORY

class ServiceNowClient:
    def __init__(self):
        self.base_url = f"https://{SERVICENOW_INSTANCE}"
        self.auth = (SERVICENOW_USERNAME, SERVICENOW_PASSWORD)
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    def create_incident(self, problem_data, analysis_result, decision):
        """
        Create a ServiceNow incident with the analysis
        """
        incident_data = {
            "short_description": f"Auto-analyzed incident: {problem_data.get('title', 'Unknown issue')}",
            "description": self._build_incident_description(problem_data, analysis_result),
            "urgency": self._map_business_impact_to_urgency(analysis_result.get('business_impact')),
            "impact": self._map_business_impact_to_impact(analysis_result.get('business_impact')),
            "category": SERVICENOW_CATEGORY,
            "subcategory": SERVICENOW_SUBCATEGORY,
            "assignment_group": SERVICENOW_ASSIGNMENT_GROUP,
            "work_notes": f"Auto-created by Incident Analyzer. Confidence: {analysis_result.get('confidence_level', 0):.2f}"
        }

        url = f"{self.base_url}/api/now/table/incident"
        response = requests.post(url, auth=self.auth, headers=self.headers, json=incident_data)

        if response.status_code in [200, 201]:
            result = response.json()
            return {
                "success": True,
                "incident_number": result.get('result', {}).get('number'),
                "sys_id": result.get('result', {}).get('sys_id')
            }
        else:
            raise Exception(f"Failed to create ServiceNow incident: {response.status_code} - {response.text}")

    def _build_incident_description(self, problem_data, analysis_result):
        """
        Build detailed incident description
        """
        description = f"""
INCIDENT ANALYSIS REPORT

Problem ID: {problem_data.get('problem_id')}
Title: {problem_data.get('title')}
Severity: {problem_data.get('severity')}

ROOT CAUSE ANALYSIS:
{analysis_result.get('probable_root_cause')}

BUSINESS IMPACT: {analysis_result.get('business_impact')}

RECOMMENDED ACTIONS:
{chr(10).join(f"- {action}" for action in analysis_result.get('recommended_actions', []))}

CONFIDENCE LEVEL: {analysis_result.get('confidence_level', 0):.2%}
RISK LEVEL: {analysis_result.get('risk_level', 'Unknown')}

ADDITIONAL INSIGHTS:
{analysis_result.get('additional_insights', 'None')}

AFFECTED ENTITIES:
{chr(10).join(f"- {entity.get('name')} ({entity.get('entity_type')})" for entity in problem_data.get('affected_entities', []))}
"""
        return description

    def _map_business_impact_to_urgency(self, business_impact):
        """
        Map business impact to ServiceNow urgency
        """
        impact_map = {
            'Low': '3',      # Low
            'Medium': '2',   # Medium
            'High': '2',     # Medium (could be 1 for High)
            'Critical': '1'  # High
        }
        return impact_map.get(business_impact, '2')

    def _map_business_impact_to_impact(self, business_impact):
        """
        Map business impact to ServiceNow impact
        """
        impact_map = {
            'Low': '3',      # Low
            'Medium': '2',   # Medium
            'High': '2',     # Medium
            'Critical': '1'  # High
        }
        return impact_map.get(business_impact, '2')