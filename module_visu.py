# module for transmission chain visualization and processing


# load packages
import module_simu


# visualization of transmission chain
def print_tree(case, depth=0):
    print("--" * depth + f"Case({case.infection_time})" + f"Case({case.generation})")
    for second in case.secondary_case:
        print_tree(second, depth + 1)


# function to traverse transmission chain of Class 'Case' to get infection time and number of secondary cases
def collect_case_info(index_case):

    infec_times, generation, num_sec = [], [], []

    def traverse(case):
        infec_times.append(case.infection_time)
        generation.append(case.generation)
        num_sec.append(len(case.secondary_case))
        for child in case.secondary_case:
            traverse(child)

    traverse(index_case)
    return infec_times, generation, num_sec


# get time series data of transmission chain on [0,T]
def get_ts_from_tree(tree, T):

    vals, gen, nsec = collect_case_info(tree)
    t_intervals = [(i, i + 1) for i in range(int(T))]
    num_new_infections = [0] * len(t_intervals)
    for i, (start, end) in enumerate(t_intervals):
        for t in vals:
            if start < t <= end:
                num_new_infections[i] += 1
    num_new_infections.insert(0, 1)  # add index case to first position

    return num_new_infections


# rebuild the tree structure from the dictionary, data is a node
def dict_to_tree(data):
    root = module_simu.Case(data["infection_time"], data['generation'])
    for child_data in data["secondary_cases"]:
        child = dict_to_tree(child_data)
        root.secondary_case.append(child)
    return root

