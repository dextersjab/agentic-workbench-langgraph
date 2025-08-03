"""Shared business context and domain knowledge across all workflows"""

from .company import COMPANY_INFO
from .support_teams import COMPANY_SUPPORT_TEAMS
from .sla_policies import BASE_SLA_POLICIES

__all__ = ['COMPANY_INFO', 'COMPANY_SUPPORT_TEAMS', 'BASE_SLA_POLICIES']