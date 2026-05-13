from app.infrastructure.metrics import render_prometheus_text


def test_render_prometheus_text_includes_counter_and_gauge_types() -> None:
    output = render_prometheus_text(
        counters={"enerlytica_records_received_total": 2.0},
        gauges={"enerlytica_data_freshness_seconds": 10.5},
    )

    assert "# TYPE enerlytica_records_received_total counter" in output
    assert "enerlytica_records_received_total 2.0" in output
    assert "# TYPE enerlytica_data_freshness_seconds gauge" in output
    assert "enerlytica_data_freshness_seconds 10.5" in output
