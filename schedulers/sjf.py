from .base import Scheduler


class SJF(Scheduler):
    """Shortest Job First — não-preemptivo."""
    name = "SJF"
    preemptive = False

    def select_next(self, ready_queue, running, current_time):
        if running is not None:
            return running
        if not ready_queue:
            return None
        # desempate: tempo de execução, depois ordem de chegada, depois id
        return min(ready_queue, key=lambda p: (p.restante, p.chegada, p.id))
