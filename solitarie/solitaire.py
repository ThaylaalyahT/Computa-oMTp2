SOLITAIRE_WIDTH = 1000
SOLITAIRE_HEIGHT = 500

import random

import flet as ft
from card import Card
from slot import Slot



class Suite:
    def __init__(self, suite_name, suite_color):
        self.name = suite_name
        self.color = suite_color


class Rank:
    def __init__(self, card_name, card_value):
        self.name = card_name
        self.value = card_value


class Solitaire(ft.Stack):
    def __init__(self):
        super().__init__()
        self.controls = []
        self.width = SOLITAIRE_WIDTH
        self.height = SOLITAIRE_HEIGHT
        self.history = []

    def did_mount(self):
        self.create_card_deck()
        self.create_slots()
        self.deal_cards()

    def move_card(self, card, from_slot, target_slot):
        """Move uma carta e armazena o estado anterior diretamente."""
        # Identificar se o movimento é do Stock para o Waste
        is_stock_to_waste = from_slot == self.stock and target_slot == self.waste

        # Encontrar a carta que estava embaixo antes do movimento
        card_below = from_slot.pile[-2] if len(from_slot.pile) > 1 else None
        card_below_was_face_up = card_below.face_up if card_below else None

        # Salvar estado antes da jogada
        self.history.append({
            "card": card,
            "from_slot": from_slot,
            "to_slot": target_slot,  # Certifique-se de que 'to_slot' está sendo armazenado corretamente
            "card_top": card.top,
            "card_left": card.left,
            "face_up": card.face_up,
            "card_below": card_below,
            "card_below_was_face_up": card_below_was_face_up,
            "is_stock_to_waste": is_stock_to_waste  # Flag indicando esse tipo de movimento
        })

        # Mover a carta
        card.place(target_slot)

        # Se havia uma carta abaixo, ela deve virar para cima
        if card_below:
            card_below.turn_face_up()

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

