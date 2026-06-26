"""Gerenciador interativo de processos para o simulador.

Uso standalone:
    python input_processos.py                  # abre o menu usando processos.csv
    python input_processos.py meus.csv         # abre com outro arquivo

Menu:
    [1] Listar processos atuais
    [2] Adicionar processo
    [3] Remover processo
    [4] Editar processo
    [5] Limpar todos os processos
    [6] Configurar parâmetros globais (quantum / sobrecarga)
    [0] Sair (e salvar)
"""
import csv
import os
import sys
from typing import List, Optional

CABECALHO = ["id", "chegada", "execucao", "prioridade", "deadline"]


# ---------------------------------------------------------------------------
# Leitura / escrita do CSV
# ---------------------------------------------------------------------------

def carregar_csv(caminho: str) -> List[dict]:
    if not os.path.exists(caminho):
        return []
    with open(caminho, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != CABECALHO:
            pass  # tolerante: lê o que houver
        return [dict(linha) for linha in reader]


def salvar_csv(caminho: str, processos: List[dict]):
    with open(caminho, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CABECALHO)
        writer.writeheader()
        for p in processos:
            writer.writerow({c: p.get(c, "") for c in CABECALHO})


def carregar_config(caminho_config: str) -> dict:
    """Lê quantum e sobrecarga de um arquivo .cfg simples (chave=valor)."""
    cfg = {"quantum": "2.0", "sobrecarga_contexto": "0.5"}
    if os.path.exists(caminho_config):
        with open(caminho_config, encoding="utf-8") as f:
            for linha in f:
                linha = linha.strip()
                if "=" in linha and not linha.startswith("#"):
                    chave, _, valor = linha.partition("=")
                    cfg[chave.strip()] = valor.strip()
    return cfg


def salvar_config(caminho_config: str, cfg: dict):
    with open(caminho_config, "w", encoding="utf-8") as f:
        f.write("# Parâmetros globais da simulação\n")
        for chave, valor in cfg.items():
            f.write(f"{chave} = {valor}\n")


# ---------------------------------------------------------------------------
# Validação de campos
# ---------------------------------------------------------------------------

def pedir(prompt: str, tipo, obrigatorio: bool = True,
          minimo=None, maximo=None, default=None):
    """Lê um valor do terminal com validação de tipo e intervalo.

    Retorna None se o campo for opcional e o usuário deixar em branco.
    """
    sufixo = f" [{default}]" if default is not None else (" (Enter = sem valor)" if not obrigatorio else "")
    while True:
        raw = input(f"  {prompt}{sufixo}: ").strip()
        if raw == "":
            if default is not None:
                return tipo(default)
            if not obrigatorio:
                return None
            print("  ⚠  Campo obrigatório — não pode ficar em branco.")
            continue
        try:
            valor = tipo(raw)
        except (ValueError, TypeError):
            nome_tipo = "inteiro" if tipo is int else "número"
            print(f"  ⚠  Valor inválido. Esperado: {nome_tipo}.")
            continue
        if minimo is not None and valor < minimo:
            print(f"  ⚠  Valor mínimo: {minimo}.")
            continue
        if maximo is not None and valor > maximo:
            print(f"  ⚠  Valor máximo: {maximo}.")
            continue
        return valor


def pedir_id(processos: List[dict], editando: Optional[str] = None) -> str:
    """Pede um ID único (string), verificando duplicatas."""
    while True:
        valor = input("  id (identificador único, ex: P1): ").strip()
        if not valor:
            print("  ⚠  ID não pode ser vazio.")
            continue
        duplicado = any(
            p["id"] == valor and valor != editando
            for p in processos
        )
        if duplicado:
            print(f"  ⚠  Já existe um processo com id '{valor}'. Escolha outro.")
            continue
        return valor


# ---------------------------------------------------------------------------
# Exibição
# ---------------------------------------------------------------------------

def linha_sep(larguras):
    return "+-" + "-+-".join("-" * l for l in larguras.values()) + "-+"


def imprimir_processos(processos: List[dict]):
    if not processos:
        print("  (nenhum processo cadastrado)")
        return
    colunas = CABECALHO
    larguras = {c: max(len(c), *(len(str(p.get(c, ""))) for p in processos))
                for c in colunas}
    sep = linha_sep(larguras)
    cab = "| " + " | ".join(c.ljust(larguras[c]) for c in colunas) + " |"
    print(sep)
    print(cab)
    print(sep)
    for p in processos:
        linha = "| " + " | ".join(str(p.get(c, "")).ljust(larguras[c]) for c in colunas) + " |"
        print(linha)
    print(sep)
    print(f"  {len(processos)} processo(s) cadastrado(s).")


def imprimir_config(cfg: dict):
    print(f"  quantum            = {cfg['quantum']}")
    print(f"  sobrecarga_contexto = {cfg['sobrecarga_contexto']}")


# ---------------------------------------------------------------------------
# Ações do menu
# ---------------------------------------------------------------------------

def acao_adicionar(processos: List[dict]):
    print("\n── Adicionar processo ──")
    proc = {}
    proc["id"]         = pedir_id(processos)
    proc["chegada"]    = pedir("chegada    (instante de chegada, ≥ 0)", float, minimo=0.0)
    proc["execucao"]   = pedir("execucao   (tempo total de CPU, > 0)", float, minimo=0.001)
    proc["prioridade"] = pedir("prioridade (inteiro, 1 = maior prioridade)", int, minimo=1, default=1)
    dl = pedir("deadline   (instante máximo absoluto)", float, obrigatorio=False, minimo=0.0)
    proc["deadline"]   = "" if dl is None else dl

    processos.append(proc)
    print(f"  ✓ Processo '{proc['id']}' adicionado.")


def acao_remover(processos: List[dict]):
    if not processos:
        print("  Nenhum processo para remover.")
        return
    print("\n── Remover processo ──")
    imprimir_processos(processos)
    alvo = input("  ID do processo a remover (Enter = cancelar): ").strip()
    if not alvo:
        return
    antes = len(processos)
    processos[:] = [p for p in processos if p["id"] != alvo]
    if len(processos) < antes:
        print(f"  ✓ Processo '{alvo}' removido.")
    else:
        print(f"  ⚠  Processo '{alvo}' não encontrado.")


def acao_editar(processos: List[dict]):
    if not processos:
        print("  Nenhum processo para editar.")
        return
    print("\n── Editar processo ──")
    imprimir_processos(processos)
    alvo = input("  ID do processo a editar (Enter = cancelar): ").strip()
    if not alvo:
        return
    proc = next((p for p in processos if p["id"] == alvo), None)
    if proc is None:
        print(f"  ⚠  Processo '{alvo}' não encontrado.")
        return

    print(f"  Editando '{alvo}' — Enter mantém o valor atual.")
    novo_id = pedir_id(processos, editando=alvo)
    chegada  = pedir("chegada",    float, minimo=0.0,    default=proc["chegada"])
    execucao = pedir("execucao",   float, minimo=0.001,  default=proc["execucao"])
    prio     = pedir("prioridade", int,   minimo=1,      default=proc["prioridade"])
    dl_atual = proc["deadline"] if proc["deadline"] != "" else None
    dl       = pedir("deadline (Enter = sem deadline)", float, obrigatorio=False,
                     minimo=0.0, default=dl_atual)

    proc["id"]         = novo_id
    proc["chegada"]    = chegada
    proc["execucao"]   = execucao
    proc["prioridade"] = prio
    proc["deadline"]   = "" if dl is None else dl
    print(f"  ✓ Processo '{novo_id}' atualizado.")


def acao_limpar(processos: List[dict]):
    if not processos:
        print("  Lista já está vazia.")
        return
    confirma = input(f"  Remover todos os {len(processos)} processos? (s/N): ").strip().lower()
    if confirma == "s":
        processos.clear()
        print("  ✓ Todos os processos foram removidos.")
    else:
        print("  Cancelado.")


def acao_config(cfg: dict):
    print("\n── Configurar parâmetros globais ──")
    imprimir_config(cfg)
    print()
    q  = pedir("quantum            (> 0)", float, minimo=0.001, default=cfg["quantum"])
    sc = pedir("sobrecarga_contexto (≥ 0)", float, minimo=0.0,   default=cfg["sobrecarga_contexto"])
    cfg["quantum"] = str(q)
    cfg["sobrecarga_contexto"] = str(sc)
    print("  ✓ Parâmetros atualizados.")


# ---------------------------------------------------------------------------
# Loop principal do menu
# ---------------------------------------------------------------------------

def menu(caminho_csv: str):
    caminho_cfg = os.path.splitext(caminho_csv)[0] + ".cfg"
    processos   = carregar_csv(caminho_csv)
    cfg         = carregar_config(caminho_cfg)

    opcoes = {
        "1": ("Listar processos",            lambda: imprimir_processos(processos)),
        "2": ("Adicionar processo",          lambda: acao_adicionar(processos)),
        "3": ("Remover processo",            lambda: acao_remover(processos)),
        "4": ("Editar processo",             lambda: acao_editar(processos)),
        "5": ("Limpar todos os processos",   lambda: acao_limpar(processos)),
        "6": ("Configurar quantum / sobrecarga", lambda: acao_config(cfg)),
        "0": ("Salvar e sair",               None),
    }

    print(f"\n{'━' * 50}")
    print("  Gerenciador de Processos — Simulador de Escalonamento")
    print(f"  Arquivo: {caminho_csv}")
    print(f"{'━' * 50}")
    imprimir_processos(processos)
    print()
    imprimir_config(cfg)

    while True:
        print(f"\n{'─' * 40}")
        for chave, (descricao, _) in opcoes.items():
            print(f"  [{chave}] {descricao}")
        print(f"{'─' * 40}")

        escolha = input("  Opção: ").strip()

        if escolha not in opcoes:
            print("  ⚠  Opção inválida.")
            continue

        descricao, acao = opcoes[escolha]
        if acao is None:  # opção 0 = sair
            break
        acao()

    salvar_csv(caminho_csv, processos)
    salvar_config(caminho_cfg, cfg)
    print(f"\n  ✓ Salvo em '{caminho_csv}' e '{caminho_cfg}'.")
    print(f"  Execute  python main.py {caminho_csv}  para rodar a simulação.\n")
    return processos, cfg


if __name__ == "__main__":
    caminho = sys.argv[1] if len(sys.argv) > 1 else "processos.csv"
    menu(caminho)
