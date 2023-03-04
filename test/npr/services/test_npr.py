from npr.services.npr import NPRAPI


def test_npr():
    """
    This is one of the very few integration tests in this suite.
    It is meant to be a canary for when NPR updates their API.

    This test is meant to throw if we cannot consume the upstream api.
    """
    api = NPRAPI()
    found = api.search_stations("wxxi")
    assert found
