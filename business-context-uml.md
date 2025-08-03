# Business Context UML Diagram

This diagram shows the data model for our business context architecture using the hybrid approach.

```mermaid
classDiagram
    class CompanyInfo {
        +name: string
        +support_hours: string
        +support_email: string
        +support_phone: string
        +ticket_portal: string
    }

    class SupportTeam {
        +name: string
        +description: string
        +response_time_hours: int
        +resolution_time_hours: int
    }

    class PriorityDefinition {
        +name: string
        +description: string
        +response_time_hours: int
        +resolution_time_hours: int
        +examples: List[string]
    }

    class BaseSLAPolicies {
        +priority_multipliers: Dict[string, float]
        +business_hours: BusinessHours
    }

    class BusinessHours {
        +start: string
        +end: string
        +timezone: string
        +working_days: List[string]
    }

    class IssueCategory {
        +keywords: List[string]
        +typical_team: string
        +escalation_triggers: List[string]
    }

    class RoutingRules {
        +auto_escalate_keywords: List[string]
        +specialist_triggers: Dict[string, string]
    }

    class SupportDeskState {
        +messages: List[Dict]
        +current_user_input: string
        +needs_clarification: bool
        +clarification_attempts: int
        +max_clarification_attempts: int
        +issue_category: IssueCategoryType
        +issue_priority: IssuePriorityType
        +gathering_round: int
        +max_gathering_rounds: int
        +needs_more_info: bool
        +info_completeness_confidence: float
        +missing_categories: List[string]
        +user_context: Dict
        +current_response: string
        +custom_llm_chunk: string
        +ticket_id: string
        +ticket_status: string
        +assigned_team: string
        +sla_commitment: string
        +next_steps: string
        +contact_information: Dict
        +estimated_resolution_time: string
        +escalation_path: string
    }

    class BusinessContext {
        <<module>>
        +COMPANY_INFO: CompanyInfo
        +COMPANY_SUPPORT_TEAMS: Dict[string, SupportTeam]
        +BASE_SLA_POLICIES: BaseSLAPolicies
        +PRIORITY_DEFINITIONS: Dict[string, PriorityDefinition]
        +BUSINESS_HOURS_MULTIPLIER: Dict[string, float]
    }

    class SupportDeskBusinessContext {
        <<module>>
        +MAX_GATHERING_ROUNDS: int
        +IssueCategoryType: Literal
        +IssuePriorityType: Literal
        +ISSUE_CATEGORIES: Dict[string, IssueCategory]
        +SUPPORT_TEAMS: Dict[string, SupportTeam]
        +ROUTING_RULES: RoutingRules
        +KB_CATEGORIES: List[string]
        +get_sla_commitment(priority): tuple
        +SLA_COMMITMENTS: Dict[string, tuple]
    }

    class TicketData {
        +ticket_id: string
        +ticket_status: string
        +priority: string
        +category: string
        +assigned_team: string
        +sla_commitment: string
        +issue_summary: string
        +next_steps: string
        +support_email: string
        +support_phone: string
        +ticket_portal: string
        +created_timestamp: string
        +estimated_resolution: string
    }

    BusinessContext --> CompanyInfo : contains
    BusinessContext --> SupportTeam : contains multiple
    BusinessContext --> BaseSLAPolicies : contains
    BusinessContext --> PriorityDefinition : contains multiple
    BaseSLAPolicies --> BusinessHours : contains

    SupportDeskBusinessContext ..> BusinessContext : imports from
    SupportDeskBusinessContext --> IssueCategory : contains multiple
    SupportDeskBusinessContext --> RoutingRules : contains
    SupportDeskBusinessContext --> SupportTeam : extends from company

    SupportDeskState ..> SupportDeskBusinessContext : uses types from
    TicketData ..> SupportDeskBusinessContext : uses SLA from
    TicketData ..> SupportDeskState : generated from

    note for BusinessContext "Shared company-wide business context\nlocated in backend/src/business_context/"
    note for SupportDeskBusinessContext "Workflow-specific business context\nextends company definitions\nlocated in backend/src/workflows/support_desk/"
    note for SupportDeskState "Runtime state for workflow execution\nTracks conversation and ticket progress"
```

## Key Components

### Company-wide Business Context (Shared)
- **CompanyInfo**: Basic company information (name, support hours, contact details)
- **SupportTeam**: Team definitions with SLA response and resolution times
- **PriorityDefinition**: Priority levels (P1-P4) with descriptions and examples
- **BaseSLAPolicies**: Company-wide SLA policies including business hours and priority multipliers

### Support Desk Workflow Context (Specific)
- Extends company definitions with workflow-specific rules
- **IssueCategory**: Categories (hardware, software, access, network, other) with keywords and routing rules
- **RoutingRules**: Auto-escalation keywords and specialist triggers
- Imports and extends company support teams
- Provides `get_sla_commitment()` function that derives SLAs from company policies

### Runtime Data
- **SupportDeskState**: The workflow state that tracks conversation progress and ticket details
- **TicketData**: Final ticket output generated from state with all necessary information

## Relationships
- Solid arrows (→) indicate composition/containment
- Dashed arrows (..>) indicate usage/dependency
- The diagram illustrates the hybrid approach where shared business context is imported and extended by workflow-specific contexts