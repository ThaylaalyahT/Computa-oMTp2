import flet as ft
CARD_WIDTH = 70
CARD_HEIGHT = 100
DROP_PROXIMITY = 30
CARD_OFFSET = 20


class Card(ft.GestureDetector):
    def __init__(self, solitaire, suite, rank):
        super().__init__()
        self.mouse_cursor = ft.MouseCursor.MOVE
        self.drag_interval = 5
        self.on_pan_start = self.start_drag
        self.on_pan_update = self.drag
        self.on_pan_end = self.drop
        self.on_tap = self.click
        self.on_double_tap = self.doubleclick
        self.suite = suite
        self.rank = rank
        self.face_up = False
        self.top = None
        self.left = None
        self.solitaire = solitaire
        self.slot = None
        self.content = ft.Container(
            width=CARD_WIDTH,
            height=CARD_HEIGHT,
            border_radius=ft.border_radius.all(6),
            content=ft.Image(src=self.get_card_image_src()),  
        )
        self.draggable_pile = [self]

    def get_card_image_src(self):
        if self.face_up:
            return f"{self.rank.name}_{self.suite.name}.png"  
        else:
            return self.solitaire.card_back_image 

    def turn_face_up(self):
        self.face_up = True
        self.content.content.src = f"{self.rank.name}_{self.suite.name}.png"
        self.solitaire.update()

    def turn_face_down(self):
        self.face_up = False
        self.content.content.src = self.get_card_image_src()
        self.solitaire.update()
        

    def move_on_top(self):
        for card in self.draggable_pile:
            self.solitaire.controls.remove(card)
            self.solitaire.controls.append(card)
        self.solitaire.update()

    def bounce_back(self):
        for card in self.draggable_pile:
            if card.slot in self.solitaire.tableau:
                card.top = card.slot.top + card.slot.pile.index(card) * CARD_OFFSET
            else:
                card.top = card.slot.top
            card.left = card.slot.left
        self.solitaire.update()

    def place(self, slot):

        if hasattr(self, 'draggable_pile') and self.draggable_pile:  
            cards_to_place = self.draggable_pile
        else:  
            cards_to_place = [self]  

        for card in cards_to_place:
            if slot in self.solitaire.tableau:
                card.top = slot.top + len(slot.pile) * CARD_OFFSET
            else:
                card.top = slot.top
            card.left = slot.left

            
            if card.slot is not None:
                card.slot.pile.remove(card)

            
            card.slot = slot

            
            slot.pile.append(card)

        if self.solitaire.check_win():
            self.solitaire.winning_sequence()

        self.solitaire.update()

    def get_draggable_pile(self):

        if (
            self.slot is not None
            and self.slot != self.solitaire.stock
            and self.slot != self.solitaire.waste
        ):
            self.draggable_pile = self.slot.pile[self.slot.pile.index(self) :]
        else:  
            self.draggable_pile = [self]

    def start_drag(self, e: ft.DragStartEvent):
        if self.face_up:
            self.get_draggable_pile()
            self.move_on_top()

    def drag(self, e: ft.DragUpdateEvent):
        if self.face_up:
            for card in self.draggable_pile:
                card.top = (
                    max(0, self.top + e.delta_y)
                    + self.draggable_pile.index(card) * CARD_OFFSET
                )
                card.left = max(0, self.left + e.delta_x)
                self.solitaire.update()

    def drop(self, e: ft.DragEndEvent):
        from_slot = self.slot
        if self.face_up:
            for slot in self.solitaire.tableau:
                if (
                    abs(self.top - (slot.top + len(slot.pile) * CARD_OFFSET))
                    < DROP_PROXIMITY
                    and abs(self.left - slot.left) < DROP_PROXIMITY
                ) and self.solitaire.check_tableau_rules(self, slot):
                    self.solitaire.move_card(self, from_slot, slot)
                    return

            if len(self.draggable_pile) == 1:
                for slot in self.solitaire.foundations:
                    if (
                        abs(self.top - slot.top) < DROP_PROXIMITY
                        and abs(self.left - slot.left) < DROP_PROXIMITY
                    ) and self.solitaire.check_foundations_rules(self, slot):
                        self.solitaire.move_card(self, from_slot, slot)
                        return

            self.bounce_back()

    def click(self, e):
        from_slot = self.slot  
        self.get_draggable_pile()  

        if self.slot in self.solitaire.tableau:
            
            if not self.face_up and self == self.slot.get_top_card():
                self.turn_face_up()

        elif self.slot == self.solitaire.stock:
            
            if self.face_up:
                self.turn_face_down()  

            self.move_on_top()  
            self.place(self.solitaire.waste)  
            self.turn_face_up()  

            
            if self.solitaire.stock.pile:
                next_card = self.solitaire.stock.pile[-1]  
                next_card.turn_face_down()  

            
            self.solitaire.move_card(self, from_slot, self.solitaire.waste)

    def doubleclick(self, e):
        from_slot = self.slot
        self.get_draggable_pile()
        if self.face_up and len(self.draggable_pile) == 1:
            self.move_on_top()
            for slot in self.solitaire.foundations:
                if self.solitaire.check_foundations_rules(self, slot):
                    self.solitaire.move_card(self, from_slot, slot)
                    return