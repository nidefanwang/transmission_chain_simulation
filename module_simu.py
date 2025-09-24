# module for transmission chain generation and simulation


# load packages
import numpy as np
import scipy
import random
import os


# function to set random number seed
def setup_seed(seed):
    random.seed(seed)
    os.environ['PYTHONISTA'] = str(seed)
    np.random.seed(seed)


# convert tree to nested dictionary to save the tree
def tree_to_dict(root_case):
    return {
        "infection_time": root_case.infection_time,
        "generation": root_case.generation,
        "secondary_cases": [tree_to_dict(child) for child in root_case.secondary_case]
    }


# define infected individuals class
class Case:
    def __init__(self, infection_time, generation):
        self.infection_time = infection_time
        self.generation = generation
        self.secondary_case = []


# function to generate transmission chain
def generate_tree(max_generation, max_time, fun_num_sec, fun_gi):

    index_case = Case(0, 0)  # index case

    def build_chain(cur_case, cur_generation):

        if cur_generation >= max_generation:
            return

        num_secondary = fun_num_sec()  # function to generate secondary cases number
        if num_secondary == 0:
            return

        for _ in range(num_secondary):
            infection_time_secondary = cur_case.infection_time + fun_gi()
            if infection_time_secondary > max_time:
                continue
            secondary_case = Case(infection_time_secondary, cur_generation+1)
            cur_case.secondary_case.append(secondary_case)
            build_chain(secondary_case, cur_generation + 1)  # subsequent transmission chain

    build_chain(index_case, 0)
    return index_case


# function for random number generation of sec_num or GI
def func_sec_gi(type_rv='sec_num', par1=2, par2=1e8):

    if type_rv == 'sec_num':  # random number for secondary cases, par1, par2 are mean and shape parameters of nbinom
        def ff():
            tmp_n = par2
            tmp_p = par2 / (par2 + par1)
            resul = np.random.negative_binomial(n=tmp_n, p=tmp_p)
            return resul
    elif type_rv == 'gi':  # random number for generation interval, par1, par2 are mean and var of gamma
        def ff():
            tmp_b = par2 / par1
            tmp_a = par1 / tmp_b
            tmp_l = scipy.stats.gamma.ppf(0.05, a=tmp_a, scale=tmp_b)
            tmp_r = scipy.stats.gamma.ppf(0.95, a=tmp_a, scale=tmp_b)
            resul = np.random.gamma(shape=tmp_a, scale=tmp_b)
            while resul < tmp_l or resul > tmp_r:
                resul = np.random.gamma(shape=tmp_a, scale=tmp_b)
            return resul
    else:
        print('error type')
        return

    return ff


# function to simulate and save
def fun_simu(n_simu=500, M = 1000, T=25, G_mean=5, G_var=9, R0=2.5, phi=1e8, seed=1):

    setup_seed(seed)
    forest = []
    for _ in range(n_simu):
        print(_)
        tmp_tree = generate_tree(M, T, fun_num_sec=func_sec_gi('sec_num', R0, phi),
                                 fun_gi=func_sec_gi('gi', G_mean, G_var))
        forest.append(tmp_tree)

    dict_forest = [tree_to_dict(tree) for tree in forest]  # convert trees to nested dictionary

    return dict_forest


# determine max generation according to T, input mean and var of generation interval
def M_from_T(T, epsilon, G_mean, G_var):
    b = G_var/G_mean
    a = G_mean/b
    G_epsilon = scipy.stats.gamma.ppf(epsilon, a=a, scale=b)
    M = int(T / G_epsilon)
    return M

