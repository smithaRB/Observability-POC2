#!/usr/bin/env python3
"""
LangGraph Multi-Agent Incident Analyzer
Converts the linear pipeline into a proper agentic workflow with three agents:
- Detection Agent: Processes Dynatrace data
- Diagnosis Agent: Performs LLM analysis
- Remediation Agent: Executes decisions
"""

from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage
from dynatrace_client import DynatraceClient
from llm_analyzer import LLMAnalyzer
from decision_engine import DecisionEngine
from servicenow_client import ServiceNowClient
from slack_client import SlackClient
from config import DEFAULT_HOURS_BACK
import logging

logger = logging.getLogger(__name__)

class IncidentState(TypedDict):
    """State for the incident analysis workflow"""
    problem_id: str
    problem_data: Dict[str, Any]
    analysis_result: Dict[str, Any]
    decision: Dict[str, Any]
    action_taken: str
    errors: List[str]

class DetectionAgent:
    """Agent responsible for fetching and processing Dynatrace problem data"""

    def __init__(self):
        self.dynatrace = DynatraceClient()

    def process(self, state: IncidentState) -> IncidentState:
        """Fetch detailed problem data from Dynatrace"""
        try:
            problem_id = state['problem_id']
            logger.info(f"Detection Agent: Processing problem {problem_id}")

            # Get detailed problem data
            problem_details = self.dynatrace.get_problem_details(problem_id)
            formatted_data = self.dynatrace.format_problem_for_llm(problem_details)

            # Skip if already resolved
            if formatted_data.get('status') == 'RESOLVED':
                state['errors'].append("Problem already resolved")
                return state

            state['problem_data'] = formatted_data
            logger.info(f"Detection Agent: Successfully processed {problem_id}")

        except Exception as e:
            error_msg = f"Detection Agent failed: {str(e)}"
            logger.error(error_msg)
            state['errors'].append(error_msg)

        return state

class DiagnosisAgent:
    """Agent responsible for LLM-based root cause analysis"""

    def __init__(self):
        self.llm = LLMAnalyzer()

    def process(self, state: IncidentState) -> IncidentState:
        """Analyze problem data with LLM"""
        try:
            if 'problem_data' not in state or not state['problem_data']:
                state['errors'].append("No problem data available for analysis")
                return state

            logger.info(f"Diagnosis Agent: Analyzing problem {state['problem_id']}")

            analysis_result = self.llm.analyze_incident(state['problem_data'])
            state['analysis_result'] = analysis_result

            logger.info(f"Diagnosis Agent: Analysis complete with confidence {analysis_result.get('confidence_level', 0):.2f}")

        except Exception as e:
            error_msg = f"Diagnosis Agent failed: {str(e)}"
            logger.error(error_msg)
            state['errors'].append(error_msg)

        return state

class RemediationAgent:
    """Agent responsible for deciding and executing remediation actions"""

    def __init__(self):
        self.decision_engine = DecisionEngine()
        self.servicenow = ServiceNowClient()
        self.slack = SlackClient()

    def process(self, state: IncidentState) -> IncidentState:
        """Make decision and execute action"""
        try:
            if 'analysis_result' not in state or not state['analysis_result']:
                state['errors'].append("No analysis result available for decision")
                return state

            logger.info(f"Remediation Agent: Making decision for problem {state['problem_id']}")

            # Make decision
            decision = self.decision_engine.make_decision(state['analysis_result'])
            state['decision'] = decision

            # Execute action
            if decision['action'] == 'create_ticket':
                self._create_ticket(state)
            elif decision['action'] == 'slack_notification':
                self._send_notification(state)

            logger.info(f"Remediation Agent: Action taken - {decision['action']}")

        except Exception as e:
            error_msg = f"Remediation Agent failed: {str(e)}"
            logger.error(error_msg)
            state['errors'].append(error_msg)

        return state

    def _create_ticket(self, state: IncidentState):
        """Create ServiceNow ticket"""
        try:
            ticket_result = self.servicenow.create_incident(
                state['problem_data'],
                state['analysis_result'],
                state['decision']
            )
            state['action_taken'] = f"ServiceNow ticket created: {ticket_result.get('incident_number')}"
        except Exception as e:
            logger.error(f"Failed to create ServiceNow ticket: {str(e)}")
            # Fallback to Slack
            self._send_notification(state)

    def _send_notification(self, state: IncidentState):
        """Send Slack notification"""
        try:
            slack_result = self.slack.send_notification(
                state['problem_data'],
                state['analysis_result'],
                state['decision']
            )
            state['action_taken'] = "Slack notification sent"
        except Exception as e:
            logger.error(f"Failed to send Slack notification: {str(e)}")
            state['action_taken'] = "Failed to send notification"

class IncidentAnalyzerGraph:
    """LangGraph workflow for incident analysis"""

    def __init__(self):
        self.detection_agent = DetectionAgent()
        self.diagnosis_agent = DiagnosisAgent()
        self.remediation_agent = RemediationAgent()
        self.graph = self._build_graph()

    def _build_graph(self):
        """Build the LangGraph workflow"""
        workflow = StateGraph(IncidentState)

        # Add nodes
        workflow.add_node("detection", self.detection_agent.process)
        workflow.add_node("diagnosis", self.diagnosis_agent.process)
        workflow.add_node("remediation", self.remediation_agent.process)

        # Define flow
        workflow.set_entry_point("detection")
        workflow.add_edge("detection", "diagnosis")
        workflow.add_edge("diagnosis", "remediation")
        workflow.add_edge("remediation", END)

        return workflow.compile()

    def analyze_incident(self, problem_id: str) -> Dict[str, Any]:
        """Run the complete analysis workflow for a single incident"""
        initial_state: IncidentState = {
            "problem_id": problem_id,
            "problem_data": {},
            "analysis_result": {},
            "decision": {},
            "action_taken": "",
            "errors": []
        }

        logger.info(f"Starting LangGraph workflow for problem {problem_id}")
        final_state = self.graph.invoke(initial_state)
        logger.info(f"Completed LangGraph workflow for problem {problem_id}")

        return dict(final_state)

def run_langgraph_analysis(hours_back: int = DEFAULT_HOURS_BACK):
    """Run the LangGraph-based analysis pipeline"""
    logger.info(f"Starting LangGraph incident analysis for last {hours_back} hours")

    dynatrace = DynatraceClient()
    analyzer = IncidentAnalyzerGraph()

    try:
        # Fetch problems
        problems_response = dynatrace.get_recent_problems(hours_back)
        problems = problems_response.get('problems', [])

        logger.info(f"Found {len(problems)} problems to analyze with LangGraph")

        results = []
        for problem in problems:
            try:
                problem_id = problem.get('problemId')
                result = analyzer.analyze_incident(problem_id)
                results.append(result)

                # Log summary
                if result.get('errors'):
                    logger.warning(f"Problem {problem_id} had errors: {result['errors']}")
                else:
                    logger.info(f"Problem {problem_id} processed successfully: {result.get('action_taken', 'No action')}")

            except Exception as e:
                logger.error(f"Failed to process problem {problem.get('problemId')}: {str(e)}")
                continue

        logger.info(f"LangGraph analysis complete. Processed {len(results)} problems.")
        return results

    except Exception as e:
        logger.error(f"LangGraph pipeline failed: {str(e)}")
        raise

if __name__ == "__main__":
    # Example usage
    results = run_langgraph_analysis()
    print(f"Analysis complete. Results: {len(results)} incidents processed.")