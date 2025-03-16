import json

SOLITAIRE_WIDTH = 1000
SOLITAIRE_HEIGHT = 500

import random

import flet as ft
from card import Card, CARD_WIDTH, CARD_HEIGHT
from slot import Slot
import os


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
        self.controls = []
        self.width = SOLITAIRE_WIDTH
        self.height = SOLITAIRE_HEIGHT
        self.history = []
        self.card_back_image = "images/default_back.png"
        self.SAVE_FILE = "solitaire_save.json"  # 🔹 Definindo como atributo da instância


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
        """Move uma carta e armazena o estado anterior diretamente."""
        is_stock_to_waste = from_slot == self.stock and target_slot == self.waste
        card_below = from_slot.pile[-2] if len(from_slot.pile) > 1 else None
        card_below_was_face_up = card_below.face_up if card_below else None

        self.history.append({
            "card": card,
            "from_slot": from_slot,
            "to_slot": target_slot,
            "card_top": card.top,
            "card_left": card.left,
            "face_up": card.face_up,
            "card_below": card_below,
            "card_below_was_face_up": card_below_was_face_up,
            "is_stock_to_waste": is_stock_to_waste
        })

        card.place(target_slot)

        if card_below:
            card_below.turn_face_up()

        if card not in self.controls:
            self.controls.append(card)

        print(f"Movido {card.rank.name} de {card.suite.name} de {from_slot} para {target_slot}.")

        self.update()

    def undo_move(self):
        """Desfaz a última jogada, incluindo movimentos do Stock para o Waste."""
        if not self.history:
            print("🚫 Nenhum movimento para desfazer.")
            return

        last_move = self.history.pop()

        card = last_move["card"]
        from_slot = last_move["from_slot"]
        to_slot = last_move["to_slot"]  # Agora, to_slot deve estar corretamente registrado
        card_below = last_move.get("card_below")
        card_below_was_face_up = last_move.get("card_below_was_face_up")
        is_stock_to_waste = last_move["is_stock_to_waste"]

        if is_stock_to_waste:
            # Voltar a carta para o Stock
            card.turn_face_down()  # Virar a carta de volta para baixo
            card.move_on_top()  # Garantir que ela volte para o topo
            card.place(self.stock)  # Colocar a carta de volta no Stock
            print(f"🔄 Desfeito: {card.rank.name} de {card.suite.name} voltou para o Stock.")
        else:
            # Restaurar a posição e a face da carta
            card.top = last_move["card_top"]
            card.left = last_move["card_left"]
            card.face_up = last_move["face_up"]
            card.place(from_slot)

            # Se a carta abaixo existir e estava virada para cima, virá-la para baixo
            if card_below and not card_below_was_face_up:
                card_below.turn_face_down()

            print(f"🔄 Desfeito: {card.rank.name} de {card.suite.name} voltou para {from_slot}.")

        if not self.history:
            print("🛑 Nenhum outro movimento pode ser desfeito.")

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

        self.controls.append(self.stock)
        self.controls.append(self.waste)
        self.controls.extend(self.foundations)
        self.controls.extend(self.tableau)

        undo_button = ft.ElevatedButton("Undo", on_click=lambda _: self.undo_move())
        undo_container = ft.Container(
            content=undo_button,
            top=SOLITAIRE_HEIGHT - 500,
            left=SOLITAIRE_WIDTH - 200,
        )
        self.controls.append(undo_container)

        restart_button = ft.ElevatedButton("Restart", on_click=lambda _: self.restart_game())
        restart_container = ft.Container(content=restart_button, top=SOLITAIRE_HEIGHT - 450, left=SOLITAIRE_WIDTH - 200)
        self.controls.append(restart_container)

        def change_card_back_handler(e):
            selected_option = e.control.value
            self.change_card_back(selected_option)

        card_back_options = ["Yellow flower.png", "Pink Flower.png", "Black Pattern.png", "Purple Pattern.png", "default_back.png"]

        card_back_dropdown = ft.Dropdown(
            options=[ft.dropdown.Option(text=option) for option in card_back_options],
            on_change=change_card_back_handler,
            width=200,
            label="Change Theme Card"
        )

        card_back_container = ft.Container(content=card_back_dropdown, top=SOLITAIRE_HEIGHT - 400,
                                           left=SOLITAIRE_WIDTH - 200)

        self.controls.append(card_back_container)

        save_button = ft.ElevatedButton("Salvar Jogo", on_click=self.save_game_state)
        save_container = ft.Container(content=save_button, top=SOLITAIRE_HEIGHT - 500, left=SOLITAIRE_WIDTH - 100)
        self.controls.append(save_container)

        # Botão "Carregar Jogo Salvo" (condicional)
        if os.path.exists(self.SAVE_FILE):
            load_button = ft.ElevatedButton(
                "Carregar Jogo Salvo",
                on_click=self.load_game_state,
                bgcolor=ft.colors.BLUE,
                color=ft.colors.WHITE
            )
            load_container = ft.Container(content=load_button, top=SOLITAIRE_HEIGHT - 450, left=SOLITAIRE_WIDTH - 100)
            self.controls.append(load_container)

        self.update()


    def deal_cards(self):
        random.shuffle(self.cards)
        self.controls.extend(self.cards)

        # deal to tableau
        first_slot = 0
        remaining_cards = self.cards

        while first_slot < len(self.tableau):
            for slot in self.tableau[first_slot:]:
                top_card = remaining_cards[0]
                top_card.place(slot)
                remaining_cards.remove(top_card)
            first_slot += 1

        # place remaining cards to stock pile
        for card in remaining_cards:
            card.place(self.stock)
            print(f"Card in stock: {card.rank.name} {card.suite.name}")

        self.update()

        for slot in self.tableau:
            slot.get_top_card().turn_face_up()

        self.update()

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
        cards_num = 0
        for slot in self.foundations:
            cards_num += len(slot.pile)
        if cards_num == 52:
            return True
        return False

    def winning_sequence(self):
        """Exibe a animação de vitória e permite reiniciar o jogo."""
        # Animar as cartas para mostrar que o jogo foi vencido
        for slot in self.foundations:
            for card in slot.pile:
                card.animate_position = 2000
                card.move_on_top()
                card.top = random.randint(0, SOLITAIRE_HEIGHT)
                card.left = random.randint(0, SOLITAIRE_WIDTH)
                self.update()

        # Mostrar o diálogo de vitória
        self.controls.append(
            ft.AlertDialog(
                title=ft.Text("Congratulations, you won!"),
                actions=[
                    ft.TextButton("Play Again", on_click=lambda _: self.restart_game())
                ],
                open=True
            )
        )

        # Atualizar a interface
        self.update()

    def restart_game(self):
        """Reinicia o jogo, limpando o estado e embaralhando as cartas novamente."""
        # Limpar histórico de jogadas
        self.history = []

        # Limpar as pilhas de cartas
        self.stock.pile.clear()
        self.waste.pile.clear()
        for foundation in self.foundations:
            foundation.pile.clear()
        for tableau_slot in self.tableau:
            tableau_slot.pile.clear()

        # Remover as cartas da interface (se ainda estiverem visíveis)
        self.controls = [self.stock, self.waste]  # Manter apenas os controles principais
        self.controls.extend(self.foundations)
        self.controls.extend(self.tableau)

        # Remover as cartas anteriores
        self.controls = [control for control in self.controls if not isinstance(control, Card)]

        # Criar e embaralhar o baralho novamente
        self.create_card_deck()
        random.shuffle(self.cards)

        # Recriar os slots
        self.create_slots()

        # Distribuir as cartas novamente
        self.deal_cards()

        # Atualizar a interface
        self.update()

        print("🔄 Jogo reiniciado!")

    def save_game_state(self, e):
        try:
            # Criar um dicionário com o estado atual do jogo
            game_state = {
                "history": []  # Vamos armazenar as movimentações de cartas
            }

            # Salvar o estado das cartas (pilhas: stock, waste, foundations, tableau)
            # Salvar o estado do tableau
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

            # Salvar o estado das foundations
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

            # Salvar o estado do waste
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

            # Salvar o estado do stock (cartas restantes)
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
            print("Game state saved successfully.")
        except Exception as e:
            print(f"Error saving game state: {e}")

    def load_game_state(self, e):
        try:
            if not os.path.exists(self.SAVE_FILE):
                print("❌ Arquivo de salvamento não encontrado!")
                return

            with open(self.SAVE_FILE, "r") as file:
                game_state = json.load(file)

            print("✅ Jogo carregado:", game_state)

            # Limpar o estado do jogo antes de carregar o novo
            self.clear_game_state()

            # Remover todas as cartas antigas de self.controls
            self.controls = [control for control in self.controls if not isinstance(control, Card)]

            # Recriar as cartas e colocá-las nas pilhas corretas
            cards_to_add = []  # Lista para armazenar as cartas antes de adicioná-las ao self.controls

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

                if from_slot_name.startswith("tableau"):
                    index = int(from_slot_name.replace("tableau", ""))
                    slot = self.tableau[index]
                elif from_slot_name.startswith("foundation"):
                    index = int(from_slot_name.replace("foundation", ""))
                    slot = self.foundations[index]
                elif from_slot_name == "waste":
                    slot = self.waste
                elif from_slot_name == "stock":
                    slot = self.stock

                print(
                    f"DEBUG: Adicionando carta {card.rank.name} de {card.suite.name} ao slot {slot} com top={card.top} e left={card.left}")
                card.place(slot)  # Colocar a carta no slot correto

                if face_up:
                    card.turn_face_up()  # Virar a carta para cima se necessário

                cards_to_add.append(card)

            # Adicionar todas as cartas ao self.controls
            for card in cards_to_add:
                if card not in self.controls:
                    self.controls.append(card)

            self.update()
            print(" Estado do jogo restaurado!")

        except Exception as ex:
            print(f"❌ Erro ao carregar o jogo: {ex}")

    def clear_game_state(self):
        """Limpa o estado atual do jogo, removendo todas as cartas e resets."""
        # Limpar o histórico de jogadas
        self.history = []

        # Limpar as pilhas de cartas
        self.stock.pile.clear()
        self.waste.pile.clear()

        # Limpar as pilhas das fundações
        for foundation in self.foundations:
            foundation.pile.clear()

        # Limpar as pilhas do tableau
        for tableau_slot in self.tableau:
            tableau_slot.pile.clear()

        # Limpar os controles das cartas na interface (se estiverem visíveis)
        self.controls = [self.stock, self.waste]  # Manter apenas os controles principais
        self.controls.extend(self.foundations)
        self.controls.extend(self.tableau)

        # Remover as cartas anteriores
        self.controls = [control for control in self.controls if not isinstance(control, Card)]

        # Recriar os controles
        self.create_controls()  # Chamar a função que cria os botões e outros controles

        # Atualizar a interface
        self.update()

        print("Estado do jogo limpo.")

    def create_controls(self):
        """Cria os botões e outros controles da interface."""
        undo_button = ft.ElevatedButton("Undo", on_click=lambda _: self.undo_move())
        undo_container = ft.Container(
            content=undo_button,
            top=SOLITAIRE_HEIGHT - 500,
            left=SOLITAIRE_WIDTH - 200,
        )
        self.controls.append(undo_container)

        restart_button = ft.ElevatedButton("Restart", on_click=lambda _: self.restart_game())
        restart_container = ft.Container(content=restart_button, top=SOLITAIRE_HEIGHT - 450, left=SOLITAIRE_WIDTH - 200)
        self.controls.append(restart_container)

        def change_card_back_handler(e):
            selected_option = e.control.value
            self.change_card_back(selected_option)

        card_back_options = ["Yellow flower.png", "Pink Flower.png", "Black Pattern.png", "Purple Pattern.png",
                             "default_back.png"]

        card_back_dropdown = ft.Dropdown(
            options=[ft.dropdown.Option(text=option) for option in card_back_options],
            on_change=change_card_back_handler,
            width=200,
            label="Change Theme Card"
        )

        card_back_container = ft.Container(content=card_back_dropdown, top=SOLITAIRE_HEIGHT - 400,
                                           left=SOLITAIRE_WIDTH - 200)

        self.controls.append(card_back_container)

        save_button = ft.ElevatedButton("Salvar Jogo", on_click=self.save_game_state)
        save_container = ft.Container(content=save_button, top=SOLITAIRE_HEIGHT - 500, left=SOLITAIRE_WIDTH - 100)
        self.controls.append(save_container)

        # Botão "Carregar Jogo Salvo" (condicional)
        if os.path.exists(self.SAVE_FILE):
            load_button = ft.ElevatedButton(
                "Carregar Jogo Salvo",
                on_click=self.load_game_state,
                bgcolor=ft.colors.BLUE,
                color=ft.colors.WHITE
            )
            load_container = ft.Container(content=load_button, top=SOLITAIRE_HEIGHT - 450, left=SOLITAIRE_WIDTH - 100)
            self.controls.append(load_container)

        self.update()






