"""Interface comum a todos os algoritmos de escalonamento.

Cada algoritmo só precisa decidir QUAL processo roda a seguir.
O motor de simulação (engine.py) cuida de tudo o mais: chegadas, fila de
prontos, sobrecarga de contexto, contagem de preempções e métricas.
"""
from abc import ABC, abstractmethod
from typing import List, Optional

from models import Process, SimConfig


class Scheduler(ABC):
    name: str = "Scheduler"

    # Pode interromper um processo em execução antes dele terminar?
    preemptive: bool = False

    # Se True, o motor reavalia select_next() toda vez que um processo NOVO
    # chega (além de ao fim de cada fatia de tempo). Use True para algoritmos
    # como EDF, cuja decisão depende de quem está na fila (ex.: deadline mais
    # urgente). Use False para Round-Robin, cuja troca só ocorre ao fim do
    # quantum, independente de quem chegou no meio do caminho.
    preempt_on_arrival: bool = False

    @abstractmethod
    def select_next(self, ready_queue: List[Process], running: Optional[Process],
                     current_time: float) -> Optional[Process]:
        """Decide qual processo deve ocupar a CPU agora.

        - `ready_queue`: processos prontos, NUNCA inclui `running`.
        - `running`: processo atualmente na CPU (ou None se CPU livre).
        - Se `running` deve continuar, retorne o próprio `running`.
        - Caso contrário, retorne um processo de `ready_queue` (não precisa
          removê-lo da lista — o motor faz isso).
        - Retorne None apenas se não houver nenhum processo disponível.
        """
        raise NotImplementedError

    def time_slice(self, process: Process, config: SimConfig) -> float:
        """Por quanto tempo (no máximo) o processo roda antes do motor
        chamar select_next() de novo.

        Para algoritmos não-preemptivos, o padrão (retornar o tempo restante
        inteiro) já é o comportamento certo: o processo só solta a CPU quando
        termina.
        """
        return process.restante
