---
name: sustainable-seafood-restaurant-guide
description: Generate interactive HTML restaurant dining guides that cross-reference menu items against Seafood Watch sustainability data and accommodate dietary constraints. Use when a user wants to prepare for a restaurant meal, analyze a restaurant menu, get sustainable seafood guidance, or create a personalized dining guide. Triggers on requests involving restaurant menus, seafood sustainability, dining prep, or "restaurant guide". The output is a single self-contained .html file optimized for mobile viewing at the table.
---

# Sustainable Seafood Restaurant Guide

Generate a personalized, interactive HTML dining guide for any restaurant by cross-referencing the menu against Seafood Watch sustainability ratings and the user's dietary constraints.

## Workflow

### 0. Ensure Seafood Watch data is available

Check if `references/seafood-watch-ratings.md` exists. If not, run the fetch script:

```bash
uv run --with pdfplumber scripts/fetch-seafood-watch.py
```

This downloads the Seafood Watch PDF and extracts ~2,050 species entries. Only needs to run once — the data is cached locally.

### 1. Gather dietary constraints

Ask the user before doing anything else:

> What dietary constraints should I accommodate? Examples:
> - Vegan/vegetarian (with any exceptions, e.g. sustainable seafood)
> - Dairy-free, egg-free, gluten-free
> - Allergies (shellfish, nuts, soy, etc.)
> - Other preferences (no red meat, low-mercury, etc.)
> - Drink preferences (no red wine, beer only, etc.)

Also ask: **Do they have a wine/drink list?** The guide can include pairing recommendations if available.

Include all constraints — both food and drink — in the diet banner at the top of the guide.

### 2. Get the menu

Accept the menu in any form:
- Pasted text
- Photo/screenshot (read with the Read tool)
- URL to the restaurant's website (fetch and extract)
- PDF menu file

Extract every dish: name, price, description/ingredients. Organize by the menu's own sections.

### 3. Research the restaurant

Always research the restaurant thoroughly online. Search for:
- Sourcing philosophy (local, sustainable, farm-to-table claims)
- Known purveyors or suppliers
- Menu change frequency (seasonal? daily?)
- Wine/beer/drinks list (even if not on the menu PDF)
- Reviews mentioning specific dishes, ingredients, or preparation details
- Any sustainability commitments or certifications

This context informs the guide's commentary and fills gaps in the menu (e.g., drink options found in reviews but not on the PDF). Use multiple sources — restaurant website, review sites, food publications, community forums. Every source discovered becomes a link in the Sources footer.

### 4. Cross-reference against Seafood Watch

For every seafood item on the menu, look up the species in `references/seafood-watch-ratings.md`.

**How to search the ratings file** (5,500+ lines - never load fully):
- Grep for the common name (e.g., `salmon`, `mussels`, `lingcod`)
- Read the surrounding lines to get the full entry (species, methods, origins, scores)
- Check the Quick Reference table at line ~5556 for common species at a glance

**Rating categories:**
| Color | Rating | Score | Meaning |
|-------|--------|-------|---------|
| Green | Best Choice | ~3.5+ | Well managed, responsibly caught/farmed |
| Blue | Certified | Varies | Third-party certified (MSC, ASC, etc.) |
| Yellow | Good Alternative | ~2.5-3.49 | Some concerns |
| Red | Avoid | <2.5 | Overfished or harmful methods |

**Key nuances to capture:**
- Same species can have different ratings by harvest method (diver-caught vs dredged scallops)
- Farmed vs wild matters enormously (farmed mussels = Best Choice, wild = varies)
- Regional differences (CA Dungeness has whale entanglement concerns vs Alaska)
- "Super Green" species are both sustainable AND nutritious
- When the menu doesn't specify method/origin, note the range of possible ratings

Where possible, find species-specific Seafood Watch recommendation pages (e.g., `seafoodwatch.org/recommendation/lingcod/lingcod-790`) and include them in the Sources footer.

### 5. Assess every dish against dietary constraints

For each menu item, determine:
- **Clear yes** - fully compatible (mark as recommended if also sustainable)
- **Clear no** - contains a restricted ingredient (mark as skip, note the ingredient)
- **Ask server** - likely compatible but needs confirmation (dairy in sauce? egg in batter?)
- **Conditional** - compatible if modified (e.g., "ask for oil instead of butter")

Apply domain knowledge about common hidden ingredients:
- Aioli = egg-based; mousse = usually cream/egg; roux = often butter
- Beer batter often contains egg; levain/sourdough is usually dairy-free
- Fish sauce is not dairy but is not vegan; honey is not vegan for strict vegans
- Pesto typically contains parmesan; many dressings contain dairy
- Caesar dressing = parmesan + egg; tartar sauce = mayo (egg)
- Clam chowder (Boston) = cream; cioppino = typically dairy-free (tomato base)

### 6. Build the recommended order

Select the best combination considering:
1. Dietary compatibility (fully compatible items first)
2. Sustainability rating (Best Choice > Good Alternative > Avoid)
3. Meal balance (variety of flavors, textures, courses)
4. Practical ordering (shareable starters, individual mains)

Include backup options and note what to do if a server confirms/denies a questionable item.

### 7. Generate the HTML guide

Write a single self-contained .html file following the design in `assets/template.html`.

**Required sections (as tabs):**
1. **My Order** - numbered recommended dishes with brief rationale
2. **Full Menu** - every dish with sustainability badges, dietary badges, and verdicts
3. **Wine/Drinks** - pairings, with preference note if user has drink constraints
4. **Ask Server** - specific questions to verify ingredients, formatted as cards

