#!/bin/bash
# Writes media/fonts/<LANG>/fonts.txt for every language whose script the vanilla SDF fonts lack
# (KO JP CH CN TH): the vanilla <LANG>/fonts.txt plus every Sdf* UI font mapped to that language's
# vanilla 4x Large bitmap font. "4x/..." resolves to media/fonts/<LANG>/4x/ whatever the font size
# option is (TextManager.getFontFilePath tries <LANG>/<sizeDir>/4x/..., then <LANG>/4x/...).
# Rerun after a game update that changes a vanilla <LANG>/fonts.txt.
G="${1:-C:/Program Files (x86)/Steam/steamapps/common/ProjectZomboid}/media/fonts"
OUT="$(dirname "$0")/../Contents/mods/SdfFontFix/42/media/fonts"
for L in KO JP CH CN TH; do
  # the font the vanilla fonts.txt uses for "Large" (zomboidLargeKorean.fnt, ...)
  large=$(awk '/^font Large$/ {f=1} f && /fnt *=/ {gsub(/.*fnt *= *|,.*/, ""); print; exit}' "$G/$L/fonts.txt")
  if [ ! -f "$G/$L/4x/$large" ]; then
    echo "missing $L/4x/$large" >&2
    exit 1
  fi
  mkdir -p "$OUT/$L"
  {
    cat "$G/$L/fonts.txt"
    for n in SdfRegular SdfItalic SdfBold SdfBoldItalic SdfOldRegular SdfOldBold SdfOldItalic SdfOldBoldItalic SdfRobertoSans SdfCaveat; do
      printf '\nfont %s\n{\n    fnt = 4x/%s,\n}\n' "$n" "$large"
    done
  } > "$OUT/$L/fonts.txt"
  echo "$L -> 4x/$large"
done
