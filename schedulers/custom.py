from .base import Scheduler


class AlgoritmoEquipe(Scheduler):
    """
    Híbrido Prioridade + SJF

    Ciclo:

    1. Escolhe o processo de maior prioridade
       (menor valor de prioridade).
    2. Executa metade do tempo restante dele.
    3. Escolhe o processo com menor tempo restante
       (excluindo o processo anterior), desde que esse
       tempo seja estritamente menor que o restante de
       P_alto. Se nenhum processo satisfizer a condição,
       pula direto para o passo 5.
    4. Executa esse processo até terminar.
    5. Volta para o processo prioritário e executa
       o restante dele.
    6. Reinicia o ciclo.

    Desempates:
        prioridade -> chegada -> id
        menor restante -> chegada -> id
    """

    name = "Prioridade-SJF Hibrido"

    preemptive = True
    preempt_on_arrival = False

    def __init__(self):
        self.fase = "novo_ciclo"

        self.processo_prioritario = None
        self.processo_curto = None

        self.metade_executada = False
        self.retorno_prioritario = False

    def _escolher_prioritario(self, candidatos):
        return min(
            candidatos,
            key=lambda p: (
                p.prioridade,
                p.chegada,
                p.id
            )
        )

    def _escolher_curto(self, candidatos):
        return min(
            candidatos,
            key=lambda p: (
                p.restante,
                p.chegada,
                p.id
            )
        )

    def _limpar_ciclo(self):
        self.fase = "novo_ciclo"
        self.processo_prioritario = None
        self.processo_curto = None
        self.metade_executada = False
        self.retorno_prioritario = False

    def select_next(self, ready_queue, running, current_time):

        candidatos = list(ready_queue)

        if running is not None:
            candidatos.append(running)

        if not candidatos:
            return None

        # remove referências para processos que já terminaram
        if (
            self.processo_prioritario is not None
            and self.processo_prioritario.restante <= 1e-9
        ):
            self._limpar_ciclo()

        if (
            self.processo_curto is not None
            and self.processo_curto.restante <= 1e-9
        ):
            self.processo_curto = None

        #
        # INÍCIO DE UM NOVO CICLO
        #
        if self.fase == "novo_ciclo":

            self.processo_prioritario = self._escolher_prioritario(
                candidatos
            )

            self.fase = "primeira_metade"

            return self.processo_prioritario

        #
        # PRIMEIRA METADE DO PRIORITÁRIO
        #
        if self.fase == "primeira_metade":

            if self.processo_prioritario in candidatos:
                return self.processo_prioritario

            self._limpar_ciclo()
            return self.select_next(
                ready_queue,
                running,
                current_time
            )

        #
        # PROCESSO MAIS CURTO
        #
        if self.fase == "menor_processo":

            # Só considera P_curto se seu tempo restante for estritamente
            # menor que o restante de P_alto. Caso contrário não há ganho
            # real em interrompê-lo: o "job curto" demoraria mais do que
            # o próprio P_alto ainda precisa, contradizendo a premissa.
            outros = [
                p
                for p in candidatos
                if p is not self.processo_prioritario
                and p.restante < self.processo_prioritario.restante
            ]

            if not outros:
                self.fase = "segunda_metade"
                return self.processo_prioritario

            if (
                self.processo_curto is None
                or self.processo_curto.restante <= 1e-9
            ):
                self.processo_curto = self._escolher_curto(
                    outros
                )

            return self.processo_curto

        #
        # RETORNO AO PRIORITÁRIO
        #
        if self.fase == "segunda_metade":

            if (
                self.processo_prioritario is not None
                and self.processo_prioritario.restante > 1e-9
            ):
                return self.processo_prioritario

            self._limpar_ciclo()

            return self.select_next(
                ready_queue,
                running,
                current_time
            )

        return self._escolher_prioritario(candidatos)

    def time_slice(self, process, config):

        #
        # PRIMEIRA METADE
        #
        if (
            self.fase == "primeira_metade"
            and process is self.processo_prioritario
        ):
            self.fase = "menor_processo"

            return max(
                process.restante / 2.0,
                0.001
            )

        #
        # MENOR PROCESSO
        # roda até terminar
        #
        if (
            self.fase == "menor_processo"
            and process is self.processo_curto
        ):
            self.fase = "segunda_metade"

            return process.restante

        #
        # SEGUNDA METADE
        #
        if (
            self.fase == "segunda_metade"
            and process is self.processo_prioritario
        ):
            self._limpar_ciclo()

            return process.restante

        return process.restante