from fractions import Fraction
import numpy as np


scale_ls = [1, 0.975, 0.95, 0.925, 0.9, 0.875, 0.85, 0.825, 0.8]
# microstate_ls = [1, n_action//2, n_action//4, n_action//3, n_action//10]


class Player(object):
    def __init__(self, n_action):
        self.n_action = n_action
        self.scale_value = scale_ls[np.random.randint(len(scale_ls))]
        self.microstate_ls = [1, n_action//2, n_action//4, n_action//3, n_action//10]
        self.n_microstate = np.random.choice(self.microstate_ls)
        while self.n_microstate == 0:  # Force it to pick an integer larget than zero
            self.n_microstate = np.random.choice(self.microstate_ls)

        self.Bernoulli_p = Fraction(self.n_microstate, self.n_action)

        self.odd = self.Bernoulli_p**(-1)*self.scale_value
        self.bet = np.random.randint(1, 30001)
        self.action = set(np.random.choice(self.n_action, self.n_microstate, replace=False))  # if self.n_microstate > 0 else set(np.random.randint(self.n_action, size=1))

    def __repr__(self):
        return (f"my bet: {self.bet}, my betting action: {self.action}, my Bernoulli_p: {self.Bernoulli_p},my chosen odd: {self.odd}")
