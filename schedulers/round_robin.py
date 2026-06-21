from .base import Scheduler


class RoundRobin(Scheduler):
    """Round-Robin com quantum fixo — preemptivo."""
    name = "Round-Robin"
    preemptive = True
    preempt_on_arrival = False  # só troca ao fim do quantum, não a cada chegada

    def select_next(self, ready_queue, running, current_time):
        if running is not None:
            # Só chegamos aqui quando o quantum de `running` acabou de
            # esgotar (o motor garante isso via time_slice). Se não há
            # mais ninguém pronto, ela mesma continua — sem nova troca
            # de contexto.
            if not ready_queue:
                return running
            return ready_queue[0]
        if not ready_queue:
            return None
        return ready_queue[0]

    def time_slice(self, process, config):
        return config.quantum
