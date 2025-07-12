"""
Prompts for categorization node in HelpHub workflow.

TODO for participants: Adapt these prompts to match your organization's
IT service categories and classification standards.
"""

# Main categorization prompt
CATEGORIZATION_PROMPT = """
You are an IT support specialist categorizing user requests. 

User Request: {user_input}
Conversation History: {conversation_history}
Knowledge Base Context: {kb_articles}
User Context: {user_context}

Categories:
1. **HARDWARE** - Physical equipment issues (laptops, printers, monitors, phones)
2. **SOFTWARE** - Application problems (installations, crashes, licensing, updates)
3. **NETWORK** - Connectivity issues (Wi-Fi, VPN, internet, slow connections)
4. **ACCESS** - Account and permission issues (passwords, login, file access)
5. **BILLING** - Financial and licensing questions (software licenses, invoices)

Analyze the request and determine:
1. Primary category
2. Confidence level (0.0 to 1.0)
3. Secondary category if applicable
4. Reasoning for the categorization

Consider:
- Keywords and technical terms
- Symptoms described
- User's role and department
- Similar issues in knowledge base

Format your response as:
CATEGORY: [category]
CONFIDENCE: [0.0-1.0]
REASONING: [explanation]
SECONDARY: [category if applicable]

TODO for participants:
- Add your organization's specific categories
- Include department-specific classification rules
- Add confidence thresholds for auto-routing
- Customize reasoning templates
- Add multi-language support if needed
"""

# Subcategory classification prompt
SUBCATEGORY_PROMPT = """
Provide detailed subcategorization for this {category} issue:

User Request: {user_input}
Primary Category: {category}

Subcategories for {category}:
{subcategories}

Determine:
1. Most specific subcategory
2. Urgency indicators
3. Common resolution approaches
4. Required technical skills level

TODO for participants:
- Define subcategories for each main category
- Add skill level requirements for each subcategory
- Include resolution time estimates
- Map to specific support teams or individuals
"""

# Multi-category handling prompt
MULTI_CATEGORY_PROMPT = """
This request appears to involve multiple categories:

User Request: {user_input}
Identified Categories: {categories}

Determine:
1. Primary issue to address first
2. Secondary issues to track
3. Dependencies between issues
4. Recommended handling approach

Options:
- SEQUENTIAL: Handle one issue at a time
- PARALLEL: Address multiple issues simultaneously
- ESCALATE: Requires coordination between teams

TODO for participants:
- Define rules for multi-category prioritization
- Add team coordination procedures
- Include dependency mapping logic
- Customize for your support structure
"""

# Category validation prompt
VALIDATION_PROMPT = """
Validate this categorization against organizational standards:

Original Request: {user_input}
Proposed Category: {category}
Confidence: {confidence}
Reasoning: {reasoning}

Validation checks:
1. Does category match request symptoms?
2. Are there better category alternatives?
3. Is confidence level appropriate?
4. Does this align with similar historical tickets?

Provide:
- APPROVED or REVISION_NEEDED
- Alternative category if revision needed
- Validation reasoning

TODO for participants:
- Add your organization's validation rules
- Include historical ticket analysis
- Add quality scoring metrics
- Implement continuous learning feedback
"""
