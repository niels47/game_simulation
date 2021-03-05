import numpy as np
from player import Player


class Mall(object):

    def __init__(self):
        self.player_in_mall = None
        self.player_action_ls = None
        self.player_bet_ls = None
        self.player_odd_ls = None
        self.player_Bernoulli_p_ls = None
        self.n_players = None
        self.player_all_action_set = set()

        self.updated = False  # Indicate the mall receives the house's action then updates its profit, edge, etc.
        self.interval = -1  # Note the interval 0 as the first interval for receiving betting.
        self.volume = 0
        self.profit = 0

        self.cost = 0.00001
        """
        Set some small and practical number for the mall
        to prevent from the error of ZeroDividing.
        This is a fixed cost for the mall.
        """

        self.gain = None  # It equals to (self.profit/self.cost + 1)
        self.RTP = None  # It also equals to (-self.profit)
        self.edge = None  # It is also called the profit ratio.
        # self.target_edge = None

        self.externality = None
        """
        Made by the house's or others' manipulations
        so that resultant action may be deviated from the random one.
        """

        # For events recording.
        self.gain_history = []
        self.edge_history = []
        self.player_bet_history = []
        self.player_odd_history = []
        self.player_action_history = []
        self.player_Bernoulli_p_history = []
        self.externality_history = []

        # For debug.
        self.manipulated = None
        # True iff the house has involved in the interval
        # even the result action by manipulation is the same as the original random one.
        # None if the manipupating is needed to determined by the house.

        self.manipulated_history = []

    def check_manipulation(self, ask_house):
        self.manipulated = ask_house
        return None

    def get_interval_utility_for_a_player(self, house_action, player):
        """
        Calculate an interval profit or utility of a player in this mall at specific house's action.
        """
        if house_action in player.action:
            return (-(player.odd - 1)*player.bet)
        else:
            return player.bet

    def get_interval_utility(self, house_action):
        """
        Calculate an interval profit or utility of this mall at specific house's action.
        """
        return sum([self.get_interval_utility_for_a_player(house_action, x) for x in self.player_in_mall])

    def get_interval_cost_for_a_player(self, house_action, player):  # The interval cost of this mall

        if house_action in player.action:
            return (-(player.odd - 1)*player.bet)
        else:
            return 0

    def get_interval_cost(self, house_action):  # The interval cost of this mall
        return sum([self.get_interval_cost_for_a_player(house_action, x) for x in self.player_in_mall])

    def update_for(self, house_action, house_random_action):
        """
        Receive house' final decided action
        Note this mothod should follows player_betting chronologically.
        If the executing order of two methods is nonchronological,
        then it should be stopped.
        """
        if not self.updated and self.interval == -1:
            print("One should execute the method `player_betting` first!")
            # sys.exit()
            assert True is False
        if not self.updated:  # Prevent twice updates within an interval.
            self.volume = self.volume + sum(self.player_bet_ls)
            # self.cost = self.cost + sum([self.get_interval_cost_for_a_player(house_action, x) for x in self.player_in_mall])
            self.profit = self.profit + sum([self.get_interval_utility_for_a_player(house_action, x) for x in self.player_in_mall])
            # self.gain = self.profit/self.cost
            self.edge = self.profit/self.volume
            self.RTP = 1 - self.edge
            self.player_all_action_set = set()  # Need clear out before the next interval.
            self.updated = True
            # self.update_externality(house_action, house_random_action, self.player_in_mall)
            return None
        else:
            print("This mall has been updated during this interval. One should execute player_betting for going into the next interval.")

        #  sys.exit()
            assert True is False
        # return None

    def update_externality(self, house_action, house_random_action, player_in_mall):
        if house_action == house_random_action:
            self.externality = 0                # Maybe prevent round-off errors?
        else:
            # self.externality = sum([self.get_interval_utility(house_action, x) - self.get_interval_utility(house_random_action, x) for x in self.player_in_mall])
            self.externality = self.get_interval_utility(house_action) - self.get_interval_utility(house_random_action)
            return None

    def reset_manipulated(self):
        self.manipulated = None
        return None

    def player_betting(self, n_action):
        self.n_players = np.random.randint(1, 101)
        self.player_in_mall = [Player(n_action) for _ in range(self.n_players)]
        if not self.updated and self.interval == -1:
            self.interval = self.interval + 1  # Note the interval will go to next only if the method player_betting executed
            # self.player_action_ls = [x.action for x in self.player_in_mall]
            self.player_bet_ls = [x.bet for x in self.player_in_mall]

            for p in self.player_in_mall:
                self.player_all_action_set = self.player_all_action_set.union(p.action)
            # self.player_odd_ls = [x.odd for x in self.player_in_mall]
            # self.player_Bernoulli_p_ls = [x.Bernoulli_p for x in self.player_in_mall]
            #    self.updated = False # Set this false for going to the next interval.
            return None

        elif self.updated:      # Allow players' betting only when their corresponding mall makes its state updated at last interval.
            self.updated = False  # Set this false for waiting the house's action later.
            self.interval = self.interval + 1
            # self.player_action_ls = [x.action for x in self.player_in_mall]  # player_in_mall.action
            self.player_bet_ls = [x.bet for x in self.player_in_mall]  # player_in_mall.bet

            for p in self.player_in_mall:
                self.player_all_action_set = self.player_all_action_set.union(p.action)
            # self.player_odd_ls = [x.odd for x in self.player_in_mall]  # player_in_mall.odd
            # self.player_Bernoulli_p_ls = [x.Bernoulli_p for x in self.player_in_mall]  # player_in_mall.Bernoulli_p

            return None

        elif not self.updated:
            print("This malls is not updated!")

            # return None
            # sys.exit()
            assert True is False
        # else:
        #    print("Something odd!")
        #    return None
        #    sys.exit()

    def reset(self):
        pass

    def history_record(self):  # It always follows the updating movement if one want to record data.
        assert self.updated is True
        self.gain_record(False)
        self.edge_record(False)
        self.player_bet_record(False)
        self.player_action_record(False)
        self.manipulated_state_record(False)
        self.player_odd_record(False)
        self.externality_record(False)
        self.player_Bernoulli_p_record(False)
        return None

    def gain_record(self, switch=True):
        if switch:
            if self.interval == (-1 or 0):
                assert self.gain_history == []
            self.gain_history.append(self.gain)
            return None
        else:
            pass

    def edge_record(self, switch=True):
        if switch:
            if self.interval == (-1 or 0):
                assert self.edge_history == []
            self.edge_history.append(self.edge)
            return None
        else:
            pass

    def player_Bernoulli_p_record(self, switch=True):
        if switch:
            if self.interval == (-1 or 0):
                assert self.player_Bernoulli_p_history == []
            self.player_Bernoulli_p_history.append(self.player_Bernoulli_p_ls)
            return None
        else:
            pass

    def player_odd_record(self, switch=True):
        if switch:
            if self.interval == (-1 or 0):
                assert self.player_odd_history == []
            self.player_odd_history.append(self.player_odd_ls)
            return None
        else:
            pass

    def player_action_record(self, switch=True):
        if switch:
            if self.interval == (-1 or 0):
                assert self.player_action_history == []
            self.player_action_history.append(self.player_action_ls)
            return None
        else:
            pass

    def player_bet_record(self, switch=True):
        if switch:
            if self.interval == (-1 or 0):
                assert self.player_bet_history == []
            self.player_bet_history.append(self.player_bet_ls)
            return None
        else:
            pass

    def manipulated_state_record(self, switch=True):
        if switch:
            if self.interval == (-1 or 0):
                assert self.manipulated_history == []
            self.manipulated_history.append(self.manipulated)
            return None
        else:
            pass

    def externality_record(self, switch=True):
        if switch:
            if self.interval == (-1 or 0):
                assert self.externality_history == []
            self.externality_history.append(self.externality)
            return None
        else:
            pass
