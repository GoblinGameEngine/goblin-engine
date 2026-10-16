# 02 Open questions: decisions and defaults

## Decided by the user (2026-10-15)
1. **Day 0 is a Wednesday.** The bible's date wins: 2752-05-24.
   - The single source is `remake/events.json` `start_weekday: 2`, read by `GameCalendar` (00 §4.1).
   - The Communicator's Date & Time app must use the same source.
   - NpcLife moves off its Monday assumption, and lives are rebaked.
2. **The islanders come down often and settle in large numbers.**
   - Large families; half of all island children settle on the floor.
   - Friction in the less affluent areas.
   - Most settle on the South Sea shore, and fewest on the North Sea shore.
   - **Done in canon** (`tools/bible/canon_sky.py` → `sky_islands.json`, `research/bible/13_sky_islands.md`):
     `market_moorings`, `line_ranks`, `settled`, the Skein's `families` / `coming_down` / `line_or_ground`, and history
     at VY 418, 431, 452, 474, 486 and 489.
3. **"Lowliners" is approved.** Discrimination follows the region: hardly felt in the north, real friction in the
   South.
   - The South Sea cities have whole Line Rows built as surface warrens (00 §9.5).
   - **Proper ethnic names wait for the political work.** Use `[ETHNONYM: …]` placeholders.
4. **Every town gets its own flea market**, each unique.
   - People travel to other towns' markets on weekends (`market_trip`, 00 §6.3).
   - Every market has static mooring attachments (anchor blocks; masts in towns and cities) and tent room outside.
5. **Names:** the four city names are approved, and all 22 are in 07 §2.
6. **Sign style by region:**
   - the North Land stately and classic;
   - the South Land laid-back and California;
   - the river towns a gradient;
   - the islands flashy and modern with ethnic flair.
   - The Grok sheets are in 08: 18 image_gen sheets plus 2 reserve edits, ≤ 20 images.

7. **Bright Week (≥ 5 islands at any market):** a celebration; the full market, local booths included, is open
   every day while they stay (mode CELEBRATION, 00 §4.2, §6.4).
8. **The Sky Holiday (≥ 7 islands at a town or village market):** the town and surrounding area declare a holiday
   (mode HOLIDAY, 00 §6.4). The names and customs are in canon (`market_moorings.bright_week` / `sky_holiday`;
   lexicon "Bright Week", "the Low Sky").

## Defaults I chose (none block the build)
1. **City limits** = the ellipse inscribed in `plan_city`'s bounds, written to `law/settlements.json` `limits`.
   Outskirts are r 0.60–0.95 (villages 0.5–0.95).
2. **Market size:**
   - cities `pop/120`;
   - towns and villages `ceil((40 + pop/140)/10)*10`, at least 40;
   - 1.8 paved spaces per stall plus a grass apron.
   - 2,660 stalls in all.
3. **Mooring tiers:** every tier takes a raft of up to 10 (the Ten Knot). Only the first islands anchor to the
   ground; the rest lash to them.
   - city: a Mooring Field with 24 blocks and 2 masts, 6 islands anchored;
   - town (≥ 5k): 1 mast and 12 blocks, 4 anchored;
   - village: 8 blocks, 3 anchored.
   - Tents spill onto fields, parks, school grounds and closed streets on Bright Week and holidays.
4. **Booking rates** (a host a week): city 0.40, town 0.25, village 0.15. Great Fairs and Market Days 0.8–1.0.
   - Followers form a chain, each drawing one more with q: city 0.60, town 0.45, village 0.42; Great Fair 0.75; Market
     Day town 0.60, village 0.55.
   - **Expected:** ≈ 20 Bright Weeks a year (~5 a season) and ≈ 1.8 Sky Holidays a year on the map. A given small town
     has a holiday about once a decade.
4b. **Holiday area:** the host town plus every settlement and farm within 8 km. A city inside the radius is not
    declared, but its trips get ×3.
    - **Essential work** continues: hospital, care, police and fire, transit, utilities and charging, food and drink,
      lodging, farm chores.
    - Holiday days are those opening with ≥ 7 islands, at most 3 in a row.
    - **Announced** the evening before by the town council: the Wire radio, the Boards, bells, and a PDA (Communicator)
      alert. Bright Week goes out as a marquee, a radio advert and a PDA news item when the 5th island books.
5. **The Three-Day Knot** is kept at moorings by the **market knot**, renewed every third day.
6. **Stays:** 70 % one weekend, 18 % two, 12 % three; 21 days maximum.
7. **Weekdays while moored:** islanders run only their stalls and tents. Local stalls stay shut Mon–Thu.
8. **Hours while moored:** islanders 09:00–18:00 daily. Gondolas carry passengers 24 h; cargo runs 07:00–19:00.
9. **Lowliner numbers:** **29,000 (12 % of the floor)**:

   | region | Lowliners |
   |---|---|
   | south_shore | 15,000 |
   | southland | 7,000 |
   | kettle_valley | 4,800 |
   | northland | 1,400 |
   | north_shore | 800 |

   About 1,500 arrive a year since the Full Book (VY 486).
10. **Regional friction model:** an attitude term `regional_friction(t, finances band, local Lowliner share)`.
    - Hiring weight 0.85 in poor or hostile southern contexts, 1.0 elsewhere.
    - Southern wage median ×0.85 via the job mix.
    - No policing mechanic.
11. **Structural root of disadvantage (canon):**
    - the Settlers' Shares Act, VY 474: island-born settlers wait two years for a birth share;
    - the Draw Housing Ruling, VY 489: they queue for Draw homes like everyone else, which the South's poorer streets
      resent.
12. **Line Rows:**
    - Solana Point ~14–18 blocks, Oceanview 3–5, Playa Verde 2–3, Pelican Cove 1;
    - 1–2 blocks in Kessler, Calder, Bellhaven and Harrow Falls;
    - none as warrens in the north.
    - Per-lot civs from the settlers' home islands. 3–5 storeys, stepping to 2 at block ends.
13. **Weekend trip rate:** 0.06 per adult per market day (about once in 6 weekends). ×2.5 toward a fair. A gravity
    choice by stalls, distance² and the market's draw.
14. **Currency:** Columbia dollars everywhere. Fair letters act as the Skein's credit.
15. **Fees:** free admission and parking (Great Fairs C$ 5 parking). Rents: day C$ 30, season C$ 220 a month, shed
    C$ 480 a month.
16. **Lights:** no new real lights. Markets claim up to 8 of StreetLights' 28 pooled lights.
17. **Ownership:** the island mooring pieces, `moorings` layout and the surface warren generator are **requests** to
    the warren stream, scheduled after its current work.
18. **Sign texture rule:** market signs carry their names. Island and business signs are blanks; the names are drawn
    by the existing text systems.
19. **No night sheets:** the emissive masks come from the day sheets.
20. **Aligned:** `research/sky_islands/03_society.md`, `02_history.md` and `00_plan.md` now match the canon change.
