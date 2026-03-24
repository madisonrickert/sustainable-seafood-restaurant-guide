# Sustainable Seafood Restaurant Guide

A [Claude Code](https://claude.com/claude-code) skill that generates interactive HTML dining guides for any restaurant, cross-referencing menu items against [Seafood Watch](https://www.seafoodwatch.org/) sustainability ratings and your dietary constraints.

## What it does

Give it a restaurant menu (pasted text, URL, photo, or PDF) and your dietary needs, and it produces a single self-contained `.html` file you can open on your phone at the table. The guide includes:

- **My Order** — a numbered recommended order balancing sustainability and dietary compatibility
- **Full Menu** — every dish assessed with color-coded sustainability badges (Best Choice / Good Alternative / Avoid) and dietary flags (dairy, egg, gluten, etc.)
- **Drinks** — wine/beer pairings sourced from reviews and the restaurant's drink list
- **Ask Server** — specific questions to verify ingredients, prioritized by importance
- **Restaurant Background** — sourcing philosophy, suppliers, and sustainability commitments
- **Sources** — linked references for all sustainability data and restaurant research

## Install

### Claude Code

```bash
npx skills install https://github.com/madisonrickert/sustainable-seafood-restaurant-guide
```

### Manual

Clone the repo and copy the skill directory to your Claude Code skills path (`~/.claude/skills/`).

## Seafood Watch data

The sustainability database is not included in the repo (it's copyrighted by the Monterey Bay Aquarium). **The skill automatically runs the fetch script on first use** — no manual setup required. It downloads the [Seafood Watch Complete Recommendation List](https://www.seafoodwatch.org/globalassets/sfw/pdf/whats-new/seafood-watch-complete-recommendation-list.pdf) PDF, extracts all ~2,050 species entries, and writes them to `references/seafood-watch-ratings.md`.

To manually refresh the data:

```bash
uv run --with pdfplumber scripts/fetch-seafood-watch.py
```

## Usage

Ask Claude to make a restaurant guide:

> "I'm going to Anchor Oyster Bar in SF tonight. Here's the menu: [paste/link]. Can you make me a dining guide?"

The skill will ask about your dietary constraints, research the restaurant, cross-reference everything against Seafood Watch, and generate an HTML guide.

## Dietary constraints

The skill handles any combination of dietary needs:

- Vegan/vegetarian (with exceptions like sustainable seafood)
- Dairy-free, egg-free, gluten-free
- Allergies (shellfish, nuts, soy, etc.)
- Drink preferences (no red wine, etc.)
- Custom constraints

It applies domain knowledge about hidden ingredients (aioli = egg, roux = butter, Caesar dressing = parmesan + egg, etc.) and flags items that need server confirmation.

## Sustainability ratings

Ratings come from the Monterey Bay Aquarium's Seafood Watch program:

| Badge | Rating | Meaning |
|-------|--------|---------|
| Green | Best Choice | Well managed, responsibly caught/farmed |
| Blue | Certified | Third-party certified (MSC, ASC, etc.) |
| Yellow | Good Alternative | Some concerns |
| Red | Avoid | Overfished or harmful methods |

The skill captures nuances like harvest method (diver-caught vs dredged), farmed vs wild, and regional differences (e.g., CA Dungeness crab has whale entanglement concerns that Alaska Dungeness doesn't).

## Project structure

```
sustainable-seafood-restaurant-guide/
├── SKILL.md                          # Skill definition and workflow
├── scripts/
│   └── fetch-seafood-watch.py        # Downloads sustainability data
├── references/
│   └── seafood-watch-ratings.md      # Generated (gitignored)
└── assets/
    └── template.html                 # Design reference / working example
```

## Attribution

Sustainability data: [Seafood Watch](https://www.seafoodwatch.org/) by the Monterey Bay Aquarium. Seafood Watch is a registered trademark of the Monterey Bay Aquarium Foundation.

## License

MIT — see [LICENSE](LICENSE).

## Author

Madison Rickert
