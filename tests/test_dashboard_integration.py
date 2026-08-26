"""
Integration tests for dashboard agent.
"""
import pytest
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.agents.dashboard_agent import DashboardAgent

@pytest.fixture
def agent():
    return DashboardAgent()

def test_dashboard_agent_state_management(agent):
    agent.active_incidents = [{'id': '1'}, {'id': '2'}]
    summary = agent.get_status_summary()
    assert len(summary['active_incidents']) == 2
    
def test_approval_workflow(agent):
    pid1 = agent.request_approval({'details': 'P1'})
    pid2 = agent.request_approval({'details': 'P2'})
    pid3 = agent.request_approval({'details': 'P3'})
    
    assert len(agent.pending_approvals) == 3
    
    agent.process_approval(pid1, 'approve')
    agent.process_approval(pid2, 'reject', 'not good')
    
    assert len(agent.pending_approvals) == 1
    assert len(agent.approved_plans) == 1
    assert len(agent.rejected_plans) == 1

def test_agent_logging(agent):
    for i in range(150):
        agent.log_agent_activity('Intake', 'running', f'task {i}')
        
    assert len(agent.agent_logs) == 100
    assert agent.agent_logs[-1]['task'] == 'task 149'
