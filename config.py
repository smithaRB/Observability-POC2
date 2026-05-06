import os

# Dynatrace Configuration
DYNATRACE_BASE_URL = os.getenv("DYNATRACE_BASE_URL", "https://your-environment.live.dynatrace.com")
DYNATRACE_API_TOKEN = os.getenv("DYNATRACE_API_TOKEN")

# LLM Configuration (Using Claude)
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-3-sonnet-20240229")

# ServiceNow Configuration
SERVICENOW_INSTANCE = os.getenv("SERVICENOW_INSTANCE", "your-instance.service-now.com")
SERVICENOW_USERNAME = os.getenv("SERVICENOW_USERNAME")
SERVICENOW_PASSWORD = os.getenv("SERVICENOW_PASSWORD")
SERVICENOW_ASSIGNMENT_GROUP = os.getenv("SERVICENOW_ASSIGNMENT_GROUP", "IT Operations")
SERVICENOW_CATEGORY = os.getenv("SERVICENOW_CATEGORY", "Software")
SERVICENOW_SUBCATEGORY = os.getenv("SERVICENOW_SUBCATEGORY", "Application")

# Slack Configuration
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

# Decision Engine Configuration
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.8"))
HIGH_RISK_ACTIONS_STR = os.getenv("HIGH_RISK_ACTIONS", "restart_service,scale_down,delete_resources")
HIGH_RISK_ACTIONS = [action.strip() for action in HIGH_RISK_ACTIONS_STR.split(",")]

# Analysis Configuration
DEFAULT_HOURS_BACK = int(os.getenv("DEFAULT_HOURS_BACK", "24"))