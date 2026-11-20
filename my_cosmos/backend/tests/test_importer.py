from pathlib import Path

from app.importer import canonical_doi, clean_title, import_csv, normalize_country


CSV_PATH = Path(__file__).resolve().parents[2] / "sample_export.csv"


def test_csv_dry_run_matches_lesson_18():
    report = import_csv(CSV_PATH, dry_run=True)

    assert report["rows_in"] == 6
    assert report["papers_out"] == 3
    assert report["skipped"] == {"no abstract": 1}
    assert report["duplicates_removed"] == 2


def test_normalization_and_duplicates():
    assert canonical_doi("https://doi.org/10.1/ABC") == "10.1/abc"
    assert normalize_country("U.S.A.") == "United States"
    assert normalize_country("Atlantis") == "Atlantis"
    assert clean_title("Optical Navigation for Small Bodies!") == "optical navigation for small bodies"
