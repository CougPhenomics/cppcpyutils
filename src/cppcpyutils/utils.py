import numpy as np


def mean(a, m):
    '''
    Input:
        a: numpy array
        m: binary mask
    Output:
        float number
    '''

    return(np.mean(a[np.where(m > 0)]))


def std(a, m):
    '''
    Input:
        a: numpy array
        m: binary mask
    Output:
        float number
    '''
    return(np.std(a[np.where(m > 0)]))
