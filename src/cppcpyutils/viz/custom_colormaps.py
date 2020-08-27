import numpy as np
from matplotlib import cm
from matplotlib.colors import ListedColormap


def get_colors(style='imagingwin'):
    '''
    Input:
        style - define custom colors. Default is "imagingwin".
    Returns:
        an array of colors
    '''

    if style == 'imagingwin':
        hsv = cm.get_cmap('hsv', 256)
        newcolors = hsv(np.linspace(0, 1, 256))
        keep = newcolors[5:-25,:]
        newcolors = np.vstack((keep[:10,:],keep))
        black = np.array([0, 0, 0, 1])
        newcolors[:10,:] = black

    elif style == 'hue':
        hsv = cm.get_cmap('hsv', 256)
        hsvcolors = hsv(np.linspace(0, 1, 256))
        newcolors = hsvcolors[0:127]

    else:
        raise ValueError('that color map is not supported')

    return newcolors


def get_cmap(style='imagingwin'):
    '''
    Input:
        style - choose your custom colormap by name. Default is "imagingwin".
    Output:
        a colormap for use with matplotlib
    '''

    cmapcolors = get_colors(style)
    newcmp = ListedColormap(cmapcolors)

    return newcmp
