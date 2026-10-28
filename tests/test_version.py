from scripts.check_version import version_report


def test_source_versions_match_pyproject():
    versions = version_report(include_installed=False)

    assert set(versions.values()) == {versions["pyproject"]}
