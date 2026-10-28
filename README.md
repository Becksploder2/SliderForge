# SliderForge

**Windows sports gameplay-slider companion** — v1.3 Stadium Branding Beta.

The desktop app is written in Python/Tkinter. It includes game selections for **College Football 25, 26, 27; Madden NFL 25, 26, 27; and NHL 25, 26, 27**, with separate game modes, experimental slider profiles, and a GitHub Releases update checker.

## Run the Windows application

1. Download this repository (Code → Download ZIP), extract it, and run `START_WINDOWS.bat`. Python 3 is currently required for the source version.
2. Run `INSTALL_BRANDING.bat` to install Pillow for properly scaled logos and stadium photos.
3. Optionally run `INSTALL_CAPTURE.bat` to enable the capture-card workflow.

## Dynamic team backgrounds (desktop)

The native Tkinter app now displays a team-colored header with a logo watermark, updated automatically when your team, opponent, game, or venue changes. Select YOUR TEAM, OPPONENT, HOME or AWAY as the background source. Control opacity (5–40%) or switch the background off. Use **Import team logo** to save a local PNG, JPG, or WebP image for the currently selected team. Imported logos are stored through `branding.py`, without downloading protected team marks. Where no image is imported, team initials are shown instead. The earlier HTML prototype remains separate.

The current implementation decorates the header area, not the entire slider grid. The desktop application has not yet been tested on a physical Windows machine.

## Stadium Experience (v1.3)

Select a team to change the stadium-name banner and foreground team logo. Stadium photographs and official team logos **are not bundled**; the app uses a generic field and initials until images are imported. The team-to-stadium name mapping is currently partial and can be expanded.

For a **TeamBuilder team**, click **New TeamBuilder Team**, enter the team name, then **Import Team Logo**. Its stadium stays generic unless you optionally import a screenshot of the team's stadium from TeamBuilder.

Branding is saved under `%USERPROFILE%\.sliderforge\branding` and is recalled per game/team. Existing slider profiles are stored separately in `%USERPROFILE%\.sliderforge\sliderforge.db`.

## Updates

The built-in updater checks the releases of this repository (beta channel by default). It downloads a validated update ZIP, but **does not automatically install** it. Release tags must have a semantic version such as `v1.3.1`.

## Current limitations

- NHL sliders are experimental placeholders and require verification against each game's menus.
- PWHL league-based team names do not guarantee in-game availability.
- Windows source launch was smoke-tested under a virtual display; a native Windows runtime test is still needed.
- Capturing official logos or stadium screenshots from EA's website is **not automated**.
- EA, NCAA, NFL, NHL, PWHL, university and team marks are not included or endorsed.

## Browser demo

The original [index.html](index.html) prototype is preserved as a separate early UI test; the desktop application's main entrypoint is [SliderForge.py](SliderForge.py).

For detailed v1.3 notes, read [README_v1_3.md](README_v1_3.md).
