import cv2
import numpy as np


def greenness_index(img, mask):
    """Compute greenness index

    Parameters
    ----------
    img: numpy array
        rgb image
    mask: numpy-array
        binary image


    Returns
    -------
    grayscale image : numpy array

    """

    # Compute greenness
    # split color channels
    b, g, r = cv2.split(img)
    # print green intensity
    # g_img = pcv.visualize.pseudocolor(g, cmap='Greens', background='white', min_value=0, max_value=255, mask=mask, axes=False)

    # convert color channels to int16 so we can add them (values will be greater than 255 which is max of current uint8 format)
    g = g.astype('uint16')
    r = r.astype('uint16')
    b = b.astype('uint16')
    denom = g + r + b

    # greenness index
    out_flt = np.zeros_like(denom, dtype='float32')
    # divide green by sum of channels to compute greenness index with values 0-1
    gi = np.divide(g, denom, out=out_flt,
                   where=np.logical_and(denom != 0, mask > 0))

    return gi
