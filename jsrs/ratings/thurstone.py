import numpy as np
from scipy.stats import norm

# sample_data_text = '''0	72	73	70	73	73	69	60
# 2	0	32	1	18	6	2	1
# 1	42	0	1	19	17	2	1
# 4	73	73	0	59	63	44	22
# 1	56	5	15	0	24	9	7
# 1	68	57	11	50	0	15	10
# 5	72	72	30	65	59	0	18
# 14	73	73	52	67	64	56	0'''
# sample_data = [[int(cell) for cell in sample.split('\t')] for sample in sample_data_text.split('\n')]
#
# sample_matrix = np.array(sample_data)

def thurstone(ratings):
    '''ratings has columns:
    n: number of comparisons between a and b,
    f: number of times a was greater than b,
    a_id: a's id,
    b_id: b's id,
    subject_id: id of subject'''
    # ratings = ratings / n # TODO We are passing in a pre-normalized matrix
    ratings = norm.ppf(ratings)
    ratings = [
        np.mean([cell if ~np.isinf(cell) else 0.0 for cell in rating])
        for rating in ratings.T
    ]
    return ratings

# print(thurstone(sample_matrix[0, 1] + sample_matrix[1, 0], sample_matrix))
