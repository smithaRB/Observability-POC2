import requests
import json
from config import SLACK_WEBHOOK_URL

class SlackClient:
    def __init__(self):
        self.webhook_url = SLACK_WEBHOOK_URL

    def send_notification(self, problem_data, analysis_result, decision):
        """
        Send notification to Slack with incident analysis
        """
        message = self._build_slack_message(problem_data, analysis_result, decision)

        payload = {
            "text": "Incident Analysis Alert",
            "blocks": message
        }

        response = requests.post(self.webhook_url, json=payload)

        if response.status_code == 200:
            return {"success": True}
        else:
            raise Exception(f"Failed to send Slack notification: {response.status_code} - {response.text}")

    def _build_slack_message(self, problem_data, analysis_result, decision):
        """
        Build Slack message blocks
        """
        confidence = analysis_result.get('confidence_level', 0)
        confidence_percent = f"{confidence:.1%}"

        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"🚨 Incident Analysis: {problem_data.get('title', 'Unknown Issue')}"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Problem ID:*\n{problem_data.get('problem_id')}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Severity:*\n{problem_data.get('severity', 'Unknown')}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Confidence:*\n{confidence_percent}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Business Impact:*\n{analysis_result.get('business_impact', 'Unknown')}"
                    }
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Root Cause Analysis:*\n{analysis_result.get('probable_root_cause')}"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Recommended Actions:*\n" + "\n".join(f"• {action}" for action in analysis_result.get('recommended_actions', []))
                }
            }
        ]

        # Add decision information
        if decision.get('requires_human_review'):
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"⚠️ *Human Review Required*\n{decision.get('reason')}"
                }
            })
        else:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"✅ *Auto-Resolution*\nServiceNow ticket created. {decision.get('reason')}"
                }
            })

        # Add affected entities if any
        affected_entities = problem_data.get('affected_entities', [])
        if affected_entities:
            entity_text = "\n".join(f"• {entity.get('name')} ({entity.get('entity_type')})" for entity in affected_entities[:5])
            if len(affected_entities) > 5:
                entity_text += f"\n• ... and {len(affected_entities) - 5} more"

            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Affected Entities:*\n{entity_text}"
                }
            })

        return blocks