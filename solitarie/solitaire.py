
SOLITAIRE_WIDTH = 1000
SOLITAIRE_HEIGHT = 500

import random
import json
import flet as ft
from card import Card, CARD_WIDTH, CARD_HEIGHT
from slot import Slot
import os
import time
import threading


class Suite:
    def __init__(self, suite_name, suite_color):
        self.name = suite_name
        self.color = suite_color

    def to_dict(self):
        return {"name": self.name, "color": self.color}

    @staticmethod
    def from_dict(data):
        return Suite(data["name"], data["color"])

class Rank:
    def __init__(self, card_name, card_value):
        self.name = card_name
        self.value = card_value

    def to_dict(self):
        return {"name": self.name, "value": self.value}

    @staticmethod
    def from_dict(data):
        return Rank(data["name"], data["value"])



class Solitaire(ft.Stack):
    def __init__(self):
        super().__init__()
        self.tempo_decorrido = 0
        self.controls = []
        self.width = SOLITAIRE_WIDTH
        self.height = SOLITAIRE_HEIGHT
        self.history = []
        self.card_back_image = "images/default_back.png"
        self.SAVE_FILE = "solitaire_save.json"  # 🔹 Definindo como atributo da instância
        self.pontuacao = 0
        self.tempo_inicial = None
        self.PONTOS_TABLEAU = 5
        self.PONTOS_FOUNDATION = 15
        self.PONTOS_STOCK_FOUNDATION = 10
        self.PONTOS_STOCK_TABLEAU = 5
        self.pontuacao_text = None  # Adicionado o atributo pontuacao_text
        self.tempo_text = None  # Adicionado o atributo tempo_text
        self.timer_started = False  # Adiciona a flag para controlar o cronômetro
        self.interface_pronta = False  # Adiciona a flag interface_pronta
        self.dicas_usadas = 0  # Inicializa o contador de dicas


    def did_mount(self):
        self.create_card_deck()
        self.create_slots()
        self.deal_cards()



    def change_card_back(self, image_name):
        """Atualiza o fundo das cartas e redesenha todas as cartas."""
        print("change_card_back chamado com:", image_name)
        self.card_back_image = f"images/{image_name}"

        # Atualiza as cartas no estoque e no descarte
        for card in self.stock.pile + self.waste.pile:
            card.content.content.src = card.get_card_image_src()

        # Atualiza as cartas nas fundações
        for foundation in self.foundations:
            for card in foundation.pile:
                card.content.content.src = card.get_card_image_src()

        # Atualiza as cartas no tableau
        for tableau_slot in self.tableau:
            for card in tableau_slot.pile:
                print("Atualizando carta do tableau:", card.rank.name, card.suite.name)
                card.content.content.src = card.get_card_image_src()
                print("Nova src da carta:", card.content.content.src)
        print("update chamado")
        self.update()

    def get_slot_at(self, x, y):
        for slot in self.controls:
            if isinstance(slot, Slot):
                if slot.left <= x < slot.left + CARD_WIDTH and slot.top <= y < slot.top + CARD_HEIGHT:
                    return slot
        return None

    def move_card(self, card, from_slot, target_slot):
        """Move uma carta e atualiza a pontuação."""
        is_stock_to_waste = from_slot == self.stock and target_slot == self.waste
        card_below = from_slot.pile[-2] if len(from_slot.pile) > 1 else None
        card_below_was_face_up = card_below.face_up if card_below else None

        pontos_ganhos = 0

        print(f"Movimento: {card.rank.name} de {card.suite.name}")
        print(f"De: {from_slot}")
        print(f"Para: {target_slot}")

        print(f"Stock antes do movimento: {self.stock.pile}")
        print(f"Waste antes do movimento: {self.waste.pile}")
        print(f"Foundations antes do movimento: {[f.pile for f in self.foundations]}")
        print(f"Tableau antes do movimento: {[f.pile for f in self.tableau]}")

        if from_slot in self.tableau and target_slot in self.tableau:
            pontos_ganhos = self.PONTOS_TABLEAU
            print("Pontuação: Tableau para Tableau")
        elif from_slot in self.tableau and target_slot in self.foundations:
            pontos_ganhos = self.PONTOS_FOUNDATION
            print("Pontuação: Tableau para Fundação")
        elif from_slot == self.waste and target_slot in self.foundations:
            pontos_ganhos = self.PONTOS_STOCK_FOUNDATION
            print("Pontuação: Waste para Fundação")
            print(f"from_slot é self.waste: {from_slot == self.waste}")
            print(f"target_slot está em self.foundations: {target_slot in self.foundations}")
            print(f"ID do target_slot: {id(target_slot)}")
            print(f"IDs dos slots em foundations: {[id(f) for f in self.foundations]}")
        elif from_slot == self.waste and target_slot in self.tableau:
            pontos_ganhos = self.PONTOS_STOCK_TABLEAU
            print("Pontuação: Waste para Tableau")

        self.pontuacao += pontos_ganhos
        print(f"Pontos ganhos: {pontos_ganhos}")
        print(f"Pontuação atual: {self.pontuacao}")

        self.history.append({
            "card": card,
            "from_slot": from_slot,
            "to_slot": target_slot,
            "card_top": card.top,
            "card_left": card.left,
            "face_up": card.face_up,
            "card_below": card_below,
            "card_below_was_face_up": card_below_was_face_up,
            "is_stock_to_waste": is_stock_to_waste,
            "pontos_ganhos": pontos_ganhos,
        })

        card.place(target_slot)

        if card_below:
            card_below.turn_face_up()

        if card not in self.controls:
            self.controls.append(card)

        print(f"Movido {card.rank.name} de {card.suite.name} de {from_slot} para {target_slot}.")

        print(f"Stock depois do movimento: {self.stock.pile}")
        print(f"Waste depois do movimento: {self.waste.pile}")
        print(f"Foundations depois do movimento: {[f.pile for f in self.foundations]}")
        print(f"Tableau depois do movimento: {[f.pile for f in self.tableau]}")

        self.pontuacao_text.value = f"Pontuação: {self.pontuacao}"  # Atualiza o valor do texto existente
        print(f"Texto de pontuação: {self.pontuacao_text.value}")

        self.pontuacao_text.update()  # Atualiza o controle existente
        print("Texto de pontuação atualizado na tela.")

        if not self.timer_started:
            self.tempo_inicial = time.time()
            self.tempo_thread = threading.Thread(target=self.atualizar_tempo_thread)
            self.tempo_thread.daemon = True
            self.tempo_thread.start()
            self.timer_started = True

        self.update()

    def undo_move(self):
        """Desfaz a última jogada e subtrai os pontos ganhos."""
        if not self.history:
            print(" Nenhum movimento para desfazer.")
            return

        last_move = self.history.pop()

        card = last_move["card"]
        from_slot = last_move["from_slot"]
        to_slot = last_move["to_slot"]
        card_below = last_move.get("card_below")
        card_below_was_face_up = last_move.get("card_below_was_face_up")
        is_stock_to_waste = last_move["is_stock_to_waste"]

        pontos_ganhos = last_move.get("pontos_ganhos", 0)
        self.pontuacao -= pontos_ganhos

        if is_stock_to_waste:
            card.turn_face_down()
            card.move_on_top()
            card.place(self.stock)
            print(f" Desfeito: {card.rank.name} de {card.suite.name} voltou para o Stock.")
        else:
            card.top = last_move["card_top"]
            card.left = last_move["card_left"]
            card.face_up = last_move["face_up"]
            card.place(from_slot)

            if card_below and not card_below_was_face_up:
                card_below.turn_face_down()

            print(f" Desfeito: {card.rank.name} de {card.suite.name} voltou para {from_slot}.")

        if not self.history:
            print(" Nenhum outro movimento pode ser desfeito.")

        self.pontuacao_text.value = f"Pontuação: {self.pontuacao}"
        self.pontuacao_text.update()

        self.update()

    def create_card_deck(self):
        suites = [
            Suite("hearts", "RED"),
            Suite("diamonds", "RED"),
            Suite("clubs", "BLACK"),
            Suite("spades", "BLACK"),
        ]
        ranks = [
            Rank("Ace", 1),
            Rank("2", 2),
            Rank("3", 3),
            Rank("4", 4),
            Rank("5", 5),
            Rank("6", 6),
            Rank("7", 7),
            Rank("8", 8),
            Rank("9", 9),
            Rank("10", 10),
            Rank("Jack", 11),
            Rank("Queen", 12),
            Rank("King", 13),
        ]

        self.cards = []

        for suite in suites:
            for rank in ranks:
                self.cards.append(Card(solitaire=self, suite=suite, rank=rank))

    def create_slots(self):
        """Cria os slots do jogo e os controles da interface."""
        self.stock = Slot(solitaire=self, top=0, left=0, border=ft.border.all(1))
        self.waste = Slot(solitaire=self, top=0, left=100, border=None)

        self.foundations = []
        x = 300
        for i in range(4):
            self.foundations.append(
                Slot(solitaire=self, top=0, left=x, border=ft.border.all(1, "outline"))
            )
            x += 100

        self.tableau = []
        x = 0
        for i in range(7):
            self.tableau.append(Slot(solitaire=self, top=150, left=x, border=None))
            x += 100

        # Adiciona os slots à lista de controles
        self.controls.extend([self.stock, self.waste])
        self.controls.extend(self.foundations)
        self.controls.extend(self.tableau)

        # Criação dos controles da interface
        controls_config = [
            {
                "type": "button",
                "text": "Undo",
                "on_click": lambda _: self.undo_move(),
                "top": SOLITAIRE_HEIGHT - 500,
                "left": SOLITAIRE_WIDTH - 200,
            },
            {
                "type": "button",
                "text": "Restart",
                "on_click": lambda _: self.restart_game(),
                "top": SOLITAIRE_HEIGHT - 450,
                "left": SOLITAIRE_WIDTH - 200,
            },
            {
                "type": "dropdown",
                "options": ["Yellow flower.png", "Pink Flower.png", "Black Pattern.png", "Purple Pattern.png",
                            "default_back.png"],
                "on_change": self.change_card_back_handler,
                "width": 200,
                "label": "Change Theme Card",
                "top": SOLITAIRE_HEIGHT - 300,
                "left": SOLITAIRE_WIDTH - 200,
            },
            {
                "type": "button",
                "text": "Salvar Jogo",
                "on_click": self.save_game_state,
                "top": SOLITAIRE_HEIGHT - 500,
                "left": SOLITAIRE_WIDTH - 100,
            },
            {
                "type": "button",
                "text": "Dica",
                "on_click": lambda _: self.fornecer_dica(),
                "top": SOLITAIRE_HEIGHT - 400,  # Ajuste a posição conforme necessário
                "left": SOLITAIRE_WIDTH - 200,
            },
        ]

        if os.path.exists(self.SAVE_FILE):
            controls_config.append(
                {
                    "type": "button",
                    "text": "Carregar Jogo",
                    "on_click": self.load_game_state,
                    "top": SOLITAIRE_HEIGHT - 450,
                    "left": SOLITAIRE_WIDTH - 100,
                }
            )

        for config in controls_config:
            if config["type"] == "button":
                button = ft.ElevatedButton(config["text"], on_click=config["on_click"], bgcolor=config.get("bgcolor"),
                                           color=config.get("color"))
                container = ft.Container(content=button, top=config["top"], left=config["left"])
                self.controls.append(container)
            elif config["type"] == "dropdown":
                dropdown = ft.Dropdown(
                    options=[ft.dropdown.Option(text=option) for option in config["options"]],
                    on_change=config["on_change"],
                    width=config["width"],
                    label=config["label"],
                )
                container = ft.Container(content=dropdown, top=config["top"], left=config["left"])
                self.controls.append(container)

        self.pontuacao_text = ft.Text(f"Pontuação: {self.pontuacao}", top=SOLITAIRE_HEIGHT - 200,
                                      left=SOLITAIRE_WIDTH - 200)
        self.controls.append(self.pontuacao_text)

        self.tempo_text = ft.Text("Tempo: 00:00", top=SOLITAIRE_HEIGHT - 200, left=SOLITAIRE_WIDTH - 100)
        self.controls.append(self.tempo_text)

        self.dicas_restantes_text = ft.Text(f"Dicas Restantes: {self.calcular_dicas_restantes()}",
                                            top=SOLITAIRE_HEIGHT - 150, left=SOLITAIRE_WIDTH - 200)
        self.controls.append(self.dicas_restantes_text)

    def deal_cards(self):
        """Distribui as cartas e inicia o cronômetro."""
        random.shuffle(self.cards)
        self.controls.extend(self.cards)

        first_slot = 0
        remaining_cards = self.cards

        while first_slot < len(self.tableau):
            for slot in self.tableau[first_slot:]:
                top_card = remaining_cards[0]
                top_card.place(slot)
                remaining_cards.remove(top_card)
            first_slot += 1

        for card in remaining_cards:
            card.place(self.stock)
            print(f"Card in stock: {card.rank.name} {card.suite.name}")

        self.update()

        for slot in self.tableau:
            slot.get_top_card().turn_face_up()

        self.update()

        self.interface_pronta = True

    def check_foundations_rules(self, card, slot):
        top_card = slot.get_top_card()
        if top_card is not None:
            return (
                card.suite.name == top_card.suite.name
                and card.rank.value - top_card.rank.value == 1
            )
        else:
            return card.rank.name == "Ace"

    def check_tableau_rules(self, card, slot):
        top_card = slot.get_top_card()
        if top_card is not None:
            return (
                card.suite.color != top_card.suite.color
                and top_card.rank.value - card.rank.value == 1
                and top_card.face_up
            )
        else:
            return card.rank.name == "King"

    def restart_stock(self):
        while len(self.waste.pile) > 0:
            card = self.waste.get_top_card()
            card.turn_face_down()
            card.move_on_top()
            card.place(self.stock)

    def check_win(self):
        """Verifica se o jogo foi ganho e chama a sequência de vitória."""
        cards_num = 0
        for slot in self.foundations:
            cards_num += len(slot.pile)
        if cards_num == 52:
            self.winning_sequence()
            return True
        return False

    def winning_sequence(self):
        """Exibe a animação de vitória e a pontuação final."""
        for slot in self.foundations:
            for card in slot.pile:
                card.animate_position = 2000
                card.move_on_top()
                card.top = random.randint(0, SOLITAIRE_HEIGHT)
                card.left = random.randint(0, SOLITAIRE_WIDTH)
                self.update()

        tempo_decorrido = time.time() - self.tempo_inicial
        pontos_tempo = self.calcular_pontos_tempo(tempo_decorrido)
        penalidade_dicas = self.calcular_penalidade_dicas()  # Calcula a penalidade das dicas
        pontuacao_final = self.pontuacao + pontos_tempo - penalidade_dicas

        # Mostrar o diálogo de vitória com pontuação e tempo
        dialog = ft.AlertDialog(
            title=ft.Text("Parabéns, você ganhou!"),
            content=ft.Text(
                f"Pontuação: {self.pontuacao}\nPontuação de tempo: {pontos_tempo}\nTempo decorrido: {self.formatar_tempo(tempo_decorrido)}\nDicas Usadas: {self.dicas_usadas}\nPenalidade de Dicas: {penalidade_dicas}\nPontuação final: {pontuacao_final}"),
            actions=[ft.TextButton("Jogar novamente", on_click=lambda _: self.restart_game())],
            open=True,
        )
        self.controls.append(dialog)
        self.update()

    def restart_game(self):
        """Reinicia o jogo, limpando o estado e redefinindo a pontuação e o tempo."""
        try:
            self.clear_game_state()

            # Recriar o baralho e distribuir as cartas
            self.create_card_deck()
            random.shuffle(self.cards)
            self.deal_cards()

            # Redefinir pontuação e tempo
            self.pontuacao = 0
            self.tempo_inicial = None
            self.timer_started = False

            # Redefinir dicas
            self.dicas_usadas = 0
            self.dicas_restantes_text.value = f"Dicas Restantes: {self.calcular_dicas_restantes()}"
            self.dicas_restantes_text.update()

            # Atualizar texto de pontuação e tempo
            self.pontuacao_text.value = f"Pontuação: {self.pontuacao}"
            self.pontuacao_text.update()
            self.tempo_text.value = "Tempo: 00:00"
            self.tempo_text.update()

            self.update()

            print("Jogo reiniciado!")
        except Exception as e:
            print(f"Erro ao reiniciar o jogo: {e}")

    def save_game_state(self, e):
        try:
            # Calcular o tempo decorrido antes de salvar
            tempo_decorrido = time.time() - self.tempo_inicial if self.tempo_inicial else 0

            # Criar um dicionário com o estado atual do jogo
            game_state = {
                "history": [],
                "pontuacao": self.pontuacao,
                "tempo_inicial": self.tempo_inicial,
                "timer_started": self.timer_started,
                "dicas_usadas": self.dicas_usadas,
                "tempo": tempo_decorrido  # Salva o tempo decorrido em segundos
            }

            # Salvar o estado das cartas (tableau, foundations, stock e waste)
            for tableau_slot in self.tableau:
                for card in tableau_slot.pile:
                    move = {
                        "card": {
                            "suite": card.suite.to_dict(),
                            "rank": card.rank.to_dict(),
                            "face_up": card.face_up,
                            "top": card.top,
                            "left": card.left,
                        },
                        "from_slot": f"tableau{self.tableau.index(tableau_slot)}",
                    }
                    game_state["history"].append(move)

            for foundation in self.foundations:
                for card in foundation.pile:
                    move = {
                        "card": {
                            "suite": card.suite.to_dict(),
                            "rank": card.rank.to_dict(),
                            "face_up": card.face_up,
                            "top": card.top,
                            "left": card.left,
                        },
                        "from_slot": f"foundation{self.foundations.index(foundation)}",
                    }
                    game_state["history"].append(move)

            for card in self.waste.pile:
                move = {
                    "card": {
                        "suite": card.suite.to_dict(),
                        "rank": card.rank.to_dict(),
                        "face_up": card.face_up,
                        "top": card.top,
                        "left": card.left,
                    },
                    "from_slot": "waste",
                }
                game_state["history"].append(move)

            for card in self.stock.pile:
                move = {
                    "card": {
                        "suite": card.suite.to_dict(),
                        "rank": card.rank.to_dict(),
                        "face_up": card.face_up,
                        "top": card.top,
                        "left": card.left,
                    },
                    "from_slot": "stock",
                }
                game_state["history"].append(move)

            # Salvar o arquivo de estado
            with open(self.SAVE_FILE, "w") as f:
                json.dump(game_state, f, indent=4)
            print("✅ Estado do jogo salvo com sucesso.")

        except Exception as e:
            print(f"❌ Erro ao salvar o jogo: {e}")

    def load_game_state(self, e):
        try:
            if not os.path.exists(self.SAVE_FILE):
                print("❌ Arquivo de salvamento não encontrado!")
                return

            with open(self.SAVE_FILE, "r") as file:
                game_state = json.load(file)

            print("✅ Jogo carregado:", game_state)

            # Restaurar pontuação, tempo e dicas
            self.pontuacao = game_state.get("pontuacao", 0)
            self.tempo_inicial = game_state.get("tempo_inicial")
            self.timer_started = game_state.get("timer_started", False)
            self.dicas_usadas = game_state.get("dicas_usadas", 0)

            # Limpar o estado do jogo e recriar os slots
            self.clear_game_state()
            self.create_slots()

            # Recriar as cartas e colocá-las nos slots corretos
            for move in game_state["history"]:
                card_data = move["card"]
                suite = Suite.from_dict(card_data["suite"])
                rank = Rank.from_dict(card_data["rank"])
                face_up = card_data["face_up"]
                top = card_data["top"]
                left = card_data["left"]

                card = Card(solitaire=self, suite=suite, rank=rank)
                card.face_up = face_up
                card.top = top
                card.left = left

                from_slot_name = move["from_slot"]

                if from_slot_name == "stock":
                    slot = self.stock
                elif from_slot_name == "waste":
                    slot = self.waste
                elif from_slot_name.startswith("tableau"):
                    index = int(from_slot_name.replace("tableau", ""))
                    slot = self.tableau[index]
                elif from_slot_name.startswith("foundation"):
                    index = int(from_slot_name.replace("foundation", ""))
                    slot = self.foundations[index]
                else:
                    slot = None

                if slot:
                    card.place(slot)
                    if face_up:
                        print(f"DEBUG: Virando carta para cima: {card.rank.name} de {card.suite.name}")
                        card.turn_face_up()
                    else:
                        print(f"DEBUG: Carta virada para baixo: {card.rank.name} de {card.suite.name}")
                    if card not in self.controls:
                        self.controls.append(card)

            # Atualizar textos da interface
            self.pontuacao_text.value = f"Pontuação: {self.pontuacao}"
            self.pontuacao_text.update()

            if self.tempo_inicial:
                tempo_decorrido = time.time() - self.tempo_inicial
                self.tempo_text.value = f"Tempo: {self.formatar_tempo(tempo_decorrido)}"
            else:
                self.tempo_text.value = "Tempo: 00:00"

            self.tempo_text.update()
            self.dicas_restantes_text.value = f"Dicas Restantes: {self.calcular_dicas_restantes()}"
            self.dicas_restantes_text.update()

            self.update()
            self.interface_pronta = True

            print(" Estado do jogo restaurado!")

        except Exception as ex:
            print(f"❌ Erro ao carregar o jogo: {ex}")

    def clear_game_state(self):
        """Limpa o estado atual do jogo, removendo todas as cartas e resets, mas preservando tempo e pontuação."""
        # Resetar apenas os elementos do jogo, sem afetar o tempo e a pontuação
        self.history = []
        self.stock.pile.clear()
        self.waste.pile.clear()

        for foundation in self.foundations:
            foundation.pile.clear()

        for tableau_slot in self.tableau:
            tableau_slot.pile.clear()

        # Limpar os controles de cartas, mas manter os textos da interface
        self.controls.clear()

        # Recriar os slots e controles
        self.create_slots()
        self.update()

        print("🧹 Estado do jogo limpo, mantendo tempo e pontuação.")

    def change_card_back_handler(self, e):
        selected_option = e.control.value
        self.change_card_back(selected_option)


    def formatar_tempo(self, segundos):
        """Formata o tempo decorrido em minutos e segundos."""
        minutos = int(segundos // 60)
        segundos = int(segundos % 60)
        return f"{minutos:02d}:{segundos:02d}"

    def calcular_pontos_tempo(self, tempo_decorrido):
        """Calcula os pontos de tempo com base em limiares."""
        if tempo_decorrido < 120:  # Menos de 2 minuto
            return 500
        elif tempo_decorrido < 180:  # Menos de 3 minutos
            return 300
        elif tempo_decorrido < 240:  # Menos de 4 minutos
            return 100
        else:  # Mais de 4 minutos
            return 50

    def atualizar_tempo_thread(self):
        """Atualiza o tempo decorrido na tela em uma thread."""
        while self.tempo_inicial:
            if self.interface_pronta:
                tempo_decorrido = time.time() - self.tempo_inicial
                tempo_formatado = self.formatar_tempo(tempo_decorrido)
                self.tempo_text.value = f"Tempo: {tempo_formatado}"  # Substituição completa do texto
                self.tempo_text.update()
            time.sleep(1)

    def fornecer_dica(self):
        """Fornece uma dica ao jogador."""
        movimento_encontrado = False

        # Verificar movimentos no tableau
        for from_slot in self.tableau:
            if from_slot.pile:
                card = from_slot.get_top_card()
                for to_slot in self.tableau:
                    if from_slot != to_slot and self.check_tableau_rules(card, to_slot):
                        self.move_card(card, from_slot, to_slot)
                        card.move_on_top()  # Coloca a carta no topo visualmente
                        movimento_encontrado = True
                        self.dicas_usadas += 1  # Incrementa o contador de dicas
                        break  # Encontrou um movimento, sai do loop
                if not movimento_encontrado:
                    for to_slot in self.foundations:
                        if self.check_foundations_rules(card, to_slot):
                            self.move_card(card, from_slot, to_slot)
                            card.move_on_top()  # Coloca a carta no topo visualmente
                            movimento_encontrado = True
                            self.dicas_usadas += 1  # Incrementa o contador de dicas
                            break  # Encontrou um movimento, sai do loop
            if movimento_encontrado:
                break  # sai do loop externo

        if movimento_encontrado:
            self.dicas_restantes_text.value = f"Dicas Restantes: {self.calcular_dicas_restantes()}"
            self.dicas_restantes_text.update()
            return  # Movimento realizado no tableau

        # Verificar movimentos no estoque
        if self.stock.pile:
            card = self.stock.get_top_card()
            card.turn_face_up()
            card.move_on_top()
            card.place(self.waste)
            self.update()  # Atualiza a interface
            for to_slot in self.tableau:
                if self.check_tableau_rules(card, to_slot):
                    self.move_card(card, self.waste, to_slot)
                    card.move_on_top()  # Coloca a carta no topo visualmente
                    self.dicas_usadas += 1  # Incrementa o contador de dicas
                    return  # Movimento realizado do estoque
            for to_slot in self.foundations:
                if self.check_foundations_rules(card, to_slot):
                    self.move_card(card, self.waste, to_slot)
                    card.move_on_top()  # Coloca a carta no topo visualmente
                    self.dicas_usadas += 1  # Incrementa o contador de dicas
                    return  # Movimento realizado do estoque
            self.dicas_usadas += 1  # Incrementa o contador de dicas.
            self.dicas_restantes_text.value = f"Dicas Restantes: {self.calcular_dicas_restantes()}"
            self.dicas_restantes_text.update()
            return  # Carta virada do estoque e colocada no descarte

        # Nenhum movimento encontrado
        self.exibir_mensagem_fim_jogo()

    def exibir_mensagem_fim_jogo(self):
        """Exibe uma mensagem de fim de jogo."""
        dialog = ft.AlertDialog(
            title=ft.Text("Fim de Jogo"),
            content=ft.Text("Não há mais movimentos possíveis. Deseja iniciar um novo jogo?"),
            actions=[
                ft.TextButton("Sim", on_click=lambda _: self.restart_game()),
                ft.TextButton("Não", on_click=lambda _: dialog.close()),  # usando dialog.close()
            ],
            open=True,
        )
        self.controls.append(dialog)
        self.update()

    def calcular_dicas_restantes(self):
        """Calcula o número de dicas restantes."""
        max_dicas = 5  # Defina o número máximo de dicas aqui
        return max_dicas - self.dicas_usadas

    def calcular_penalidade_dicas(self):
        """Calcula a penalidade total com base no número de dicas usadas."""
        penalidade_total = 0
        penalidade_base = 10  # Penalidade inicial por dica
        for i in range(self.dicas_usadas):
            penalidade_total += penalidade_base * (i + 1)  # Diminui a penalidade por dica
        return int(penalidade_total)