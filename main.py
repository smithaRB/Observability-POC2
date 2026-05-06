#!/usr/bin/env python3
"""
LLM-Powered Incident Analyzer
Main orchestration script that pulls incidents from Dynatrace,
analyzes them with Claude, and routes to ServiceNow or Slack based on confidence.
"""

import logging
import time
from datetime import datetime
from dynatrace_client import DynatraceClient
from llm_analyzer import LLMAnalyzer
from decision_engine import DecisionEngine
from servicenow_client import ServiceNowClient
from slack_client import SlackClient
from config import DEFAULT_HOURS_BACK

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('incident_analyzer.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class IncidentAnalyzer:
    def __init__(self):
        self.dynatrace = DynatraceClient()
        self.llm = LLMAnalyzer()
        self.decision_engine = DecisionEngine()
        self.servicenow = ServiceNowClient()
        self.slack = SlackClient()

    def run_analysis_pipeline(self, hours_back=DEFAULT_HOURS_BACK):
        """
        Main pipeline: fetch problems -> analyze -> decide -> act
        """
        logger.info(f"Starting incident analysis pipeline for last {hours_back} hours")

        try:
            # Step 1: Fetch recent problems from Dynatrace
            problems_response = self.dynatrace.get_recent_problems(hours_back)
            problems = problems_response.get('problems', [])

            logger.info(f"Found {len(problems)} problems to analyze")

            processed_count = 0
            for problem in problems:
                try:
                    self._process_single_problem(problem)
                    processed_count += 1
                    time.sleep(1)  # Rate limiting
                except Exception as e:
                    logger.error(f"Failed to process problem {problem.get('problemId')}: {str(e)}")
                    continue

            logger.info(f"Successfully processed {processed_count} out of {len(problems)} problems")

        except Exception as e:
            logger.error(f"Pipeline failed: {str(e)}")
            raise

    def _process_single_problem(self, problem_summary):
        """
        Process a single problem through the entire pipeline
        """
        problem_id = problem_summary.get('problemId')
        logger.info(f"Processing problem: {problem_id}")

        # Get detailed problem data
        problem_details = self.dynatrace.get_problem_details(problem_id)
        formatted_data = self.dynatrace.format_problem_for_llm(problem_details)

        # Skip if problem is already resolved
        if formatted_data.get('status') == 'RESOLVED':
            logger.info(f"Skipping resolved problem: {problem_id}")
            return

        # Step 2: Analyze with LLM
        logger.info(f"Analyzing problem {problem_id} with LLM")
        analysis_result = self.llm.analyze_incident(formatted_data)

        # Step 3: Make decision
        decision = self.decision_engine.make_decision(analysis_result)
        logger.info(f"Decision for {problem_id}: {decision['action']} - {decision['reason']}")

        # Step 4: Execute action
        if decision['action'] == 'create_ticket':
            self._create_servicenow_ticket(formatted_data, analysis_result, decision)
        elif decision['action'] == 'slack_notification':
            self._send_slack_notification(formatted_data, analysis_result, decision)

    def _create_servicenow_ticket(self, problem_data, analysis_result, decision):
        """
        Create ServiceNow incident
        """
        try:
            ticket_result = self.servicenow.create_incident(problem_data, analysis_result, decision)
            logger.info(f"Created ServiceNow ticket: {ticket_result.get('incident_number')}")
        except Exception as e:
            logger.error(f"Failed to create ServiceNow ticket: {str(e)}")
            # Fallback to Slack
            self._send_slack_notification(problem_data, analysis_result, {
                'action': 'slack_notification',
                'reason': f"ServiceNow creation failed: {str(e)}",
                'requires_human_review': True
            })

    def _send_slack_notification(self, problem_data, analysis_result, decision):
        """
        Send notification to Slack
        """
        try:
            slack_result = self.slack.send_notification(problem_data, analysis_result, decision)
            logger.info("Slack notification sent successfully")
        except Exception as e:
            logger.error(f"Failed to send Slack notification: {str(e)}")

def main():
    """
    Main entry point
    """
    analyzer = IncidentAnalyzer()

    # Run analysis for last configured hours
    analyzer.run_analysis_pipeline()

    # Optional: Run continuously
    # while True:
    #     analyzer.run_analysis_pipeline(hours_back=1)  # Check last hour
    #     time.sleep(3600)  # Wait 1 hour

if __name__ == "__main__":
    main()