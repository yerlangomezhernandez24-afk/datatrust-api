from scripts.smoke_http_e2e import run_smoke


def test_real_loopback_http_flow_uses_temporary_database():
    result = run_smoke()

    assert result["host"] == "127.0.0.1"
    assert result["health"] == 200
    assert result["dashboard"] == 200
    assert result["security_headers"] == {
        "health_nosniff": "nosniff",
        "dashboard_frame_options": "DENY",
    }
    assert result["profiles"] == 200
    assert result["upload"] == 201
    assert result["selected_profile"] == "orders_usd_v1"
    assert result["list"] == 200
    assert result["detail"] == 200
    assert result["first_issue_page"] == 200
    assert result["last_issue_page"] == 200
    assert result["export"] == 200
    assert result["export_has_bom"] is True
    assert result["unknown_run"] == 404
    assert result["oversized_upload"] == 413
    assert result["oversized_upload_persisted"] is False
    assert result["temporary_database_removed"] is True
