"""
Prompts for routing node in HelpHub workflow.

TODO for participants: Customize routing logic to match your organization's
support team structure and escalation procedures.
"""

# Main routing decision prompt
ROUTING_PROMPT = """
You are an IT support routing specialist determining the best resolution path.

Ticket Information:
Category: {category}
Priority: {priority}
User: {user_context}
Description: {description}
Business Impact: {business_impact}

Available Routes:

**IMMEDIATE ESCALATION** (for critical issues)
- Senior Support Team
- Emergency Response Team
- Management Escalation

**SERVICEHUB QUEUES** (standard processing)
- Identity Management (access, passwords, permissions)
- Application Support (software issues, installations)
- Infrastructure Team (network, servers, hardware)
- Field Support (on-site hardware, equipment)
- Finance Team (billing, licensing, procurement)
- General Queue (triage, unknown issues)

**SPECIALIZED TEAMS**
- Security Team (incidents, breaches, compliance)
- Database Team (data issues, performance)
- Network Operations (connectivity, infrastructure)
- Vendor Management (third-party software/hardware)

Routing Criteria:
1. **Technical Expertise**: Required skill level and specialization
2. **Response Time**: Priority-based SLA requirements
3. **Availability**: Team capacity and business hours
4. **Escalation Path**: Chain of command for complex issues
5. **Geographic Location**: Site-specific support needs

Provide routing decision:
ROUTE: [ESCALATION/SERVICEHUB/SPECIALIZED]
TARGET: [specific team or queue]
REASONING: [detailed justification]
ESTIMATED_RESOLUTION: [hours/days]
ESCALATION_TRIGGER: [conditions requiring escalation]

TODO for participants:
- Map teams to your organizational structure
- Add skill-based routing algorithms
- Include workload balancing logic
- Customize for your geographic distribution
- Add business hours and timezone handling
"""

# Load balancing prompt
LOAD_BALANCING_PROMPT = """
Multiple teams can handle this {category} issue. Select optimal assignment:

Available Teams: {available_teams}
Current Workloads: {team_workloads}
Team Specialties: {team_specialties}
SLA Requirements: {sla_requirements}

Balancing Factors:
1. **Current Queue Depth**: Tickets waiting per team
2. **Skill Match**: Expertise level for this issue type
3. **Response Time**: Team's current response performance
4. **Availability**: Business hours and shift coverage
5. **Historical Performance**: Success rate for similar issues

Optimization Goals:
- Minimize response time
- Balance workload distribution
- Maximize resolution success rate
- Maintain SLA compliance

Recommendation:
ASSIGNED_TEAM: [team name]
BALANCING_REASON: [why this team was selected]
ALTERNATIVE_TEAMS: [backup options]
MONITORING_METRICS: [what to track]

TODO for participants:
- Implement your team structure and specialties
- Add real-time workload monitoring
- Include skill certification tracking
- Customize performance metrics
"""

# Escalation path prompt
ESCALATION_PATH_PROMPT = """
Define escalation path for this {priority} {category} issue:

Current Assignment: {current_team}
Issue Complexity: {complexity_level}
Time Elapsed: {elapsed_time}
Previous Attempts: {previous_attempts}
User Context: {user_context}

Escalation Triggers:
1. **Time-based**: SLA breach imminent or occurred
2. **Complexity**: Issue beyond current team's expertise
3. **Impact**: Business impact higher than initially assessed
4. **User-requested**: VIP user or management request
5. **Technical**: Requires additional system access or expertise

Escalation Levels:
**Level 1**: Senior technician within same team
**Level 2**: Team lead or specialist team
**Level 3**: Management and cross-functional teams
**Level 4**: Executive leadership and vendor escalation

Define escalation:
CURRENT_LEVEL: [1-4]
NEXT_LEVEL: [1-4]
ESCALATION_REASON: [specific trigger]
TIMEFRAME: [when to escalate]
NOTIFICATION_LIST: [who to inform]
HANDOFF_REQUIREMENTS: [information to transfer]

TODO for participants:
- Define your escalation hierarchy
- Add role-specific escalation triggers
- Include management notification procedures
- Customize for your organizational structure
"""

# Business rules engine prompt
BUSINESS_RULES_PROMPT = """
Apply organizational business rules to this routing decision:

Standard Routing: {standard_routing}
User Profile: {user_profile}
Time Context: {time_context}
Special Circumstances: {special_circumstances}

Business Rules to Evaluate:

**User-based Rules**:
- VIP users get premium routing
- Department-specific routing preferences
- Geographic location requirements
- Language and cultural considerations

**Time-based Rules**:
- Business hours vs after-hours routing
- Holiday and weekend procedures
- Timezone considerations for global teams
- Shift handoff protocols

**Issue-based Rules**:
- Security issues require immediate specialized routing
- Compliance-related issues need audit trail
- Vendor issues require contract management involvement
- Training requests route to learning team

**Organizational Rules**:
- Budget approval requirements for procurement
- Change management processes for system modifications
- Documentation requirements for knowledge base
- Quality assurance and review processes

Rule Assessment:
APPLICABLE_RULES: [list of triggered rules]
ROUTING_MODIFICATIONS: [changes from standard routing]
COMPLIANCE_REQUIREMENTS: [additional procedures needed]
APPROVAL_REQUIRED: [management or budget approvals]
DOCUMENTATION_NEEDS: [special recording requirements]

TODO for participants:
- Encode your organization's specific business rules
- Add compliance and regulatory requirements
- Include budget and approval workflows
- Customize for your industry standards
"""
