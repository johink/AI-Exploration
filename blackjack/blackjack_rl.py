#Blackjack Bot
from itertools import product
import numpy as np
import matplotlib.pyplot as plt
plt.style.use('ggplot')

class RandomChoiceRobot(object):
    def __init__(self):
        pass

    def make_decision(self, my_score, dealer_score):
        if np.random.rand() < .5:
            return "H"
        else:
            return "S"

    def update(self, state_seq, score):
        pass

class HeuristicRobot(object):
    def __init__(self):
        pass

    def make_decision(self, my_score, dealer_score):
        points = my_score[1]
        if points >= 20:
            return "S"
        elif points - 10 > dealer_score[1] and points >= 16:
            return "S"
        elif dealer_score[1] in [4,5,6] and points > 13:
            return "S"
        else:
            return "H"

    def update(self, state_seq, score):
        pass

class RLRobot:
    def __init__(self, alpha = .5, tau = .9, epsilon = .25, training_epochs = 100000):
        self.alpha = alpha
        self.tau = tau
        self.epsilon = epsilon
        self.action_value = {}
        points_showing = range(22)
        for myscore, dealerscore, have_ace, choice in product(points_showing, points_showing, [True, False], ["H","S"]):
            self.action_value[(myscore, dealerscore, have_ace, choice)] = 10 #Optimistic Initial Values

        self.initial_train(training_epochs)
        self.epsilon = 0

    def make_decision(self, my_score, dealer_score):
        if np.random.rand() < self.epsilon:
            return ["S","H"][np.random.randint(0,2)]
        else:
            have_ace, my_points = my_score
            their_points = dealer_score[1]
            stand_score = self.action_value[(my_points, their_points, have_ace, "S")]
            hit_score = self.action_value[(my_points, their_points, have_ace, "H")]
            if stand_score > hit_score:
                return "S"
            else:
                return "H"

    def update(self, state_seq, score):
        for i, state in enumerate(reversed(state_seq)):
            self.action_value[state] = self.action_value[state] * (1 - self.alpha) + score * (self.tau ** (i+1)) * self.alpha

    def initial_train(self, epochs = 1000):
        BJTraining(self, epochs)


#CardCountingRobot
class DealerRobot:
    def __init__(self):
        pass

    def make_decision(self, my_score, dealer_score):
        if my_score[1] >= 17:
            return "S"
        else:
            return "H"

    def update(self, state_seq, score):
        pass

#Thought about doing this but it feels unwieldy
class Human:
    def __init__(self, name):
        self.name = name

    def make_decision(self, my_score, dealer_score):
        pass

class Card(object):
    def __init__(self, rank, suit, revealed):
        self.rank = rank
        self.suit = suit
        self.revealed = revealed

    def __str__(self):
        return "{} of {}".format(self.rank, self.suit) if self.revealed else "Hidden"

class Hand(object):
    def __init__(self):
        self.cards = []

    def add_card(self, card):
        self.cards.append(card)

    def discard(self, card_to_toss):
        temp = [card for card in self.cards if card.rank == card_to_toss.rank and card.suit == card_to_toss.suit]
        if len(temp) + 1 != len(self.cards):
            raise RuntimeError("Discarding card which isn't in hand")
        else:
            self.cards = temp

    def discard_all(self):
        self.cards = []

    def score_hand(self, all_cards = True):
        mapper = {'A':1, 'J':10, 'Q':10, 'K':10}
        ranks = [card.rank for card in self.cards if all_cards or card.revealed]
        has_ace = 'A' in ranks
        score = sum([mapper[rank] if rank in mapper else int(rank) for rank in ranks])
        return has_ace, score

    def __str__(self):
        return ", ".join([str(card) for card in self.cards])

class Deck(object):
    def __init__(self, n_decks = 1):
        self.n_decks = n_decks
        self.cards = self.shuffle()

    def shuffle(self):
        cards = list(product(["Hearts","Diamonds","Clubs","Spades"], list("23456789JQKA") + ["10"]))
        cards = [Card(card[1], card[0], False) for card in cards * self.n_decks]
        np.random.shuffle(cards)
        return cards

    def draw(self):
        if len(self.cards) == 0:
            self.cards = self.shuffle()
        return self.cards.pop()

    def __str__(self):
        return "\n".join([str(card) for card in self.cards])

class Player(object):
    def __init__(self, name, initial_money, robot = False, AI = None):
        self.name = name
        self.money = initial_money
        self.hand = Hand()
        self.robot = robot
        self.AI = AI

    def get_card(self, card):
        self.hand.add_card(card)

    def __str__(self):
        return "{} - ${:,.2f}".format(self.name, self.money)

    def request_choice(self, dealer_score):
        if not self.robot:
            return input("{}: Your hand is {}\n(H)it or (S)tand? >> ".format(self.name,', '.join([card.rank for card in self.hand.cards])))
        else:
            return self.AI.make_decision(self.hand.score_hand(), dealer_score)


    def request_bet(self):
        if not self.robot:
            value = input("{}, place a bet! (You have {}) >> ".format(self.name, self.money))
            while not value.isnumeric():
                value = input("Please enter a valid number >> ".format(self.name, self.money))
            return float(value)

        else:
            return 50


