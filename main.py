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
if platform not in ("android", "ios"):
    Window.size = (360, 800)




def light_haptic_feedback(*args):
    """Light haptic feedback on Android and iOS."""

    if platform == "android":
        try:
            from jnius import autoclass

            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            Context = autoclass("android.content.Context")
            Build_VERSION = autoclass("android.os.Build$VERSION")
            VibrationEffect = autoclass("android.os.VibrationEffect")

            activity = PythonActivity.mActivity

            if Build_VERSION.SDK_INT >= 31:
                vibrator_manager = activity.getSystemService(
                    Context.VIBRATOR_MANAGER_SERVICE
                )
                vibrator = vibrator_manager.getDefaultVibrator()
            else:
                vibrator = activity.getSystemService(
                    Context.VIBRATOR_SERVICE
                )

            if vibrator is None or not vibrator.hasVibrator():
                return

            if Build_VERSION.SDK_INT >= 26:
                effect = VibrationEffect.createOneShot(
                    20,
                    VibrationEffect.DEFAULT_AMPLITUDE
                )
                vibrator.vibrate(effect)
            else:
                vibrator.vibrate(20)

        except Exception:
            pass

    elif platform == "ios":
        try:
            from pyobjus import autoclass

            UIImpactFeedbackGenerator = autoclass(
                "UIImpactFeedbackGenerator"
            )

            generator = UIImpactFeedbackGenerator.alloc().initWithStyle_(0)
            generator.prepare()
            generator.impactOccurred()

        except Exception:
            pass

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
        label = Label(
            text=text,
            font_size=size,
            color=(0.78, 0.82, 0.88, 1),
            halign='left',
            valign='middle'
        )
        label.bind(size=lambda widget, _value: setattr(widget, 'text_size', widget.size))
        return label

    @staticmethod
    def _section_title(text):
        label = Label(
            text=text,
            size_hint_y=None,
            height=dp(19),
            font_size='10sp',
            bold=True,
            color=(0.55, 0.72, 0.92, 1),
            halign='left',
            valign='middle'
        )
        label.bind(size=lambda widget, _value: setattr(widget, 'text_size', widget.size))
        return label

    def _field_pair(self, parent, label, box):
        holder = BoxLayout(orientation='vertical', spacing=dp(2))
        holder.add_widget(self._label(label, '10sp'))
        holder.add_widget(box.widget)
        parent.add_widget(holder)

    def _update_strategy_style(self, *_args):
        """Make the recommendation instantly readable without changing strategy logic."""
        if not hasattr(self, 'strategy_textbox'):
            return

        value = self.strategy_textbox.text().strip().upper()
        widget = self.strategy_textbox.widget

        # Neutral/default
        widget.background_color = (0.11, 0.13, 0.17, 1)
        widget.foreground_color = (1, 1, 1, 1)

        # Colours are deliberately high-contrast and only affect presentation.
        if value.startswith('STAND'):
            widget.background_color = (0.10, 0.38, 0.22, 1)
        elif value.startswith('HIT'):
            widget.background_color = (0.08, 0.30, 0.52, 1)
        elif value.startswith('DD') or '/DD' in value:
            widget.background_color = (0.56, 0.31, 0.05, 1)
        elif value.startswith('SPLIT') or '/SPLIT' in value:
            widget.background_color = (0.38, 0.16, 0.52, 1)
        elif 'SURR' in value:
            widget.background_color = (0.48, 0.12, 0.13, 1)

    def initUI(self):
        # Header
        title = Label(
            text='BLACKJACK CALCULATOR',
            size_hint_y=None,
            height=dp(32),
            font_size='20sp',
            bold=True,
            color=(1, 1, 1, 1),
        )
        self.add_widget(title)

        subtitle = Label(
            text='CARD COUNT  •  BET SIZE  •  PLAY DECISION',
            size_hint_y=None,
            height=dp(17),
            font_size='9sp',
            color=(0.55, 0.63, 0.72, 1),
        )
        self.add_widget(subtitle)

        # ---------- COUNT ----------
        self.add_widget(self._section_title('COUNT'))

        self.top_value_box = TextBox('0', font_size='12sp')
        self.new_value_box = TextBox('0', font_size='12sp')
        self.decks_left_box = TextBox('0', font_size='12sp')
        self.value_box = TextBox('0', font_size='12sp')
        self.true_count_box = TextBox('0', font_size='12sp')
        self.decks_combo = ComboBox(['1', '2', '3', '4', '5', '6', '7', '8'])
        self.decks_combo.currentIndexChanged_connect(self.select_decks)
        self.top_value_box.on_change(self.update_new_value_box)

        metrics = GridLayout(cols=3, spacing=dp(5), size_hint_y=None, height=dp(92))
        self._field_pair(metrics, 'Cards dealt', self.top_value_box)
        self._field_pair(metrics, 'Cards left', self.new_value_box)
        self._field_pair(metrics, 'Decks left', self.decks_left_box)
        self._field_pair(metrics, 'Running count', self.value_box)
        self._field_pair(metrics, 'TRUE COUNT', self.true_count_box)

        deck_holder = BoxLayout(orientation='vertical', spacing=dp(2))
        deck_holder.add_widget(self._label('Decks', '10sp'))
        deck_holder.add_widget(self.decks_combo.widget)
        metrics.add_widget(deck_holder)
        self.add_widget(metrics)

        # Make True Count slightly more prominent.
        self.true_count_box.widget.background_color = (0.12, 0.25, 0.39, 1)
        self.true_count_box.widget.foreground_color = (1, 1, 1, 1)

        # ---------- COUNT CARD ----------
        self.add_widget(self._section_title('CARD COUNT INPUT'))

        count_buttons = GridLayout(cols=3, spacing=dp(5), size_hint_y=None, height=dp(42))
        self.addButton = ButtonBox('2–6\n+1')
        self.sevenEightNineButton = ButtonBox('7–9\n0')
        self.subtractButton = ButtonBox('10–A\n−1')

        # Different tones make the three count groups easier to identify.
        self.addButton.widget.background_color = (0.12, 0.40, 0.25, 1)
        self.sevenEightNineButton.widget.background_color = (0.25, 0.29, 0.35, 1)
        self.subtractButton.widget.background_color = (0.46, 0.16, 0.18, 1)

        for wrapper in (self.addButton, self.sevenEightNineButton, self.subtractButton):
            wrapper.widget.font_size = '13sp'
            count_buttons.add_widget(wrapper.widget)

        self.add_widget(count_buttons)

        self.addButton.widget.bind(
            on_release=lambda *_: (self.add_one(), self.add_one_to_top_value_box())
        )
        self.sevenEightNineButton.widget.bind(
            on_release=lambda *_: (self.add_seven_eight_nine(), self.add_one_to_top_value_box())
        )
        self.subtractButton.widget.bind(
            on_release=lambda *_: (self.subtract_one(), self.add_one_to_top_value_box())
        )

        # ---------- BET ----------
        self.add_widget(self._section_title('BET'))

        self.min_bet_box = TextBox('', readonly=False, input_filter='float', font_size='12sp')
        self.stake_required_box = TextBox('0', font_size='12sp')
        self.bet_amount_box = TextBox('0', font_size='12sp')
        self.min_bet_box.on_change(self.update_stake_required)

        bets = GridLayout(cols=3, spacing=dp(5), size_hint_y=None, height=dp(47))
        self._field_pair(bets, 'Minimum bet', self.min_bet_box)
        self._field_pair(bets, '100-unit bank', self.stake_required_box)
        self._field_pair(bets, 'SUGGESTED BET', self.bet_amount_box)
        self.add_widget(bets)
        self.bet_amount_box.widget.background_color = (0.13, 0.24, 0.19, 1)

        # ---------- HAND ----------
        self.add_widget(self._section_title('PLAY YOUR HAND  •  TAP DEALER CARD FIRST'))

        card_names = ['Ace', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King']
        card_grid = GridLayout(cols=7, spacing=dp(4), size_hint_y=None, height=dp(78))
        wrappers = {}

        # Two compact rows give the hand section more room for the decision panel.
        for name in card_names:
            wrapper = ButtonBox(name)
            wrapper.widget.font_size = '12sp'
            wrappers[name] = wrapper
            wrapper.widget.bind(on_release=lambda _button, w=wrapper: self._card_pressed(w))
            card_grid.add_widget(wrapper.widget)

        # Fill the final grid slot.
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

        self.insure_textbox = TextBox('', font_size='12sp')
        self.card_label = TextBox('', font_size='12sp')
        dealer_row = GridLayout(cols=2, spacing=dp(5), size_hint_y=None, height=dp(47))
        self._field_pair(dealer_row, "Dealer's card", self.card_label)
        self._field_pair(dealer_row, 'Insurance', self.insure_textbox)
        self.add_widget(dealer_row)

        self.your_cards_textbox1 = TextBox('', font_size='11sp')
        self.your_cards_textbox2 = TextBox('', font_size='11sp')
        self.your_cards_textbox3 = TextBox('', font_size='11sp')
        self.your_cards_textbox4 = TextBox('', font_size='11sp')
        self.your_cards_textbox5 = TextBox('', font_size='11sp')

        cards_row = GridLayout(cols=5, spacing=dp(4), size_hint_y=None, height=dp(44))
        for index, box in enumerate([
            self.your_cards_textbox1, self.your_cards_textbox2,
            self.your_cards_textbox3, self.your_cards_textbox4,
            self.your_cards_textbox5,
        ], start=1):
            self._field_pair(cards_row, f'Card {index}', box)
        self.add_widget(cards_row)

        # ---------- DECISION ----------
        self.add_widget(self._section_title('RECOMMENDED PLAY'))

        self.strategy_textbox = TextBox('', font_size='24sp')
        self.total_box = TextBox('', font_size='18sp')

        # Large central recommendation; the existing strategy code still writes
        # to self.strategy_textbox exactly as before.
        result_row = BoxLayout(orientation='horizontal', spacing=dp(5), size_hint_y=None, height=dp(64))

        strategy_holder = BoxLayout(orientation='vertical', spacing=dp(2))
        strategy_holder.add_widget(self._label('ACTION', '10sp'))
        strategy_holder.add_widget(self.strategy_textbox.widget)

        total_holder = BoxLayout(orientation='vertical', spacing=dp(2))
        total_holder.add_widget(self._label('TOTAL', '10sp'))
        total_holder.add_widget(self.total_box.widget)

        # Give ACTION more visual weight than TOTAL.
        strategy_holder.size_hint_x = 0.72
        total_holder.size_hint_x = 0.28
        result_row.add_widget(strategy_holder)
        result_row.add_widget(total_holder)
        self.add_widget(result_row)

        self.strategy_textbox.widget.bind(text=self._update_strategy_style)
        self._update_strategy_style()

        # ---------- CONTROLS ----------
        self.refreshButton = ButtonBox('NEW HAND')
        self.refreshAllButton = ButtonBox('RESET SHOE')
        self.refreshButton.widget.background_color = (0.14, 0.32, 0.48, 1)
        self.refreshAllButton.widget.background_color = (0.30, 0.32, 0.36, 1)

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



# ---------------------------------------------------------------------------
# GOOGLE PLAY BILLING
# ---------------------------------------------------------------------------
# IMPORTANT:
# - Create this subscription product in Play Console with product ID:
#       blackjack_premium
# - Set its auto-renewing base plan to £19.99 / month in Play Console.
# - Add a 3-day free-trial offer in Play Console.
# - Do NOT hard-code the £19.99 price or trial duration here. Google Play
#   returns the eligible offer and handles trial -> paid renewal automatically.
#
# This client-side entitlement check is suitable for getting the app working,
# but for stronger anti-tamper protection Google recommends verifying purchase
# tokens on your own backend as well.
# ---------------------------------------------------------------------------

GOOGLE_PLAY_SUBSCRIPTION_ID = "blackjack_premium"


class SubscriptionGate(BoxLayout):
    """Shown while Google Play checks entitlement, or when a subscription is required."""

    def __init__(self, app, **kwargs):
        super().__init__(
            orientation="vertical",
            spacing=dp(14),
            padding=dp(24),
            **kwargs
        )
        self.app = app

        self.add_widget(Label(
            text="BLACKJACK CALCULATOR",
            font_size="22sp",
            bold=True,
            size_hint_y=None,
            height=dp(55),
        ))

        self.status = Label(
            text="Checking your Google Play subscription...",
            font_size="15sp",
            halign="center",
            valign="middle",
        )
        self.status.bind(size=lambda widget, _value: setattr(widget, "text_size", widget.size))
        self.add_widget(self.status)

        self.subscribe_button = Button(
            text="START 3-DAY FREE TRIAL",
            size_hint_y=None,
            height=dp(54),
            disabled=True,
        )
        attach_button_feedback(self.subscribe_button)
        self.subscribe_button.bind(on_release=lambda *_: self.app.billing.start_purchase())
        self.add_widget(self.subscribe_button)

        self.restore_button = Button(
            text="RESTORE / CHECK SUBSCRIPTION",
            size_hint_y=None,
            height=dp(48),
            disabled=True,
        )
        attach_button_feedback(self.restore_button)
        self.restore_button.bind(on_release=lambda *_: self.app.billing.check_entitlement())
        self.add_widget(self.restore_button)

        self.price_info = Label(
            text="3 days free, then £19.99 per month. Auto-renews until cancelled.",
            font_size="12sp",
            halign="center",
            valign="middle",
            size_hint_y=None,
            height=dp(55),
        )
        self.price_info.bind(size=lambda widget, _value: setattr(widget, "text_size", widget.size))
        self.add_widget(self.price_info)

    def set_ready(self):
        self.subscribe_button.disabled = False
        self.restore_button.disabled = False

    def set_status(self, message):
        self.status.text = message


if platform == "android":
    from jnius import autoclass, PythonJavaClass, java_method

    PythonActivity = autoclass("org.kivy.android.PythonActivity")
    BillingClient = autoclass("com.android.billingclient.api.BillingClient")
    QueryProductDetailsParams = autoclass(
        "com.android.billingclient.api.QueryProductDetailsParams"
    )
    QueryProductDetailsProduct = autoclass(
        "com.android.billingclient.api.QueryProductDetailsParams$Product"
    )
    QueryPurchasesParams = autoclass(
        "com.android.billingclient.api.QueryPurchasesParams"
    )
    BillingFlowParams = autoclass("com.android.billingclient.api.BillingFlowParams")
    BillingFlowProductDetailsParams = autoclass(
        "com.android.billingclient.api.BillingFlowParams$ProductDetailsParams"
    )
    AcknowledgePurchaseParams = autoclass(
        "com.android.billingclient.api.AcknowledgePurchaseParams"
    )
    PendingPurchasesParams = autoclass(
        "com.android.billingclient.api.PendingPurchasesParams"
    )
    Purchase = autoclass("com.android.billingclient.api.Purchase")
    PurchaseState = autoclass("com.android.billingclient.api.Purchase$PurchaseState")


    class _PurchasesUpdatedListener(PythonJavaClass):
        __javainterfaces__ = [
            "com/android/billingclient/api/PurchasesUpdatedListener"
        ]
        __javacontext__ = "app"

        def __init__(self, owner):
            super().__init__()
            self.owner = owner

        @java_method(
            "(Lcom/android/billingclient/api/BillingResult;Ljava/util/List;)V"
        )
        def onPurchasesUpdated(self, billing_result, purchases):
            self.owner._on_purchases_updated(billing_result, purchases)


    class _BillingClientStateListener(PythonJavaClass):
        __javainterfaces__ = [
            "com/android/billingclient/api/BillingClientStateListener"
        ]
        __javacontext__ = "app"

        def __init__(self, owner):
            super().__init__()
            self.owner = owner

        @java_method("(Lcom/android/billingclient/api/BillingResult;)V")
        def onBillingSetupFinished(self, billing_result):
            self.owner._on_billing_setup_finished(billing_result)

        @java_method("()V")
        def onBillingServiceDisconnected(self):
            self.owner._on_billing_disconnected()


    class _ProductDetailsResponseListener(PythonJavaClass):
        __javainterfaces__ = [
            "com/android/billingclient/api/ProductDetailsResponseListener"
        ]
        __javacontext__ = "app"

        def __init__(self, owner):
            super().__init__()
            self.owner = owner

        @java_method(
            "(Lcom/android/billingclient/api/BillingResult;"
            "Lcom/android/billingclient/api/QueryProductDetailsResult;)V"
        )
        def onProductDetailsResponse(self, billing_result, query_result):
            self.owner._on_product_details_response(billing_result, query_result)


    class _PurchasesResponseListener(PythonJavaClass):
        __javainterfaces__ = [
            "com/android/billingclient/api/PurchasesResponseListener"
        ]
        __javacontext__ = "app"

        def __init__(self, owner):
            super().__init__()
            self.owner = owner

        @java_method(
            "(Lcom/android/billingclient/api/BillingResult;Ljava/util/List;)V"
        )
        def onQueryPurchasesResponse(self, billing_result, purchases):
            self.owner._on_query_purchases_response(billing_result, purchases)


    class _AcknowledgePurchaseResponseListener(PythonJavaClass):
        __javainterfaces__ = [
            "com/android/billingclient/api/AcknowledgePurchaseResponseListener"
        ]
        __javacontext__ = "app"

        def __init__(self, owner):
            super().__init__()
            self.owner = owner

        @java_method("(Lcom/android/billingclient/api/BillingResult;)V")
        def onAcknowledgePurchaseResponse(self, billing_result):
            self.owner._on_acknowledge_response(billing_result)


class GooglePlayBilling:
    """Small Google Play Billing wrapper for the one monthly subscription."""

    def __init__(self, app):
        self.app = app
        self.client = None
        self.product_details = None

        # Keep listener objects alive for the lifetime of BillingClient.
        self.purchases_updated_listener = None
        self.connection_listener = None
        self.product_details_listener = None
        self.purchases_response_listener = None
        self.ack_listener = None

    def start(self):
        if platform != "android":
            # Desktop is used as a development preview only.
            Clock.schedule_once(lambda _dt: self.app.set_entitled(True), 0)
            return

        try:
            self.purchases_updated_listener = _PurchasesUpdatedListener(self)
            self.connection_listener = _BillingClientStateListener(self)
            self.product_details_listener = _ProductDetailsResponseListener(self)
            self.purchases_response_listener = _PurchasesResponseListener(self)
            self.ack_listener = _AcknowledgePurchaseResponseListener(self)

            pending_params = (
                PendingPurchasesParams.newBuilder()
                .enableOneTimeProducts()
                .build()
            )

            self.client = (
                BillingClient.newBuilder(PythonActivity.mActivity)
                .setListener(self.purchases_updated_listener)
                .enablePendingPurchases(pending_params)
                .build()
            )
            self.client.startConnection(self.connection_listener)

        except Exception as exc:
            self._ui_status("Google Play Billing could not start: " + str(exc))

    def _on_billing_setup_finished(self, billing_result):
        if billing_result.getResponseCode() == BillingClient.BillingResponseCode.OK:
            self._ui_ready()
            self.query_product_details()
            self.check_entitlement()
        else:
            self._ui_status(
                "Google Play Billing error: " + billing_result.getDebugMessage()
            )

    def _on_billing_disconnected(self):
        self._ui_status("Google Play connection lost. Tap Restore to try again.")

    def query_product_details(self):
        if not self.client or not self.client.isReady():
            return

        try:
            product = (
                QueryProductDetailsProduct.newBuilder()
                .setProductId(GOOGLE_PLAY_SUBSCRIPTION_ID)
                .setProductType(BillingClient.ProductType.SUBS)
                .build()
            )

            products = autoclass("java.util.ArrayList")()
            products.add(product)

            params = (
                QueryProductDetailsParams.newBuilder()
                .setProductList(products)
                .build()
            )

            self.client.queryProductDetailsAsync(
                params,
                self.product_details_listener
            )
        except Exception as exc:
            self._ui_status("Could not load subscription: " + str(exc))

    def _on_product_details_response(self, billing_result, query_result):
        if billing_result.getResponseCode() != BillingClient.BillingResponseCode.OK:
            self._ui_status(
                "Could not load subscription: " + billing_result.getDebugMessage()
            )
            return

        details_list = query_result.getProductDetailsList()
        if details_list is None or details_list.size() == 0:
            self._ui_status(
                "Subscription not found. Check that blackjack_premium is active in Play Console."
            )
            return

        self.product_details = details_list.get(0)
        self._ui_status("Subscription ready.")

    def start_purchase(self):
        """Launch Google's subscription purchase sheet."""
        if platform != "android":
            return

        if not self.client or not self.client.isReady():
            self._ui_status("Connecting to Google Play...")
            self.start()
            return

        if self.product_details is None:
            self._ui_status("Loading subscription...")
            self.query_product_details()
            return

        try:
            offers = self.product_details.getSubscriptionOfferDetails()
            if offers is None or offers.size() == 0:
                self._ui_status(
                    "No eligible subscription offer is available for this Google account."
                )
                return

            # Prefer an eligible offer whose first pricing phase is free.
            # If the account is no longer trial-eligible, fall back to the first
            # eligible offer/base-plan offer returned by Google Play.
            selected_offer = None

            for index in range(offers.size()):
                offer = offers.get(index)
                phases = offer.getPricingPhases().getPricingPhaseList()

                if phases is not None and phases.size() > 0:
                    first_phase = phases.get(0)
                    if first_phase.getPriceAmountMicros() == 0:
                        selected_offer = offer
                        break

            if selected_offer is None:
                selected_offer = offers.get(0)

            product_params = (
                BillingFlowProductDetailsParams.newBuilder()
                .setProductDetails(self.product_details)
                .setOfferToken(selected_offer.getOfferToken())
                .build()
            )

            params_list = autoclass("java.util.ArrayList")()
            params_list.add(product_params)

            flow_params = (
                BillingFlowParams.newBuilder()
                .setProductDetailsParamsList(params_list)
                .build()
            )

            result = self.client.launchBillingFlow(
                PythonActivity.mActivity,
                flow_params
            )

            if result.getResponseCode() != BillingClient.BillingResponseCode.OK:
                self._ui_status(
                    "Could not start purchase: " + result.getDebugMessage()
                )

        except Exception as exc:
            self._ui_status("Could not start purchase: " + str(exc))

    def _on_purchases_updated(self, billing_result, purchases):
        code = billing_result.getResponseCode()

        if code == BillingClient.BillingResponseCode.OK and purchases is not None:
            self._process_purchase_list(purchases)
        elif code == BillingClient.BillingResponseCode.USER_CANCELED:
            self._ui_status("Purchase cancelled.")
        else:
            self._ui_status(
                "Purchase error: " + billing_result.getDebugMessage()
            )

    def check_entitlement(self):
        """Restore/check active subscriptions every time the app starts."""
        if platform != "android":
            self.app.set_entitled(True)
            return

        if not self.client or not self.client.isReady():
            self._ui_status("Connecting to Google Play...")
            if self.client is None:
                self.start()
            return

        try:
            params = (
                QueryPurchasesParams.newBuilder()
                .setProductType(BillingClient.ProductType.SUBS)
                .build()
            )
            self.client.queryPurchasesAsync(
                params,
                self.purchases_response_listener
            )
        except Exception as exc:
            self._ui_status("Could not check subscription: " + str(exc))

    def _on_query_purchases_response(self, billing_result, purchases):
        if billing_result.getResponseCode() != BillingClient.BillingResponseCode.OK:
            self._ui_status(
                "Could not check subscription: " + billing_result.getDebugMessage()
            )
            return

        self._process_purchase_list(purchases)

    def _process_purchase_list(self, purchases):
        entitled = False
        pending = False

        if purchases is not None:
            for index in range(purchases.size()):
                purchase = purchases.get(index)
                products = purchase.getProducts()

                owns_our_subscription = False
                if products is not None:
                    for p_index in range(products.size()):
                        if str(products.get(p_index)) == GOOGLE_PLAY_SUBSCRIPTION_ID:
                            owns_our_subscription = True
                            break

                if not owns_our_subscription:
                    continue

                state = purchase.getPurchaseState()

                if state == PurchaseState.PURCHASED:
                    entitled = True

                    # A new subscription purchase must be acknowledged.
                    if not purchase.isAcknowledged():
                        self._acknowledge(purchase.getPurchaseToken())

                elif state == PurchaseState.PENDING:
                    pending = True

        if entitled:
            self._ui_status("Subscription active.")
            Clock.schedule_once(lambda _dt: self.app.set_entitled(True), 0)
        else:
            Clock.schedule_once(lambda _dt: self.app.set_entitled(False), 0)
            if pending:
                self._ui_status("Your Google Play purchase is pending.")
            else:
                self._ui_status("A subscription is required to use the calculator.")

    def _acknowledge(self, purchase_token):
        try:
            params = (
                AcknowledgePurchaseParams.newBuilder()
                .setPurchaseToken(purchase_token)
                .build()
            )
            self.client.acknowledgePurchase(params, self.ack_listener)
        except Exception as exc:
            self._ui_status("Purchase acknowledgement error: " + str(exc))

    def _on_acknowledge_response(self, billing_result):
        if billing_result.getResponseCode() != BillingClient.BillingResponseCode.OK:
            self._ui_status(
                "Subscription active, but acknowledgement failed: "
                + billing_result.getDebugMessage()
            )

    def _ui_ready(self):
        Clock.schedule_once(
            lambda _dt: self.app.subscription_gate.set_ready()
            if self.app.subscription_gate else None,
            0
        )

    def _ui_status(self, message):
        Clock.schedule_once(
            lambda _dt: self.app.subscription_gate.set_status(message)
            if self.app.subscription_gate else None,
            0
        )

    def end(self):
        if platform == "android" and self.client is not None:
            try:
                self.client.endConnection()
            except Exception:
                pass


class BlackjackApp(App):
    title = 'Blackjack Calculator'

    def build(self):
        Window.clearcolor = (0.06, 0.07, 0.09, 1)

        self.subscription_gate = SubscriptionGate(self)
        self.billing = GooglePlayBilling(self)

        if platform == "android":
            Clock.schedule_once(lambda _dt: self.billing.start(), 0.25)
            return self.subscription_gate

        # Keep desktop development/testing convenient.
        return MyWidget()

    def set_entitled(self, entitled):
        """Switch between the paywall and the actual calculator."""
        if entitled:
            if not isinstance(self.root, MyWidget):
                self.root_window.remove_widget(self.root)
                self.root = MyWidget()
                self.root_window.add_widget(self.root)
        else:
            if not isinstance(self.root, SubscriptionGate):
                self.subscription_gate = SubscriptionGate(self)
                self.subscription_gate.set_ready()
                self.root_window.remove_widget(self.root)
                self.root = self.subscription_gate
                self.root_window.add_widget(self.root)

    def on_stop(self):
        if hasattr(self, "billing"):
            self.billing.end()


if __name__ == '__main__':
    BlackjackApp().run()
