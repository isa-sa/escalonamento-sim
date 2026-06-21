from .base import Scheduler


class FIFO(Scheduler):
    """First Come, First Served — não-preemptivo."""
    name = "FIFO"
    preemptive = False

    def select_next(self, ready_queue, running, current_time):
        if running is not None:
            return running  # não-preemptivo: continua até terminar
        if not ready_queue:
            return None
        return min(ready_queue, key=lambda p: (p.chegada, p.id))
