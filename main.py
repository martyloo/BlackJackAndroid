from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp, sp, Metrics
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.utils import platform


# Use a 360x800 preview window only on desktop.
# On Android, do NOT force Window.size — Android must provide the full device screen.
if platform != "android":
    Window.size = (360, 800)




def light_haptic_feedback(*args):
    """Android vibration pulse for button presses using VibratorManager on Android 12+."""
    if platform != "android":
        return
    try:
        from jnius import autoclass

        PythonActivity = autoclass("org.kivy.android.PythonActivity")
        Context = autoclass("android.content.Context")
        Build_VERSION = autoclass("android.os.Build$VERSION")
        VibrationEffect = autoclass("android.os.VibrationEffect")

        activity = PythonActivity.mActivity

        if Build_VERSION.SDK_INT >= 31:
            vibrator_manager = activity.getSystemService(Context.VIBRATOR_MANAGER_SERVICE)
            vibrator = vibrator_manager.getDefaultVibrator()
        else:
            vibrator = activity.getSystemService(Context.VIBRATOR_SERVICE)

        if vibrator is None or not vibrator.hasVibrator():
            print("HAPTIC: no vibrator available")
            return

        if Build_VERSION.SDK_INT >= 26:
            effect = VibrationEffect.createOneShot(
                90,
                VibrationEffect.DEFAULT_AMPLITUDE
            )
            vibrator.vibrate(effect)
        else:
            vibrator.vibrate(90)

        print("HAPTIC: vibration requested")
    except Exception as exc:
        print("HAPTIC ERROR:", exc)

def enable_haptics_for_buttons(root):
    """Attach subtle haptic feedback to every Kivy Button in the widget tree."""
    try:
        from kivy.uix.button import Button
        widgets = [root]
        while widgets:
            widget = widgets.pop()
            if isinstance(widget, Button):
                widget.bind(on_press=light_haptic_feedback)
            widgets.extend(getattr(widget, "children", []))
    except Exception:
        pass




def attach_button_feedback(button):
    """Make every button visibly and physically react to a tap."""
    normal = tuple(button.background_color)
    pressed = (0.46, 0.62, 0.78, 1)

    def _restore(_dt):
        button.background_color = normal

    def _press(*_args):
        # Immediate strong visual feedback.
        button.background_color = pressed
        # Restore after a minimum visible interval so very quick taps still flash.
        Clock.schedule_once(_restore, 0.12)
        light_haptic_feedback()

    button.bind(on_press=_press)

class TextBox:
    """Small compatibility wrapper so the original Qt logic stays unchanged."""

    def __init__(self, value='', readonly=True, multiline=False, input_filter=None, font_size='13sp'):
        # Keep the 360dp design exactly as tested, but automatically reduce
        # text on narrower Android devices so changing values never clip.
        if isinstance(font_size, str) and font_size.endswith('sp'):
            self.base_font_sp = float(font_size[:-2])
        else:
            self.base_font_sp = float(font_size)

        self.widget = TextInput(
            text=str(value),
            readonly=readonly,
            multiline=multiline,
            input_filter=input_filter,
            font_size=sp(self.base_font_sp),
            padding=[dp(5), dp(6)],
            background_normal='',
            background_active='',
            background_color=(0.13, 0.15, 0.18, 1),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(1, 1, 1, 1),
        )
        Window.bind(size=self._update_responsive_font)
        self._update_responsive_font()

    def _update_responsive_font(self, *_args):
        density = Metrics.density or 1.0
        logical_width_dp = Window.width / density
        # 360dp and wider: original size. Below 360dp: scale down smoothly.
        # Never go below 72% so values remain comfortably readable.
        scale = min(1.0, max(0.72, logical_width_dp / 360.0))
        self.widget.font_size = sp(self.base_font_sp * scale)

    def text(self):
        return self.widget.text

    def setText(self, value):
        self.widget.text = str(value)

    def toPlainText(self):
        return self.widget.text

    def clear(self):
        self.widget.text = ''

    def setReadOnly(self, value):
        self.widget.readonly = bool(value)

    def on_change(self, callback):
        self.widget.bind(text=lambda _widget, _value: callback())


