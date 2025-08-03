"""
ServiceHub Support Ticket Policy

Comprehensive business domain policy that provides realistic enterprise IT support context
for grounding AI agents in actual business constraints and procedures.

This is part of the context engineering approach to provide domain-specific grounding
for AI agents operating in business environments.
"""

from ..business_context import KB_CATEGORIES

SERVICEHUB_SUPPORT_TICKET_POLICY = """
## ServiceHub IT Support Policy & Procedures

### ServiceHub Business Context
**Organization**: ServiceHub Ltd - Professional services company (650 employees)
**Locations**: London HQ, Manchester office, Edinburgh satellite office, 40% remote workforce
**Core Systems**: ServiceHub Portal, Dynamics 365, SharePoint Online, Azure AD, Salesforce CRM
**Support Hours**: 7:00-19:00 GMT weekdays, emergency on-call for P1 issues
**Maintenance Windows**: Sundays 02:00-06:00 GMT (advance notice required for user-facing changes)

### Service Level Agreements (SLA)
**Critical (P1)**: 1 hour response, 4 hours resolution
**High (P2)**: 4 hours response, 24 hours resolution  
**Medium (P3)**: 1 business day response, 3 business days resolution
**Low (P4)**: 2 business days response, 5 business days resolution

### Priority Classification Guidelines
- **Critical (P1)**: System outages affecting >50 users, security breaches, data loss, Salesforce CRM down, payroll system failures
- **High (P2)**: Individual unable to work, failed hardware, access lockouts, VPN connectivity issues for remote workers
- **Medium (P3)**: Performance issues, software requests, password resets, ServiceHub Portal slow response
- **Low (P4)**: How-to questions, feature requests, training needs, general inquiries

### Department-Specific Procedures

**Finance Department**: 
- Access to Dynamics 365 Finance requires CFO approval and compliance training
- All financial system changes require change advisory board (CAB) approval
- PCI DSS compliance mandatory for payment processing access
- Month-end/year-end: P2 priority for any finance system issues

**Sales Team**:
- Salesforce CRM issues automatically elevated to P1 during business hours
- Mobile device setup priority for field sales representatives
- Lead data export requires data protection officer approval

**Engineering**:
- Development environment access requires technical lead approval
- GitHub Enterprise and Azure DevOps access tied to project assignments
- Code repository access reviews conducted monthly

**HR Department**:
- BambooHR system access restricted to HR team and approved managers
- Employee data requests require GDPR compliance verification
- Payroll system access requires dual approval (HR Director + IT Security)

### Vendor Relationships & Escalation Contacts
- **Microsoft 365**: Premier Support Contract #MS-SH-2024-001, escalate via Sarah Chen (sarah.chen@servicehub.com)
- **Salesforce**: Success Plan, contact via Tom Mitchell (tom.mitchell@servicehub.com)
- **Hardware Warranty**: Dell ProSupport Plus, Lenovo Premier Support
- **Network Infrastructure**: BT Business, emergency contact 0800-800-150

### Business-Specific Procedures

**Software Requests**: 
- Standard catalogue items (Office 365, Adobe Acrobat, Zoom Pro): Department head approval via ServiceHub Portal
- Purchases >£100: Business case required, finance approval, procurement process via Emma Thompson (procurement@servicehub.com)
- Engineering tools: Technical Architecture Review Board approval required
- Creative software: Marketing Director approval for Adobe Creative Suite

**Hardware Replacements**: 
- Warranty replacements: Auto-approved, asset tag transfer required
- New equipment: Budget approval required, standard builds mandatory
- BYOD policy: Security baseline configuration, MDM enrollment mandatory
- Return process: Asset disposal via TechCycle Ltd, data destruction certificate required

**Access Management**:
- New starters: Access provisioned within 24 hours of HR system notification
- Role changes: Manager approval + HR confirmation required
- Contractors: Limited access, maximum 6-month duration, sponsor required
- Departing employees: Access revoked within 2 hours of HR notification
- Emergency access: On-call manager approval, 24-hour temporary access maximum

**Location-Specific Considerations**:
- Manchester office: Shared printer pool, badge access via facilities team
- Edinburgh satellite: Local IT contact Jamie Ross (jamie.ross@servicehub.com)
- Remote workers: VPN mandatory, home broadband support excluded
- London HQ: Hot-desking environment, mobile device priority for desk booking

### Compliance & Security Requirements

**Data Protection (GDPR)**:
- EU employee data: Data Protection Officer review mandatory
- Data subject access requests: 72-hour response SLA
- Data breach reporting: Immediate escalation to DPO and legal team
- Cross-border data transfer: Adequacy decision verification required

**Financial Compliance**:
- SOX controls: Segregation of duties for financial system access
- Audit trail: All financial system changes logged and retained 7 years
- External auditor access: Temporary read-only accounts, audit committee approval

**Security Protocols**:
- Password resets: Employee ID + manager confirmation + security questions
- Privileged access: Multi-factor authentication mandatory, quarterly review
- VPN access: Security awareness training required, certificate-based authentication
- Shared mailboxes: Business justification, expiry date, quarterly access review
- Cloud storage: OneDrive for Business only, external sharing restrictions apply

### Communication Standards
- Use ServiceHub terminology: "Portal" not "system", "colleagues" not "users"
- Include relevant reference numbers: Salesforce case numbers, Microsoft incident IDs
- Realistic timelines based on SLA commitments and current workload
- Escalation paths clearly communicated with contact information
- Business impact assessment for all P1/P2 issues

### Quality Assurance & Continuous Improvement
- Customer satisfaction surveys: Mandatory for P1/P2 tickets, optional for P3/P4
- Knowledge base updates: Within 48 hours of novel issue resolution
- Post-incident reviews: Required for any outage >2 hours, stakeholder attendance mandatory
- Monthly service review: Department heads, SLA performance, trend analysis
- Quarterly business review: IT Director, key stakeholders, budget and roadmap discussions
"""