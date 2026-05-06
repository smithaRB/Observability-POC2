#!/usr/bin/env python3
"""
Test script for Incident Analyzer components
Tests individual components without making actual API calls
"""

import json
from unittest.mock import Mock, patch
from dynatrace_client import DynatraceClient
from llm_analyzer import LLMAnalyzer
from decision_engine import DecisionEngine
from servicenow_client import ServiceNowClient
from slack_client import SlackClient

def test_dynatrace_client():
    """Test Dynatrace client with mock data"""
    print("Testing Dynatrace Client...")

    # Mock response data
    mock_problem_data = {
        "problem": {
            "problemId": "P-12345",
            "title": "High CPU usage on web server",
            "status": "OPEN",
            "severityLevel": "PERFORMANCE",
            "startTime": 1640995200000,
            "endTime": None
        },
        "impactedEntities": [
            {
                "entityId": "HOST-ABC123",
                "entityType": "HOST",
                "name": "web-server-01"
            }
        ],
        "rootCause": {
            "description": "CPU utilization exceeded 90% for 15 minutes",
            "entityId": "HOST-ABC123"
        }
    }

    client = DynatraceClient()
    formatted = client.format_problem_for_llm(mock_problem_data)

    assert formatted['problem_id'] == 'P-12345'
    assert formatted['title'] == 'High CPU usage on web server'
    assert len(formatted['affected_entities']) == 1

    print("✓ Dynatrace Client test passed")

def test_decision_engine():
    """Test decision engine logic"""
    print("Testing Decision Engine...")

    engine = DecisionEngine()

    # Test high confidence, low risk
    analysis_high_conf = {
        'confidence_level': 0.9,
        'recommended_actions': ['clear_cache', 'notify_team'],  # Use approved actions
        'risk_level': 'Low'
    }
    decision = engine.make_decision(analysis_high_conf)
    assert decision['action'] == 'create_ticket'

    # Test low confidence
    analysis_low_conf = {
        'confidence_level': 0.3,
        'recommended_actions': ['investigate_logs'],
        'risk_level': 'Medium'
    }
    decision = engine.make_decision(analysis_low_conf)
    assert decision['action'] == 'slack_notification'
    assert decision['requires_human_review'] == True

    # Test high risk action
    analysis_high_risk = {
        'confidence_level': 0.9,
        'recommended_actions': ['restart_service', 'scale_down_resources'],
        'risk_level': 'High'
    }
    decision = engine.make_decision(analysis_high_risk)
    assert decision['action'] == 'slack_notification'
    assert decision['requires_human_review'] == True

    print("✓ Decision Engine test passed")

def test_llm_analyzer_mock():
    """Test LLM analyzer with mocked Claude response"""
    print("Testing LLM Analyzer (mocked)...")

    analyzer = LLMAnalyzer()

    # Mock problem data
    problem_data = {
        "problem_id": "P-12345",
        "title": "High CPU usage",
        "affected_entities": [{"name": "web-server-01"}]
    }

    # Mock Claude response
    mock_response = {
        "probable_root_cause": "CPU bottleneck due to high traffic",
        "business_impact": "Medium",
        "recommended_actions": ["Scale up CPU resources", "Optimize application code"],
        "confidence_level": 0.8,
        "risk_level": "Low",
        "additional_insights": "Monitor traffic patterns"
    }

    with patch.object(analyzer.client.messages, 'create') as mock_create:
        mock_message = Mock()
        mock_message.content = [Mock()]
        mock_message.content[0].text = json.dumps(mock_response)
        mock_create.return_value = mock_message

        result = analyzer.analyze_incident(problem_data)

        assert result['confidence_level'] == 0.8
        assert result['probable_root_cause'] == "CPU bottleneck due to high traffic"
        assert len(result['recommended_actions']) == 2

    print("✓ LLM Analyzer test passed")

def test_servicenow_client_mock():
    """Test ServiceNow client with mocked response"""
    print("Testing ServiceNow Client (mocked)...")

    client = ServiceNowClient()

    problem_data = {"title": "Test Problem"}
    analysis_result = {"probable_root_cause": "Test cause"}
    decision = {"reason": "Test"}

    with patch('servicenow_client.requests.post') as mock_post:
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "result": {"number": "INC0012345", "sys_id": "abc123"}
        }
        mock_post.return_value = mock_response

        result = client.create_incident(problem_data, analysis_result, decision)

        assert result['success'] == True
        assert result['incident_number'] == 'INC0012345'

    print("✓ ServiceNow Client test passed")

def test_slack_client_mock():
    """Test Slack client with mocked response"""
    print("Testing Slack Client (mocked)...")

    client = SlackClient()

    problem_data = {"title": "Test Problem"}
    analysis_result = {"confidence_level": 0.8}
    decision = {"action": "slack_notification"}

    with patch('slack_client.requests.post') as mock_post:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        result = client.send_notification(problem_data, analysis_result, decision)

        assert result['success'] == True

    print("✓ Slack Client test passed")

def run_all_tests():
    """Run all component tests"""
    print("Running Incident Analyzer Component Tests")
    print("=" * 50)

    try:
        test_dynatrace_client()
        test_decision_engine()
        test_llm_analyzer_mock()
        test_servicenow_client_mock()
        test_slack_client_mock()

        print("=" * 50)
        print("✅ All tests passed! Components are working correctly.")
        print("\nNext steps:")
        print("1. Set up environment variables in .env file")
        print("2. Update config.py with your actual endpoints")
        print("3. Test with real API calls (use caution with production systems)")
        print("4. Run main.py or langgraph_agents.py")

    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        raise

if __name__ == "__main__":
    run_all_tests()