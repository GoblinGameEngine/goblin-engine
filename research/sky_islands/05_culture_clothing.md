# 5. Culture, language and clothing

Canon data: sky_islands.json → `lexicon`, `sayings`, `foods`, `clothing` (with `for_the_outfit_generator`), `names`,
and each island's `colors`, `customs`, `landmark`.

## Language
- The Aloft speak the floor's Lakes English, with each clan's heritage mixed in (Lake Spanish, Carrow French, Polish
  words), plus a sky cant built on rope, weight and wind:
  - **the floor / the Ground**; **groundfolk / heavies**;
  - **a lashing**; **a raft**; **the knives**;
  - **plumb**; **lark**; **skybox**;
  - **lift**, which means buoyancy, but also wealth, room and permission ("we haven't the lift for a goat");
  - **to weigh** (to judge); **ground-weight**; **the Lightening**;
  - **the neighbour** (the Steward, in sight of the Box); **a white** (a cloud you're inside);
  - **downwind** (later, the future) and **upwind** (the past).
- **Sayings:**
  - *Three days lashed and then the knives.*
  - *Every kilo is a person's breath.*
  - *No flame, no fall.*
  - *The wind keeps no promises; the knot does.*

## Names
- A person is named by given name, clan and island: **"Wren Okafor of Halyard"**.
- **Given names** mix the floor's pools with weather and bird words (`names.given_sky`: Wren, Lark, Rime, Brume,
  Kestrel, Tarn, Oriel and others).
- Some clans give a separate **floor name** for dealing with groundfolk.
- **On marrying across a bridge**, a person takes the new island ("of Bowline") and keeps their clan, unless clan custom
  says otherwise.

## Food
- Everything is electric: there is no flame aloft.
- **Dishes:**
  - cloud porridge (oats in snowmelt with honey);
  - roof greens;
  - air-cured goat (dried on the rim racks);
  - dove pie (only on islands that eat their doves);
  - **snow honey** (fresh snow eaten with honey: the snow feast);
  - hoist bread, baked the day a hoist comes up;
  - berry wine;
  - moss tea, said to keep off ground-sickness;
  - **lashing stew**: every island at a raft adds something to one pot.

## Clothing
- **The principle:** warm, layered and light (every gram counts), and knitted in the clan's colours so a stranger's
  island can be read at a glance.
- **Two real cousins:**
  - **The Sámi gákti.** A dominant colour with contrasting bands, appliqué and ribbon at the collar, sleeves and hem.
    Its colours, patterns and jewellery tell where the wearer is from, whether they are married, and sometimes their
    family [1][2].
  - **The Inuit two-layer parka.** An inner layer turned in and an outer layer turned out, with warm air trapped
    between. It is loose, with drawstrings to vent, and the hood ruff makes a still-air boundary round the face [3][4].
- **Aloft there is no fur.** The Aloft make the same system from wool, down and waxed skycloth.

### For the outfit generator (sky_islands.json → `clothing.for_the_outfit_generator`)
- **climate tag:** `cold`.
- **layers:**
  - base: unseen;
  - mid: a **gansey** (patterned jumper) in the clan colours;
  - outer: one of the outer garments below.
- **Outer garments:**
  - `rigger_anorak`: hip-length pullover, hood, drawstring hem, waxed skycloth. Clan main or grey, with accent bands on
    the arms.
  - `long_coat`: knee-length quilted down coat with toggles and a high collar. Main colour, trimmed in the second.
  - `gakti_tunic`: a tunic-coat with broad contrasting bands at the hem, cuffs and collar, belted. Main colour, accent
    bands.
  - `parka`: deep hood with a down-felt ruff. For elders and plumbs.
  - `cape_coat`: a short shoulder cape over a jacket, for factors and knot keepers. Second colour.
  - `vest_quilted`: worn over the gansey for roof work. Accent colour.
- **Head:** knit cap with ear flaps and a tassel (clan band), balaclava (in a white), hood, a tall felted hat for
  elders, or a wide knit headband for the young.
- **Hands:** patterned mittens with grip palms, or fingerless gloves (riggers, knitters).
- **Neck:** a very long striped scarf (the stripe order is the clan's), or a cowl.
- **Legs:** wool or felt trousers, patterned knit leggings under a tunic or skirt, or a quilted wrap skirt.
- **Feet:** felted wool boots with soft soles, or light laced rigger boots with sticky soles.
- **Harness:** a webbing harness with a short tether and clip, worn by riggers, fence wardens and every child near the
  rim.
- **Knit patterns:** clan-order stripes, peerie bands, snowflake/star yokes, cable (rope) knit, chevrons (the island's
  bridge style drawn as a zigzag), checks, dove borders.
- **Palette:**
  - each island's `colors`: [main, second, accent], from 24 palettes;
  - plus undyed greys and creams (#e8e2d0, #b8b0a0, #6f6a60) with anything;
  - moss greens and lichen yellows are common;
  - bright floor-bought synthetics show off a plumb's wealth.
- **By age and role:**
  - children: brightest, harnessed, many layers;
  - riggers: anorak, harness, fingerless gloves, knit cap;
  - elders: parka or long coat, with feathers on the collar in some clans (one per lashing remembered);
  - plumbs: a tailored parka in the clan main colour over a floor-made jacket;
  - knot keepers: a cape coat with a cord of knots worn as a sash.

## Customs (two per island, from 24)
See sky_islands.json → `customs` for the full list:
- cord names: a knot for every lashing crossed;
- bell-speech;
- the silent dusk;
- the long kitchen;
- rope-mark tattoos;
- the snow feast;
- Weighing Day;
- the Long Drop;
- matrilocal, patrilocal or chosen-island marriage;
- kite mail;
- "no birds" (doves are cousins);
- cloud singing in a white;
- rail dancing;
- guest weight;
- "the neighbour";
- lantern vigils;
- the plumb's story owed;
- two names;
- children as ballast;
- tether-splice weddings;
- map walls;
- feather coats.

## Sources
1. [Polarpedia: Gákti](https://polarpedia.eu/en/gakti/)
2. [Gákti](https://en.wikipedia.org/wiki/G%C3%A1kti) (Wikipedia)
3. [UBC Museum of Anthropology: inner parka (RRN record)](https://www.rrncommunity.org/items/30789/print)
4. [AskNature: fur-rimmed parkas create a protective boundary layer](https://asknature.org/innovation/fur-rimmed-parkas-create-a-protective-boundary-layer/)
