# AWS Incident Analyzer Architecture Sequence

This document describes the AWS incident analyzer workflow and the interaction between EventBridge, the application, Dynatrace, Claude, the decision engine, ServiceNow, and Slack.

```mermaid
sequenceDiagram
    participant EB as EventBridge
    participant APP as Incident Analyzer
    participant DT as Dynatrace API
    participant CLAUDE as Claude API
    participant DE as Decision Engine
    participant SNOW as ServiceNow
    participant SLACK as Slack

    EB->>APP: Trigger every 15 min
    activate APP

    Note over APP: Detection Agent
    APP->>DT: GET /api/v2/problems
    DT-->>APP: Problem records
    APP->>DT: GET /api/v2/logs/search
    DT-->>APP: Related logs

    Note over APP: Diagnosis Agent
    APP->>CLAUDE: POST /v1/messages
    Note right of CLAUDE: Full incident package<br/>200K context window
    CLAUDE-->>APP: Structured JSON analysis

    Note over APP: Cross-validate
    APP->>APP: Compare LLM vs Davis AI
    APP->>APP: Adjust confidence

    Note over APP: Remediation Agent
    APP->>DE: evaluate analysis + risk

    alt Confidence ≥ 80% AND Low Risk
        APP->>SNOW: POST /api/now/table/incident
        SNOW-->>APP: INC0012345
    else Low Confidence OR High Risk
        APP->>SLACK: POST webhook
        SLACK-->>APP: 200 OK
    end

    deactivate APP
```

## Notes

- EventBridge triggers the incident analyzer on a schedule.
- The app collects problem and log data from Dynatrace for diagnosis.
- Claude analyzes the incident package and returns structured JSON.
- The app cross-validates results with Dynatrace Davis AI before adjusting confidence.
- The decision engine evaluates risk and decides whether to create a ServiceNow incident or send a Slack alert.
