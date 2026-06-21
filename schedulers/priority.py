from .base import Scheduler


class PriorityScheduler(Scheduler):
    """Escalonamento por prioridade — não-preemptivo. 1 = maior prioridade."""
    name = "Prioridade"
    preemptive = False

    def select_next(self, ready_queue, running, current_time):
        if running is not None:
            return running
        if not ready_queue:
            return None
        return min(ready_queue, key=lambda p: (p.prioridade, p.chegada, p.id))
