# SDF Font Fix (CJK/Thai)

A Project Zomboid Build 42 mod that fixes question marks in the new windows when the game language is Korean, Japanese, Chinese or Thai.

The B42 windows built on the new UI (the fishing panel, the build menu, newspapers and flyers) use SDF fonts (`UIFont.Sdf*`). Those fonts hold Latin, Cyrillic and Greek only (873 glyphs), so Korean, Japanese, Chinese and Thai text is drawn as `?`. This mod maps every Sdf* font to the game's own large bitmap font for the language, through `media/fonts/<LANG>/fonts.txt`:

| Language | Font |
|---|---|
| KO | `KO/4x/zomboidLargeKorean.fnt` |
| JP | `JP/4x/zomboidLargeJapanese.fnt` |
| CH, CN | `CH/4x/zomboidLargeChinese.fnt`, `CN/4x/zomboidLargeChinese.fnt` |
| TH | `TH/4x/zomboidLargeThai.fnt` |

- Only those five languages change. The other languages already have their letters in the SDF fonts and are untouched.
- Fonts load at startup: enable the mod in the main-menu mod list, then restart the game.
- Simplified Chinese (CN): the vanilla Chinese font (shared with CH) lacks 874 simplified characters that the vanilla CN translation uses (们 这 来 时 ...), so they stay blank in these windows. Measured 2026-10-30.
- Japanese: `Translate/JP/Tooltip.json` fills `Tooltip_FishingTip` (the fishing panel guide), which the vanilla JP translation leaves in English.
- The 4x font is used at every font size setting. In those windows English text also uses it, and bold, italic and serif styles look the same.

## Install

- Steam Workshop: (link added after the first upload)
- Manual: copy `Contents/mods/SdfFontFix` to `%USERPROFILE%\Zomboid\mods\`.

## Compatibility

- Fonts and one translation line only: no Lua, no gameplay change. Safe to add to or remove from an existing save.
- Each `media/fonts/<LANG>/fonts.txt` is a copy of the vanilla file with the Sdf* fonts appended; regenerate them with `tools/make_fonts_txt.sh` after a game update that changes a vanilla file.
- Another mod that also replaces one of these `fonts.txt` files conflicts (the one loaded last wins).

## Testing

`TEST_LANG=JP pzt run` (PZTestHarness; KO JP CH CN TH, default KO) starts the game in that language and takes screenshots of the fishing panel and a newspaper text panel.

## Support

If this mod helps you, you can support it via [PayPal](https://www.paypal.com/paypalme/TalkingHands619/3). It's optional; every feature stays free.
