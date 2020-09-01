import pytest
import numpy as np
import cppcpyutils as cppc

TEST_NP = np.array([1,2,3])
TEST_MASK = np.array([1,0,1])

def test_mean():
    assert cppc.utils.mean(TEST_NP, TEST_MASK) == 2


def test_std():
    assert cppc.utils.std(TEST_NP, TEST_MASK) == 1

