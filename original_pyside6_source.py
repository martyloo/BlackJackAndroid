import sys
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QHBoxLayout,
    QTextEdit,
    QComboBox,
    QScrollArea
)

class MyWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.dealers_card_received = False
        self.current_textbox_index = 0
        self.text_boxes_full = False

    def initUI(self):
        self.original_value = 0
        
        self.cards_dealt_label = QLabel('No. Cards Dealt:', self)
        self.top_value_box = QLineEdit(str(self.original_value), self)
        self.top_value_box.setReadOnly(True)
        self.top_value_box.setFixedWidth(self.top_value_box.sizeHint().width() // 2)

        self.new_value_box_label = QLabel('No. Cards Left:', self)
        self.new_value_box = QLineEdit(str(self.original_value), self)
        self.new_value_box.setReadOnly(True)
        self.top_value_box.textChanged.connect(self.update_new_value_box)
        self.new_value_box.setFixedWidth(self.top_value_box.sizeHint().width() // 2)

        self.decks_left_box_label = QLabel('No. Decks Left:', self)
        self.decks_left_box = QLineEdit(str(self.original_value), self)
        self.decks_left_box.setReadOnly(True)
        self.decks_left_box.setFixedWidth(self.top_value_box.sizeHint().width() // 2)
        
        self.count_label = QLabel('Running Count:', self)
        self.value_box = QLineEdit(str(self.original_value), self)
        self.value_box.setReadOnly(True)
        self.value_box.setFixedWidth(self.top_value_box.sizeHint().width() // 2)
        
        self.true_count_label = QLabel('True Count:', self)
        self.true_count_box = QLineEdit('0', self)
        self.true_count_box.setReadOnly(True)
        self.true_count_box.setFixedWidth(self.top_value_box.sizeHint().width() // 2)
        
        self.addButton = QPushButton('2, 3, 4, 5, 6', self)
        self.addButton.clicked.connect(self.add_one)
        self.addButton.clicked.connect(self.add_one_to_top_value_box)

        self.sevenEightNineButton = QPushButton('7, 8, 9', self)
        self.sevenEightNineButton.clicked.connect(self.add_seven_eight_nine)
        self.sevenEightNineButton.clicked.connect(self.add_one_to_top_value_box)

        self.subtractButton = QPushButton('10, Jack, Queen, King, Ace', self)
        self.subtractButton.clicked.connect(self.subtract_one)
        self.subtractButton.clicked.connect(self.add_one_to_top_value_box)
        
        self.aceButton = QPushButton('Ace', self)
        self.jackButton = QPushButton('Jack', self)
        self.eightButton = QPushButton('8', self)
        self.tenButton = QPushButton('10', self)
        self.sevenButton = QPushButton('7', self)
        self.nineButton = QPushButton('9', self)
        self.sixButton = QPushButton('6', self)
        self.queenButton = QPushButton('Queen', self)
        self.kingButton = QPushButton('King', self)
        self.fiveButton = QPushButton('5', self)
        self.fourButton = QPushButton('4', self)
        self.threeButton = QPushButton('3', self)
        self.twoButton = QPushButton('2')
        
        self.button_to_label = {
            self.aceButton: 'Ace',
            self.jackButton: 'Jack',
            self.eightButton: '8',
            self.tenButton: '10',
            self.sevenButton: '7',
            self.nineButton: '9',
            self.sixButton: '6',
            self.queenButton: 'Queen',
            self.kingButton: 'King',
            self.fiveButton: '5',
            self.fourButton: '4',
            self.threeButton: '3',
            self.twoButton: '2'
        }
        
        for button in self.button_to_label:
            button.clicked.connect(self.show_card)
        
        button_layout = QVBoxLayout()
        button_layout.addWidget(self.aceButton)
        button_layout.addWidget(self.jackButton)
        button_layout.addWidget(self.eightButton)
        button_layout.addWidget(self.fiveButton)
        
        button_layout2 = QVBoxLayout()
        button_layout2.addWidget(self.kingButton)
        button_layout2.addWidget(self.tenButton)
        button_layout2.addWidget(self.sevenButton)
        button_layout2.addWidget(self.fourButton)
        button_layout2.addWidget(self.twoButton)
        
        button_layout3 = QVBoxLayout()
        button_layout3.addWidget(self.queenButton)
        button_layout3.addWidget(self.nineButton)
        button_layout3.addWidget(self.sixButton)
        button_layout3.addWidget(self.threeButton)
        
        self.decks_combo = QComboBox(self)
        self.decks_combo.addItems(['1', '2', '3', '4', '5', '6', '7', '8'])
        self.decks_combo.currentIndexChanged.connect(self.select_decks)
        
        combo_layout = QHBoxLayout()
        combo_layout.addWidget(QLabel('No. of Decks:', self))
        combo_layout.addWidget(self.decks_combo)
        combo_layout.addWidget(self.decks_left_box_label)
        combo_layout.addWidget(self.decks_left_box)
        
        layout = QVBoxLayout()
        
        dealt_and_left_layout = QHBoxLayout()
        dealt_and_left_layout.addWidget(self.cards_dealt_label)
        dealt_and_left_layout.addWidget(self.top_value_box)
        dealt_and_left_layout.addWidget(self.new_value_box_label)
        dealt_and_left_layout.addWidget(self.new_value_box)

        count_layout = QHBoxLayout()
        count_layout.addWidget(self.count_label)
        count_layout.addWidget(self.value_box)
        count_layout.addWidget(self.true_count_label)
        count_layout.addWidget(self.true_count_box)

        layout.addLayout(dealt_and_left_layout)
        layout.addLayout(count_layout)
        layout.addLayout(combo_layout)
        
        layout.addWidget(self.addButton)
        layout.addWidget(self.sevenEightNineButton)
        layout.addWidget(self.subtractButton)

        min_bet_layout = QHBoxLayout()
        self.min_bet_label = QLabel('Min Bet:', self)
        self.min_bet_box = QLineEdit(self)
        self.min_bet_box.setFixedWidth(self.top_value_box.sizeHint().width() // 2)
        self.min_bet_box.textChanged.connect(self.update_stake_required)
        self.min_bet_box.textChanged.connect(self.update_bet_amount)

        self.stake_required_label = QLabel('Stake:', self)
        self.stake_required_box = QLineEdit(self)
        self.stake_required_box.setReadOnly(True)
        self.stake_required_box.setFixedWidth(self.top_value_box.sizeHint().width() // 2)
        
        self.bet_amount_label = QLabel('Bet:', self)
        self.bet_amount_box = QLineEdit(self)
        self.bet_amount_box.setReadOnly(True)
        self.bet_amount_box.setFixedWidth(self.top_value_box.sizeHint().width() // 2)

        min_bet_layout.addWidget(self.min_bet_label)
        min_bet_layout.addWidget(self.min_bet_box)
        min_bet_layout.addWidget(self.stake_required_label)
        min_bet_layout.addWidget(self.stake_required_box)
        min_bet_layout.addWidget(self.bet_amount_label)
        min_bet_layout.addWidget(self.bet_amount_box)
        
        layout.addLayout(min_bet_layout)

        hbox = QHBoxLayout()

        hbox.addLayout(button_layout)
        hbox.addLayout(button_layout2)
        hbox.addLayout(button_layout3)
        
        layout.addLayout(hbox)

        card_info_layout = QHBoxLayout()
        self.insure_label = QLabel('Insure:', self)
        self.insure_textbox = QTextEdit('', self)
        self.insure_textbox.setReadOnly(True)
        queen_button_size = self.queenButton.sizeHint()
        self.insure_textbox.setFixedWidth(queen_button_size.width())
        self.insure_textbox.setFixedHeight(queen_button_size.height())

        self.dealers_card_label = QLabel('Dealers Face Card:', self)
        self.card_label = QTextEdit('', self)
        self.card_label.setReadOnly(True)
        
        
        self.card_label.setFixedWidth(queen_button_size.width())
        self.card_label.setFixedHeight(queen_button_size.height())
        
        card_info_layout.addWidget(self.insure_label)
        card_info_layout.addWidget(self.insure_textbox)
        card_info_layout.addWidget(self.dealers_card_label)
        card_info_layout.addWidget(self.card_label)
        layout.addLayout(card_info_layout)

        your_cards_layout = QVBoxLayout()
        
        # Place "Your Cards" label on the same row as the first two text boxes
        your_cards_row1_layout = QHBoxLayout()
        self.your_cards_label = QLabel('Your Cards:', self)
        self.your_cards_textbox1 = QTextEdit('', self)
        self.your_cards_textbox2 = QTextEdit('', self)
        your_cards_textboxes_row1 = [self.your_cards_textbox1, self.your_cards_textbox2]
        your_cards_row1_layout.addWidget(self.your_cards_label)
        for textbox in your_cards_textboxes_row1:
            textbox.setFixedWidth(self.queenButton.sizeHint().width())
            textbox.setFixedHeight(self.queenButton.sizeHint().height())
            your_cards_row1_layout.addWidget(textbox)
        your_cards_layout.addLayout(your_cards_row1_layout)

        # Add "Hit Cards" label and bottom three text boxes
        your_cards_row2_layout = QHBoxLayout()
        self.hit_cards_label = QLabel('Hit Cards:', self)
        self.your_cards_textbox3 = QTextEdit('', self)
        self.your_cards_textbox4 = QTextEdit('', self)
        self.your_cards_textbox5 = QTextEdit('', self)
        your_cards_textboxes_row2 = [self.your_cards_textbox3, self.your_cards_textbox4, self.your_cards_textbox5]
        your_cards_row2_layout.addWidget(self.hit_cards_label)
        for textbox in your_cards_textboxes_row2:
            textbox.setFixedWidth(self.queenButton.sizeHint().width())
            textbox.setFixedHeight(self.queenButton.sizeHint().height())
            your_cards_row2_layout.addWidget(textbox)
        your_cards_layout.addLayout(your_cards_row2_layout)

        layout.addLayout(your_cards_layout)

        strategy_and_total_layout = QHBoxLayout()
        
        self.strategy_label = QLabel('Strategy:', self)
        self.strategy_textbox = QTextEdit('', self)
        self.strategy_textbox.setFixedWidth(self.queenButton.sizeHint().width())
        self.strategy_textbox.setFixedHeight(self.queenButton.sizeHint().height())
        
        self.total_label = QLabel('Total:', self)
        self.total_box = QLineEdit('', self)
        self.total_box.setReadOnly(True)
        self.total_box.setFixedWidth(self.queenButton.sizeHint().width())
        self.total_box.setFixedHeight(self.queenButton.sizeHint().height())
        
        strategy_and_total_layout.addWidget(self.strategy_label)
        strategy_and_total_layout.addWidget(self.strategy_textbox)
        strategy_and_total_layout.addWidget(self.total_label)
        strategy_and_total_layout.addWidget(self.total_box)
        
        layout.addLayout(strategy_and_total_layout)

        self.refreshButton = QPushButton('Refresh', self)
        self.refreshButton.clicked.connect(self.refresh)
        layout.addWidget(self.refreshButton)

        self.refreshAllButton = QPushButton('Refresh All', self)
        self.refreshAllButton.clicked.connect(self.refresh_all)
        layout.addWidget(self.refreshAllButton)

        self.setLayout(layout)
        
    def add_one(self):
        self.original_value += 1
        self.value_box.setText(str(self.original_value))
        self.update_true_count()
        
    def add_one_to_top_value_box(self):
        current_value = int(self.top_value_box.text())
        self.top_value_box.setText(str(current_value + 1))
        self.update_true_count()
        
    def subtract_one(self):
        self.original_value -= 1
        self.value_box.setText(str(self.original_value))
        self.update_true_count()
        
    def update_new_value_box(self):
        total_decks = int(self.decks_combo.currentText())
        cards_dealt = int(self.top_value_box.text())
        new_value = 52 * total_decks - cards_dealt
        self.new_value_box.setText(str(new_value))
        decks_left = total_decks - cards_dealt / 52
        self.decks_left_box.setText(f"{decks_left:.2f}")
        self.update_true_count()
        
    def select_decks(self, index):
        self.update_new_value_box()

    def update_true_count(self):
        try:
            running_count = int(self.value_box.text())
            decks_left = float(self.decks_left_box.text())
            if decks_left > 0:
                true_count = running_count / decks_left
            else:
                true_count = 0
            self.true_count_box.setText(f"{true_count:.2f}")
        except ValueError:
            self.true_count_box.setText("0")
        self.update_bet_amount()

    def update_stake_required(self):
        try:
            min_bet = float(self.min_bet_box.text())
            stake_required = min_bet * 100
            self.stake_required_box.setText(f"{stake_required:.2f}")
        except ValueError:
            self.stake_required_box.setText("0")
        self.update_bet_amount()

    def update_bet_amount(self):
        try:
            min_bet = float(self.min_bet_box.text())
            true_count = float(self.true_count_box.text())
            bet_amount = (true_count - 1) * min_bet
            if bet_amount < min_bet:
                bet_amount = min_bet
            self.bet_amount_box.setText(f"{bet_amount:.2f}")
        except ValueError:
            self.bet_amount_box.setText("0")

    def refresh(self):
        self.card_label.clear()
        self.dealers_card_received = False
        self.current_textbox_index = 0
        self.text_boxes_full = False
        for i in range(1, 6):
            getattr(self, f"your_cards_textbox{i}").clear()
        self.strategy_textbox.clear()
        self.total_box.clear()
        self.insure_textbox.clear()

    def refresh_all(self):
        self.original_value = 0
        self.card_label.clear()
        self.dealers_card_received = False
        self.current_textbox_index = 0
        self.text_boxes_full = False
        for i in range(1, 6):
            getattr(self, f"your_cards_textbox{i}").clear()
        self.top_value_box.setText('0')
        self.new_value_box.setText('0')
        self.decks_left_box.setText('0')
        self.value_box.setText('0')
        self.true_count_box.setText('0')
        self.min_bet_box.clear()
        self.stake_required_box.setText('0')
        self.bet_amount_box.setText('0')
        self.strategy_textbox.clear()
        self.insure_textbox.clear()
        self.total_box.clear()
        self.decks_combo.setCurrentIndex(0)
        self.reset_buttons()

    def reset_buttons(self):
        self.addButton.setEnabled(True)
        self.sevenEightNineButton.setEnabled(True)
        self.subtractButton.setEnabled(True)
        for button in self.button_to_label.keys():
            button.setEnabled(True)

    def add_seven_eight_nine(self):
        pass
        
    def show_card(self):
        sender = self.sender()
        card_label_text = self.button_to_label[sender]
        if not self.dealers_card_received:
            self.card_label.setText(card_label_text)
            self.dealers_card_received = True
        else:
            if not self.text_boxes_full:
                text_boxes = [self.your_cards_textbox1, self.your_cards_textbox2, self.your_cards_textbox3, self.your_cards_textbox4, self.your_cards_textbox5]
                current_textbox = text_boxes[self.current_textbox_index]
                current_textbox.setText(card_label_text)
                self.current_textbox_index += 1
                if self.current_textbox_index >= len(text_boxes):
                    self.text_boxes_full = True

                self.check_conditions()
                self.update_total()

    def update_total(self):
        card_values = {
            '2': 2, '3': 3, '4': 4, '5': 5, '6': 6,
            '7': 7, '8': 8, '9': 9, '10': 10,
            'Jack': 10, 'Queen': 10, 'King': 10, 'Ace': 11
        }
        text_boxes = [
            self.your_cards_textbox1, self.your_cards_textbox2,
            self.your_cards_textbox3, self.your_cards_textbox4,
            self.your_cards_textbox5
        ]
        total = 0
        aces_count = 0
        
        for textbox in text_boxes:
            card = textbox.toPlainText()
            if card:
                value = card_values.get(card, 0)
                total += value
                if card == 'Ace':
                    aces_count += 1
        
        while total > 21 and aces_count:
            total -= 10
            aces_count -= 1

        self.total_box.setText(str(total))

    def check_conditions(self):
        dealer_card = self.card_label.toPlainText()
        text_boxes = [
            self.your_cards_textbox1, self.your_cards_textbox2,
            self.your_cards_textbox3, self.your_cards_textbox4,
            self.your_cards_textbox5
        ]
        card_values = {
            '2': 2, '3': 3, '4': 4, '5': 5, '6': 6,
            '7': 7, '8': 8, '9': 9, '10': 10,
            'Jack': 10, 'Queen': 10, 'King': 10, 'Ace': 11
        }
        true_count = float(self.true_count_box.text())
        
        # Calculate the total value and count Aces
        total_value = 0
        aces_count = 0
        your_cards = []
        for textbox in text_boxes:
            card = textbox.toPlainText()
            if card:
                value = card_values.get(card, 0)
                total_value += value
                if card == 'Ace':
                    aces_count += 1
                your_cards.append(card)

        #####################
        while total_value > 21 and aces_count > 0:
            total_value -= 10
            aces_count -= 1

        if dealer_card in ['2', '3', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace'] and aces_count >= 3 and total_value == 15:
            self.strategy_textbox.setText('HIT')
            return
        if dealer_card in ['2', '3', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace'] and aces_count >= 3 and total_value == 16:
            self.strategy_textbox.setText('HIT')
            return
        if dealer_card in ['4', '5', '6'] and aces_count >= 3 and total_value == 15:
            self.strategy_textbox.setText('DD/HIT')
            return
        if dealer_card in ['4', '5', '6'] and aces_count >= 3 and total_value == 16:
            self.strategy_textbox.setText('DD/HIT')
            return
        #####################

        # Check the insurance condition
        if dealer_card == 'Ace' and true_count > 3:
            self.insure_textbox.setText('Insure')
        else:
            self.insure_textbox.clear()

        # Check if your_card1 and your_card2 are both Aces
        your_card1 = self.your_cards_textbox1.toPlainText()
        your_card2 = self.your_cards_textbox2.toPlainText()

        if your_card1 == 'Ace' and your_card2 == 'Ace':
            self.strategy_textbox.setText('SPLIT')
            return
        #Standing on 10s but not effecting the split conditions
        if total_value == 20:
            split_conditions = [
                {'cards': ['Ace', 'Ace']},
                {'cards': ['King', 'King']},
                {'cards': ['Jack', 'Jack']},
                {'cards': ['Queen', 'Queen']},
                {'cards': ['10', '10']},
            # Add any other SPLIT conditions here
            ]
            can_split = False
            for condition in split_conditions:
                if set(condition['cards']) == set(your_cards[:2]):
                    if 'dealer_cards' in condition:
                        if dealer_card in condition['dealer_cards']:
                            can_split = True
                            break
                    else:
                        can_split = True
                        break

            if not can_split:
                self.strategy_textbox.setText('STAND')
                return
        ############# ALL SOFT TOTALS INCLUDING HIT CARDS##################
        
        if dealer_card in ['7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace'] and aces_count >= 1 and total_value - 11 == 11: #11 + 1 = 12
            self.strategy_textbox.setText('HIT')
            return
        if dealer_card in ['5', '6'] and aces_count >= 1 and not (your_card1 == '6' and your_card2 == '6') and total_value - 11 == 11:
            self.strategy_textbox.setText('STAND')
            return
        if dealer_card in ['4'] and aces_count >= 1 and not (your_card1 == '6' and your_card2 == '6') and total_value - 11 == 11:
            if true_count <= 0:
                self.strategy_textbox.setText('HIT')
        if dealer_card in ['4'] and aces_count >= 1 and not (your_card1 == '6' and your_card2 == '6') and total_value - 11 == 11:
            if true_count >= 0.01:
                self.strategy_textbox.setText('STAND')
                return
        if dealer_card in ['3'] and aces_count >= 1 and not (your_card1 == '6' and your_card2 == '6') and total_value - 11 == 11:
            if true_count >= 2:
                self.strategy_textbox.setText('STAND')
        if dealer_card in ['3'] and aces_count >= 1 and not (your_card1 == '6' and your_card2 == '6') and total_value - 11 == 11:
            if true_count <= 1.99:
                self.strategy_textbox.setText('HIT')
                return
        if dealer_card in ['2'] and aces_count >= 1 and not (your_card1 == '6' and your_card2 == '6') and total_value - 11 == 11:
            if true_count >= 3:
                self.strategy_textbox.setText('STAND')
        if dealer_card in ['2'] and aces_count >= 1 and not (your_card1 == '6' and your_card2 == '6') and total_value - 11 == 11: #11 + 1 = 12
            if true_count <= 2.99:
                self.strategy_textbox.setText('HIT')
                return

        if dealer_card in ['2', '3', '4', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace']:
            if aces_count >= 1 and total_value - 11 == 12:  # Ace (1) + 12 = 13
                self.strategy_textbox.setText('HIT')
                return
        if dealer_card in ['5', '6']:
            if aces_count >= 1 and total_value - 11 == 12:  # Ace (1) + 12 = 13
                self.strategy_textbox.setText('DD/HIT')
                return
        if dealer_card in ['2', '3', '4', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace']: 
            if aces_count >= 1 and total_value - 11 == 13:  # Ace (1) + 13 = 14
                self.strategy_textbox.setText('HIT')
                return
        if dealer_card in ['5', '6']:
            if aces_count >= 1 and total_value - 11 == 13:  # Ace (1) + 13 = 14
                self.strategy_textbox.setText('DD/HIT')
                return
        if dealer_card in ['2', '3', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace']: 
            if aces_count >= 1 and total_value - 11 == 14:  # Ace (1) + 14 = 15
                self.strategy_textbox.setText('HIT')
                return
        if dealer_card in ['4', '5', '6']:
            if aces_count >= 1 and total_value - 11 == 14:  # Ace (1) + 14 = 15
                self.strategy_textbox.setText('DD/HIT')
                return
        if dealer_card in ['2', '3', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace']: 
            if aces_count >= 1 and total_value - 11 == 15:  # Ace (1) + 15 = 16
                self.strategy_textbox.setText('HIT')
                return
        if dealer_card in ['4', '5', '6']:
            if aces_count >= 1 and total_value - 11 == 15:  # Ace (1) + 15 = 16
                self.strategy_textbox.setText('DD/HIT')
                return
        if dealer_card in ['7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace']: 
            if aces_count >= 1 and total_value - 11 == 16:  # Ace (1) + 16 = 17
                self.strategy_textbox.setText('HIT')
                return
        if dealer_card in ['3', '4', '5', '6']:
            if aces_count >= 1 and total_value - 11 == 16:  # Ace (1) + 16 = 17
                self.strategy_textbox.setText('DD/HIT')
                return
        if dealer_card in ['2'] and aces_count >= 1 and total_value - 11 == 16:  # Ace (1) + 16 = 17
            if true_count >= 1:
                self.strategy_textbox.setText('DD/HIT')
                return
        if dealer_card in ['2'] and aces_count >= 1 and total_value - 11 == 16:  # Ace (1) + 16 = 17
            if true_count <= 0.99:
                self.strategy_textbox.setText('HIT')
                return
        if dealer_card in ['9', '10', 'Jack', 'Queen', 'King', 'Ace']: 
            if aces_count >= 1 and total_value - 11 == 17:  # Ace (1) + 17 = 18
                self.strategy_textbox.setText('HIT')
                return
        if dealer_card in ['7', '8']: 
            if aces_count >= 1 and total_value - 11 == 17:  # Ace (1) + 17 = 18
                self.strategy_textbox.setText('STAND')
                return
        if dealer_card in ['2', '3', '4', '5', '6']: 
            if aces_count >= 1 and total_value - 11 == 17:  # Ace (1) + 17 = 18
                self.strategy_textbox.setText('DD/STAND')
                return
        if dealer_card in ['2', '3', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace']: 
            if aces_count >= 1 and total_value - 11 == 18:  # Ace (1) + 18 = 19
                self.strategy_textbox.setText('STAND')
                return
        if dealer_card in ['5', '6'] and aces_count >= 1 and total_value - 11 == 18:  # Ace (1) + 18 = 19
            if true_count >= 1:    
                self.strategy_textbox.setText('DD/STAND')
                return
        if dealer_card in ['5', '6'] and aces_count >= 1 and total_value - 11 == 18:  # Ace (1) + 18 = 19
            if true_count <= 0.99:    
                self.strategy_textbox.setText('STAND')
                return
        if dealer_card in ['4'] and aces_count >= 1 and total_value - 11 == 18:  # Ace (1) + 18 = 19
            if true_count >= 3:    
                self.strategy_textbox.setText('DD/STAND')
                return
        if dealer_card in ['4'] and aces_count >= 1 and total_value - 11 == 18:  # Ace (1) + 18 = 19
            if true_count <= 2.99:    
                self.strategy_textbox.setText('STAND')
                return
        if aces_count >= 1 and total_value - 11 == 19:  # Ace (1) + 19 = 20
            self.strategy_textbox.setText('STAND')
            return
        if aces_count >= 1 and total_value - 11 == 20:  # Ace (1) + 19 = 20
            self.strategy_textbox.setText('STAND')
            return
        # Check if one card is an Ace and the other cards add up to 9
        if aces_count >= 1 and total_value - 11 == 9:  # Ace (11) + 9 = 20
            self.strategy_textbox.setText('STAND')
            return
        # Check if one card is an Ace and the other cards add up to 8
        if dealer_card in ['2', '3', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace']:
            if aces_count >= 1 and total_value - 11 == 8:  # Ace (11) + 8 = 19
                self.strategy_textbox.setText('STAND')
                return
        if dealer_card in ['5', '6']:
            if aces_count >= 1 and total_value - 11 == 8:  # Ace (11) + 8 = 19
                if true_count >= 1:
                    self.strategy_textbox.setText('DD/STAND')
                    return
        if dealer_card in ['5', '6']:
            if aces_count >= 1 and total_value - 11 == 8:  # Ace (11) + 8 = 19
                if true_count <= 0.99:
                    self.strategy_textbox.setText('STAND')
                    return
        if dealer_card in ['4']:
            if aces_count >= 1 and total_value - 11 == 8:  # Ace (11) + 8 = 19
                if true_count >= 3:
                    self.strategy_textbox.setText('DD/STAND')
                    return
        if dealer_card in ['4']:
            if aces_count >= 1 and total_value - 11 == 8:  # Ace (11) + 8 = 19
                if true_count <= 2.99:
                    self.strategy_textbox.setText('STAND')
                    return
        # Check if one card is an Ace and the other cards add up to 7
        if dealer_card in ['2', '3', '4', '5', '6']:
            if aces_count >= 1 and total_value - 11 == 7:  # Ace (11) + 7 = 18
                self.strategy_textbox.setText('DD/STAND')
                return
        if dealer_card in ['7', '8']:
            if aces_count >= 1 and total_value - 11 == 7:  # Ace (11) + 7 = 19
                self.strategy_textbox.setText('STAND')
                return
        if dealer_card in ['9', '10', 'Jack', 'Queen', 'King', 'Ace']:
            if aces_count >= 1 and total_value - 11 == 7:  # Ace (11) + 7 = 19
                self.strategy_textbox.setText('HIT')
                return
        # Check if one card is an Ace and the other cards add up to 6
        if dealer_card in ['7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace']:
            if aces_count >= 1 and total_value - 11 == 6:  # Ace (11) + 6 = 18
                self.strategy_textbox.setText('HIT')
                return
        if dealer_card in ['3', '4', '5', '6']:
            if aces_count >= 1 and total_value - 11 == 6:  # Ace (11) + 6 = 18
                self.strategy_textbox.setText('DD/HIT')
                return
        if dealer_card in ['2']:
            if aces_count >= 1 and total_value - 11 == 6:  # Ace (11) + 8 = 19
                if true_count >= 1:
                    self.strategy_textbox.setText('DD/HIT')
                    return
        if dealer_card in ['2']:
            if aces_count >= 1 and total_value - 11 == 6:  # Ace (11) + 8 = 19
                if true_count <= 0.99:
                    self.strategy_textbox.setText('HIT')
                    return
        # Check if one card is an Ace and the other cards add up to 5
        if dealer_card in ['2', '3', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace']:
            if aces_count >= 1 and total_value - 11 == 5:  # Ace (11) + 6 = 18
                self.strategy_textbox.setText('HIT')
                return
        if dealer_card in ['4', '5', '6']:
            if aces_count >= 1 and total_value - 11 == 5:  # Ace (11) + 6 = 18
                self.strategy_textbox.setText('DD/HIT')
                return
        # Check if one card is an Ace and the other cards add up to 4
        if dealer_card in ['2', '3', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace']:
            if aces_count >= 1 and total_value - 11 == 4:  # Ace (11) + 4 = 18
                self.strategy_textbox.setText('HIT')
                return
        if dealer_card in ['4', '5', '6']:
            if aces_count >= 1 and total_value - 11 == 4:  # Ace (11) + 4 = 18
                self.strategy_textbox.setText('DD/HIT')
                return
        # Check if one card is an Ace and the other cards add up to 4
        if dealer_card in ['2', '3', '4', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace']:
            if aces_count >= 1 and total_value - 11 == 3:  # Ace (11) + 3 = 18
                self.strategy_textbox.setText('HIT')
                return
        if dealer_card in ['5', '6']:
            if aces_count >= 1 and total_value - 11 == 3:  # Ace (11) + 4 = 18
                self.strategy_textbox.setText('DD/HIT')
                return
        # Check if one card is an Ace and the other cards add up to 2
        if dealer_card in ['2', '3', '4', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace']:
            if aces_count >= 1 and total_value - 11 == 2:  # Ace (11) + 3 = 18
                self.strategy_textbox.setText('HIT')
                return
        if dealer_card in ['5', '6']:
            if aces_count >= 1 and total_value - 11 == 2:  # Ace (11) + 4 = 18
                self.strategy_textbox.setText('DD/HIT')
                return

        your_card1 = self.your_cards_textbox1.toPlainText()
        your_card2 = self.your_cards_textbox2.toPlainText()

        ##########ALL SPLITTING CONDITIONS####################
        # Check for SPLIT condition
        if your_card1 == 'Ace' and your_card2 == 'Ace':
            self.strategy_textbox.setText('SPLIT')
        # Check for STAND condition
        if dealer_card in ['2', '3', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace'] and \
            your_card1 in ['10', 'Jack', 'Queen', 'King'] and \
            your_card1 == your_card2:
            self.strategy_textbox.setText('STAND')
        # Check for SPLIT or STAND condition based on True Count for dealer card 4
        if dealer_card == '4' and \
             your_card1 in ['10', 'Jack', 'Queen', 'King'] and \
             your_card1 == your_card2:
            if true_count >= 6:
                self.strategy_textbox.setText('SPLIT')
        if dealer_card == '4' and \
             your_card1 in ['10', 'Jack', 'Queen', 'King'] and \
             your_card1 == your_card2:
            if true_count <= 5.99:
                self.strategy_textbox.setText('STAND')
        # Check for SPLIT or STAND condition based on True Count for dealer card 5
        if dealer_card == '5' and \
             your_card1 in ['10', 'Jack', 'Queen', 'King'] and \
             your_card1 == your_card2:
            if true_count >= 5:
                self.strategy_textbox.setText('SPLIT')
        if dealer_card == '5' and \
             your_card1 in ['10', 'Jack', 'Queen', 'King'] and \
             your_card1 == your_card2:
            if true_count <= 4.99:
                self.strategy_textbox.setText('STAND')
        # Check for SPLIT or STAND condition based on True Count for dealer card 6
        if dealer_card == '6' and \
             your_card1 in ['10', 'Jack', 'Queen', 'King'] and \
             your_card1 == your_card2:
            if true_count >= 4:
                self.strategy_textbox.setText('SPLIT')
        if dealer_card == '6' and \
             your_card1 in ['10', 'Jack', 'Queen', 'King'] and \
             your_card1 == your_card2:
            if true_count <= 3.99:
                self.strategy_textbox.setText('STAND')
        # Check for STAND condition splitting 9s
        if dealer_card in ['2', '3', '4', '5', '6', '8', '9'] and \
             your_card1 in ['9'] and \
             your_card1 == your_card2:
            self.strategy_textbox.setText('SPLIT')
        # Check for STAND condition splitting 9s
        if dealer_card in ['7', '10', 'Jack', 'Queen', 'King', 'Ace'] and \
             your_card1 in ['9'] and \
             your_card1 == your_card2:
            self.strategy_textbox.setText('STAND')
        # Check for STAND condition splitting 8s
        if your_card1 == '8' and your_card2 == '8':
            self.strategy_textbox.setText('SPLIT')
        # Check for STAND condition splitting 7s
        if dealer_card in ['2', '3', '4', '5', '6', '7'] and \
             your_card1 in ['7'] and \
             your_card1 == your_card2:
            self.strategy_textbox.setText('SPLIT')
        # Check for STAND condition splitting 7s
        if dealer_card in ['8', '9', '10', 'Jack', 'Queen', 'King', 'Ace'] and \
             your_card1 in ['7'] and \
             your_card1 == your_card2:
            self.strategy_textbox.setText('HIT')
        # Check for STAND condition splitting 6s
        if dealer_card in ['3', '4', '5', '6'] and \
             your_card1 in ['6'] and \
             your_card1 == your_card2:
            self.strategy_textbox.setText('SPLIT')
        # Check for STAND condition splitting 6s
        if dealer_card in ['7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace'] and \
             your_card1 in ['6'] and \
             your_card1 == your_card2:
            self.strategy_textbox.setText('HIT')
        # Check for DD after Split condition splitting 6s
        if dealer_card in ['2'] and \
             your_card1 in ['6'] and \
             your_card1 == your_card2:
            if true_count <= 2.99:
                self.strategy_textbox.setText('DAS/HIT')
        if dealer_card in ['2'] and \
             your_card1 in ['6'] and \
             your_card1 == your_card2:
            if true_count >= 3:
                self.strategy_textbox.setText('DAS/STAND')
        # Check for STAND condition splitting 5s
        if dealer_card in ['2', '3', '4', '5', '6', '7', '8', '9'] and \
             your_card1 in ['5'] and \
             your_card1 == your_card2:
            self.strategy_textbox.setText('DD/HIT')
        # Check for DD/STAND or HIT condition based on True Count for dealer card 10, Jack, Queen, King
        if dealer_card in ['10', 'Jack', 'Queen', 'King', 'Ace'] and \
             your_card1 == '5' and your_card2 == '5':
            if true_count >= 4:
                self.strategy_textbox.setText('DD/HIT')
        if dealer_card in ['10', 'Jack', 'Queen', 'King', 'Ace'] and \
             your_card1 == '5' and your_card2 == '5':
            if true_count <= 3.99:
                self.strategy_textbox.setText('HIT')
        # Check for STAND condition splitting 4s
        if dealer_card in ['2', '3', '4', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace'] and \
             your_card1 in ['4'] and \
             your_card1 == your_card2:
            self.strategy_textbox.setText('HIT')
        # Check for STAND condition splitting 4s
        if dealer_card in ['5'] and \
             your_card1 in ['4'] and \
             your_card1 == your_card2:
            self.strategy_textbox.setText('DAS/HIT')
        # Check for DD/STAND or HIT condition based on True Count for dealer card 6
        if dealer_card in ['6'] and \
             your_card1 == '4' and your_card2 == '4':
            if true_count >= 2:
                self.strategy_textbox.setText('DAS/DD')
        if dealer_card in ['6'] and \
             your_card1 == '4' and your_card2 == '4':
            if true_count <= 1.99:
                self.strategy_textbox.setText('DAS/HIT')
       
        # Check for STAND condition splitting 3s
        if dealer_card in ['4', '5', '6', '7'] and \
             your_card1 in ['2','3'] and \
             your_card1 == your_card2:
            self.strategy_textbox.setText('SPLIT')
        # Check for STAND condition splitting 4s
        if dealer_card in ['8', '9', '10', 'Jack', 'Queen', 'King', 'Ace'] and \
             your_card1 in ['2','3'] and \
             your_card1 == your_card2:
            self.strategy_textbox.setText('HIT')
        # Check for STAND condition splitting 3s
        if dealer_card in ['2', '3'] and \
             your_card1 in ['2','3'] and \
             your_card1 == your_card2:
            self.strategy_textbox.setText('DAS/HIT')

        ############### ALL SOFT CONDITIONS ####################
        # Check for STAND condition when one card is Ace and the other is 9
        if (your_card1 == 'Ace' and your_card2 == '9') or (your_card1 == '9' and your_card2 == 'Ace'):
            self.strategy_textbox.setText('STAND')
        # Check for STAND condition when dealer's card is 2, 3, 7, 8, 9, 10, Jack, Queen, King, and one card is Ace and the other is 8
        if dealer_card in ['2', '3', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace'] and \
             ((your_card1 == 'Ace' and your_card2 == '8') or (your_card1 == '8' and your_card2 == 'Ace')):
            self.strategy_textbox.setText('STAND')
        # Check for STAND condition when dealer's card is 5, 6, and one card is Ace and the other is 8
        if dealer_card in ['5', '6'] and \
             ((your_card1 == 'Ace' and your_card2 == '8') or (your_card1 == '8' and your_card2 == 'Ace')):
            if true_count >= 1:
                self.strategy_textbox.setText('DD/STAND')
        if dealer_card in ['5', '6'] and \
             ((your_card1 == 'Ace' and your_card2 == '8') or (your_card1 == '8' and your_card2 == 'Ace')):
            if true_count <= 0.99:
                self.strategy_textbox.setText('STAND')
        # Check for STAND condition when dealer's card is 4, and one card is Ace and the other is 8
        if dealer_card in ['4'] and \
             ((your_card1 == 'Ace' and your_card2 == '8') or (your_card1 == '8' and your_card2 == 'Ace')):
            if true_count >= 3:
                self.strategy_textbox.setText('DD/STAND')
        if dealer_card in ['4'] and \
             ((your_card1 == 'Ace' and your_card2 == '8') or (your_card1 == '8' and your_card2 == 'Ace')):
            if true_count <= 2.99:
                self.strategy_textbox.setText('STAND')
        # Check for STAND condition when dealer's card is 5, 6, and one card is Ace and the other is 8
        if dealer_card in ['2', '3', '4', '5', '6'] and \
             ((your_card1 == 'Ace' and your_card2 == '7') or (your_card1 == '7' and your_card2 == 'Ace')):
            self.strategy_textbox.setText('DD/STAND')
        # Check for STAND condition when dealer's card is 7, 8, and one card is Ace and the other is 8
        if dealer_card in ['7', '8'] and \
             ((your_card1 == 'Ace' and your_card2 == '7') or (your_card1 == '7' and your_card2 == 'Ace')):
            self.strategy_textbox.setText('STAND')
        # Check for STAND condition when dealer's card is 7, 8, and one card is Ace and the other is 8
        if dealer_card in ['9', '10', 'Jack', 'Queen', 'King', 'Ace'] and \
             ((your_card1 == 'Ace' and your_card2 == '7') or (your_card1 == '7' and your_card2 == 'Ace')):
            self.strategy_textbox.setText('HIT')
        # Check for STAND condition when dealer's card is 7, 8, and one card is Ace and the other is 8
        if dealer_card in ['7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace'] and \
             ((your_card1 == 'Ace' and your_card2 == '6') or (your_card1 == '6' and your_card2 == 'Ace')):
            self.strategy_textbox.setText('HIT')
        # Check for STAND condition when dealer's card is 7, 8, and one card is Ace and the other is 8
        if dealer_card in ['3', '4', '5', '6'] and \
             ((your_card1 == 'Ace' and your_card2 == '6') or (your_card1 == '6' and your_card2 == 'Ace')):
            self.strategy_textbox.setText('DD/HIT')
        # Check for STAND condition when dealer's card is 2, and one card is Ace and the other is 8
        if dealer_card in ['2'] and \
             ((your_card1 == 'Ace' and your_card2 == '6') or (your_card1 == '6' and your_card2 == 'Ace')):
            if true_count >= 1:
                self.strategy_textbox.setText('DD/HIT')
                return
        if dealer_card in ['2'] and \
             ((your_card1 == 'Ace' and your_card2 == '6') or (your_card1 == '6' and your_card2 == 'Ace')):
            if true_count <= 0.99:
                self.strategy_textbox.setText('HIT')
                return
        # Check for STAND condition when dealer's card is 7, 8, and one card is Ace and the other is 8
        if dealer_card in ['2', '3', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace'] and \
             ((your_card1 == 'Ace' and your_card2 == '5') or (your_card1 == '5' and your_card2 == 'Ace')):
            self.strategy_textbox.setText('HIT')
        # Check for STAND condition when dealer's card is 7, 8, and one card is Ace and the other is 8
        if dealer_card in ['4', '5', '6'] and \
             ((your_card1 == 'Ace' and your_card2 == '5') or (your_card1 == '5' and your_card2 == 'Ace')):
            self.strategy_textbox.setText('DD/HIT')
        # Check for STAND condition when dealer's card is 7, 8, and one card is Ace and the other is 8
        if dealer_card in ['2', '3', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace'] and \
             ((your_card1 == 'Ace' and your_card2 == '4') or (your_card1 == '4' and your_card2 == 'Ace')):
            self.strategy_textbox.setText('HIT')
        # Check for STAND condition when dealer's card is 7, 8, and one card is Ace and the other is 8
        if dealer_card in ['4', '5', '6'] and \
             ((your_card1 == 'Ace' and your_card2 == '4') or (your_card1 == '4' and your_card2 == 'Ace')):
            self.strategy_textbox.setText('DD/HIT')
        # Check for STAND condition when dealer's card is 7, 8, and one card is Ace and the other is 8
        if dealer_card in ['2', '3', '4', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace'] and \
             ((your_card1 == 'Ace' and your_card2 == '3') or (your_card1 == '3' and your_card2 == 'Ace')):
            self.strategy_textbox.setText('HIT')
        if dealer_card in ['5', '6'] and \
             ((your_card1 == 'Ace' and your_card2 == '3') or (your_card1 == '3' and your_card2 == 'Ace')):
            self.strategy_textbox.setText('DD/HIT')
        # Check for STAND condition when dealer's card is 7, 8, and one card is Ace and the other is 8
        if dealer_card in ['2', '3', '4', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace'] and \
             ((your_card1 == 'Ace' and your_card2 == '2') or (your_card1 == '2' and your_card2 == 'Ace')):
            self.strategy_textbox.setText('HIT')
        if dealer_card in ['5', '6'] and \
             ((your_card1 == 'Ace' and your_card2 == '2') or (your_card1 == '2' and your_card2 == 'Ace')):
            self.strategy_textbox.setText('DD/HIT')

        ############## ALL HARD CONDITIONS ###################
        
        if total_value >= 21:
            self.strategy_textbox.setText('STAND')
            return
        if total_value == 7 and aces_count == 0:
            self.strategy_textbox.setText('HIT')
            return
        if total_value == 5 and aces_count == 0:
            self.strategy_textbox.setText('HIT')
            return
        if total_value == 6 and aces_count == 0 and not (your_card1 == '3' and your_card2 == '3'):
            self.strategy_textbox.setText('HIT')
            return
        if dealer_card in ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace'] and aces_count == 0 and not (your_card1 == '9' and your_card2 == '9') and total_value == 18:
            self.strategy_textbox.setText('STAND')
            return
        if dealer_card in ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace'] and aces_count == 0 and total_value == 17:
            self.strategy_textbox.setText('STAND')
            return
        if dealer_card in ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace'] and aces_count == 0 and total_value == 19:
            self.strategy_textbox.setText('STAND')
            return

        # Check if the "Dealer's Card" value box is "2", "3", "4", "5", or "6", 
        # and the "Your Cards" text boxes do not hold an "Ace",
        # and your_card1 and your_card2 do not both hold an 8, and the "Total" value box shows 16
        if dealer_card in ['2', '3', '4', '5', '6'] and aces_count == 0 and not (your_card1 == '8' and your_card2 == '8') and total_value == 16:
            self.strategy_textbox.setText('STAND')
            return
        if dealer_card in ['7'] and aces_count == 0 and not (your_card1 == '8' and your_card2 == '8') and total_value == 16:	
            self.strategy_textbox.setText('HIT')
            return
        if dealer_card in ['8'] and aces_count == 0 and not (your_card1 == '8' and your_card2 == '8') and total_value == 16:
            if true_count >= 4:	
            	self.strategy_textbox.setText('HIT/Surr')
            	return
        if dealer_card in ['8'] and aces_count == 0 and not (your_card1 == '8' and your_card2 == '8') and total_value == 16:
            if true_count <= 3.99:	
            	self.strategy_textbox.setText('HIT')
            	return
        if dealer_card in ['9'] and aces_count == 0 and not (your_card1 == '8' and your_card2 == '8') and total_value == 16:
            if true_count >= 4:
                self.strategy_textbox.setText('STAND/Surr')
        if dealer_card in ['9'] and aces_count == 0 and not (your_card1 == '8' and your_card2 == '8') and total_value == 16:
            if true_count <= -1:
                self.strategy_textbox.setText('HIT')
        if dealer_card in ['9'] and aces_count == 0 and not (your_card1 == '8' and your_card2 == '8') and total_value == 16:
            if (true_count >= -1.01 and true_count <= 3.99) :
                self.strategy_textbox.setText('HIT/Surr')
        if dealer_card in ['10', 'Jack', 'Queen', 'King'] and aces_count == 0 and not (your_card1 == '8' and your_card2 == '8') and total_value == 16:
            if true_count >= 0:
                self.strategy_textbox.setText('STAND/Surr')
        if dealer_card in ['10', 'Jack', 'Queen', 'King'] and aces_count == 0 and not (your_card1 == '8' and your_card2 == '8') and total_value == 16:
            if true_count <= -0.01:
                self.strategy_textbox.setText('HIT/Surr')
        ## SURENDER/INSURE ##
        if dealer_card == 'Ace' and aces_count == 0 and not (your_card1 == '8' and your_card2 == '8') and total_value == 16:
                self.strategy_textbox.setText('HIT/Surr')
        if dealer_card == 'Ace' and aces_count == 0 and not (your_card1 == '8' and your_card2 == '8') and total_value == 16:
        	if true_count >= 3:
            		self.strategy_textbox.setText('HIT/Surr')
        # Check if the "Dealer's Card" value box is "2", "3", "4", "5", or "6", 
        # and the "Your Cards" text boxes do not hold an "Ace",
        # and your_card1 and your_card2 do not both hold an 8, and the "Total" value box shows 15
        if dealer_card in ['2', '3', '4', '5', '6'] and aces_count == 0 and total_value == 15:
            self.strategy_textbox.setText('STAND')
            return
        if dealer_card in ['7', '8'] and aces_count == 0 and total_value == 15:
            self.strategy_textbox.setText('HIT')
            return
        if dealer_card in ['10', 'Jack', 'Queen', 'King'] and aces_count == 0 and total_value == 15:
            if true_count >= 4:
                self.strategy_textbox.setText('STAND/Surr')
                return
       	if dealer_card in ['10', 'Jack', 'Queen', 'King'] and aces_count == 0 and total_value == 15:
            if true_count <= -0.01:
                self.strategy_textbox.setText('HIT')
                return
        if dealer_card in ['10', 'Jack', 'Queen', 'King'] and aces_count == 0 and total_value == 15:
            if (true_count <= 3.99 and true_count >= 0) :
                self.strategy_textbox.setText('HIT/Surr')
        if dealer_card in ['9', 'Ace'] and aces_count == 0 and total_value == 15:
            if true_count >= 2:
            	self.strategy_textbox.setText('HIT/Surr')
            	return
        if dealer_card in ['9', 'Ace'] and aces_count == 0 and total_value == 15:
            if true_count <= 1.99:
            	self.strategy_textbox.setText('HIT')
            	return

        # Check if the "Dealer's Card" value box is "2", "3", "4", "5", or "6", 
        # and the "Your Cards" text boxes do not hold an "Ace",
        # and your_card1 and your_card2 do not both hold an 8, and the "Total" value box shows 14
        if dealer_card in ['2', '3', '4', '5', '6'] and aces_count == 0 and not (your_card1 == '7' and your_card2 == '7') and total_value == 14:
            self.strategy_textbox.setText('STAND')
            return
        if dealer_card in ['7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace'] and aces_count == 0 and not (your_card1 == '7' and your_card2 == '7') and total_value == 14:
            self.strategy_textbox.setText('HIT')
            return
        # Check if the "Dealer's Card" value box is "2", "3", "4", "5", or "6", 
        # and the "Your Cards" text boxes do not hold an "Ace",
        # and your_card1 and your_card2 do not both hold an 8, and the "Total" value box shows 14
        if dealer_card in ['3', '4', '5', '6'] and aces_count == 0 and total_value == 13:
            self.strategy_textbox.setText('STAND')
            return
        if dealer_card in ['7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace'] and aces_count == 0 and total_value == 13:
            self.strategy_textbox.setText('HIT')
            return
        if dealer_card in ['2'] and aces_count == 0 and total_value == 13:
            if true_count <= -1:
                self.strategy_textbox.setText('HIT')
        if dealer_card in ['2'] and aces_count == 0 and total_value == 13:
            if true_count >= -0.99:
                self.strategy_textbox.setText('STAND')
                return
        # Check if the "Dealer's Card" value box is "2", "3", "4", "5", or "6", 
        # and the "Your Cards" text boxes do not hold an "Ace",
        # and your_card1 and your_card2 do not both hold an 8, and the "Total" value box shows 12
        if dealer_card in ['7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace'] and aces_count == 0 and not (your_card1 == '6' and your_card2 == '6') and total_value == 12:
            self.strategy_textbox.setText('HIT')
            return
        if dealer_card in ['5', '6'] and aces_count == 0 and not (your_card1 == '6' and your_card2 == '6') and total_value == 12:
            self.strategy_textbox.setText('STAND')
            return
        if dealer_card in ['4'] and aces_count == 0 and not (your_card1 == '6' and your_card2 == '6') and total_value == 12:
            if true_count <= 0:
                self.strategy_textbox.setText('HIT')
        if dealer_card in ['4'] and aces_count == 0 and not (your_card1 == '6' and your_card2 == '6') and total_value == 12:
            if true_count >= 0.01:
                self.strategy_textbox.setText('STAND')
                return
        if dealer_card in ['3'] and aces_count == 0 and not (your_card1 == '6' and your_card2 == '6') and total_value == 12:
            if true_count >= 2:
                self.strategy_textbox.setText('STAND')
        if dealer_card in ['3'] and aces_count == 0 and not (your_card1 == '6' and your_card2 == '6') and total_value == 12:
            if true_count <= 1.99:
                self.strategy_textbox.setText('HIT')
                return
        if dealer_card in ['2'] and aces_count == 0 and not (your_card1 == '6' and your_card2 == '6') and total_value == 12:
            if true_count >= 3:
                self.strategy_textbox.setText('STAND')
        if dealer_card in ['2'] and aces_count == 0 and not (your_card1 == '6' and your_card2 == '6') and total_value == 12:
            if true_count <= 2.99:
                self.strategy_textbox.setText('HIT')
                return
        #Check if the "Dealer's Card" value box is "2", "3", "4", "5", or "6", 
        # and the "Your Cards" text boxes do not hold an "Ace",
        # and your_card1 and your_card2 do not both hold an 8, and the "Total" value box shows 12
        if dealer_card in ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King'] and aces_count == 0 and total_value == 11:
            self.strategy_textbox.setText('DD/HIT')
            return
        if dealer_card in ['Ace'] and aces_count == 0 and total_value == 11:
            if true_count >= 1:
                self.strategy_textbox.setText('DD/HIT')
        if dealer_card in ['Ace'] and aces_count == 0 and total_value == 11:
            if true_count <= 0.99:
                self.strategy_textbox.setText('HIT')
                return
        #Check if the "Dealer's Card" value box is "2", "3", "4", "5", or "6", 
        # and the "Your Cards" text boxes do not hold an "Ace",
        # and your_card1 and your_card2 do not both hold an 8, and the "Total" value box shows 12
        if dealer_card in ['2', '3', '4', '5', '6', '7', '8', '9'] and aces_count == 0 and not (your_card1 == '5' and your_card2 == '5') and total_value == 10:
            self.strategy_textbox.setText('DD/HIT')
            return
        if dealer_card in ['10', 'Jack', 'Queen', 'King', 'Ace'] and aces_count == 0 and not (your_card1 == '5' and your_card2 == '5') and total_value == 10:
            if true_count >= 4:
                self.strategy_textbox.setText('DD/HIT')
        if dealer_card in ['10', 'Jack', 'Queen', 'King', 'Ace'] and aces_count == 0 and not (your_card1 == '5' and your_card2 == '5') and total_value == 10:
            if true_count <= 3.99:
                self.strategy_textbox.setText('HIT')
            return
        #Check if the "Dealer's Card" value box is "2", "3", "4", "5", or "6", 
        # and the "Your Cards" text boxes do not hold an "Ace",
        # and your_card1 and your_card2 do not both hold an 8, and the "Total" value box shows 12
        if dealer_card in ['8', '9', '10', 'Jack', 'Queen', 'King', 'Ace'] and aces_count == 0 and total_value == 9:
            self.strategy_textbox.setText('HIT')
            return
        if dealer_card in ['3', '4', '5', '6'] and aces_count == 0 and total_value == 9:
            self.strategy_textbox.setText('DD/HIT')
            return
        if dealer_card in ['7'] and aces_count == 0 and total_value == 9:
            if true_count >= 3:
                self.strategy_textbox.setText('DD/HIT')
        if dealer_card in ['7'] and aces_count == 0 and total_value == 9:
            if true_count <= 2.99:
                self.strategy_textbox.setText('HIT')
                return
        if dealer_card in ['2'] and aces_count == 0 and total_value == 9:
            if true_count >= 1:
                self.strategy_textbox.setText('DD/HIT')
        if dealer_card in ['2'] and aces_count == 0 and total_value == 9:
            if true_count <= 0.99:
                self.strategy_textbox.setText('HIT')
                return
        #Check if the "Dealer's Card" value box is "2", "3", "4", "5", or "6", 
        # and the "Your Cards" text boxes do not hold an "Ace",
        # and your_card1 and your_card2 do not both hold an 8, and the "Total" value box shows 12
        if dealer_card in ['2', '3', '4', '5', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace'] and aces_count == 0 and not (your_card1 == '4' and your_card2 == '4') and total_value == 8:
            self.strategy_textbox.setText('HIT')
            return
        if dealer_card in ['6'] and aces_count == 0 and not (your_card1 == '4' and your_card2 == '4') and total_value == 8:
            if true_count >= 2:
                self.strategy_textbox.setText('DD/HIT')
                return
        if dealer_card in ['6'] and aces_count == 0 and not (your_card1 == '4' and your_card2 == '4') and total_value == 8:
            if true_count <= 1.99:
                self.strategy_textbox.setText('HIT')
                return

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec())