# Korean SDF Font Fix

A Project Zomboid Build 42 mod that fixes Korean text showing as question marks in the new windows.

The B42 windows built on the new UI (the fishing panel, the build menu, newspapers and flyers) use SDF fonts (`UIFont.Sdf*`) that have no Hangul. This mod maps every Sdf* font to the game's own large Korean font (`media/fonts/KO/4x/zomboidLargeKorean.fnt`) through `media/fonts/KO/fonts.txt`.

- Only active when the game language is Korean.
- Fonts load at startup: enable the mod in the main-menu mod list, then restart the game.
- The same font is used at every font size setting. In those windows English text also uses it, and bold, italic and serif styles look the same.

## Install

- Steam Workshop: (link added after the first upload)
- Manual: copy `Contents/mods/KoreanSdfFont` to `%USERPROFILE%\Zomboid\mods\`.

## Compatibility

- Fonts only: no Lua, no gameplay change. Safe to add to or remove from an existing save.
- `media/fonts/KO/fonts.txt` is a copy of the vanilla file with the Sdf* fonts appended; regenerate it with `tools/make_fonts_txt.sh` after a game update that changes the vanilla file.
- Another mod that also replaces `KO/fonts.txt` conflicts (the one loaded last wins).

## Testing

`pzt run` (PZTestHarness) starts the game in Korean and takes screenshots of the fishing panel, a flyer, a newspaper and a panel with Korean text in the Sdf fonts.

## Support

If this mod helps you, you can support it via [PayPal](https://www.paypal.com/paypalme/TalkingHands619/3). It's optional; every feature stays free.