class ButtonBox:
    def __init__(self, text):
        self.widget = Button(
            text=text,
            font_size='14sp',
            background_normal='',
            background_down='',
            background_color=(0.20, 0.24, 0.30, 1),
            color=(1, 1, 1, 1),
        )
        attach_button_feedback(self.widget)

    def setEnabled(self, enabled):
        self.widget.disabled = not enabled


class ComboBox:
    def __init__(self, values):
        self.values = [str(value) for value in values]
        self.widget = Spinner(
            text=self.values[0],
            values=self.values,
            font_size='14sp',
            background_normal='',
            background_color=(0.20, 0.24, 0.30, 1),
        )
        self._callback = None
        self.widget.bind(text=self._changed)

    def _changed(self, _widget, value):
        if self._callback:
            self._callback(self.values.index(value))

    def currentText(self):
        return self.widget.text

    def currentIndexChanged_connect(self, callback):
        self._callback = callback

    def setCurrentIndex(self, index):
        self.widget.text = self.values[index]


class MyWidget(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', spacing=dp(5), padding=dp(7), **kwargs)
        self.original_value = 0
        self.dealers_card_received = False
        self.current_textbox_index = 0
        self.text_boxes_full = False
        self._sender_button = None
        self.initUI()

    @staticmethod
    def _label(text, size='12sp'):
        return Label(text=text, font_size=size, color=(0.9, 0.92, 0.95, 1), halign='left', valign='middle')

    def _field_pair(self, parent, label, box):
        holder = BoxLayout(orientation='vertical', spacing=dp(1))
        holder.add_widget(self._label(label, '11sp'))
        holder.add_widget(box.widget)
        parent.add_widget(holder)

    def initUI(self):
        title = Label(
            text='BLACKJACK CALCULATOR',
            size_hint_y=None,
            height=dp(30),
            font_size='18sp',
            bold=True,
            color=(1, 1, 1, 1),
        )
        self.add_widget(title)

        self.top_value_box = TextBox('0', font_size='11sp')
        self.new_value_box = TextBox('0', font_size='11sp')
        self.decks_left_box = TextBox('0', font_size='11sp')
        self.value_box = TextBox('0', font_size='11sp')
        self.true_count_box = TextBox('0', font_size='11sp')
        self.decks_combo = ComboBox(['1', '2', '3', '4', '5', '6', '7', '8'])
        self.decks_combo.currentIndexChanged_connect(self.select_decks)
        self.top_value_box.on_change(self.update_new_value_box)

        metrics = GridLayout(cols=3, spacing=dp(4), size_hint_y=None, height=dp(108))
        self._field_pair(metrics, 'Cards dealt', self.top_value_box)
        self._field_pair(metrics, 'Cards left', self.new_value_box)
        self._field_pair(metrics, 'Decks left', self.decks_left_box)
        self._field_pair(metrics, 'Running count', self.value_box)
        self._field_pair(metrics, 'True count', self.true_count_box)
        deck_holder = BoxLayout(orientation='vertical', spacing=dp(1))
        deck_holder.add_widget(self._label('No. of decks', '11sp'))
        deck_holder.add_widget(self.decks_combo.widget)
        metrics.add_widget(deck_holder)
        self.add_widget(metrics)

        self.addButton = ButtonBox('2, 3, 4, 5, 6   (+1)')
        self.sevenEightNineButton = ButtonBox('7, 8, 9   (0)')
        self.subtractButton = ButtonBox('10, J, Q, K, A   (-1)')
        for wrapper in (self.addButton, self.sevenEightNineButton, self.subtractButton):
            wrapper.widget.size_hint_y = None
            wrapper.widget.height = dp(38)
            self.add_widget(wrapper.widget)
        self.addButton.widget.bind(on_release=lambda *_: (self.add_one(), self.add_one_to_top_value_box()))
        self.sevenEightNineButton.widget.bind(on_release=lambda *_: (self.add_seven_eight_nine(), self.add_one_to_top_value_box()))
        self.subtractButton.widget.bind(on_release=lambda *_: (self.subtract_one(), self.add_one_to_top_value_box()))

        self.min_bet_box = TextBox('', readonly=False, input_filter='float', font_size='11sp')
        self.stake_required_box = TextBox('0', font_size='11sp')
        self.bet_amount_box = TextBox('0', font_size='11sp')
        self.min_bet_box.on_change(self.update_stake_required)
        bets = GridLayout(cols=3, spacing=dp(4), size_hint_y=None, height=dp(54))
        self._field_pair(bets, 'Minimum bet', self.min_bet_box)
        self._field_pair(bets, 'Stake', self.stake_required_box)
        self._field_pair(bets, 'Suggested bet', self.bet_amount_box)
        self.add_widget(bets)

        card_names = ['Ace', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King']
        card_grid = GridLayout(cols=4, spacing=dp(4), size_hint_y=None, height=dp(150))
        wrappers = {}
        for name in card_names:
            wrapper = ButtonBox(name)
            wrappers[name] = wrapper
            wrapper.widget.bind(on_release=lambda _button, w=wrapper: self._card_pressed(w))
            card_grid.add_widget(wrapper.widget)
        blank = Label(text='')
        card_grid.add_widget(blank)
        card_grid.add_widget(Label(text=''))
        card_grid.add_widget(Label(text=''))
        self.add_widget(card_grid)

        self.aceButton = wrappers['Ace']
        self.twoButton = wrappers['2']
        self.threeButton = wrappers['3']
        self.fourButton = wrappers['4']
        self.fiveButton = wrappers['5']
        self.sixButton = wrappers['6']
        self.sevenButton = wrappers['7']
        self.eightButton = wrappers['8']
        self.nineButton = wrappers['9']
        self.tenButton = wrappers['10']
        self.jackButton = wrappers['Jack']
        self.queenButton = wrappers['Queen']
        self.kingButton = wrappers['King']
        self.button_to_label = {wrapper: name for name, wrapper in wrappers.items()}

        self.insure_textbox = TextBox('')
        self.card_label = TextBox('')
        dealer_row = GridLayout(cols=2, spacing=dp(4), size_hint_y=None, height=dp(53))
        self._field_pair(dealer_row, 'Insurance', self.insure_textbox)
        self._field_pair(dealer_row, "Dealer's card", self.card_label)
        self.add_widget(dealer_row)

        self.your_cards_textbox1 = TextBox('')
        self.your_cards_textbox2 = TextBox('')
        self.your_cards_textbox3 = TextBox('')
        self.your_cards_textbox4 = TextBox('')
        self.your_cards_textbox5 = TextBox('')
        cards_row = GridLayout(cols=5, spacing=dp(3), size_hint_y=None, height=dp(50))
        for index, box in enumerate([
            self.your_cards_textbox1, self.your_cards_textbox2,
            self.your_cards_textbox3, self.your_cards_textbox4,
            self.your_cards_textbox5,
        ], start=1):
            self._field_pair(cards_row, str(index), box)
        self.add_widget(cards_row)

        self.strategy_textbox = TextBox('')
        self.total_box = TextBox('', font_size='12sp')
        result_row = GridLayout(cols=2, spacing=dp(4), size_hint_y=None, height=dp(55))
        self._field_pair(result_row, 'Strategy', self.strategy_textbox)
        self._field_pair(result_row, 'Total', self.total_box)
        self.add_widget(result_row)

        self.refreshButton = ButtonBox('NEW HAND')
        self.refreshAllButton = ButtonBox('RESET ALL')
        refresh_row = GridLayout(cols=2, spacing=dp(5), size_hint_y=None, height=dp(42))
        refresh_row.add_widget(self.refreshButton.widget)
        refresh_row.add_widget(self.refreshAllButton.widget)
        self.refreshButton.widget.bind(on_release=lambda *_: self.refresh())
        self.refreshAllButton.widget.bind(on_release=lambda *_: self.refresh_all())
        self.add_widget(refresh_row)

        self.update_new_value_box()

    def _card_pressed(self, wrapper):
        self._sender_button = wrapper
        self.show_card()

    def sender(self):
        return self._sender_button

    def add_one(self):
        self.original_value += 1
        self.value_box.setText(str(self.original_value))
        self.update_true_count()
        
    def add_one_to_top_value_box(self):
        current_value = int(self.top_value_box.text())
        self.top_value_box.setText(str(current_value + 1))
        # top_value_box is bound to update_new_value_box(), which refreshes
        # Cards Left, Decks Left and then the True Count.
        
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


class BlackjackApp(App):
    title = 'Blackjack Calculator'

    def build(self):
        Window.clearcolor = (0.06, 0.07, 0.09, 1)
        return MyWidget()





if __name__ == '__main__':
    BlackjackApp().run()
