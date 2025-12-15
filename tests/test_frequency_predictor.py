from aac.predictors.frequency import FrequencyPredictor


def test_frequency_predictor_orders_by_frequency() -> None:
    predictor = FrequencyPredictor(
        {
            "hello": 10,
            "help": 5,
            "helium": 1,
            "world": 20,
        }
    )

    results = predictor.predict("he")

    values = [r.suggestion.value for r in results]
    scores = [r.score for r in results]

    assert set(values) == {"hello", "help", "helium"}
    assert scores == [10.0, 5.0, 1.0]
