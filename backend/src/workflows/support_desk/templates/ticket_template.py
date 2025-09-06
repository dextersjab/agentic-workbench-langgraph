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
            font-family: 'Inter', -apple-system, 'Helvetica Neue', sans-serif;
            margin: 0;
            padding: 40px 20px;
            background-color: #faf8f6;
            color: #2c2c2c;
        }}
        .ticket-container {{
            max-width: 640px;
            margin: 0 auto;
            background-color: #ffffff;
            border-radius: 2px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
            overflow: hidden;
            position: relative;
        }}
        .ticket-container::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 8px;
            bottom: 0;
            width: 0;
            border-left: 2px dashed rgba(232, 228, 224, 0.6);
            border-spacing: 6px;
        }}
        .ticket-container::after {{
            content: '';
            position: absolute;
            top: 50%;
            left: 12px;
            transform: translateY(-50%);
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background-color: #faf8f6;
            box-shadow: inset 0 0 0 1px #e8e4e0;
        }}
        .ticket-header {{
            background: #f7f5f3;
            padding: 48px 40px 48px 56px;
            border-bottom: 1px solid #e8e4e0;
            text-align: left;
            position: relative;
            display: flex;
            flex-direction: column;
            align-items: flex-start;
        }}
        .ticket-label {{
            font-size: 11px;
            font-weight: 400;
            color: #8b7c6f;
            text-transform: uppercase;
            letter-spacing: 3px;
            margin-bottom: 16px;
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        .ticket-label::before {{
            content: '✦';
            font-size: 16px;
            opacity: 0.5;
        }}
        .ticket-id {{
            font-size: 24px;
            font-weight: 300;
            margin: 0;
            letter-spacing: -0.5px;
            color: #2c2c2c;
            position: relative;
            display: inline-block;
            padding: 8px 16px;
            background-color: #faf8f6;
            border: 1px solid #e8e4e0;
            border-radius: 2px;
            margin-left: -16px;
        }}
        .ticket-id-row {{
            display: flex;
            align-items: center;
            gap: 16px;
        }}
        .ticket-status {{
            display: inline-block;
            background-color: #2c2c2c;
            color: #ffffff;
            padding: 4px 12px;
            border-radius: 2px;
            font-size: 10px;
            font-weight: 400;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            align-self: center;
        }}
        .ticket-body {{
            padding: 48px 40px 48px 56px;
        }}
        .info-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 32px;
            margin-bottom: 48px;
        }}
        .info-item {{
            padding-bottom: 16px;
            border-bottom: 1px solid #e8e4e0;
        }}
        .info-label {{
            font-size: 11px;
            color: #8b7c6f;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            margin-bottom: 8px;
            font-weight: 400;
        }}
        .info-value {{
            font-size: 16px;
            font-weight: 400;
            color: #2c2c2c;
            letter-spacing: -0.2px;
            padding: 4px 8px;
            border-radius: 2px;
            border: 1px solid transparent;
            transition: all 0.2s ease;
        }}
        .info-value[contenteditable="true"]:hover {{
            background-color: #faf8f6;
            border-color: #e8e4e0;
        }}
        .info-value[contenteditable="true"]:focus {{
            outline: none;
            background-color: #ffffff;
            border-color: #2c2c2c;
            box-shadow: 0 0 0 2px rgba(44, 44, 44, 0.1);
        }}
        .priority-high {{
            color: #d04437;
        }}
        .priority-medium {{
            color: #daa520;
        }}
        .priority-low {{
            color: #5e7a5e;
        }}
        .issue-details {{
            background-color: #faf8f6;
            border-radius: 2px;
            padding: 32px;
            margin-bottom: 32px;
            border: 1px solid #e8e4e0;
        }}
        .section-title {{
            font-size: 13px;
            font-weight: 500;
            color: #2c2c2c;
            text-transform: none;
            letter-spacing: 0;
            margin-bottom: 16px;
        }}
        .issue-text {{
            color: #4a4a4a;
            line-height: 1.7;
            font-size: 14px;
            font-weight: 300;
            padding: 4px 8px;
            border-radius: 2px;
            border: 1px solid transparent;
            transition: all 0.2s ease;
        }}
        .issue-text[contenteditable="true"]:hover {{
            background-color: #ffffff;
            border-color: #e8e4e0;
        }}
        .issue-text[contenteditable="true"]:focus {{
            outline: none;
            background-color: #ffffff;
            border-color: #2c2c2c;
            box-shadow: 0 0 0 2px rgba(44, 44, 44, 0.1);
        }}
        .next-steps {{
            background-color: #f7f5f3;
            border-radius: 2px;
            padding: 32px;
            margin-bottom: 32px;
            border: 1px solid #e8e4e0;
        }}
        .contact-info {{
            background-color: transparent;
            padding: 32px 0;
            border-top: 1px solid #e8e4e0;
        }}
        .contact-info .issue-text {{
            font-size: 13px;
            line-height: 2;
        }}
        .contact-info strong {{
            font-weight: 500;
            color: #2c2c2c;
        }}
        .timestamp {{
            text-align: center;
            color: #8b7c6f;
            font-size: 11px;
            margin-top: 40px;
            padding-top: 32px;
            border-top: 1px solid #e8e4e0;
            font-weight: 300;
            letter-spacing: 0.5px;
        }}
        .ticket-actions {{
            display: flex;
            gap: 16px;
            justify-content: center;
            margin-top: 32px;
            padding-top: 32px;
            border-top: 1px solid #e8e4e0;
        }}
        .action-button {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 12px 24px;
            border: none;
            border-radius: 2px;
            font-family: inherit;
            font-size: 13px;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 1px;
            cursor: pointer;
            transition: all 0.2s ease;
            text-decoration: none;
        }}
        .action-button:hover {{
            transform: translateY(-1px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }}
        .action-button:active {{
            transform: translateY(0);
        }}
        .action-button.primary {{
            background-color: #2c2c2c;
            color: #ffffff;
        }}
        .action-button.primary:hover {{
            background-color: #1a1a1a;
        }}
        .action-button.secondary {{
            background-color: #f7f5f3;
            color: #2c2c2c;
            border: 1px solid #e8e4e0;
        }}
        .action-button.secondary:hover {{
            background-color: #e8e4e0;
        }}
    </style>
    <script>
        function handleVerifyAndSend() {{
            // Collect all edited field values
            const ticketData = {{
                ticket_id: document.querySelector('.ticket-id').textContent,
                priority: document.querySelector('.info-value.priority-high, .info-value.priority-medium, .info-value.priority-low').textContent,
                category: document.querySelectorAll('.info-value')[1].textContent,
                assigned_team: document.querySelectorAll('.info-value')[2].textContent,
                sla_commitment: document.querySelectorAll('.info-value')[3].textContent,
                issue_summary: document.querySelector('.issue-details .issue-text').textContent,
                next_steps: document.querySelector('.next-steps .issue-text').textContent
            }};
            
            // Show confirmation
            if (confirm('Verify and send this ticket? This will finalize the ticket with the current values.')) {{
                alert('Ticket verified and sent successfully!\\nTicket ID: ' + ticketData.ticket_id);
                console.log('Verified ticket data:', ticketData);
            }}
        }}
        
        function handleReEvaluate() {{
            if (confirm('Re-evaluate this ticket? This will reprocess the original request with updated information.')) {{
                alert('Ticket sent for re-evaluation. The system will reprocess the request.');
                console.log('Re-evaluation requested');
            }}
        }}
    </script>
</head>
<body>
    <div class="ticket-container">
        <div class="ticket-header">
            <div class="ticket-label">Support Ticket</div>
            <div class="ticket-id-row">
                <h1 class="ticket-id">{ticket_id}</h1>
                <span class="ticket-status">{ticket_status}</span>
            </div>
        </div>
        
        <div class="ticket-body">
            <div class="info-grid">
                <div class="info-item">
                    <div class="info-label">Priority</div>
                    <div class="info-value priority-{priority_class}" contenteditable="true">{priority}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Category</div>
                    <div class="info-value" contenteditable="true">{category}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Assigned Team</div>
                    <div class="info-value" contenteditable="true">{assigned_team}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">SLA Commitment</div>
                    <div class="info-value" contenteditable="true">{sla_commitment}</div>
                </div>
            </div>
            
            <div class="issue-details">
                <div class="section-title">Issue Summary</div>
                <div class="issue-text" contenteditable="true">{issue_summary}</div>
            </div>
            
            <div class="next-steps">
                <div class="section-title">Next Steps</div>
                <div class="issue-text" contenteditable="true">{next_steps}</div>
            </div>
            
            <div class="contact-info">
                <div class="section-title">Contact Information</div>
                <div class="issue-text">
                    <strong>Support Email:</strong> {support_email}<br>
                    <strong>Support Phone:</strong> {support_phone}<br>
                    <strong>Ticket Portal:</strong> {ticket_portal}
                </div>
            </div>
            
            <div class="ticket-actions">
                <button class="action-button primary" onclick="handleVerifyAndSend()">
                    <span>✓</span>
                    <span>Verify & Send</span>
                </button>
                <button class="action-button secondary" onclick="handleReEvaluate()">
                    <span>🔄</span>
                    <span>Re-evaluate</span>
                </button>
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
    priority = ticket_data.get("priority", "medium").lower()
    priority_class = priority if priority in ["high", "medium", "low"] else "medium"

    # Format the template with ticket data
    return TICKET_HTML_TEMPLATE.format(
        ticket_id=ticket_data.get("ticket_id", "TK-000000"),
        ticket_status=ticket_data.get("ticket_status", "CREATED"),
        priority=ticket_data.get("priority", "Medium").upper(),
        priority_class=priority_class,
        category=ticket_data.get("category", "General").title(),
        assigned_team=ticket_data.get("assigned_team", "Support Team").capitalize(),
        sla_commitment=ticket_data.get("sla_commitment", "24 hours"),
        issue_summary=ticket_data.get("issue_summary", "No summary provided"),
        next_steps=ticket_data.get(
            "next_steps",
            "Your ticket has been received and will be processed according to the SLA.",
        ),
        support_email=ticket_data.get("support_email", "support@company.com"),
        support_phone=ticket_data.get("support_phone", "1-800-SUPPORT"),
        ticket_portal=ticket_data.get("ticket_portal", "https://support.company.com"),
        created_timestamp=ticket_data.get("created_timestamp", "Just now"),
    )
