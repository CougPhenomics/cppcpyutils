from mpl_toolkits.axes_grid1.anchored_artists import AnchoredSizeBar
import matplotlib.font_manager as fm
import numpy as np
from matplotlib import cm
from matplotlib.colors import ListedColormap


def add_scalebar(pseudoimg,
                 pixelresolution,
                 barwidth,
                 barlabel,
                 barlocation='lower center',
                 fontprops=None,
                 scalebar=None):
    """Add scalebar to matplotlib false color image

    Parameters
    ----------
    pseudoimg : matplotlib figure
        false color image
    pixelresolution : int
        physical size represented by a pixel in mm
    barwidth : float
        size of the scale bar in mm
    barlabel : str
        text for the bar label
    barlocation : str or tuple
        position of scale bar in figure, optional
    fontprops : mpl.fm
        font properties as specified by matplotlib.font_manager, optional
    scalebar : mpl axis object
        a preestablished scale bar, optional

    Returns
    -------
    pseudoimg with a scalebar : matplotlib figure

    """

    if fontprops is None:
        fontprops = fm.FontProperties(size=8, weight='bold')

    ax = pseudoimg.gca()

    if scalebar is None:
        scalebar = AnchoredSizeBar(ax.transData,
                                   barwidth / pixelresolution,
                                   barlabel,
                                   barlocation,
                                   pad=0.15,
                                   sep=3,
                                   color='white',
                                   frameon=False,
                                   size_vertical=barwidth/pixelresolution/40,
                                   fontproperties=fontprops)

    ax.add_artist(scalebar)

    return ax.get_figure()


def get_colors(style='imagingwin'):
    """
    Parameters
    ----------
    style : str
        name of custom color palette. Default is "imagingwin"

    Returns
    -------
    an array of colors : ndarray


    Raises
    ------
    ValueError
        if style is not recognized

    """

    if style == 'imagingwin':
        hsv = cm.get_cmap('hsv', 256)
        newcolors = hsv(np.linspace(0, 1, 256))
        keep = newcolors[5:-25, :]
        newcolors = np.vstack((keep[:10, :], keep))
        black = np.array([0, 0, 0, 1])
        newcolors[:10, :] = black

    elif style == 'hue':
        hsv = cm.get_cmap('hsv', 256)
        hsvcolors = hsv(np.linspace(0, 1, 256))
        newcolors = hsvcolors[0:127]

    else:
        raise ValueError('that color map is not supported')

    return newcolors


def get_cmap(style='imagingwin'):
    """
    Parameters
    ----------
    style : str
        name of custom color palette. Default is "imagingwin"

    Returns
    -------
    a matplotlib Colormap

    """

    cmapcolors = get_colors(style)
    newcmp = ListedColormap(cmapcolors)

    return newcmp
