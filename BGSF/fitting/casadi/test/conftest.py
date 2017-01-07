"""
"""
import pytest

def pytest_addoption(parser):
    try:
        parser.addoption(
            "--plot",
            action="store_true",
            dest='plot',
            help="Have tests update plots (it is slow)",
        )
    except ValueError:
        #triggers when another conftest has added this already
        pass

@pytest.fixture
def plot(request):
    return request.config.getoption("--plot")
