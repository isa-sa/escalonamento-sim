"""Motor de simulação de eventos discretos para escalonamento de CPU.

Este motor é genérico: funciona para qualquer Scheduler (preemptivo ou não),
desde que ele implemente `select_next` (e opcionalmente `time_slice`).

Decisões de projeto / suposições assumidas (documentem no relatório):
  - quantum e sobrecarga_contexto são parâmetros GLOBAIS da simulação
    (SimConfig), não por processo.
  - A sobrecarga de contexto é cobrada toda vez que a CPU passa a executar
    um processo diferente do que estava rodando antes — inclusive a
    primeira vez que qualquer processo é despachado (idle -> rodando).
    Se o professor exigir que a primeira execução não pague sobrecarga,
    é só ajustar a condição marcada com "# AJUSTE OPCIONAL" abaixo.
  - "Estouro de deadline" não interrompe a execução: o processo continua
    rodando normalmente, só é marcado como deadline_ok = False se terminar
    depois do prazo.
"""
import math
from dataclasses import dataclass
from typing import List, Optional

from models import Process, SimConfig
from schedulers.base import Scheduler

EPS = 1e-9


@dataclass
class Segmento:
    """Um trecho do log de execução, usado para montar o Gantt."""
    tipo: str                      # "exec" | "contexto" | "idle"
    processo_id: Optional[str]
    inicio: float
    fim: float


@dataclass
class ResultadoSimulacao:
    algoritmo: str
    processos: List[Process]
    log: List[Segmento]
    trocas_contexto: int
    preempcoes: int
    tempo_total: float
    tempo_ocioso: float


def simular(processos: List[Process], scheduler: Scheduler, config: SimConfig,
            verbose: bool = False) -> ResultadoSimulacao:
    """Roda a simulação completa para um conjunto de processos e um algoritmo."""
    for p in processos:
        p.reset()

    pendentes = sorted(processos, key=lambda p: (p.chegada, p.id))
    ready_queue: List[Process] = []
    running: Optional[Process] = None
    completados: List[Process] = []
    log: List[Segmento] = []

    trocas_contexto = 0
    preempcoes = 0
    tempo_ocioso = 0.0
    time = 0.0

    def adicionar_chegadas(t: float):
        while pendentes and pendentes[0].chegada <= t + EPS:
            ready_queue.append(pendentes.pop(0))

    adicionar_chegadas(time)

    total = len(processos)
    guard = 0
    max_iter = 10000 + total * 2000  # trava de segurança contra loop infinito

    while len(completados) < total:
        guard += 1
        if guard > max_iter:
            raise RuntimeError(
                "Simulação não convergiu (possível bug no select_next() do "
                "scheduler customizado, ex.: retornando sempre um processo "
                "diferente e nunca deixando ninguém terminar)."
            )

        # CPU livre e ninguém pronto -> avança até a próxima chegada
        if running is None and not ready_queue:
            proximo = pendentes[0].chegada
            log.append(Segmento("idle", None, time, proximo))
            tempo_ocioso += proximo - time
            time = proximo
            adicionar_chegadas(time)
            continue

        candidato = scheduler.select_next(ready_queue, running, time)
        if candidato is None:
            # segurança: não deveria acontecer havendo processo disponível
            if pendentes:
                time = pendentes[0].chegada
                adicionar_chegadas(time)
                continue
            break

        if verbose:
            def descreve(p):
                return f"{p.id}(rest={p.restante:.1f}, prio={p.prioridade}, dl={p.deadline})"
            prontos_str = ", ".join(descreve(p) for p in ready_queue) or "-"
            rodando_str = descreve(running) if running else "-"
            print(f"[t={time:5.1f}] prontos=[{prontos_str}]  rodando={rodando_str}"
                  f"  -> escolhido: {candidato.id}"
                  f"{'  (TROCA)' if candidato is not running else ''}")

        if candidato is not running:
            if running is not None:
                preempcoes += 1
                running.preempcoes += 1
                ready_queue.append(running)
            if candidato in ready_queue:
                ready_queue.remove(candidato)

            if config.sobrecarga_contexto > 0:  # AJUSTE OPCIONAL: ver docstring
                trocas_contexto += 1
                fim_overhead = time + config.sobrecarga_contexto
                log.append(Segmento("contexto", candidato.id, time, fim_overhead))
                time = fim_overhead
                adicionar_chegadas(time)

            if candidato.inicio is None:
                candidato.inicio = time
            running = candidato

        slice_len = scheduler.time_slice(running, config)
        roda_por = min(slice_len, running.restante)
        fim_fatia = time + roda_por

        proxima_chegada = pendentes[0].chegada if pendentes else math.inf
        if scheduler.preempt_on_arrival and proxima_chegada < fim_fatia - EPS:
            fim_fatia = proxima_chegada

        log.append(Segmento("exec", running.id, time, fim_fatia))
        decorrido = fim_fatia - time
        running.restante -= decorrido
        time = fim_fatia
        adicionar_chegadas(time)

        if running.restante <= EPS:
            running.termino = time
            completados.append(running)
            running = None

    return ResultadoSimulacao(
        algoritmo=scheduler.name,
        processos=processos,
        log=log,
        trocas_contexto=trocas_contexto,
        preempcoes=preempcoes,
        tempo_total=time,
        tempo_ocioso=tempo_ocioso,
    )
