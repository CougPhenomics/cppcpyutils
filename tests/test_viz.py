import pytest
import cppcpyutils as cppc
import numpy as np
import matplotlib

def test_get_colors_badinput():
    TEST_CMAP = 'test'
    with pytest.raises(ValueError):
        cppc.viz.get_colors(TEST_CMAP)


def test_get_colors_imagingwin():
    cols = cppc.viz.get_colors('imagingwin')
    assert (cols[0:10] == np.array([0, 0, 0, 1])).all()


def test_get_colors_hue():
    cols = cppc.viz.get_colors('hue')
    assert isinstance(cols,np.ndarray)


def test_get_cmap():
    cmap = cppc.viz.get_cmap('hue')
    assert isinstance(cmap, matplotlib.colors.ListedColormap)
