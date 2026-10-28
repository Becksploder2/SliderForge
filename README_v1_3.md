# SliderForge v1.3 — Stadium Branding Beta

Windows Tkinter app. Start with `START_WINDOWS.bat`; Python 3 required. For correct high-quality JPG/PNG scaling, run `INSTALL_BRANDING.bat` (installs Pillow). OpenCV capture is optional via `INSTALL_CAPTURE.bat`.

## Branding

The stadium banner switches with the selected team. Real stadium **names** are mapped for a subset of official CFB teams; actual stadium photographs and licensed logos are **not bundled**. Until a user supplies an image the banner shows an original generic football field and a generated initials placeholder. Import both a team logo and stadium picture with the provided buttons.

For TeamBuilder, click **New TeamBuilder Team** and enter its name. This intentionally starts with a generic stadium and offers optional logo and stadium-screenshot imports. Never assume that a custom team uses a real university venue. Changes are saved per game and team under `%USERPROFILE%\.sliderforge\branding`. You can remove a logo or reset the stadium image. Preserve attribution and obtain rights for any images before redistributing them.

## GitHub updates

The Update Center defaults to `Becksploder2/SliderForge`, beta channel. To notify users about a newer version, publish a GitHub Release tagged `v1.3.1` or later, attaching a ZIP whose filename contains `SliderForge`. The app checks and downloads the ZIP but **does not self-install**. It does not run downloaded code. Existing profiles stay in `%USERPROFILE%\.sliderforge`.

## Known limits

NHL slider values remain experimental placeholders; TeamBuilder capture from EA's website is not automatic. PWHL names are league-based and availability in each NHL game is unverified. All six football and three NHL game selections retained. Windows GUI smoke-start tested under a virtual Linux display; native Windows runtime and in-game behavior unverified.
