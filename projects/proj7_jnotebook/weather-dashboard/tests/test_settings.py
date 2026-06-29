from weather_dashboard.settings import DEFAULT_CITY, DEFAULT_UNITS


def test_default_settings():
    assert DEFAULT_CITY == "Berlin"
    assert DEFAULT_UNITS == "metric"
