"""Ponto de entrada do simulador.

Uso:
    python main.py
    python main.py meus_processos.csv

O CSV precisa ter as colunas: id,chegada,execucao,prioridade,deadline
(deadline pode ficar vazio se o processo não tiver prazo).
"""
import csv
import sys

from models import Process, SimConfig
from engine import simular
from metrics import tabela_processos, resumo
from visualization import plotar_gantt

from schedulers import FIFO, SJF, PriorityScheduler, RoundRobin, EDF, AlgoritmoEquipe


def carregar_processos(caminho_csv: str):
    processos = []
    with open(caminho_csv, newline="", encoding="utf-8") as f:
        for linha in csv.DictReader(f):
            deadline = linha.get("deadline")
            processos.append(Process(
                id=linha["id"].strip(),
                chegada=float(linha["chegada"]),
                execucao=float(linha["execucao"]),
                prioridade=int(linha["prioridade"]) if linha.get("prioridade") not in (None, "") else 0,
                deadline=float(deadline) if deadline not in (None, "") else None,
            ))
    return processos


def imprimir_tabela(linhas):
    if not linhas:
        print("(sem processos)")
        return
    colunas = list(linhas[0].keys())
    larguras = {c: max(len(c), *(len(str(l[c])) for l in linhas)) for c in colunas}
    cab = " | ".join(c.ljust(larguras[c]) for c in colunas)
    print(cab)
    print("-" * len(cab))
    for l in linhas:
        print(" | ".join(str(l[c]).ljust(larguras[c]) for c in colunas))


def main():
    caminho_csv = sys.argv[1] if len(sys.argv) > 1 else "exemplo_processos.csv"

    # AJUSTE AQUI: quantum do Round-Robin e custo de cada troca de contexto
    config = SimConfig(quantum=2.0, sobrecarga_contexto=0.5)

    algoritmos = [
        FIFO(),
        SJF(),
        PriorityScheduler(),
        RoundRobin(),
        EDF(),
        AlgoritmoEquipe(),
    ]

    for sched in algoritmos:
        processos = carregar_processos(caminho_csv)  # recarrega "do zero" a cada algoritmo
        resultado = simular(processos, sched, config)

        print(f"\n{'=' * 60}")
        print(f"  {resultado.algoritmo}")
        print(f"{'=' * 60}")
        imprimir_tabela(tabela_processos(resultado))

        r = resumo(resultado)
        print(f"\nTurnaround médio : {r['turnaround_medio']:.2f}")
        print(f"Espera média     : {r['espera_media']:.2f}")
        print(f"Throughput       : {r['throughput']:.4f} processos/unidade de tempo")
        print(f"CPU ociosa       : {r['cpu_ociosa_pct']:.1f}%")
        print(f"Trocas contexto  : {r['trocas_contexto']}")
        print(f"Preempções       : {r['preempcoes']}")
        print(f"Estourados       : {r['processos_estourados']}")
        print(f"Tempo total sim. : {r['tempo_total_simulacao']:.2f}")

        nome_arquivo = f"gantt_{resultado.algoritmo.split()[0].lower().replace('/', '_')}.png"
        plotar_gantt(resultado, nome_arquivo)
        print(f"Gráfico salvo em : {nome_arquivo}")


if __name__ == "__main__":
    main()
