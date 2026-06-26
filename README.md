# Simulador de Escalonamento de Processos

Esqueleto funcional para o trabalho. Roda os 5 algoritmos obrigatórios
(FIFO, SJF, Prioridade, Round-Robin, EDF) + um exemplo de algoritmo
próprio em `schedulers/custom.py` (substituam pela estratégia da equipe).

## Como rodar

```bash
pip install matplotlib
python main.py                      # usa exemplo_processos.csv
python main.py meus_processos.csv   # usa outro arquivo
```

Saída: tabela de cada processo + resumo (médias, throughput, % ociosidade,
trocas de contexto, preempções) impressos no terminal, e um PNG de Gantt
por algoritmo (`gantt_fifo.png`, `gantt_sjf.png`, ...).

CSV de entrada precisa das colunas: `id,chegada,execucao,prioridade,deadline`
(`deadline` pode ficar vazio).

## Estrutura

```
models.py            Process, SimConfig (parâmetros globais: quantum, sobrecarga_contexto)
engine.py             Motor de simulação genérico (event-driven) — único, serve para todos os algoritmos
metrics.py            Cálculo da tabela final e do resumo quantitativo
visualization.py       Gera o gráfico de Gantt (matplotlib)
schedulers/base.py     Interface Scheduler (todo algoritmo novo implementa essa classe)
schedulers/fifo.py
schedulers/sjf.py
schedulers/priority.py
schedulers/round_robin.py
schedulers/edf.py
schedulers/custom.py   EXEMPLO — substituam pela lógica da equipe
main.py                 Amarra tudo, roda todos os algoritmos
processos.csv
```

## Como o motor funciona (resumo)

Cada algoritmo só decide **quem roda agora**, implementando
`select_next(ready_queue, running, current_time)`. O `engine.py` cuida de:
chegadas, fila de prontos, sobrecarga de contexto, contagem de preempções
e trocas, e fechamento das métricas de cada processo (`termino`, `espera`,
`turnaround`, `deadline_ok`).

Dois detalhes que diferenciam os algoritmos preemptivos no motor:
- `preemptive`: pode interromper um processo antes de terminar?
- `preempt_on_arrival`: a decisão é reavaliada toda vez que chega um
  processo novo (caso do EDF, que precisa comparar deadlines), ou só ao
  fim de uma fatia de tempo fixa (caso do Round-Robin, que só troca
  quando o quantum acaba)?
- `time_slice(processo, config)`: quanto tempo a fatia atual pode durar
  no máximo (RR retorna o quantum; os demais retornam o tempo restante
  inteiro, ou seja, "roda até acabar" a não ser que `preempt_on_arrival`
  corte antes).

## Decisões de projeto já tomadas (documentem/justifiquem no relatório)

1. **`quantum` e `sobrecarga_contexto` são parâmetros globais** da
   simulação (`SimConfig`), não atributos por processo — o enunciado
   tabula tudo junto, mas isso é o padrão em escalonadores reais.
2. **Toda troca do processo que ocupa a CPU paga `sobrecarga_contexto`**,
   inclusive a primeira execução (idle → rodando). Se o critério de
   avaliação exigir que a primeira execução não pague overhead, é um
   ajuste de uma linha em `engine.py` (procure o comentário
   `# AJUSTE OPCIONAL`).
3. **Estouro de deadline não interrompe a execução** — o processo só é
   marcado como atrasado (`deadline_ok = False`) se terminar depois do
   prazo; ele continua rodando normalmente até lá.
4. **Critérios de desempate**: FIFO por `chegada` então `id`; SJF por
   `restante` então `chegada` então `id`; Prioridade por `prioridade`
   (1 = maior) então `chegada` então `id`.

## O que falta vocês implementarem

- [ ] `schedulers/custom.py` — algoritmo próprio da equipe (o atual é só
      um exemplo de "prioridade com folga dinâmica" pra mostrar como
      plugar um algoritmo novo)
- [ ] Modo passo-a-passo opcional (dá pra fazer simples: depois de montar
      o `log` de segmentos em `ResultadoSimulacao`, é só iterar e dar um
      `time.sleep()`/print incremental, ou animar com matplotlib)
- [ ] Bateria de testes comparando os algoritmos em cenários diferentes
      (alta carga, deadlines apertados, muita sobrecarga de contexto) —
      é só variar `SimConfig` e o CSV de entrada e rodar `main.py`
- [ ] Relatório com a análise comparativa (o `main.py` já imprime tudo
      que vocês precisam: médias, throughput, % ociosidade, trocas de
      contexto, preempções, processos estourados)

## Testado

Os 6 algoritmos foram rodados de ponta a ponta com `exemplo_processos.csv`
sem erros, e os gráficos de Gantt foram inspecionados visualmente
(cores verde/vermelho/cinza e linhas de deadline aparecendo corretamente).
