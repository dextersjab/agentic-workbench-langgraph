"""
Prompts for ServiceHub integration node in HelpHub workflow.

TODO for participants: Customize ticket formatting and integration
details to match your ServiceHub ITSM platform configuration.
"""

# Main ServiceHub ticket creation prompt
SERVICEHUB_PROMPT = """
Format ticket information for ServiceHub ITSM platform creation:

Ticket Details:
Category: {category}
Priority: {priority}
User Request: {user_input}
Conversation: {conversation_history}
User Context: {user_context}
Routing Decision: {routing_decision}

Format Requirements:
1. **Subject Line**: Concise, searchable summary (max 80 chars)
2. **Description**: Detailed issue description with context
3. **Impact Statement**: Business impact and affected users
4. **Steps Attempted**: User's troubleshooting efforts
5. **Technical Details**: Relevant system information
6. **Resolution Notes**: Any immediate actions taken

ServiceHub Fields to Populate:
- Requester: User email and contact information
- Category/Subcategory: ServiceHub taxonomy mapping
- Priority: P1/P2/P3 with business justification
- Assignment Group: Target team from routing decision
- Configuration Item: Affected systems/services
- Location: User's physical location
- Due Date: SLA-based resolution target

Ticket Format:
SUBJECT: [concise issue summary]
DESCRIPTION: [detailed problem description]
IMPACT: [business impact statement]
STEPS_TAKEN: [troubleshooting attempts]
TECHNICAL_INFO: [system details]
URGENCY_JUSTIFICATION: [priority reasoning]
RESOLUTION_NOTES: [immediate actions]

TODO for participants:
- Map categories to your ServiceHub taxonomy
- Add organization-specific required fields
- Include asset management integration
- Customize for your ITSM workflow
- Add approval and change management requirements
"""

# SLA calculation prompt
SLA_CALCULATION_PROMPT = """
Calculate ServiceHub SLA targets for this ticket:

Ticket Information:
Priority: {priority}
Category: {category}
User Type: {user_type}
Business Hours: {business_hours}
Submission Time: {submission_time}

SLA Matrix (Business Hours):
**P1 - Critical**
- Initial Response: 30 minutes
- Resolution Target: 4 hours
- Escalation Trigger: 2 hours

**P2 - High**
- Initial Response: 2 hours
- Resolution Target: 24 hours
- Escalation Trigger: 12 hours

**P3 - Medium**
- Initial Response: 8 hours
- Resolution Target: 72 hours
- Escalation Trigger: 48 hours

Adjustment Factors:
- VIP users: 50% faster response times
- After hours: Clock stops outside business hours
- Holidays: Extended SLA during holiday periods
- Complex issues: Additional time for research

Calculate:
INITIAL_RESPONSE_BY: [timestamp]
RESOLUTION_TARGET: [timestamp]
ESCALATION_TRIGGER: [timestamp]
BUSINESS_HOURS_REMAINING: [hours until breach]
HOLIDAY_ADJUSTMENTS: [any SLA extensions]

TODO for participants:
- Define your organization's SLA commitments
- Add customer tier and contract considerations
- Include business calendar integration
- Customize for your support model
"""

# Status update prompt
STATUS_UPDATE_PROMPT = """
Generate ServiceHub status update for ticket {ticket_id}:

Current Status: {current_status}
New Status: {new_status}
Work Performed: {work_performed}
Next Steps: {next_steps}
Resolution Notes: {resolution_notes}

Update Types:
**PROGRESS_UPDATE**
- Work performed since last update
- Current troubleshooting status
- Estimated time to resolution
- Any blockers or delays

**STATUS_CHANGE**
- Reason for status change
- Impact on SLA timelines
- Required approvals or validations
- Communication to stakeholders

**RESOLUTION**
- Final resolution details
- Root cause analysis
- Prevention measures
- Knowledge base updates

**ESCALATION**
- Escalation reason and trigger
- New assignment details
- Handoff information
- Stakeholder notifications

Format update:
UPDATE_TYPE: [PROGRESS/STATUS_CHANGE/RESOLUTION/ESCALATION]
SUMMARY: [brief update summary]
DETAILS: [comprehensive work notes]
NEXT_ACTIONS: [required follow-up steps]
COMMUNICATION: [stakeholder notifications needed]
SLA_IMPACT: [effect on resolution timeline]

TODO for participants:
- Customize update templates for your workflow
- Add approval requirements for status changes
- Include customer communication templates
- Integrate with knowledge management
"""

# Resolution documentation prompt
RESOLUTION_DOCUMENTATION_PROMPT = """
Document ticket resolution for ServiceHub and knowledge base:

Ticket Details:
ID: {ticket_id}
Original Issue: {original_issue}
Final Resolution: {resolution_steps}
Root Cause: {root_cause}
Time to Resolution: {resolution_time}

Documentation Requirements:
1. **Resolution Summary**: What was done to fix the issue
2. **Root Cause Analysis**: Why the issue occurred
3. **Prevention Measures**: How to avoid recurrence
4. **Knowledge Base Article**: Reusable solution documentation
5. **Process Improvements**: Workflow or training recommendations

Create comprehensive documentation:
RESOLUTION_SUMMARY: [clear explanation of fix]
ROOT_CAUSE: [underlying cause analysis]
PREVENTION_STEPS: [measures to prevent recurrence]
KB_ARTICLE_DRAFT: [structured solution document]
PROCESS_RECOMMENDATIONS: [improvement suggestions]
LESSONS_LEARNED: [insights for future incidents]

Knowledge Base Categories:
- Common Issues: Frequently encountered problems
- How-To Guides: Step-by-step procedures
- Troubleshooting: Diagnostic workflows
- Configuration: System setup instructions
- Vendor Solutions: Third-party issue resolutions

TODO for participants:
- Define knowledge management categories
- Add quality review processes
- Include metrics and trending analysis
- Integrate with training materials
- Customize for your documentation standards
"""
