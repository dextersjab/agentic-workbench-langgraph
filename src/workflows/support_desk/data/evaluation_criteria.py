"""
Evaluation Criteria Framework for ServiceHub Domain-Specific Context Engineering

This framework defines metrics to detect whether AI responses demonstrate proper
ServiceHub policy adherence versus generic LLM behavior.
"""

from typing import Dict, Any, List
from dataclasses import dataclass

@dataclass
class PolicyAdherenceMetric:
    """Metric for measuring policy-specific behavior."""
    name: str
    description: str
    weight: float
    detection_criteria: List[str]

@dataclass
class EvaluationResult:
    """Result of domain-specific evaluation."""
    case_id: str
    policy_adherence_score: float  # 0-100
    business_context_score: float  # 0-100
    terminology_score: float       # 0-100
    compliance_score: float        # 0-100
    overall_domain_score: float    # 0-100
    generic_response_indicators: List[str]
    domain_specific_indicators: List[str]
    policy_violations: List[str]

# Policy Adherence Metrics
POLICY_ADHERENCE_METRICS = [
    PolicyAdherenceMetric(
        name="sla_commitment_accuracy",
        description="Uses correct ServiceHub SLA timeframes instead of generic estimates",
        weight=0.20,
        detection_criteria=[
            "P1: 1 hour response, 4 hours resolution",
            "P2: 4 hours response, 24 hours resolution", 
            "P3: 1 business day response, 3 business days resolution",
            "P4: 2 business days response, 5 business days resolution"
        ]
    ),
    
    PolicyAdherenceMetric(
        name="approval_process_adherence",
        description="Follows ServiceHub-specific approval workflows",
        weight=0.25,
        detection_criteria=[
            "Software >£100 requires business case and finance approval",
            "Creative software requires Marketing Director approval",
            "Technical lead approval for engineering repo access",
            "Dual approval (HR Director + IT Security) for payroll access",
            "Manager confirmation for password resets"
        ]
    ),
    
    PolicyAdherenceMetric(
        name="escalation_path_accuracy",
        description="Uses correct ServiceHub escalation contacts and procedures",
        weight=0.15,
        detection_criteria=[
            "Sarah Chen for Microsoft 365 escalation",
            "Tom Mitchell for Salesforce escalation", 
            "Emma Thompson for procurement process",
            "Jamie Ross for Edinburgh office issues",
            "On-call manager for emergency access"
        ]
    ),
    
    PolicyAdherenceMetric(
        name="department_specific_procedures",
        description="Applies department-specific ServiceHub procedures",
        weight=0.20,
        detection_criteria=[
            "Finance: Month-end P2 priority elevation",
            "Sales: Salesforce issues auto P1 during business hours",
            "Engineering: Project-tied repository access",
            "HR: GDPR compliance verification required"
        ]
    ),
    
    PolicyAdherenceMetric(
        name="location_specific_awareness",
        description="Considers ServiceHub location-specific procedures",
        weight=0.10,
        detection_criteria=[
            "Manchester office shared printer pool",
            "Edinburgh satellite office local contact",
            "London HQ hot-desking environment",
            "Remote worker VPN requirements",
            "Home broadband support exclusion"
        ]
    ),
    
    PolicyAdherenceMetric(
        name="compliance_integration",
        description="Incorporates relevant compliance requirements",
        weight=0.10,
        detection_criteria=[
            "GDPR: 72-hour response SLA for data requests",
            "SOX controls for financial system access",
            "PCI DSS for payment processing access",
            "Audit committee approval for external auditor access",
            "Data Protection Officer review for EU employee data"
        ]
    )
]

# Business Context Indicators
SERVICEHUB_TERMINOLOGY = [
    "ServiceHub Portal",
    "colleagues",  # instead of "users"
    "Portal",  # instead of "system"
    "Dynamics 365",
    "Salesforce CRM",
    "ServiceHub catalogue",
    "BambooHR system",
    "Azure DevOps",
    "GitHub Enterprise"
]

GENERIC_RESPONSE_INDICATORS = [
    "I'll escalate this to the next level",
    "Standard troubleshooting steps",
    "Contact your system administrator", 
    "Check with your IT department",
    "Generic ticket creation process",
    "Standard priority classification",
    "Typical resolution timeframe",
    "Contact vendor support"
]

DOMAIN_SPECIFIC_INDICATORS = [
    "ServiceHub Portal approval required",
    "Per ServiceHub policy",
    "ServiceHub SLA commitment",
    "Escalating to [specific ServiceHub contact]",
    "Department-specific procedure applies",
    "Compliance requirement triggered",
    "Location-specific consideration",
    "ServiceHub business context affects priority"
]

