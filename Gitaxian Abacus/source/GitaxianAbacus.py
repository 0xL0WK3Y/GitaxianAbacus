import PySimpleGUI as sg
import requests


class GitaxianAbacus():

    def __init__(self):
        sg.theme("DarkTeal9")
        self.layout = [[sg.Multiline(default_text="Enter your decklist here.", size=(50, 10), key="deck_input")],
                       [sg.Text("Mana Curve Ratio: "), sg.Text("", key="mana_curve_label")],
                       [sg.Text("Card Advantage Ratio: "), sg.Text("", key="card_advantage_label")],
                       [sg.Combo([], key="advantage_menu",size=(30,10))],
                       [sg.Text("Mana Advantage Ratio: "), sg.Text("", key="mana_advantage_label")],
                       [sg.Combo([], key="mana_menu",size=(30,10))],
                       [sg.Text("Board Interaction Ratio: "), sg.Text("", key="interaction_label")],
                       [sg.Combo([], key="interaction_menu",size=(30,))],
                       [sg.Text("Win Condition Ratio: "), sg.Text("", key="win_ratio")],
                       [sg.Combo([], key="win_menu",size=(30,10))],
                       [sg.Multiline(default_text="Enter your win condition list here or \"dntcnsdr\" to ignore this factor."
                                     , size=(50, 10), key="win_input")],
                       [sg.Text("Power Level: "), sg.Text("", key="power_level")],
                       [sg.Button("Calculate Power Level")]
                       ]
        
        self.window = sg.Window("Gitaxian Abacus", self.layout)
        self.window.set_icon('icon.ico')

    def format_decklist(self, decklist):
        new_decklist = []
        for card in decklist:
            amount = ""
            words = card.split()
            if card.split()[0].isdigit():
                amount += card.split()[0]
                if int(amount) > 1:
                    for _ in range(0,int(amount)-1):
                        new_decklist.append(' '.join(words[1:]))
                new_decklist.append(' '.join(words[1:]))
            else:
                new_decklist.append(card)
        return new_decklist

    def get_mana_ratio(self,deck):

        cmc_counts = {}
        for card in deck:

            response = requests.get(f"https://api.scryfall.com/cards/named?fuzzy={card}")
            card_data = response.json()
            cmc = card_data["cmc"]
            if cmc in cmc_counts:
                cmc_counts[cmc] += 1
            else:
                cmc_counts[cmc] = 1

        total_cmc = sum(cmc_counts.values())
        mana_curve_ratio = []
        for cmc in range(1, 8):  # Assumes the deck has cards with CMCs from 1 to 7
            count = cmc_counts.get(cmc, 0)
            ratio = count / total_cmc
            mana_curve_ratio.append(ratio)

        return mana_curve_ratio

    def calculate_card_advantage_ratio(self, deck):
        draw_keywords = ["draw", "loot", "scry", "cycle", "search", "surveil", "investigate"]
        card_count = len(deck)
        advantage_count = 0
        cards = []
        for card in deck:
            response = requests.get(f"https://api.scryfall.com/cards/named?fuzzy={card}")
            card_data = response.json()
            if "card_faces" in card_data:
                card_text = ""
                for face in card_data["card_faces"]:
                    card_text += face["oracle_text"].lower()
            else:
                card_text = card_data["oracle_text"].lower()
            if any(keyword in card_text for keyword in draw_keywords):
                advantage_count += 1
                cards.append(card_data["name"])
        card_advantage_ratio = advantage_count / card_count
        return card_advantage_ratio, cards
    
    def calculate_ramp_ratio(self, deck):
        mana_keywords = ["land", "mana", "add"]
        card_count = len(deck)
        mana_count = 0
        cards = []
        for card in deck:
            response = requests.get(f"https://api.scryfall.com/cards/named?fuzzy={card}")
            card_data = response.json()
            if "card_faces" in card_data:
                card_text = ""
                for face in card_data["card_faces"]:
                    card_text += face["oracle_text"].lower()
            else:
                card_text = card_data["oracle_text"].lower()
            if any(keyword in card_text for keyword in mana_keywords):
                mana_count += 1
                cards.append(card_data["name"])
        mana_advantage_ratio = mana_count / card_count
        return mana_advantage_ratio, cards

    def calculate_board_interaction_ratio(self, deck):
        draw_keywords = ["counter", "destroy", "exile", "deal", "deals", "fights"]
        card_count = len(deck)
        advantage_count = 0
        cards = []
        for card in deck:
            response = requests.get(f"https://api.scryfall.com/cards/named?fuzzy={card}")
            card_data = response.json()
            if "card_faces" in card_data:
                card_text = ""
                for face in card_data["card_faces"]:
                    card_text += face["oracle_text"].lower()
            else:
                card_text = card_data["oracle_text"].lower()
            if any(keyword in card_text for keyword in draw_keywords):
                advantage_count += 1
                cards.append(card_data["name"])
        board_interaction_ratio = advantage_count / card_count
        return board_interaction_ratio, cards

    def calculate_win_condition_ratio(self, deck, win_conditions):
        if win_conditions[0] == "":
            return 0, []
        elif win_conditions[0] == "dntcnsdr":
            return 1, []
        win_condition_count = 0
        card_count = len(deck)
        cards = []
        for card in deck:
            response = requests.get(f"https://api.scryfall.com/cards/named?fuzzy={card}")
            card_data = response.json()
            if "card_faces" in card_data:
                card_text = ""
                for face in card_data["card_faces"]:
                    card_text += face["oracle_text"].lower()
            else:
                card_text = card_data["oracle_text"].lower()
            for win_condition in win_conditions:
                if win_condition in card_text or win_condition in card_data.get('type_line','') or win_condition in card_data.get('creature_type', ''):
                    cards.append(card_data["name"])
                    win_condition_count += 1
                    break
        win_condition_ratio = win_condition_count / card_count
        return win_condition_ratio, cards

    def run(self):
        while True:
            event, values = self.window.read()
            if event == sg.WINDOW_CLOSED:
                break
            elif event == "Calculate Power Level":
                decklist = values["deck_input"].split("\n")
                decklist = self.format_decklist(decklist)
                winlist = values["win_input"].split("\n")

                mana_curve_ratio = self.get_mana_ratio(decklist)
                self.window["mana_curve_label"].update("Mana Curve Ratio: " + str(mana_curve_ratio))

                card_advantage_ratio, card_advantage_list = self.calculate_card_advantage_ratio(decklist)
                self.window["card_advantage_label"].update("Card Advantage Ratio: " + str(card_advantage_ratio))
                self.window["advantage_menu"].update(values=card_advantage_list)

                mana_advantage_ratio, mana_advantage_list = self.calculate_ramp_ratio(decklist)
                self.window["mana_advantage_label"].update("Mana Advantage Ratio: " + str(mana_advantage_ratio))
                self.window["mana_menu"].update(values=mana_advantage_list)

                board_interaction_ratio, interaction_list = self.calculate_board_interaction_ratio(decklist)
                self.window["interaction_label"].update("Board Interaction Ratio: " + str(board_interaction_ratio))
                self.window["interaction_menu"].update(values=interaction_list)

                win_condition_ratio, win_condition_list = self.calculate_win_condition_ratio(decklist, winlist)
                self.window["win_ratio"].update("Win Condition Ratio: " + str(win_condition_ratio))
                self.window["win_menu"].update(values=win_condition_list)

                power_level = ((sum(mana_curve_ratio) + card_advantage_ratio + mana_advantage_ratio + board_interaction_ratio + win_condition_ratio)/5)*10
                self.window["power_level"].update("Power Level: " + str(power_level))

        


if __name__ == "__main__":
    app = GitaxianAbacus()
    app.run()
