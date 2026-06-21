"""Geração do gráfico de Gantt da simulação.

Layout: uma linha por processo (eixo Y) + uma linha extra para a sobrecarga
de contexto, eixo X = tempo.
  - verde  -> execução dentro do prazo
  - cinza  -> execução de um processo que ESTOUROU o deadline
  - vermelho -> sobrecarga de troca de contexto
  - linha tracejada vertical -> deadline absoluto de cada processo
"""
import matplotlib.pyplot as plt

from engine import ResultadoSimulacao

COR_EXEC = "#4caf50"       # verde
COR_CONTEXTO = "#e53935"   # vermelho
COR_ESTOURO = "#9e9e9e"    # cinza
COR_IDLE = "#eeeeee"       # cinza bem claro (não exigido, só ajuda a leitura)


def plotar_gantt(resultado: ResultadoSimulacao, caminho_saida: str):
    processos_por_id = {p.id: p for p in resultado.processos}
    ids = sorted(processos_por_id.keys())
    y_pos = {pid: i for i, pid in enumerate(ids)}
    LINHA_CONTEXTO = -1

    altura_fig = 0.5 * (len(ids) + 1) + 1.5
    fig, ax = plt.subplots(figsize=(13, altura_fig))

    for seg in resultado.log:
        if seg.tipo == "idle":
            ax.barh(LINHA_CONTEXTO, seg.fim - seg.inicio, left=seg.inicio,
                     height=0.5, color=COR_IDLE, edgecolor="none")
            continue

        if seg.tipo == "contexto":
            ax.barh(LINHA_CONTEXTO, seg.fim - seg.inicio, left=seg.inicio,
                     height=0.6, color=COR_CONTEXTO, edgecolor="black", linewidth=0.3)
            continue

        # seg.tipo == "exec"
        p = processos_por_id[seg.processo_id]
        cor = COR_ESTOURO if p.deadline_ok is False else COR_EXEC
        y = y_pos[seg.processo_id]
        ax.barh(y, seg.fim - seg.inicio, left=seg.inicio, height=0.6,
                 color=cor, edgecolor="black", linewidth=0.3)

    # linhas verticais de deadline (uma por processo, na própria linha dele)
    for pid in ids:
        p = processos_por_id[pid]
        if p.deadline is not None:
            y = y_pos[pid]
            ax.vlines(p.deadline, y - 0.4, y + 0.4, colors="black",
                       linestyles="dashed", linewidth=1.2)

    y_labels = ["CPU / contexto"] + ids
    y_ticks = [LINHA_CONTEXTO] + [y_pos[pid] for pid in ids]
    ax.set_yticks(y_ticks)
    ax.set_yticklabels(y_labels)
    ax.set_xlabel("tempo")
    ax.set_title(f"Gráfico de Gantt — {resultado.algoritmo}")
    ax.grid(axis="x", linestyle=":", alpha=0.5)
    ax.set_xlim(left=0)

    legenda = [
        plt.Rectangle((0, 0), 1, 1, color=COR_EXEC, label="Execução"),
        plt.Rectangle((0, 0), 1, 1, color=COR_CONTEXTO, label="Sobrecarga de contexto"),
        plt.Rectangle((0, 0), 1, 1, color=COR_ESTOURO, label="Estouro de deadline"),
        plt.Line2D([0], [0], color="black", linestyle="dashed", label="Deadline absoluto"),
    ]
    ax.legend(handles=legenda, loc="upper right", fontsize=8)

    fig.tight_layout()
    fig.savefig(caminho_saida, dpi=150)
    plt.close(fig)
