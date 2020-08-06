from mpl_toolkits.axes_grid1.anchored_artists import AnchoredSizeBar
import matplotlib.font_manager as fm


def add_scalebar(pseudoimg,
                 pixelresolution,
                 barwidth,
                 barlabel,
                 barlocation='lower center',
                 fontprops=None,
                 scalebar=None):
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
