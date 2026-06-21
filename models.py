"""Modelos de dados do simulador de escalonamento."""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Process:
    """Representa um processo a ser escalonado."""
    id: str
    chegada: float
    execucao: float
    prioridade: int = 0          # 1 = maior prioridade
    deadline: Optional[float] = None

    # --- estado preenchido durante a simulação (não passe na criação) ---
    restante: float = field(init=False)
    inicio: Optional[float] = field(default=None, init=False)
    termino: Optional[float] = field(default=None, init=False)
    preempcoes: int = field(default=0, init=False)

    def __post_init__(self):
        self.restante = self.execucao

    @property
    def turnaround(self) -> Optional[float]:
        if self.termino is None:
            return None
        return self.termino - self.chegada

    @property
    def espera(self) -> Optional[float]:
        if self.turnaround is None:
            return None
        return self.turnaround - self.execucao

    @property
    def deadline_ok(self) -> Optional[bool]:
        """True/False se há deadline definido e o processo já terminou; None caso contrário."""
        if self.deadline is None or self.termino is None:
            return None
        return self.termino <= self.deadline

    def reset(self):
        """Restaura o processo ao estado inicial (necessário para rodar outro algoritmo)."""
        self.restante = self.execucao
        self.inicio = None
        self.termino = None
        self.preempcoes = 0

    def __repr__(self):
        return f"Process({self.id})"


@dataclass
class SimConfig:
    """Parâmetros globais da simulação (não variam por processo)."""
    quantum: float = 2.0
    sobrecarga_contexto: float = 0.0
