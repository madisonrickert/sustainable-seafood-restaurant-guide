#!/usr/bin/env python3
"""
Download and extract Seafood Watch recommendation data.

Downloads the Seafood Watch Complete Recommendation List PDF from the
Monterey Bay Aquarium and extracts species ratings into a structured
markdown reference file for use by the restaurant guide skill.

Requires: pdfplumber (installed automatically via uv)

Usage:
    uv run --with pdfplumber scripts/fetch-seafood-watch.py

The extracted data is written to references/seafood-watch-ratings.md.
This file is .gitignored because it contains copyrighted data from the
Monterey Bay Aquarium — each user must download their own copy.
"""

import re
import sys
import urllib.request
from collections import defaultdict
from datetime import date
from pathlib import Path

PDF_URL = "https://www.seafoodwatch.org/globalassets/sfw/pdf/whats-new/seafood-watch-complete-recommendation-list.pdf"
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "references"
OUTPUT_FILE = OUTPUT_DIR / "seafood-watch-ratings.md"
PDF_CACHE = OUTPUT_DIR / ".seafood-watch.pdf"

COLOR_MAP = {
    "Green": "Best Choice",
    "Blue": "Certified",
    "Yellow": "Good Alternative",
    "Red": "Avoid",
}


def download_pdf():
    """Download the Seafood Watch PDF if not already cached."""
    if PDF_CACHE.exists():
        print(f"  Using cached PDF: {PDF_CACHE}")
        return PDF_CACHE

    print(f"  Downloading from {PDF_URL}...")
    req = urllib.request.Request(PDF_URL, headers={
        "User-Agent": "Mozilla/5.0 (sustainable-seafood-guide data fetcher)"
    })
    with urllib.request.urlopen(req) as resp, open(PDF_CACHE, "wb") as f:
        f.write(resp.read())
    print(f"  Saved to {PDF_CACHE}")
    return PDF_CACHE


def extract_rows(pdf_path):
    """Extract table rows from the PDF using pdfplumber."""
    try:
        import pdfplumber
    except ImportError:
        print("Error: pdfplumber is required. Run with:")
        print("  uv run --with pdfplumber scripts/fetch-seafood-watch.py")
        sys.exit(1)

    print("  Extracting tables from PDF...")
    all_rows = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                for row in table:
                    if row and len(row) >= 2:
                        all_rows.append(row)

    # Also extract raw text for fallback grep searching
    raw_text = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                raw_text.append(text)

    return all_rows, "\n".join(raw_text)


def parse_entries(rows):
    """Parse table rows into structured entries grouped by color/rating."""
    entries_by_color = defaultdict(list)
    skipped = 0

    for row in rows:
        # Try to find the color in the last few columns
        color = None
        score = None
        cells = [str(c).strip() if c else "" for c in row]

        for cell in reversed(cells):
            if cell in ("Green", "Blue", "Yellow", "Red"):
                color = cell
                break

        if not color:
            skipped += 1
            continue

        # Try to extract score (float near the end)
        for cell in reversed(cells):
            try:
                val = float(cell)
                if 0 < val < 11:  # Scores are 0-10 range
                    score = val
                    break
            except (ValueError, TypeError):
                continue

        common_name = cells[0] if cells[0] else ""
        sci_name = cells[1] if len(cells) > 1 else ""
        wild_farmed = cells[2] if len(cells) > 2 else ""
        country = cells[3] if len(cells) > 3 else ""

        # Try to find method and body of water from middle columns
        method = ""
        body_of_water = ""
        for i, cell in enumerate(cells):
            if any(kw in cell.lower() for kw in ["trawl", "line", "pot", "net", "seine", "dredge", "hook", "trap", "hand", "culture", "pond", "tank", "cage"]):
                method = cell
            if any(kw in cell.lower() for kw in ["ocean", "pacific", "atlantic", "gulf", "sea", "bay", "indian"]):
                body_of_water = cell

        # Find certification if present
        cert = ""
        for cell in cells:
            if any(kw in cell for kw in ["Marine Stewardship", "Aquaculture Stewardship", "MSC", "ASC", "BAP", "Naturland", "Friend of the Sea"]):
                cert = cell
                break

        if common_name and common_name != "Common Name":  # Skip header rows
            entries_by_color[color].append({
                "common_name": common_name,
                "sci_name": sci_name,
                "wild_farmed": wild_farmed,
                "country": country,
                "body_of_water": body_of_water,
                "method": method,
                "cert": cert,
                "score": score,
            })

    print(f"  Skipped {skipped} non-data rows")
    return entries_by_color


def group_by_species(entries):
    """Group entries by common name and wild/farmed status."""
    groups = defaultdict(list)
    for entry in entries:
        key = (entry["common_name"], entry["sci_name"])
        groups[key].append(entry)
    return dict(sorted(groups.items(), key=lambda x: x[0][0].lower()))


