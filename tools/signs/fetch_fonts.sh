#!/usr/bin/env bash
# Fetch the OFL/Apache display fonts make_signs.py uses into the gitignored reference/fonts/ (Google Fonts repo).
# Only the rendered sign atlases ship (OFL allows that); the fonts themselves stay out of git.
set -u
D="$(dirname "$0")/../../reference/fonts"; mkdir -p "$D"
G=https://raw.githubusercontent.com/google/fonts/main
for p in ofl/cinzel/Cinzel%5Bwght%5D.ttf ofl/playfairdisplay/PlayfairDisplay%5Bwght%5D.ttf ofl/rye/Rye-Regular.ttf \
  ofl/abrilfatface/AbrilFatface-Regular.ttf ofl/alfaslabone/AlfaSlabOne-Regular.ttf ofl/imfellenglish/IMFeENrm28P.ttf \
  ofl/oldstandardtt/OldStandard-Bold.ttf ofl/pacifico/Pacifico-Regular.ttf ofl/lobster/Lobster-Regular.ttf \
  apache/yellowtail/Yellowtail-Regular.ttf ofl/righteous/Righteous-Regular.ttf ofl/monoton/Monoton-Regular.ttf \
  ofl/bungee/Bungee-Regular.ttf ofl/limelight/Limelight-Regular.ttf ofl/sacramento/Sacramento-Regular.ttf \
  ofl/kaushanscript/KaushanScript-Regular.ttf ofl/shrikhand/Shrikhand-Regular.ttf ofl/josefinslab/JosefinSlab%5Bwght%5D.ttf \
  apache/ultra/Ultra-Regular.ttf ofl/reemkufi/ReemKufi%5Bwght%5D.ttf ofl/arefruqaa/ArefRuqaa-Bold.ttf \
  ofl/yatraone/YatraOne-Regular.ttf ofl/rozhaone/RozhaOne-Regular.ttf ofl/delagothicone/DelaGothicOne-Regular.ttf \
  ofl/pottaone/PottaOne-Regular.ttf ofl/marcellus/Marcellus-Regular.ttf ofl/medievalsharp/MedievalSharp.ttf \
  ofl/unifrakturmaguntia/UnifrakturMaguntia-Book.ttf ofl/uncialantiqua/UncialAntiqua-Regular.ttf \
  ofl/ruslandisplay/RuslanDisplay-Regular.ttf ofl/chonburi/Chonburi-Regular.ttf ofl/oswald/Oswald%5Bwght%5D.ttf \
  ofl/fredoka/Fredoka%5Bwdth%2Cwght%5D.ttf apache/satisfy/Satisfy-Regular.ttf ofl/carterone/CarterOne.ttf \
  ofl/sancreek/Sancreek-Regular.ttf ofl/kalam/Kalam-Bold.ttf ofl/cinzeldecorative/CinzelDecorative-Bold.ttf \
  ofl/bungeeshade/BungeeShade-Regular.ttf ofl/poiretone/PoiretOne-Regular.ttf ofl/arvo/Arvo-Bold.ttf; do
  f=$(basename "$p" | sed 's/%5B.*//; s/\.ttf$//').ttf
  [ -s "$D/$f" ] && continue
  curl -sfL "$G/$p" -o "$D/$f" || { echo "missing $p"; rm -f "$D/$f"; }
done
ls "$D" | wc -l