def evaluate_domain_specificity(response: str, case_data: Dict[str, Any]) -> EvaluationResult:
    """
    Evaluate whether a response demonstrates ServiceHub domain specificity
    versus generic LLM behavior.
    
    Args:
        response: The AI agent's response text
        case_data: The test case data including expected_behavior
        
    Returns:
        EvaluationResult with detailed scoring
    """
    
    # Initialize scores
    policy_score = 0.0
    business_score = 0.0
    terminology_score = 0.0
    compliance_score = 0.0
    
    detected_generic = []
    detected_domain_specific = []
    policy_violations = []
    
    # Check for ServiceHub-specific behaviors
    # SLA commitment accuracy
    if any(sla in response for sla in ["1 hour", "4 hours", "24 hours", "1 business day", "2 business days"]):
        policy_score += 20
        detected_domain_specific.append("ServiceHub SLA timeframes mentioned")
    
    # Escalation contacts
    escalation_contacts = ["sarah chen", "tom mitchell", "emma thompson", "jamie ross"]
    for contact in escalation_contacts:
        if contact in response.lower():
            policy_score += 15
            detected_domain_specific.append(f"ServiceHub contact: {contact}")
    
    # Approval processes
    approval_terms = ["marketing director", "technical lead", "hr director", "manager approval", "business case"]
    for term in approval_terms:
        if term in response.lower():
            policy_score += 10
            detected_domain_specific.append(f"ServiceHub approval process: {term}")
    
    # Priority handling
    if "p1" in response.lower() or "critical" in response.lower():
        policy_score += 15
        detected_domain_specific.append("Priority classification mentioned")
    
    # Check ServiceHub terminology usage
    terminology_count = 0
    for term in SERVICEHUB_TERMINOLOGY:
        if term.lower() in response.lower():
            terminology_count += 1
            detected_domain_specific.append(f"ServiceHub terminology: {term}")
    terminology_score = min(100, (terminology_count / len(SERVICEHUB_TERMINOLOGY)) * 100)
    
    # Check for generic response indicators (negative scoring)
    for indicator in GENERIC_RESPONSE_INDICATORS:
        if indicator.lower() in response.lower():
            detected_generic.append(indicator)
            business_score -= 10  # Penalty for generic language
    
    # Check for domain-specific indicators (positive scoring)
    for indicator in DOMAIN_SPECIFIC_INDICATORS:
        if indicator.lower() in response.lower():
            detected_domain_specific.append(indicator)
            business_score += 15
    
    # Compliance scoring based on case requirements
    if "gdpr" in case_data.get("description", "").lower():
        if "data protection officer" in response.lower() and "72" in response:
            compliance_score += 50
        if "gdpr" in response.lower():
            compliance_score += 25
    
    if "sox" in case_data.get("description", "").lower():
        if "audit committee" in response.lower():
            compliance_score += 50
        if "compliance" in response.lower():
            compliance_score += 25
    
    # Normalize scores
    policy_score = min(100, max(0, policy_score * 100))
    business_score = min(100, max(0, business_score))
    terminology_score = min(100, max(0, terminology_score))
    compliance_score = min(100, max(0, compliance_score))
    
    # Calculate overall domain specificity score
    overall_score = (
        policy_score * 0.4 +
        business_score * 0.3 +
        terminology_score * 0.2 +
        compliance_score * 0.1
    )
    
    return EvaluationResult(
        case_id=case_data.get("id", "unknown"),
        policy_adherence_score=policy_score,
        business_context_score=business_score,
        terminology_score=terminology_score,
        compliance_score=compliance_score,
        overall_domain_score=overall_score,
        generic_response_indicators=detected_generic,
        domain_specific_indicators=detected_domain_specific,
        policy_violations=policy_violations
    )

def generate_evaluation_report(results: List[EvaluationResult]) -> Dict[str, Any]:
    """
    Generate a comprehensive evaluation report across multiple test cases.
    
    Args:
        results: List of evaluation results
        
    Returns:
        Dictionary containing aggregated metrics and analysis
    """
    
    if not results:
        return {"error": "No evaluation results provided"}
    
    # Aggregate scores
    avg_policy = sum(r.policy_adherence_score for r in results) / len(results)
    avg_business = sum(r.business_context_score for r in results) / len(results)
    avg_terminology = sum(r.terminology_score for r in results) / len(results)
    avg_compliance = sum(r.compliance_score for r in results) / len(results)
    avg_overall = sum(r.overall_domain_score for r in results) / len(results)
    
    # Count indicators
    total_generic = sum(len(r.generic_response_indicators) for r in results)
    total_domain_specific = sum(len(r.domain_specific_indicators) for r in results)
    
    # Classification
    domain_specific_responses = len([r for r in results if r.overall_domain_score >= 70])
    generic_responses = len([r for r in results if r.overall_domain_score < 40])
    mixed_responses = len(results) - domain_specific_responses - generic_responses
    
    return {
        "summary": {
            "total_cases": len(results),
            "domain_specific_responses": domain_specific_responses,
            "generic_responses": generic_responses,
            "mixed_responses": mixed_responses,
            "domain_specificity_percentage": (domain_specific_responses / len(results)) * 100
        },
        "average_scores": {
            "policy_adherence": round(avg_policy, 2),
            "business_context": round(avg_business, 2),
            "terminology_usage": round(avg_terminology, 2),
            "compliance_integration": round(avg_compliance, 2),
            "overall_domain_score": round(avg_overall, 2)
        },
        "indicators": {
            "generic_indicators_detected": total_generic,
            "domain_specific_indicators_detected": total_domain_specific,
            "specificity_ratio": total_domain_specific / max(1, total_generic)
        },
        "detailed_results": [
            {
                "case_id": r.case_id,
                "overall_score": r.overall_domain_score,
                "classification": (
                    "Domain-Specific" if r.overall_domain_score >= 70
                    else "Generic" if r.overall_domain_score < 40
                    else "Mixed"
                )
            }
            for r in results
        ]
    }