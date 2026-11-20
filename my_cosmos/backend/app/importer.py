"""Import a CSV corpus into the JSON format used by the COSMOS API."""

import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path
from typing import Iterable


COUNTRY_ALIASES = {
    "usa": "United States",
    "us": "United States",
    "u.s.": "United States",
    "u.s.a.": "United States",
    "united states of america": "United States",
}


def clean_title(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def canonical_doi(text: str) -> str:
    value = text.strip().lower()
    value = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", value)
    value = re.sub(r"^doi:\s*", "", value)
    return value


def normalize_country(text: str) -> str:
    value = text.strip()
    if not value:
        return ""
    return COUNTRY_ALIASES.get(value.lower(), value)


def split_list(text: str, separators: Iterable[str] = (";", "|")) -> list[str]:
    value = text.strip()
    if not value:
        return []

    try:
        parsed = json.loads(value)
        if isinstance(parsed, list):
            return [str(item).strip() for item in parsed if str(item).strip()]
    except json.JSONDecodeError:
        pass

    pattern = "|".join(re.escape(separator) for separator in separators)
    return [item.strip() for item in re.split(pattern, value) if item.strip()]


def load_taxonomy(folder: Path) -> dict:
    taxonomy_path = folder / "taxonomy.json"
    if taxonomy_path.exists():
        return json.loads(taxonomy_path.read_text(encoding="utf-8"))
    return {"domains": [], "countries": []}


def taxonomy_topics(taxonomy: dict) -> set[str]:
    return {topic for domain in taxonomy.get("domains", []) for topic in domain.get("topics", [])}


def build_paper(row: dict[str, str], source_id: str, year: int, taxonomy: dict) -> dict:
    doi = canonical_doi(row.get("doi", ""))
    organizations = split_list(row.get("institutions", ""))
    methods = split_list(row.get("methods", ""), (";", "|", ","))
    raw_topics = split_list(row.get("topics", ""))
    known_topics = taxonomy_topics(taxonomy)
    topics = []
    for topic in raw_topics:
        topics.append(topic if topic in known_topics else "Other topics")

    return {
        "paper_id": row.get("id", "").strip() or source_id,
        "title": row.get("title", "").strip(),
        "abstract": row.get("abstract", "").strip(),
        "authors": [],
        "publication_date": f"{year}-01-01",
        "publication_year": year,
        "journal": row.get("journal", "").strip() or None,
        "conference": None,
        "publisher": None,
        "doi": doi or None,
        "source_url": None,
        "open_access_url": None,
        "country": normalize_country(row.get("affiliation_country", "")),
        "organizations": organizations,
        "citation_count": None,
        "reference_count": None,
        "research_type": "journal-article",
        "derived": {
            "topics": list(dict.fromkeys(topics)),
            "subtopics": [],
            "missions": [],
            "spacecraft": [],
            "technologies": [],
            "methods": list(dict.fromkeys(methods)),
            "entities": [],
            "keywords": [],
            "embedding_reference": None,
        },
        "is_synthetic": False,
    }


def import_csv(csv_path: Path, out_dir: Path | None = None, dry_run: bool = False) -> dict:
    data_folder = Path(__file__).resolve().parent.parent / "data"
    taxonomy = load_taxonomy(data_folder)
    known_topics = taxonomy_topics(taxonomy)
    known_countries = {item["name"] for item in taxonomy.get("countries", [])}

    with csv_path.open("r", encoding="utf-8-sig", newline="") as file:
        rows = list(csv.DictReader(file))

    papers = []
    seen_titles = set()
    seen_dois = set()
    skipped = Counter()
    duplicates = Counter()
    unknown_countries = Counter()
    unknown_topics = Counter()

    for index, row in enumerate(rows, start=1):
        title = row.get("title", "").strip()
        abstract = row.get("abstract", "").strip()
        if not title:
            skipped["no title"] += 1
            continue
        if not abstract:
            skipped["no abstract"] += 1
            continue

        year_text = str(row.get("year", "")).strip()
        if not year_text:
            year_text = str(row.get("date", "")).strip().split("-", 1)[0]
        try:
            year = int(year_text)
        except (TypeError, ValueError):
            skipped["invalid year"] += 1
            continue
        if not 1950 <= year <= 2100:
            skipped["invalid year"] += 1
            continue

        normalized_title = clean_title(title)
        doi = canonical_doi(row.get("doi", ""))
        if normalized_title in seen_titles:
            duplicates["same title"] += 1
            continue
        if doi and doi in seen_dois:
            duplicates["same doi"] += 1
            continue

        paper = build_paper(row, f"imported-{index:05d}", year, taxonomy)
        papers.append(paper)
        seen_titles.add(normalized_title)
        if doi:
            seen_dois.add(doi)

        country = paper["country"]
        if country and country not in known_countries:
            unknown_countries[country] += 1
        for topic in split_list(row.get("topics", "")):
            if topic not in known_topics:
                unknown_topics[topic] += 1

    report = {
        "rows_in": len(rows),
        "papers_out": len(papers),
        "skipped": dict(skipped),
        "duplicates_removed": sum(duplicates.values()),
        "duplicates": dict(duplicates),
        "columns_used": {
            "paper_id": "id",
            "title": "title",
            "abstract": "abstract",
            "year": "year",
            "doi": "doi",
            "country": "affiliation_country",
            "organizations": "institutions",
            "topics": "topics",
            "methods": "methods",
        },
        "countries_without_iso_code": dict(unknown_countries),
        "topics_outside_taxonomy": dict(unknown_topics),
    }

    if not dry_run:
        destination = out_dir or (Path(__file__).resolve().parent.parent / "data_real")
        destination.mkdir(parents=True, exist_ok=True)
        (destination / "papers.json").write_text(
            json.dumps(papers, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        (destination / "taxonomy.json").write_text(
            json.dumps(taxonomy, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        (destination / "manifest.json").write_text(
            json.dumps({"source": str(csv_path), "paper_count": len(papers)}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        (destination / "report.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Import a COSMOS CSV export")
    parser.add_argument("csv")
    parser.add_argument("--out", help="Output directory")
    parser.add_argument("--dry-run", action="store_true", help="Validate without writing files")
    args = parser.parse_args()

    report = import_csv(
        Path(args.csv),
        out_dir=Path(args.out) if args.out else None,
        dry_run=args.dry_run,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if args.dry_run:
        print("Dry run: nothing written.")


if __name__ == "__main__":
    main()