def build_markdown(entries_by_color, raw_text):
    """Build the markdown reference file."""
    total = sum(len(e) for e in entries_by_color.values())

    lines = [
        "# Seafood Watch Complete Recommendation List",
        "",
        "> **Source:** Monterey Bay Aquarium Seafood Watch Program",
        f"> **Downloaded:** {date.today().isoformat()}",
        f"> **URL:** {PDF_URL}",
        "",
        "Seafood Watch is a registered trademark of the Monterey Bay Aquarium Foundation.",
        "This file is for personal use only and must not be redistributed.",
        "Run `scripts/fetch-seafood-watch.py` to regenerate.",
        "",
        "---",
        "",
        "## Rating System",
        "",
        "| Rating | Color | Score Range | Meaning |",
        "|--------|-------|-------------|---------|",
        "| Best Choice | Green | ~3.5+ | Well managed, caught/farmed responsibly |",
        "| Certified | Blue | Varies | Third-party certified sustainable (MSC, ASC, etc.) |",
        "| Good Alternative | Yellow | ~2.5-3.49 | Some concerns with management or harvest |",
        "| Avoid | Red | <2.5 | Overfished, poorly managed, or harmful methods |",
        "",
        f"**Total entries in database:** {total}",
    ]

    # Summary counts
    for color in ["Green", "Blue", "Yellow", "Red"]:
        label = COLOR_MAP[color]
        count = len(entries_by_color.get(color, []))
        lines.append(f"- {label} ({color}): {count} entries")

    lines.extend(["", "---", ""])

    # Write each section
    section_order = [("Green", "Best Choice"), ("Blue", "Certified"),
                     ("Yellow", "Good Alternative"), ("Red", "Avoid")]

    for color, label in section_order:
        entries = entries_by_color.get(color, [])
        lines.append(f"## {label} ({color})")
        lines.append("")

        if not entries:
            lines.append("(No entries found)")
            lines.extend(["", "---", ""])
            continue

        description = {
            "Green": "Species that are well managed and caught or farmed in ways that cause little harm to habitats or other wildlife.",
            "Blue": "Species that are third-party certified as sustainable by MSC, ASC, or equivalent bodies.",
            "Yellow": "Species with some concerns around management, harvest methods, or environmental impact.",
            "Red": "Species that are overfished, poorly managed, or caught/farmed in ways that harm the environment.",
        }
        lines.append(description.get(color, ""))
        lines.append("")

        grouped = group_by_species(entries)
        for (common_name, sci_name), species_entries in grouped.items():
            if sci_name and sci_name != common_name:
                lines.append(f"### {common_name} (*{sci_name}*)")
            else:
                lines.append(f"### {common_name}")
            lines.append("")

            # Group by wild/farmed
            wild = [e for e in species_entries if "Wild" in e["wild_farmed"] or "wild" in e["wild_farmed"].lower()]
            farmed = [e for e in species_entries if "Farm" in e["wild_farmed"] or "farm" in e["wild_farmed"].lower()]
            other = [e for e in species_entries if e not in wild and e not in farmed]

            for category, cat_entries in [("Wild-Caught", wild), ("Farmed", farmed), ("", other)]:
                if not cat_entries:
                    continue
                if category:
                    lines.append(f"**{category}**")

                countries = sorted(set(e["country"] for e in cat_entries if e["country"]))
                if countries:
                    lines.append(f"- **Origin:** {', '.join(countries)}")

                waters = sorted(set(e["body_of_water"] for e in cat_entries if e["body_of_water"]))
                if waters:
                    lines.append(f"- **Waters:** {', '.join(waters)}")

                methods = sorted(set(e["method"] for e in cat_entries if e["method"]))
                if methods:
                    lines.append(f"- **Methods:** {', '.join(methods)}")

                certs = sorted(set(e["cert"] for e in cat_entries if e["cert"]))
                if certs:
                    lines.append(f"- **Certifications:** {', '.join(certs)}")

                scores = [e["score"] for e in cat_entries if e["score"] is not None]
                if scores:
                    if len(scores) == 1:
                        lines.append(f"- **Score:** {scores[0]:.2f}")
                    else:
                        lines.append(f"- **Score range:** {min(scores):.2f} - {max(scores):.2f} (avg {sum(scores)/len(scores):.2f})")

                lines.append("")

        lines.extend(["---", ""])

    # Quick reference table for common restaurant species
    lines.append("## Quick Reference: Common Restaurant Species")
    lines.append("")
    lines.append("Search the sections above for detailed entries. Common menu names to grep for:")
    lines.append("")
    common_species = [
        "salmon", "tuna", "shrimp", "lobster", "crab", "cod", "halibut",
        "swordfish", "snapper", "bass", "oyster", "mussel", "clam",
        "scallop", "squid", "octopus", "tilapia", "catfish", "trout",
        "grouper", "mahi", "urchin", "abalone", "prawn", "lingcod",
        "steelhead", "rockfish", "anchovy", "sardine",
    ]
    for species in common_species:
        lines.append(f"- `{species}`")
    lines.append("")

    return "\n".join(lines)


def main():
    print("Seafood Watch Data Fetcher")
    print("=" * 40)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Download
    pdf_path = download_pdf()

    # Extract
    rows, raw_text = extract_rows(pdf_path)
    print(f"  Extracted {len(rows):,} table rows")

    # Parse
    entries_by_color = parse_entries(rows)
    for color in ["Green", "Blue", "Yellow", "Red"]:
        label = COLOR_MAP[color]
        print(f"  {label} ({color}): {len(entries_by_color.get(color, []))} entries")

    # Build markdown
    markdown = build_markdown(entries_by_color, raw_text)

    # Write
    OUTPUT_FILE.write_text(markdown)
    print(f"\n  Written to {OUTPUT_FILE}")
    print(f"  File size: {OUTPUT_FILE.stat().st_size:,} bytes")
    print(f"  Line count: {len(markdown.splitlines()):,}")
    print("\nDone! The skill can now reference this file for sustainability lookups.")


if __name__ == "__main__":
    main()


