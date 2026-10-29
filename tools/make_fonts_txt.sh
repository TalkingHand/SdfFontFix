#!/bin/bash
# Writes media/fonts/KO/fonts.txt: the vanilla KO fonts.txt plus every Sdf* UI font mapped to the
# vanilla 4x Korean bitmap font. "4x/..." resolves to media/fonts/KO/4x/ whatever the font size
# option is (TextManager.getFontFilePath tries KO/<sizeDir>/4x/..., then KO/4x/...).
# Rerun after a game update that changes the vanilla KO fonts.txt.
G="${1:-C:/Program Files (x86)/Steam/steamapps/common/ProjectZomboid}/media/fonts"
OUT="$(dirname "$0")/../Contents/mods/KoreanSdfFont/42/media/fonts/KO/fonts.txt"
{
  cat "$G/KO/fonts.txt"
  for n in SdfRegular SdfItalic SdfBold SdfBoldItalic SdfOldRegular SdfOldBold SdfOldItalic SdfOldBoldItalic SdfRobertoSans SdfCaveat; do
    printf '\nfont %s\n{\n    fnt = 4x/zomboidLargeKorean.fnt,\n}\n' "$n"
  done
} > "$OUT"
