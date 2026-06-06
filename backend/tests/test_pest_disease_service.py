from app.services.pest_disease import pest_disease_service


def test_suggest_very_humid_warm():
    weather = {"current": {"temp_c": 30, "humidity": 85, "condition": {"text": "Overcast"}, "precip_mm": 0}}
    result = pest_disease_service.suggest(weather)
    assert "leaf spot" in result.lower()
    assert "humid" in result.lower()


def test_suggest_very_humid_cool():
    weather = {"current": {"temp_c": 18, "humidity": 90, "condition": {"text": "Drizzle"}, "precip_mm": 2}}
    result = pest_disease_service.suggest(weather)
    assert "root rot" in result.lower()
    assert "cool" in result.lower()


def test_suggest_hot_dry():
    weather = {"current": {"temp_c": 35, "humidity": 25, "condition": {"text": "Sunny"}, "precip_mm": 0}}
    result = pest_disease_service.suggest(weather)
    assert "spider mites" in result.lower()
    assert "dry" in result.lower()


def test_suggest_warm_humid():
    weather = {"current": {"temp_c": 26, "humidity": 70, "condition": {"text": "Rain"}, "precip_mm": 8}}
    result = pest_disease_service.suggest(weather)
    assert "aphids" in result.lower()
    assert "rain" in result.lower()


def test_suggest_steady_rain_warmth():
    weather = {"current": {"temp_c": 22, "humidity": 55, "condition": {"text": "Rain"}, "precip_mm": 6}}
    result = pest_disease_service.suggest(weather)
    assert "black sigatoka" in result.lower()
    assert "rain" in result.lower()


def test_pest_disease_zero_temp_c_not_falsy():
    weather = {"current": {"temp_c": 0, "humidity": 90, "condition": {"text": "Drizzle"}, "precip_mm": 2}}
    result = pest_disease_service.suggest(weather)
    assert "root rot" in result.lower()


def test_pest_disease_zero_humidity_not_falsy():
    weather = {"current": {"temp_c": 35, "humidity": 0, "humid": 50, "condition": {"text": "Sunny"}, "precip_mm": 0}}
    result = pest_disease_service.suggest(weather)
    assert "spider mites" in result.lower()


def test_pest_disease_missing_current_returns_default():
    result = pest_disease_service.suggest({})
    assert "general leaf spot" in result.lower()
