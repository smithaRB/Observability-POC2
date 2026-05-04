import anthropic
import json
from config import ANTHROPIC_API_KEY, CLAUDE_MODEL

class LLMAnalyzer:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        self.model = CLAUDE_MODEL

    def analyze_incident(self, problem_data):
        """
        Send formatted problem data to Claude for analysis
        """
        prompt = self._build_analysis_prompt(problem_data)

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.1,  # Low temperature for consistent analysis
                system="You are an expert DevOps engineer analyzing IT incidents. Provide structured, actionable analysis.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            analysis_text = response.content[0].text
            return self._parse_analysis_response(analysis_text)

        except Exception as e:
            raise Exception(f"LLM analysis failed: {str(e)}")

    def _build_analysis_prompt(self, problem_data):
        """
        Build the prompt for Claude
        """
        return f"""
Analyze this IT incident from Dynatrace monitoring data and provide a structured assessment.

INCIDENT DATA:
{json.dumps(problem_data, indent=2)}

Please provide your analysis in the following JSON format:
{{
    "probable_root_cause": "Plain English explanation of the most likely root cause",
    "business_impact": "Assessment of business impact (Low/Medium/High/Critical)",
    "recommended_actions": ["Step 1", "Step 2", "Step 3"],
    "confidence_level": 0.85,
    "risk_level": "Low/Medium/High",
    "additional_insights": "Any additional observations or recommendations"
}}

Guidelines:
- Base your analysis on the provided data, not assumptions
- Confidence level should be between 0.0 and 1.0 based on data quality and clarity
- Risk level should reflect the potential impact of recommended actions
- Be specific and actionable in recommendations
- If data is insufficient, lower confidence accordingly
"""

    def _parse_analysis_response(self, response_text):
        """
        Parse Claude's response into structured data
        """
        try:
            # Extract JSON from response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            json_str = response_text[json_start:json_end]

            analysis = json.loads(json_str)

            # Validate required fields
            required_fields = ['probable_root_cause', 'business_impact', 'recommended_actions', 'confidence_level']
            for field in required_fields:
                if field not in analysis:
                    raise ValueError(f"Missing required field: {field}")

            # Ensure confidence is float
            analysis['confidence_level'] = float(analysis['confidence_level'])

            return analysis

        except (json.JSONDecodeError, ValueError) as e:
            # Fallback parsing if JSON extraction fails
            return {
                "probable_root_cause": response_text,
                "business_impact": "Unknown",
                "recommended_actions": ["Manual review required"],
                "confidence_level": 0.1,
                "risk_level": "High",
                "additional_insights": f"Failed to parse structured response: {str(e)}"
            }