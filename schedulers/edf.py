import math

from .base import Scheduler


class EDF(Scheduler):
    """Earliest Deadline First — preemptivo (reavalia a cada chegada)."""
    name = "EDF"
    preemptive = True
    preempt_on_arrival = True

    def select_next(self, ready_queue, running, current_time):
        candidatos = list(ready_queue)
        if running is not None:
            candidatos.append(running)
        if not candidatos:
            return None

        def chave(p):
            d = p.deadline if p.deadline is not None else math.inf
            return (d, p.restante, p.id)

        return min(candidatos, key=chave)