class Blackjack(object):
    def __init__(self, n_decks, n_players, min_bet = 5, max_bet = 1000, setup = True):
        self.deck = Deck(n_decks)
        self.n_players = n_players
        self.min_bet = min_bet
        self.max_bet = max_bet
        self.dealer_hand = Hand()
        self.bets = []
        if setup:
            self.players = self.setup_players(n_players)
            self.all_AI = all([player.robot for player in self.players])

    def setup_players(self, n_players):
        players = []
        for i in range(n_players):
            name = input("What is Player {}'s name? (-1 for bot) >> ".format(i))
            robot = name == "-1"
            money = float(input("How much money does Player {} have? >> ".format(i)))
            mapping = {'1': RandomChoiceRobot, '2': HeuristicRobot, '3': RLRobot, '4': DealerRobot}
            if name == "-1":
                diff = -1
                while diff not in list('1234'):
                    diff = input("What is this AI's strategy?\n1.  Random\n2.  Heuristic\n3.  Smart\n4.  Dealer\n >> ")

                name = mapping[diff].__name__
            players.append(Player(name, money, robot, mapping[diff]() if robot else Human(name)))
        return players

    def reshuffle(self):
        self.deck = self.deck.shuffle()

    def initial_deal(self):
        for player in self.players:
            player.get_card(self.deck.draw())

        self.dealer_hand.add_card(self.deck.draw())

        for player in self.players:
            player.get_card(self.draw_and_reveal())

        self.dealer_hand.add_card(self.draw_and_reveal())

    def play_n_games(self, n):
        stats = []
        for _ in range(int(n)):
            stats.append([player.money for player in self.players])
            self.place_bets()
            self.initial_deal()
            dealer_score = self.play_round()
            self.resolve_bets(dealer_score)
        return stats

    def play_blackjack(self):
        if self.all_AI:
            n_games = input("It looks like only AI are playing, how many rounds should they play? >> ")
            stats = self.play_n_games(n_games)
            stats = np.array(stats)
            fig, ax = plt.subplots()
            for i in range(len(self.players)):
                ax.plot(stats[:,i], label = self.players[i].name)

            ax.legend()
            plt.show()

        else:
            playing = True
            while playing:
                self.place_bets()
                self.initial_deal()
                dealer_score = self.play_round()
                self.resolve_bets(dealer_score)
                response = input("Q to quit, anything else to play another round >> ")
                if response == "Q":
                    playing = False
                if response == "PRINT":
                    for player in self.players:
                        if player.AI and player.AI.action_value:
                            print(player.AI.action_value)
                            for state, value in player.AI.action_value.items():
                                if value > 25 or value < -25:
                                    print(state, value)

    def place_bets(self):
        bets = []
        for player in self.players:
            max_bet = min(player.money, self.max_bet)
            bet = player.request_bet()
            bet = self.min_bet if not bet else float(bet)
            bet = min(bet, max_bet)
            player.money -= bet
            bets.append(bet)

        self.bets = bets

    def draw_and_reveal(self):
        card = self.deck.draw()
        card.revealed = True
        return card

    def play_round(self):
        if not self.all_AI:
            print("The dealer's hand is {}".format(self.dealer_hand))
        dealer_score = self.dealer_hand.score_hand(False)
        for player in self.players:
            if player.robot:
                player.state_seq = []
            stand = False
            while not stand:
                choice = player.request_choice(dealer_score)
                if player.robot:
                    has_ace, score = player.hand.score_hand()
                    player.state_seq.append((score, dealer_score[1], has_ace, choice))
                if choice in ["h","H","hit","Hit"]:
                    player.hand.add_card(self.draw_and_reveal())
                if player.hand.score_hand()[1] >= 21 or choice in ["s","S","stand","Stand"]:
                    stand = True

        for card in self.dealer_hand.cards:
            card.revealed = True

        ace, score = self.dealer_hand.score_hand()
        if score <= 11 and ace:
            score += 10

        while score < 17:
            self.dealer_hand.add_card(self.draw_and_reveal())
            ace, score = self.dealer_hand.score_hand()
            if score <= 11 and ace:
                score += 10

        return score

    def resolve_bets(self, score_to_beat):
        if not self.all_AI:
            print("The dealer's hand is {}".format(self.dealer_hand))
        for bet, player in zip(self.bets, self.players):
            ace, score = player.hand.score_hand()
            if score <= 11 and ace:
                score += 10

            for card in player.hand.cards:
                card.revealed = True
            if not self.all_AI:
                print("{}'s hand: {}".format(player.name, player.hand))

            if score > 21:
                result = "{} busts!".format(player.name)
                winnings = -bet
            elif len(player.hand.cards) == 2 and score == 21 and score_to_beat != 21:
                result = "Blackjack! {} wins big".format(player.name)
                player.money += 2.5 * bet
                winnings = 1.5 * bet
            elif score_to_beat > 21 or score > score_to_beat:
                result = "{} beats the house".format(player.name)
                player.money += 2 * bet
                winnings = bet
            else:
                winnings = -bet
                result = "{} loses with a score of {}".format(player.name, score)

            if not self.all_AI:
                print(result)

            if player.robot:
                player.AI.update(player.state_seq, winnings)
            player.hand.discard_all()

        self.dealer_hand.discard_all()

class BJTraining(Blackjack):
    def __init__(self, AI, epochs = 1000):
        self.all_AI = True
        self.deck = Deck(2)
        self.n_players = 1
        self.min_bet = 50
        self.max_bet = 50
        self.players = [Player("test", 1e10, True, AI)]
        self.dealer_hand = Hand()
        self.bets = []
        self.play_blackjack(epochs)

    def play_blackjack(self, n):
        for _ in range(n):
            self.bets = [50]
            self.initial_deal()
            dealer_score = self.play_round()
            self.resolve_bets(dealer_score)

if __name__ == "__main__":
    bj = Blackjack(n_decks = 2, n_players = 4)
    bj.play_blackjack()
