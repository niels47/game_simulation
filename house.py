import numpy as np


class House(object):

    def __init__(self, n_action, external_interval=None):
        self.n_action = n_action
        self.external_interval = external_interval
        self.random_action = None
        self.action = None
        self.manipulated = None  # True of False when a game starts.

        self.action_history = []
        self.true_random_action_history = []

    def action_record(self, house_action):
        self.action_history.append(house_action)
        return None

    def true_random_action_record(self):
        self.true_random_action_history.append(self.random_action)
        return None

    def check_mall_updated(self):
        pass

    def get_interval(self, interval):
        self.external_interval = interval
        return None

    def get_mall_edge_ls(self, mall_ls):
        return [x.edge for x in mall_ls]

    def tie_breaking(self, ls):
        if ls:
            return ls[np.random.randint(len(ls))]
        else:
            return None

    def pre_calculate_mall_interval_utility_list(self, mall_ls):
        """
        Prepare to construct (n_mall X n_action) array-like form
        """
        pre_calc_mall_interval_utility_multiple_ls = []  # Collect virtual interval profits of malls.
        for x in mall_ls:
            assert x.updated is False  # Because this class method invloves a pre-calculation a prior.
            pre_calc_mall_interval_utility_multiple_ls.append([x.get_interval_utility(j) for j in range(self.n_action)])

        pre_calc_itv_util = pre_calc_mall_interval_utility_multiple_ls
        return pre_calc_itv_util

    def pre_calculate_mall_edge_list(self, mall_ls):
        """
        Prepare to construct the pre-calculated edge list of malls
        """
        pre_calc_mall_edge_ls = []  # Collect virtual interval profits of malls.
        for x in mall_ls:
            assert x.updated is False  # Because this class method invloves a pre-calculation a prior.
            pre_calc_mall_edge_ls.append([(x.profit+x.get_interval_utility(j))/(x.volume + sum(x.player_bet_ls)) for j in range(self.n_action)])
        pre_calc_mall_edge = pre_calc_mall_edge_ls
        return pre_calc_mall_edge

    def generate_random_action(self):
        self.random_action = np.random.randint(self.n_action)
        return None

    # def choice_func_0(self):
    #     """
    #     The house uses the constant action to all malls.
    #
    #     """
    #     self.generate_random_action()
    #     constant_action = np.random.randint(self.n_action)
    #     return constant_action

    def choice_func_random_action(self, mall_ls):
        self.generate_random_action()
        # self.manipulated = False
        for m in mall_ls:
            m.check_manipulation(False)
        return self.random_action

    def choice_func_1(self, mall_ls, target_edge_upper_bound, target_edge_lower_bound):
        assert target_edge_upper_bound > target_edge_lower_bound
        assert self.external_interval is not None
        self.generate_random_action()

    #     pre_calc_mall_edge = self.pre_calculate_mall_edge_list(mall_ls)
        itv_util_for_choosing = []  # self.pre_calculate_mall_interval_utility_list
        # condition = lambda x,y: True if x > target_edge_upper_bound and y >= target_edge_lower_bound else False # Positive event. Be excluded.

        def condition(x, y):
            if x > target_edge_upper_bound and y >= target_edge_lower_bound:
                return True  # Positive events will be excluded from the following candidate list.
            else:
                return False

        if self.external_interval == 0:
            chosen_action = self.random_action  # Default. Or using other judgements is ok.

            for m in mall_ls:
                m.check_manipulation(False)
        elif self.external_interval >= 1:
            for x in mall_ls:
                # assert x.updated == False
                itv_util_for_choosing.append([
                    np.nan if condition(
                        x.edge,
                        (x.profit+x.get_interval_utility(i))/(x.volume + sum(x.player_bet_ls))
                    )
                    else x.get_interval_utility(i) for i in range(self.n_action)
                ]
                )  # Use np.nan to replace 0. In the case of [0,0,-1], np.argmax will always pick the position 0.

            result_narray = np.nansum(itv_util_for_choosing, axis=0)
            #  print(f"itv_util_for_choosing = {itv_util_for_choosing}")
            #  print(f"result_narray = {result_narray}")

            excluded_n_mall = np.count_nonzero(np.isnan(result_narray))
            #  print(f"{excluded_n_mall} excluded.")
            #  print(np.array(itv_util_for_choosing).shape)
            #  print(np.full((len(mall_ls), self.n_action), np.nan).shape)
            if np.array_equal(np.array(itv_util_for_choosing), np.full((len(mall_ls), self.n_action), np.nan), equal_nan=True):
                #      print("An all-nan array...")
                chosen_action = self.random_action

                for m in mall_ls:
                    m.check_manipulation(False)
            elif excluded_n_mall == len(mall_ls):
                chosen_action = self.random_action
                # self.manipulated = False
                for m in mall_ls:
                    m.check_manipulation(False)
                #     print("Randomly chosen.")
            else:
                # chosen_action = np.nanargmax(result_narray)
                #     print("House needs to involve...")
                chosen_action_ls = list(np.argwhere(result_narray == np.nanmax(result_narray)).flatten())
                if len(chosen_action_ls) > 1:
                    #    print("tie breaking...")
                    chosen_action = self.tie_breaking(chosen_action_ls)

                    for m in mall_ls:
                        m.check_manipulation(True)
                elif len(chosen_action_ls) == 1:
                    chosen_action = chosen_action_ls[0]

                    for m in mall_ls:
                        m.check_manipulation(True)
                else:
                    print("Something odd! Figure out this!")
                    assert True is False
        else:
            print("Something odd! Figure out this!")
            assert True is False

        return chosen_action

    def choice_func_2(self, mall_ls, target_edge_upper_bound, target_edge_lower_bound, P=1, Q=0.8):
        assert target_edge_upper_bound > target_edge_lower_bound
        assert self.external_interval is not None
        assert P <= 1 and P > 0
        assert Q <= 1 and Q > 0

        self.generate_random_action()

        #      pre_calc_mall_edge = self.pre_calculate_mall_edge_list(mall_ls)
        itv_util_for_choosing = []  # self.pre_calculate_mall_interval_utility_list

        def condition(x, y):
            if x > target_edge_upper_bound and y >= target_edge_lower_bound:
                return True  # Positive events will be excluded from the following candidate list.
            else:
                return False

        if self.external_interval == 0:
            chosen_action = self.random_action
            for m in mall_ls:
                m.check_manipulation(False)
        elif self.external_interval >= 1:
            for x in mall_ls:
                # assert x.updated == False

                itv_util_for_choosing.append([
                    x.get_interval_utility(i)
                    if not condition(x.edge, (x.profit+x.get_interval_utility(i))/(x.volume + sum(x.player_bet_ls)))
                    else np.nan if x.get_interval_utility(i) > 0
                    else abs(x.get_interval_utility(i))*P
                    if abs(x.get_interval_utility(i)) <= x.volume*(x.edge - target_edge_upper_bound)*Q
                    else x.get_interval_utility(i) for i in range(self.n_action)
                ]
                )  # Use np.nan to replace 0. In the case of [0,0,-1], np.argmax will always pick the position 0.
                #    In "x.get_interval_utility(i) <= x.volume*...", I let the equality hold since the manual did not mention this case.

                #  # Do double check for itv_util_for_choosing from other logical judging. Below here;
                #  test_for_itv_util_for_choosing = []
                #  for i in range(self.n_action):
                #      tmp_u = x.get_interval_utility(i)
                #      if condition(x.edge, (x.profit+tmp_u)/(x.volume + sum(x.player_bet_ls))):
                #          if tmp_u > 0:
                #              test_for_itv_util_for_choosing.append(np.nan)
                #          else:
                #              if -tmp_u <= x.volume*(x.edge - target_edge_upper_bound)*Q:
                #              #    print("Adding the negative one...")
                #                  test_for_itv_util_for_choosing.append(-tmp_u*P)
                #              else:
                #              #    print("Lost too much, skipped")
                #                  test_for_itv_util_for_choosing.append(tmp_u)
                #      else:
                #           test_for_itv_util_for_choosing.append(tmp_u)
                # #  print(f"itv_util_for_choosing = {itv_util_for_choosing[-1]}")
                # #  print(f"test_for_itv_util_for_choosing = {test_for_itv_util_for_choosing}")
                #  assert  test_for_itv_util_for_choosing == itv_util_for_choosing[-1]
                #  # ;above this end.

            result_narray = np.nansum(itv_util_for_choosing, axis=0)
        #   print(f"itv_util_for_choosing = {itv_util_for_choosing}")
        #   print(f"result_narray = {result_narray}")

            excluded_n_mall = np.count_nonzero(np.isnan(result_narray))
        #  print(f"{excluded_n_mall} excluded.")
        #  print(np.array(itv_util_for_choosing).shape)
        #  print(np.full((len(mall_ls), self.n_action), np.nan).shape)
            if np.array_equal(np.array(itv_util_for_choosing), np.full((len(mall_ls), self.n_action), np.nan), equal_nan=True):
                #      print("An all-nan array...")
                chosen_action = self.random_action
                for m in mall_ls:
                    m.check_manipulation(False)
            elif excluded_n_mall == len(mall_ls):
                chosen_action = self.random_action
                for m in mall_ls:
                    m.check_manipulation(False)
            #      print("Randomly chosen.")
            else:
                # chosen_action = np.nanargmax(result_narray)
                #     print("House needs to involve...")
                chosen_action_ls = list(np.argwhere(result_narray == np.nanmax(result_narray)).flatten())
                if len(chosen_action_ls) > 1:
                    #    print("tie breaking...")
                    chosen_action = self.tie_breaking(chosen_action_ls)
                    for m in mall_ls:
                        m.check_manipulation(True)
                elif len(chosen_action_ls) == 1:
                    chosen_action = chosen_action_ls[0]
                    for m in mall_ls:
                        m.check_manipulation(True)
                else:
                    print("Something odd! Figure out this!")
                    assert True is False
        else:
            print("Something odd! Figure out this!")
            assert True is False

        # return result_narray
        # print(itv_util_for_choosing)
        return chosen_action

    def choice_func_3(self, mall_ls, target_edge_upper_bound, target_edge_lower_bound):
        assert target_edge_upper_bound > target_edge_lower_bound
        assert self.external_interval is not None

        self.generate_random_action()

        pre_calc_mall_edge = self.pre_calculate_mall_edge_list(mall_ls)
        mall_with_candidated_num_set_ls = []

        if self.external_interval == 0:
            chosen_action = self.random_action
            for m in mall_ls:
                m.check_manipulation(False)
        elif self.external_interval >= 1:
            for i, m in enumerate(mall_ls):
                if m.edge > target_edge_upper_bound:
                    #    print(pre_calc_mall_edge[i])
                    mall_with_candidated_num_set_ls.append((m, {j for j in range(self.n_action) if (m.get_interval_utility(j) <= 0 and pre_calc_mall_edge[i][j] >= target_edge_lower_bound)},))
                elif m.edge < target_edge_lower_bound:
                    #    print(pre_calc_mall_edge[i])
                    mall_with_candidated_num_set_ls.append((m, {j for j in range(self.n_action) if (m.get_interval_utility(j) >= 0 and pre_calc_mall_edge[i][j] <= target_edge_upper_bound)},))
            mall_with_candidated_num_set_ls.sort(key=lambda x: x[0].volume, reverse=True)
        #  print(mall_with_candidated_num_set_ls)
            candidated_num_set_ls = [x[1] for x in mall_with_candidated_num_set_ls]
        #   print(f"candidated actions ls:{candidated_num_set_ls}")
            if candidated_num_set_ls == [set() for _ in range(len(mall_ls))]:
                chosen_action = self.random_action
                for m in mall_ls:
                    m.check_manipulation(False)
            else:
                tmp = {i for i in range(self.n_action)}
                tmp_bak = set()
                for s in candidated_num_set_ls:
                    if s:
                        tmp_bak = tmp
                        tmp = tmp.intersection(s)
                        if not tmp:
                            tmp = tmp_bak
                            break
                chosen_action_ls = list(tmp)
                if len(chosen_action_ls) > 1:
                    #  print("Manipulated. Tie breaking...")
                    chosen_action = self.tie_breaking(chosen_action_ls)
                    for m in mall_ls:
                        m.check_manipulation(True)
                elif len(chosen_action_ls) == 1:
                    #  print("Manipulated. No tie breaking...")
                    chosen_action = chosen_action_ls[0]
                    for m in mall_ls:
                        m.check_manipulation(True)
                else:
                    print("Something odd! Figure out this!")
                    assert True is False
        else:
            print("Something odd! Figure out this!")
            assert True is False
        return chosen_action

    def choice_func_3_v1(self, mall_ls, target_edge_upper_bound, target_edge_lower_bound):
        assert target_edge_upper_bound > target_edge_lower_bound
        assert self.external_interval is not None

        self.generate_random_action()

        pre_calc_mall_edge = self.pre_calculate_mall_edge_list(mall_ls)
        mall_with_candidated_num_set_ls = []

        if self.external_interval == 0:
            chosen_action = self.random_action
            for m in mall_ls:
                m.check_manipulation(False)
        elif self.external_interval >= 1:
            for i, m in enumerate(mall_ls):
                if m.edge > target_edge_upper_bound:
                    #    print(pre_calc_mall_edge[i])
                    mall_with_candidated_num_set_ls.append((m, {j for j in range(self.n_action) if (m.get_interval_utility(j) <= 0 and pre_calc_mall_edge[i][j] >= target_edge_lower_bound)},))
                elif m.edge < target_edge_lower_bound:
                    #    print(pre_calc_mall_edge[i])
                    mall_with_candidated_num_set_ls.append((m, {j for j in range(self.n_action) if (m.get_interval_utility(j) >= 0 and pre_calc_mall_edge[i][j] <= target_edge_upper_bound)},))
            mall_with_candidated_num_set_ls.sort(key=lambda x: x[0].volume, reverse=True)
            #  print(mall_with_candidated_num_set_ls)
            candidated_num_set_ls = [x[1] for x in mall_with_candidated_num_set_ls]
            #   print(f"candidated actions ls:{candidated_num_set_ls}")
            if candidated_num_set_ls == [set() for _ in range(len(mall_ls))]:
                chosen_action = self.random_action
                for m in mall_ls:
                    m.check_manipulation(False)
            else:
                tmp = {i for i in range(self.n_action)}
                tmp_bak = set()
                for s in candidated_num_set_ls:
                    if s:
                        tmp_bak = tmp
                        tmp = tmp.intersection(s)
                        if not tmp:
                            tmp = tmp_bak
                chosen_action_ls = list(tmp)
                if len(chosen_action_ls) > 1:
                    #  print("Manipulated. Tie breaking...")
                    chosen_action = self.tie_breaking(chosen_action_ls)
                    for m in mall_ls:
                        m.check_manipulation(True)
                elif len(chosen_action_ls) == 1:
                    #  print("Manipulated. No tie breaking...")
                    chosen_action = chosen_action_ls[0]
                    for m in mall_ls:
                        m.check_manipulation(True)
                else:
                    print("Something odd! Figure out this!")
                    assert True is False
        else:
            print("Something odd! Figure out this!")
            assert True is False
        return chosen_action
