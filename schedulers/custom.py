"""
Algoritmo próprio da equipe — ESTE É UM EXEMPLO/TEMPLATE.

A ideia é mostrar como plugar um algoritmo novo no mesmo motor de simulação.
Substituam a lógica de `select_next` (e `_urgencia`) pela estratégia que a
equipe realmente quer propor e justificar no relatório.

Exemplo implementado aqui: "Prioridade com folga dinâmica"
------------------------------------------------------------
Cada processo pronto recebe uma pontuação de urgência:

    urgencia = (deadline - tempo_atual) / prioridade

Quanto MENOR a urgência, mais crítico é o processo (deadline próximo e/ou
prioridade alta). Processos sem deadline recebem folga infinita, ou seja,
só competem entre si pela prioridade pura. É preemptivo e reavalia a cada
nova chegada — assim como o EDF, mas considerando também a prioridade.
"""
import math

from .base import Scheduler


class AlgoritmoEquipe(Scheduler):
    name = "Algoritmo da Equipe (exemplo)"
    preemptive = True
    preempt_on_arrival = True

    def _urgencia(self, p, current_time):
        prioridade = max(p.prioridade, 1)  # evita divisão por zero / inversão
        folga = math.inf if p.deadline is None else (p.deadline - current_time)
        return folga / prioridade

    def select_next(self, ready_queue, running, current_time):
        candidatos = list(ready_queue)
        if running is not None:
            candidatos.append(running)
        if not candidatos:
            return None

        return min(candidatos, key=lambda p: (self._urgencia(p, current_time), p.id))
