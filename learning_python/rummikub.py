import random
import logging
from colorama import Back, Style


class Peça:
    def __init__(self, cor, numero) -> None:
        self.cor = cor
        self.numero = numero


class Jogador:
    def __init__(self) -> None:
        self.nome = input(f"Digite o nome do jogador: ")
        self.peças = []
        self.jogadas = 0


class Rummikub:
    def __init__(self):
        self.qtd_pc_inicio = 14
        self.qtd_jogadores = 2
        self.cores = [
            (Back.RED, "red"),
            (Back.YELLOW, "yellow"),
            (Back.BLUE, "blue"),
            (Back.GREEN, "green"),
        ]
        self.regra_inicio = "sequecia de 30"
        self.jogadores = []
        self.tabuleiro = []
        self.peças_disponiveis = []
        self.numero_jogadas = 0
        self.vencedor = None

    def start(self):
        """Inicia o Jogo"""
        for _ in range(0, self.qtd_jogadores):
            jogador = Jogador()
            self.jogadores.append(jogador)

        self.__distribuir_peças()
        self.jogador_da_vez = random.randrange(0, len(self.jogadores))

    def __distribuir_peças(self):
        for cor in self.cores:
            for numero in range(1, 14):
                peça = Peça(cor, numero)
                self.peças_disponiveis.append(peça)

        while True:
            if all(len(jogador.peças) == 14 for jogador in self.jogadores):
                break

            for jogador in self.jogadores:
                jogador.peças.append(self.comprar_peça())

    def __proximo_jogador(self):
        if self.jogador_da_vez < len(self.jogadores) - 1:
            self.jogador_da_vez += 1
        else:
            self.jogador_da_vez = 0

    def conferir(self, jogadas):
        for index, jogada in enumerate(jogadas):
            text = ""
            for peça in jogada:
                new_text = peça.cor[0] + f"{index + 1}: {peça.numero} - {peça.cor[1]}"
                new_text += " " * (20 - len(new_text))
                text += new_text
            text += Style.RESET_ALL
            print(text)

    def pegar_peça(self):
        """Pega uma peça revelada do tabuleiro"""
        pass

    def comprar_peça(self):
        """Pega uma peça aleatoria"""
        random.shuffle(self.peças_disponiveis)
        peça = self.peças_disponiveis.pop()
        return peça

    def mostrar_jogadas(self):
        for index, jogada in enumerate(self.tabuleiro):
            print(f"Jogada {index}")
            print((f"{p.numero} - {p.cor}; " for p in jogada), end="\n\n")

    def jogar(self):
        jogador = self.jogadores[self.jogador_da_vez]
        print(f"Iniciando jogada de {jogador.nome}")
        while True:
            print("Digite uma das opções:")
            prompt = "[ ] Continuar, [0] Comprar, [1] Conferir Mão"
            prompt += (
                ", [1] Ver Tabuleiro: "
                if self.tabuleiro and jogador.jogadas > 0
                else ": "
            )
            resposta = input(prompt)
            if resposta == "0":
                peça = self.comprar_peça()
                print("Peça comprada: ")
                self.conferir([[peça]])
                jogador.peças.append(peça)
                self.__proximo_jogador()
                return
            elif resposta == "1":
                self.conferir([[peça] for peça in jogador.peças])
            elif resposta == "2":
                self.conferir(self.tabuleiro)
            else:
                break
        jogadas_tabuleiro = self.tabuleiro
        while True:
            jogadas = []
            peças_disponiveis = []
            while True:
                print("Selecione suas peças para a jogada")
                peças_disponiveis = (
                    [
                        peça
                        for peça in jogador.peças
                        if peça not in [p for j in jogadas for p in j]
                    ]
                    if jogadas
                    else jogador.peças
                )
                self.conferir([[peça] for peça in peças_disponiveis])
                numeros_selecionados = input(
                    "Digite o número das peças escolhidas separado por espaço: "
                )
                try:
                    numeros_selecionados = [
                        int(n) - 1 for n in numeros_selecionados.split()
                    ]
                    if any(numero > len(peças_disponiveis) + 1 for numero in numeros_selecionados):
                        raise Exception("Numero invalido")
                    peças_selecionadas = [
                        peça
                        for index, peça in enumerate(peças_disponiveis)
                        if index in numeros_selecionados
                    ]
                    if peças_selecionadas:
                        jogadas.append(peças_selecionadas)
                    else:
                        break
                except Exception:
                    resposta = input(
                        "Input invalido, deseja continuar? [sim/não]: "
                    )
                    if resposta.lower().strip() == "sim":
                        continue
                    else:
                        break

            if not jogadas:
                peça = self.comprar_peça()
                print("Compra de peça automatica: ")
                self.conferir([[peça]])
                jogador.peças.append(peça)
                break
            # Jogador modifica o tabuleiro com suas jogadas

            if jogadas and self.__verificar_tabuleiro(jogadas):
                self.conferir(jogadas_tabuleiro)
                resposta = input("Confirmar jogada [sim/não]: ").lower().strip()
                if resposta == "sim":
                    jogadas_tabuleiro += jogadas
                    break
        
        if jogadas_tabuleiro:
            self.tabuleiro = jogadas_tabuleiro
            self.numero_jogadas += 1
            jogador.jogadas += 1
            jogador.peças = peças_disponiveis
            if not jogador.peças:
                self.vencedor = jogador
                print(f"{jogador.nome} venceu a partida")
                exit(0)

        self.__proximo_jogador()

    def __verificar_tabuleiro(self, tabuleiro) -> bool:
        maior_jogada = []
        for index, jogada in enumerate(tabuleiro):
            try:
                tipo_jogada = self.__verificar_jogada(jogada)
                total_jogada = sum(peça.numero for peça in jogada)
                maior_jogada.append((tipo_jogada, total_jogada))

            except Exception:
                logging.info(f"Falha na verificação da jogada nº {index}\n{jogada}")
                return False

        if maior_jogada and self.numero_jogadas == 0:
            maior_trinca = max([j[1] if j[0] == 0 else 0 for j in maior_jogada])
            maior_sequencia = sum([j[1] if j[0] == 1 else 0 for j in maior_jogada])
            return any(jogada > 30 for jogada in [maior_trinca, maior_sequencia])

        return True

    def __verificar_jogada(self, peças: list):
        if len(peças) < 3:
            raise Exception("Numero de peças menor que 3")

        cores = set(peça.cor for peça in peças)
        if len(cores) == len(peças):
            if any(peça.numero != peças[0].numero for peça in peças):
                raise Exception("Peças de numeros diferentes")
            else:
                return 0
        else:
            seq = sorted(peças, key=lambda peça: peça.numero)
            for index, peça in enumerate(seq):
                if index == 0:
                    continue
                if peça.numero <= seq[index - 1].numero:
                    raise Exception("Sequência invalida")
            return 1


rm = Rummikub()
rm.start()
while not rm.vencedor:
    rm.jogar()
