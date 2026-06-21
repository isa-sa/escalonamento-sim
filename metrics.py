"""Cálculo de métricas individuais e globais a partir do resultado da simulação."""
from typing import List, Dict, Any

from engine import ResultadoSimulacao


def tabela_processos(resultado: ResultadoSimulacao) -> List[Dict[str, Any]]:
    """Monta a tabela final exigida: chegada, execucao, deadline, prioridade,
    inicio(s), termino, espera, turnaround, deadline_ok?"""
    linhas = []
    for p in sorted(resultado.processos, key=lambda x: x.id):
        linhas.append({
            "id": p.id,
            "chegada": p.chegada,
            "execucao": p.execucao,
            "deadline": p.deadline if p.deadline is not None else "-",
            "prioridade": p.prioridade,
            "inicio": p.inicio,
            "termino": p.termino,
            "espera": round(p.espera, 2) if p.espera is not None else None,
            "turnaround": round(p.turnaround, 2) if p.turnaround is not None else None,
            "deadline_ok?": "-" if p.deadline_ok is None else ("sim" if p.deadline_ok else "NÃO"),
            "preempcoes": p.preempcoes,
        })
    return linhas


def resumo(resultado: ResultadoSimulacao) -> Dict[str, Any]:
    """Médias, throughput, % de CPU ociosa, trocas de contexto, preempções."""
    processos = resultado.processos
    turnarounds = [p.turnaround for p in processos if p.turnaround is not None]
    esperas = [p.espera for p in processos if p.espera is not None]
    n = len(processos)
    estourados = sum(1 for p in processos if p.deadline_ok is False)

    return {
        "algoritmo": resultado.algoritmo,
        "turnaround_medio": sum(turnarounds) / n if n else 0.0,
        "espera_media": sum(esperas) / n if n else 0.0,
        "throughput": n / resultado.tempo_total if resultado.tempo_total else 0.0,
        "cpu_ociosa_pct": 100 * resultado.tempo_ocioso / resultado.tempo_total if resultado.tempo_total else 0.0,
        "trocas_contexto": resultado.trocas_contexto,
        "preempcoes": resultado.preempcoes,
        "processos_estourados": estourados,
        "tempo_total_simulacao": resultado.tempo_total,
    }