**If no wine/drink list is provided**, check if one was found during restaurant research. Include a Drinks tab with whatever was discovered (beers on tap, wine options from reviews, BYO/corkage policy). Only drop to 3 tabs if truly nothing is known about drinks.

## HTML Design Specification

Study `assets/template.html` for the complete implementation. Key design elements:

**Layout:** Mobile-first, single-page app with sticky tab navigation. Ocean-inspired color palette with CSS custom properties. Google Fonts: Playfair Display (headings) + DM Sans (body).

**Card types:**
- `.card.recommended` - green left border, for dishes that are both dietary-compatible and sustainable
- `.card.skip` - 50% opacity, for dishes that clearly don't work
- `.card` (plain) - for conditional/ask-server items

**Badge system:**
- `.badge.green` - "Best Choice" (Seafood Watch green)
- `.badge.yellow` - "Good Alternative"
- `.badge.red` - skip reason or "Avoid" rating, also "Dairy: butter" etc.
- `.badge.vegan` - purple, "Fully vegan" or "Vegetarian"
- `.badge.dairy-free` - blue, "No dairy" / "Dairy-free"
- `.badge.ask` - orange, "Ask re: egg" etc.
- `.badge.pick` - bordered green, "Top pick" / "Must-order" / "Safe harbor"
- Add `.badge.gf` (teal) for gluten-free when relevant

**Card verdict:** Below badges, a `.card-verdict` div with nuanced guidance. Use `<strong>` for emphasis on key actions (e.g., "**Confirm with server.**").

**Hero:** Restaurant name as a link to the restaurant's website, in italic Playfair Display, address, date. Gradient background using the sea/kelp palette. Optional subtitle line for accolades (e.g., "Since 1977 · Michelin Bib Gourmand").

**Diet banner:** Below hero, shows all of the user's constraints (food AND drink) prominently so they can show the server.

**Restaurant background:** A collapsible `<details>` section (`.bg-section`) between the diet banner and tabs. Contains the restaurant's story, sourcing philosophy, key suppliers, sustainability commitments, and notable history. Collapsed by default to keep the guide scannable, but tappable to expand. Populated from research in Step 3.

**Sources footer:** A stacked list of tappable source cards at the bottom of the page (always visible, not inside any tab). Each source is a full-width row in a unified card with:
- Color-coded type tag: green `.source-tag.data` (sustainability data, including species-specific Seafood Watch pages), gold `.source-tag.menu` (menu source), blue `.source-tag.profile` (restaurant profiles/supplier pages), purple `.source-tag.review` (reviews)
- Two-line label: source name in bold, subtitle in gray with context (e.g., "Monterey Bay Aquarium, Feb 2024")
- Links to the actual URL for each source
- Rounded corners on first/last items, divider lines between rows, seafoam hover state
- Include species-specific Seafood Watch recommendation pages for key species on the menu

**Disclaimer:** Below the source links, always include a small italic disclaimer: *"This guide was generated with AI assistance. Sustainability ratings, ingredient assumptions, and dietary assessments may contain errors. Always confirm with your server before ordering."*

## Adapting to Different Diets

The template was built for a mostly-vegan sustainable-seafood diet. Adapt the badge system and assessment logic for other diets:

**Gluten-free:** Add `.badge.gf` badges. Flag hidden gluten sources: soy sauce, beer batter, roux, breadcrumbs, pasta, levain. Many seafood preparations are naturally GF.

**Vegetarian:** Seafood items become skips. Focus sustainability assessment on egg/dairy sourcing if relevant. Highlight vegan options within vegetarian constraint.

**Pescatarian:** Similar to the template's default. All meat items are skips.

**Keto/low-carb:** Flag high-carb items (rice, pasta, bread, starchy sauces). Prioritize protein-rich dishes.

**Allergy-focused:** Allergen identification is the primary lens. Use red badges prominently for allergen presence. "Ask server" becomes especially critical - restaurants are legally required to accommodate allergy inquiries.

**Multiple constraints overlap:** A user might be "gluten-free + pescatarian + dairy-free." Apply all filters simultaneously. The badge system handles this naturally since each badge is independent.

## Resources

### references/seafood-watch-ratings.md
Complete Seafood Watch recommendation database (~2,050 entries). Organized by rating category (Best Choice, Certified, Good Alternative, Avoid) with species details including harvest methods, origins, and scores. **Search by grepping for species names** — do not load the full file. List of common restaurant species names to grep for at the end of the file.

**This file is not included in the repo** — it contains copyrighted data from the Monterey Bay Aquarium. If it doesn't exist, tell the user to run:
```
uv run --with pdfplumber scripts/fetch-seafood-watch.py
```

Seafood Watch is a registered trademark of the Monterey Bay Aquarium Foundation.

### scripts/fetch-seafood-watch.py
Downloads the Seafood Watch Complete Recommendation List PDF and extracts all species entries into `references/seafood-watch-ratings.md`. Requires `pdfplumber` (installed automatically via `uv run --with`).

### assets/template.html
Working example using a fictional restaurant ("The Kelp Garden") that demonstrates all component patterns: hero with linked name, diet banner, collapsible background section, tabbed layout (My Order, Full Menu, Drinks, Ask Server), card types (recommended/skip/conditional), badge system, card verdicts, drink pairings, server questions, source footer, and AI disclaimer. Read this file when generating a new guide to match the design language exactly.