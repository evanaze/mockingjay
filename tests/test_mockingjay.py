"""Test the main Mockingjay package."""
from src.mockingjay import __version__


def test_version():
    """Test the version number of the package."""
    assert __version__ == "0.1.0"
