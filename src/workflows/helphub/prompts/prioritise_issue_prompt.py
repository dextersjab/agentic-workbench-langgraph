"""
Prompts for priority assessment node in HelpHub workflow.

TODO for participants: Customize priority levels and criteria to match
your organization's SLA and incident management standards.
"""

# Main priority assessment prompt
PRIORITY_PROMPT = """
You are an IT support specialist assessing the priority of a support request.

User Request: {user_input}
Conversation History: {conversation_history}
Category: {category}
User Context: {user_context}

Priority Levels:
**P1 - CRITICAL (4-hour SLA)**
- Complete system outages affecting business operations
- Security breaches or data loss
- Safety-related issues
- Critical business deadlines at risk

**P2 - HIGH (24-hour SLA)**
- Partial system outages or significant performance issues
- Issues affecting multiple users
- Business processes significantly impacted
- Important deadlines at risk

**P3 - MEDIUM (72-hour SLA)**
- Single user issues with workarounds available
- General requests and questions
- Non-critical system issues
- Enhancement requests

Assess based on:
1. **Business Impact**: How many users/processes affected?
2. **Urgency**: Timeline sensitivity and deadline pressure
3. **User Role**: Business criticality of affected user
4. **System Criticality**: Importance of affected systems
5. **Workaround Availability**: Alternative solutions available?

Format your response as:
PRIORITY: [P1/P2/P3]
IMPACT: [description of business impact]
URGENCY: [description of time sensitivity]
REASONING: [detailed justification]
SLA_HOURS: [4/24/72]

TODO for participants:
- Adjust priority criteria for your organization
- Add department-specific priority rules
- Include VIP user handling procedures
- Customize SLA times for your service levels
- Add escalation triggers for each priority level
"""

# VIP user priority adjustment prompt
VIP_PRIORITY_PROMPT = """
This request is from a VIP user requiring special handling:

User: {user_name}
Role: {user_role}
Department: {department}
VIP Level: {vip_level}
Standard Priority: {standard_priority}

VIP Escalation Rules:
- C-Level executives: Minimum P2, escalate P3 to P2
- Department heads: Minimum P2 during business hours
- Board members: Immediate escalation regardless of issue
- Key client contacts: Business impact assessment required

Adjust priority considering:
1. VIP status and organizational impact
2. Business hours and availability requirements
3. Delegation and coverage options
4. Reputational risk factors

Provide:
- ADJUSTED_PRIORITY: [P1/P2/P3]
- ESCALATION_REQUIRED: [Yes/No]
- SPECIAL_HANDLING: [specific instructions]
- NOTIFICATION_LIST: [who to inform]

TODO for participants:
- Define your organization's VIP criteria
- Add role-based priority adjustments
- Include after-hours escalation procedures
- Customize notification requirements
"""

# Emergency escalation prompt
EMERGENCY_ESCALATION_PROMPT = """
Potential emergency situation detected requiring immediate assessment:

User Request: {user_input}
Urgency Indicators: {urgency_indicators}
Location: {location}
Time: {timestamp}

Emergency Categories:
**SAFETY** - Fire, flooding, electrical hazards, physical safety
**SECURITY** - Breaches, unauthorized access, malware, data theft
**INFRASTRUCTURE** - Critical system failures, power outages, network down
**DATA** - Data loss, corruption, backup failures, compliance breaches

Immediate Actions Required:
1. Confirm emergency status
2. Determine severity level
3. Identify immediate response team
4. Assess containment needs
5. Document initial response

Response Format:
EMERGENCY_LEVEL: [CRITICAL/HIGH/NORMAL]
CATEGORY: [SAFETY/SECURITY/INFRASTRUCTURE/DATA]
IMMEDIATE_ACTIONS: [bulleted list]
ESCALATION_PATH: [who to contact]
CONTAINMENT: [immediate steps needed]

TODO for participants:
- Define emergency response procedures
- Add location-specific protocols
- Include after-hours contact information
- Customize for your incident response plan
- Add compliance and legal considerations
"""

# Business impact assessment prompt
BUSINESS_IMPACT_PROMPT = """
Assess the business impact of this IT issue:

Issue Description: {user_input}
Affected Systems: {affected_systems}
User Count: {user_count}
Departments: {departments}
Business Processes: {processes}

Impact Dimensions:
1. **Revenue Impact**: Lost sales, billing delays, customer dissatisfaction
2. **Productivity Impact**: Work stoppage, reduced efficiency, missed deadlines
3. **Compliance Impact**: Regulatory violations, audit failures, legal risks
4. **Reputation Impact**: Customer perception, brand damage, stakeholder confidence

Quantify impact:
- FINANCIAL: Estimated cost per hour of downtime
- OPERATIONAL: Percentage of workforce affected
- TEMPORAL: Maximum acceptable downtime
- STRATEGIC: Long-term business consequences

Provide assessment:
IMPACT_LEVEL: [CRITICAL/HIGH/MEDIUM/LOW]
COST_PER_HOUR: [estimated financial impact]
MAX_DOWNTIME: [acceptable outage duration]
BUSINESS_JUSTIFICATION: [priority reasoning]

TODO for participants:
- Add your organization's impact calculation methods
- Include department-specific impact factors
- Define financial impact thresholds
- Add compliance and regulatory considerations
"""
