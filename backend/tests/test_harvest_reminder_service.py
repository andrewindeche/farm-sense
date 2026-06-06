from app.services.harvest_reminder import harvest_reminder_service


def test_suggest_frost():
    weather = {"current": {"temp_c": 2, "humidity": 70, "condition": {"text": "Cloudy"}, "precip_mm": 0}}
    result = harvest_reminder_service.suggest(weather)
    assert "frost" in result.lower()
    assert "immediately" in result.lower()


def test_suggest_hot_dry():
    weather = {"current": {"temp_c": 35, "humidity": 25, "condition": {"text": "Sunny"}, "precip_mm": 0}}
    result = harvest_reminder_service.suggest(weather)
    assert "early" in result.lower()
    assert "hot and dry" in result.lower()


def test_suggest_heavy_rain():
    weather = {"current": {"temp_c": 25, "humidity": 80, "condition": {"text": "Rain"}, "precip_mm": 15}}
    result = harvest_reminder_service.suggest(weather)
    assert "delay harvest" in result.lower()


def test_suggest_favorable_warm_dry():
    weather = {"current": {"temp_c": 24, "humidity": 45, "condition": {"text": "Clear"}, "precip_mm": 0}}
    result = harvest_reminder_service.suggest(weather)
    assert "favorable" in result.lower()
    assert "ideal window" in result.lower()


def test_suggest_extreme_heat():
    weather = {"current": {"temp_c": 38, "humidity": 30, "condition": {"text": "Sunny"}, "precip_mm": 0}}
    result = harvest_reminder_service.suggest(weather)
    assert "extreme heat" in result.lower()
    assert "morning" in result.lower()


def test_harvest_reminder_zero_temp_c_not_falsy():
    weather = {"current": {"temp_c": 0, "temperature": 25, "humidity": 70, "condition": {"text": "Cloudy"}, "precip_mm": 0}}
    result = harvest_reminder_service.suggest(weather)
    assert "frost" in result.lower()


def test_harvest_reminder_zero_humidity_not_falsy():
    weather = {"current": {"temp_c": 35, "humidity": 0, "humid": 80, "condition": {"text": "Sunny"}, "precip_mm": 0}}
    result = harvest_reminder_service.suggest(weather)
    assert "early" in result.lower()


def test_harvest_reminder_zero_precip_not_falsy():
    weather = {"current": {"temp_c": 24, "humidity": 45, "condition": {"text": "Clear"}, "precip_mm": 0, "rain": 10}}
    result = harvest_reminder_service.suggest(weather)
    assert "favorable" in result.lower()


def test_harvest_reminder_missing_current_defaults_to_zero():
    result = harvest_reminder_service.suggest({})
    assert "freezing" in result.lower() or "frost" in result.lower()
