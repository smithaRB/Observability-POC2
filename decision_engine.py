from config import CONFIDENCE_THRESHOLD, HIGH_RISK_ACTIONS

class DecisionEngine:
    def __init__(self):
        self.confidence_threshold = CONFIDENCE_THRESHOLD
        self.high_risk_actions = HIGH_RISK_ACTIONS

    def make_decision(self, analysis_result):
        """
        Decide whether to auto-create ticket, send to Slack, or require manual review
        """
        confidence = analysis_result.get('confidence_level', 0)
        risk_level = analysis_result.get('risk_level', 'Medium')
        recommended_actions = analysis_result.get('recommended_actions', [])

        # Check if any recommended action is high-risk
        has_high_risk_action = any(
            any(risk_action.lower() in action.lower() for risk_action in self.high_risk_actions)
            for action in recommended_actions
        )

        decision = {
            'action': None,
            'reason': '',
            'requires_human_review': False
        }

        if confidence >= self.confidence_threshold and not has_high_risk_action:
            # Auto-create ServiceNow ticket
            decision['action'] = 'create_ticket'
            decision['reason'] = f"High confidence ({confidence:.2f}) and low-risk actions"
        elif confidence < 0.5 or risk_level.lower() == 'high' or has_high_risk_action:
            # Send to Slack for human review
            decision['action'] = 'slack_notification'
            decision['reason'] = f"Low confidence ({confidence:.2f}), high risk, or high-risk actions detected"
            decision['requires_human_review'] = True
        else:
            # Medium confidence - send to Slack but don't require immediate action
            decision['action'] = 'slack_notification'
            decision['reason'] = f"Medium confidence ({confidence:.2f}) - review recommended"
            decision['requires_human_review'] = True

        return decision

    def get_runbook_actions(self):
        """
        Return list of approved runbook actions
        """
        return [
            "restart_application",
            "scale_up_resources",
            "clear_cache",
            "update_configuration",
            "notify_team",
            "monitor_metrics"
        ]