---
name: family-holiday-deal-research
description: Research budget family holiday options from a home city using parallel fare/lodging searches, then synthesize shortlist with realistic total-trip ranges and booking strategy.
---

Use this skill when a user wants cheap holiday ideas for a family within a date window and budget, especially when comparing France/Europe destinations and mixing flights, rail, and lodging.

## Goal
Produce a decision-ready shortlist of destinations with:
- realistic total trip cost ranges
- transport + lodging value signals grounded in live sources
- family fit by children’s ages and trip style
- a ranked recommendation and next-step narrowing questions

## Workflow

1. Clarify the minimum viable trip brief.
   Gather:
   - origin city
   - travel window
   - total budget and whether it includes transport
   - family size and children’s ages
   - acceptable transport modes (flight/train/driving)
   - geography constraints (country, Schengen, passport limits)
   - trip type preferences and exclusions (for example: no beach)
   - lodging flexibility
   - optimization target: cheapest, best weather, shortest trip, best value

2. Default intelligently when the user is undecided.
   - If passport uncertainty appears, default to France/Schengen.
   - If they say “cheap” but not “minimum absolute price,” optimize for best overall value, not just lowest fare.
   - For families with older children, consider theme parks, science museums, walkable cities, and mixed city+nature bases.

3. Build a candidate set before going deep.
   Use parallel web_search calls for:
   - destination ideas matching the brief
   - transport pages (airline, train, OTA, rail portals)
   - family-friendly lodging pages on Booking.com or equivalent
   - destination-specific attractions that materially affect family value (for example Europa-Park, science museums, tulip gardens)

4. Prefer source types that yield concrete pricing snippets.
   Good sources:
   - airline landing pages with “from” prices
   - SNCF / rail operator route pages with “from” fares and travel times
   - Booking.com family hotel pages with “price from” signals
   - official attraction ticket pages for family-ticket math
   Avoid over-weighting generic blog posts unless they contain current quoted prices.

5. Convert raw snippets into realistic family-total estimates.
   Use execute_code for cost ranges instead of mental math.
   Structure per option:
   - transport range for the whole family
   - lodging range for the whole stay
   - extras range (food, local transport, attraction tickets if central to value)
   Then compute low/high totals.

6. Rank on value, not just headline fare.
   A strong value option usually combines:
   - low friction from origin
   - family-suitable activities for the kids’ ages
   - reasonable lodging cost
   - manageable local transport
   - weather/season fit
   Example: rail-accessible France options can beat cheap flights once airport costs and hassle are considered.

7. Present a shortlist of about 3–5 options.
   For each option include:
   - why it fits this family
   - live pricing signals found
   - realistic total budget estimate
   - ideal trip shape (for example 4 nights, 5 nights, split stay)
   - best-for summary

8. Finish with a narrow decision prompt.
   Ask the user which destination(s) to refine and whether to optimize for nights, exact dates, or special add-ons like a theme park day.

## Heuristics learned

- Alsace from Paris is a standout “best overall value” family option when users want France/Schengen, no beach, and a manageable budget; rail convenience plus Colmar/Strasbourg pricing and optional Europa-Park can beat flight-based options.
- Valencia often performs very well for spring city value: low-cost flights, warmer weather, and family activities around the City of Arts and Sciences.
- Center Parcs / easy-drive cottage resorts are strong low-stress options and should be compared separately from city breaks because users may value convenience over maximizing nights.
- OTA “average round-trip” figures can be much higher than low-cost fare snippets; treat them as upper anchors, not the only truth.

## Pitfalls

- Don’t treat OTA average flight prices as the bookable family total; check low-cost carrier route pages too.
- Don’t forget age-based attraction pricing: a 14-year-old may count as an adult while a 10-year-old still gets child pricing.
- Don’t recommend non-Schengen or passport-friction destinations if the user signals France/Schengen only.
- Don’t present a single “price” when only fragmented live snippets are available; present grounded ranges.
- On messaging platforms that do not render markdown well, use plain text with short sections and numbered lists.

## Verification checklist

Before finalizing, confirm:
- every destination fits the user’s geography/document constraints
- each total range is derived from cited live transport/lodging signals
- family suitability matches the children’s ages
- the final ranking reflects the user’s stated optimization target
- the closing question makes it easy to move from inspiration to booking refinement
