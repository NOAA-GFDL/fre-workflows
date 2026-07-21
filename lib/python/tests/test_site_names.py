"""Regression tests for PPAN site and platform names."""

from pathlib import Path


REPOSITORY_ROOT = Path(__file__).parents[3]


def test_ppan_site_names_are_consistent():
    """The EPMT site is the default and legacy names are fully retired."""
    epmt_site = REPOSITORY_ROOT / "site" / "ppan_epmt.cylc"
    noepmt_site = REPOSITORY_ROOT / "site" / "ppan_noepmt.cylc"
    local_settings = REPOSITORY_ROOT / "for_gh_runner" / "yaml_workflow" / "local_settings.yaml"
    global_config = REPOSITORY_ROOT / "global" / "gfdl_ppan_global.cylc"

    assert epmt_site.is_file()
    assert noepmt_site.is_file()
    assert not (REPOSITORY_ROOT / "site" / "ppan_test.cylc").exists()
    assert not (REPOSITORY_ROOT / "site" / "ppan.cylc").exists()
    assert "platform = ppan_epmt" in epmt_site.read_text(encoding="utf-8")
    assert "platform = ppan_noepmt" in noepmt_site.read_text(encoding="utf-8")
    assert 'site:                    "ppan_epmt"' in local_settings.read_text(encoding="utf-8")
    assert "[[ppan_epmt]]" in global_config.read_text(encoding="utf-8")
    assert "[[ppan_noepmt]]" in global_config.read_text(encoding="utf-8")
