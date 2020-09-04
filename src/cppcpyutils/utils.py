import numpy as np


def mean(a, m):
    """masked mean

    Parameters
    ----------
    a : ndarray
        a grayscale image
    m : ndarray
        a binary image

    Returns
    -------
    mean of the grayscale image where the binary image is greater than 0 : float

    Raises
    ------
    RuntimeError
        if the image and mask do not have the same shape

    """

    if np.shape(m)!=np.shape(a):
        raise RuntimeError('The image and mask do not have the same shape')

    return(np.mean(a[np.where(m > 0)]))


def std(a, m):
    """masked standard deviation

    Parameters
    ----------
    a : ndarray
        a grayscale image
    m : ndarray
        a binary image

    Returns
    -------
    standard deviation of the grayscale image where the binary image is greater than 0 : float

    Raises
    ------
    RuntimeError
        if the image and mask do not have the same shape

    """

    if np.shape(m)!=np.shape(a):
        raise RuntimeError('The image and mask do not have the same shape')

    return(np.std(a[np.where(m > 0)]))
