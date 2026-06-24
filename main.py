"""Ponto de entrada do simulador.

Uso:
    python main.py                              # roda com exemplo_processos.csv
    python main.py meus.csv                     # usa outro arquivo CSV
    python main.py --input                      # abre o menu de processos antes de simular
    python main.py meus.csv --input             # abre o menu com outro arquivo
    python main.py --verbose sjf                # mostra rastreamento de decisões do SJF
    python main.py meus.csv --verbose edf

O CSV precisa ter as colunas: id,chegada,execucao,prioridade,deadline
(deadline pode ficar vazio se o processo não tiver prazo).

Os parâmetros quantum e sobrecarga_contexto são lidos do arquivo .cfg
gerado pelo menu (mesmo nome do CSV, extensão .cfg). Se não existir,
usa os valores padrão definidos em SimConfig.
"""
import csv
import os
import sys

from models import Process, SimConfig
from engine import simular
from metrics import tabela_processos, resumo
from visualization import plotar_gantt

from schedulers import FIFO, SJF, PriorityScheduler, RoundRobin, EDF, AlgoritmoEquipe


# ---------------------------------------------------------------------------
# Leitura de arquivos
# ---------------------------------------------------------------------------

def carregar_processos(caminho_csv: str):
    processos = []
    with open(caminho_csv, newline="", encoding="utf-8") as f:
        for linha in csv.DictReader(f):
            deadline = linha.get("deadline")
            processos.append(Process(
                id=linha["id"].strip(),
                chegada=float(linha["chegada"]),
                execucao=float(linha["execucao"]),
                prioridade=int(linha["prioridade"]) if linha.get("prioridade") not in (None, "") else 1,
                deadline=float(deadline) if deadline not in (None, "") else None,
            ))
    return processos


def carregar_config_simulacao(caminho_csv: str) -> SimConfig:
    """Lê quantum e sobrecarga do .cfg correspondente ao CSV.
    Se não existir, usa os valores padrão de SimConfig."""
    caminho_cfg = os.path.splitext(caminho_csv)[0] + ".cfg"
    cfg = {"quantum": 2.0, "sobrecarga_contexto": 0.5}
    if os.path.exists(caminho_cfg):
        with open(caminho_cfg, encoding="utf-8") as f:
            for linha in f:
                linha = linha.strip()
                if "=" in linha and not linha.startswith("#"):
                    chave, _, valor = linha.partition("=")
                    chave, valor = chave.strip(), valor.strip()
                    if chave in cfg:
                        cfg[chave] = float(valor)
    return SimConfig(quantum=cfg["quantum"], sobrecarga_contexto=cfg["sobrecarga_contexto"])


# ---------------------------------------------------------------------------
# Exibição de tabela
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    args = sys.argv[1:]
    caminho_csv  = "exemplo_processos.csv"
    verbose_alvo = None
    abrir_input  = False

    i = 0
    while i < len(args):
        if args[i] == "--verbose":
            verbose_alvo = args[i + 1].lower()
            i += 2
        elif args[i] == "--input":
            abrir_input = True
            i += 1
        else:
            caminho_csv = args[i]
            i += 1

    # Abre o menu interativo de processos se pedido
    if abrir_input:
        from input_processos import menu as menu_input
        menu_input(caminho_csv)

    # Carrega parâmetros do .cfg gerado pelo menu (ou usa padrão)
    config = carregar_config_simulacao(caminho_csv)

    print(f"\n  Arquivo  : {caminho_csv}")
    print(f"  quantum  : {config.quantum}  |  sobrecarga_contexto: {config.sobrecarga_contexto}\n")

    algoritmos = [
        FIFO(),
        SJF(),
        PriorityScheduler(),
        RoundRobin(),
        EDF(),
        AlgoritmoEquipe(),
    ]

    for sched in algoritmos:
        processos = carregar_processos(caminho_csv)
        verbose   = verbose_alvo is not None and verbose_alvo in sched.name.lower()

        print(f"\n{'=' * 60}")
        print(f"  {sched.name}")
        print(f"{'=' * 60}")
        if verbose:
            print("--- rastreamento de decisões de escalonamento ---")

        resultado = simular(processos, sched, config, verbose=verbose)

        if verbose:
            print("--- fim do rastreamento ---\n")

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

        nome_gantt = f"gantt_{sched.name.split()[0].lower().replace('/', '_')}.png"
        plotar_gantt(resultado, nome_gantt)
        print(f"Gráfico salvo em : {nome_gantt}")


if __name__ == "__main__":
    main()

