"""
DashboardAgent bridges the orchestrator and the Streamlit frontend.
"""
from typing import Dict, Any, List
from datetime import datetime
from src.utils.dashboard_utils import generate_plan_id, format_timestamp

class DashboardAgent:
    """Backend agent managing state for the enhanced dashboard."""
    def __init__(self, name: str = 'DashboardAgent'):
        self.name = name
        self.active_incidents = []
        self.pending_approvals = []
        self.approved_plans = []
        self.rejected_plans = []
        self.agent_logs = []
        self.metrics = {
            'avg_response_time_ms': 0,
            'total_incidents_handled': 0,
            'incidents_today': 0,
            'solver_calls_saved': 0,
            'coverage_percentage': 100.0,
            'avg_route_quality': 1.0,
            'human_decisions_required': 0,
            'human_decisions_made': 0
        }

    def get_status_summary(self) -> Dict[str, Any]:
        """Return current system status."""
        active_agent = 'idle'
        if self.agent_logs:
            active_agent = self.agent_logs[-1].get('agent', 'idle')
            
        return {
            'active_incidents': self.active_incidents,
            'pending_approval_count': len(self.pending_approvals),
            'active_agent': active_agent,
            'last_update': format_timestamp(datetime.now()),
            'system_health': 'healthy' if len(self.pending_approvals) < 5 else 'degraded'
        }

    def request_approval(self, plan: Dict[str, Any]) -> str:
        """Add plan to pending_approvals queue."""
        plan_id = generate_plan_id()
        plan['plan_id'] = plan_id
        plan['timestamp'] = datetime.now().isoformat()
        self.pending_approvals.append(plan)
        print(f'[ALERT] Routing plan {plan_id} awaiting human approval')
        self.metrics['human_decisions_required'] += 1
        return plan_id

    def process_approval(self, plan_id: str, decision: str, reason: str = '') -> Dict[str, Any]:
        """Process a pending approval plan."""
        target_plan = next((p for p in self.pending_approvals if p['plan_id'] == plan_id), None)
        if not target_plan:
            return {'status': 'error', 'message': f'Plan {plan_id} not found.'}
            
        self.pending_approvals.remove(target_plan)
        target_plan['decision'] = decision
        target_plan['reason'] = reason
        target_plan['decision_time'] = datetime.now().isoformat()
        
        if decision.lower() == 'approve' or decision.lower() == 'approved':
            self.approved_plans.append(target_plan)
            print(f'[OK] Plan {plan_id} approved and queued for execution')
        else:
            self.rejected_plans.append(target_plan)
            print(f'[WARN] Plan {plan_id} rejected. Reason: {reason}')
            
        self.metrics['human_decisions_made'] += 1
        return {'status': 'success', 'plan_id': plan_id, 'decision': decision}

    def log_agent_activity(self, agent_name: str, status: str, task: str) -> None:
        """Append to agent_logs with timestamp. Keep only last 100 entries."""
        entry = {
            'agent': agent_name,
            'status': status,
            'task': task,
            'timestamp': datetime.now().isoformat(),
            'duration_ms': 0
        }
        self.agent_logs.append(entry)
        if len(self.agent_logs) > 100:
            self.agent_logs.pop(0)

    def update_metrics(self, new_metrics: Dict[str, Any]) -> None:
        """Merge new_metrics into current metrics."""
        for k, v in new_metrics.items():
            if k in ['avg_response_time_ms', 'avg_route_quality', 'coverage_percentage']:
                self.metrics[k] = (self.metrics[k] + v) / 2.0
            elif isinstance(v, (int, float)):
                if k in self.metrics:
                    self.metrics[k] += v
                else:
                    self.metrics[k] = v

    def export_report(self) -> str:
        """Generate a text report of current status."""
        lines = [
            '=========================================',
            'ResQ-MAR System Report',
            f'Generated: {format_timestamp(datetime.now())}',
            '=========================================',
            f"Total Incidents Handled: {self.metrics.get('total_incidents_handled', 0)}",
            f"Active Incidents: {len(self.active_incidents)}",
            f"Pending Approvals: {len(self.pending_approvals)}",
            f"Decisions Made: {self.metrics.get('human_decisions_made', 0)}",
            f"Coverage Percentage: {self.metrics.get('coverage_percentage', 0):.2f}%",
            f"Solver Calls Saved: {self.metrics.get('solver_calls_saved', 0)}",
            '========================================='
        ]
        return '\n'.join(lines)

if __name__ == "__main__":
    agent = DashboardAgent()
    agent.log_agent_activity("IntakeAgent", "running", "Processing new report")
    print(agent.get_status_summary())
