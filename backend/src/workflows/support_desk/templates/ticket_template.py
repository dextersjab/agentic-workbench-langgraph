"""
HTML template for support ticket display in Open WebUI artifacts.

This template provides a consistent, professional ticket format.
"""

TICKET_HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Support Ticket</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .ticket-container {{
            max-width: 600px;
            margin: 0 auto;
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }}
        .ticket-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 24px;
            text-align: center;
        }}
        .ticket-id {{
            font-size: 24px;
            font-weight: 600;
            margin: 0;
            letter-spacing: 1px;
        }}
        .ticket-status {{
            display: inline-block;
            background-color: rgba(255, 255, 255, 0.2);
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 500;
            margin-top: 8px;
            text-transform: uppercase;
        }}
        .ticket-body {{
            padding: 24px;
        }}
        .info-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 24px;
        }}
        .info-item {{
            background-color: #f8f9fa;
            padding: 16px;
            border-radius: 6px;
            border-left: 3px solid #667eea;
        }}
        .info-label {{
            font-size: 12px;
            color: #6c757d;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 4px;
        }}
        .info-value {{
            font-size: 16px;
            font-weight: 600;
            color: #212529;
        }}
        .priority-high {{
            color: #dc3545;
        }}
        .priority-medium {{
            color: #ffc107;
        }}
        .priority-low {{
            color: #28a745;
        }}
        .issue-details {{
            background-color: #f8f9fa;
            border-radius: 6px;
            padding: 20px;
            margin-bottom: 20px;
        }}
        .section-title {{
            font-size: 14px;
            font-weight: 600;
            color: #495057;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 12px;
        }}
        .issue-text {{
            color: #212529;
            line-height: 1.6;
        }}
        .next-steps {{
            background-color: #e7f3ff;
            border-radius: 6px;
            padding: 20px;
            margin-bottom: 20px;
            border-left: 3px solid #007bff;
        }}
        .contact-info {{
            background-color: #fff3cd;
            border-radius: 6px;
            padding: 20px;
            border-left: 3px solid #ffc107;
        }}
        .timestamp {{
            text-align: center;
            color: #6c757d;
            font-size: 12px;
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid #e9ecef;
        }}
    </style>
</head>
<body>
    <div class="ticket-container">
        <div class="ticket-header">
            <h1 class="ticket-id">{ticket_id}</h1>
            <span class="ticket-status">{ticket_status}</span>
        </div>
        
        <div class="ticket-body">
            <div class="info-grid">
                <div class="info-item">
                    <div class="info-label">Priority</div>
                    <div class="info-value priority-{priority_class}">{priority}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Category</div>
                    <div class="info-value">{category}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Assigned Team</div>
                    <div class="info-value">{assigned_team}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">SLA Commitment</div>
                    <div class="info-value">{sla_commitment}</div>
                </div>
            </div>
            
            <div class="issue-details">
                <div class="section-title">Issue Summary</div>
                <div class="issue-text">{issue_summary}</div>
            </div>
            
            <div class="next-steps">
                <div class="section-title">Next Steps</div>
                <div class="issue-text">{next_steps}</div>
            </div>
            
            <div class="contact-info">
                <div class="section-title">Contact Information</div>
                <div class="issue-text">
                    <strong>Support Email:</strong> {support_email}<br>
                    <strong>Support Phone:</strong> {support_phone}<br>
                    <strong>Ticket Portal:</strong> {ticket_portal}
                </div>
            </div>
            
            <div class="timestamp">
                Created: {created_timestamp}
            </div>
        </div>
    </div>
</body>
</html>
"""

def generate_ticket_html(ticket_data: dict) -> str:
    """
    Generate HTML for a support ticket using the template.
    
    Args:
        ticket_data: Dictionary containing ticket information
        
    Returns:
        Formatted HTML string
    """
    # Map priority to CSS class
    priority = ticket_data.get('priority', 'medium').lower()
    priority_class = priority if priority in ['high', 'medium', 'low'] else 'medium'
    
    # Format the template with ticket data
    return TICKET_HTML_TEMPLATE.format(
        ticket_id=ticket_data.get('ticket_id', 'TK-000000'),
        ticket_status=ticket_data.get('ticket_status', 'CREATED'),
        priority=ticket_data.get('priority', 'Medium').upper(),
        priority_class=priority_class,
        category=ticket_data.get('category', 'General').title(),
        assigned_team=ticket_data.get('assigned_team', 'Support Team').capitalize(),
        sla_commitment=ticket_data.get('sla_commitment', '24 hours'),
        issue_summary=ticket_data.get('issue_summary', 'No summary provided'),
        next_steps=ticket_data.get('next_steps', 'Your ticket has been received and will be processed according to the SLA.'),
        support_email=ticket_data.get('support_email', 'support@company.com'),
        support_phone=ticket_data.get('support_phone', '1-800-SUPPORT'),
        ticket_portal=ticket_data.get('ticket_portal', 'https://support.company.com'),
        created_timestamp=ticket_data.get('created_timestamp', 'Just now')
    )