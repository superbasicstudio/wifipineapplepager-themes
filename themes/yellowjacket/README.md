# YellowJacket

High-contrast black and yellow theme for the WiFi Pineapple Pager.

## Design

- **Pure black backgrounds** with bold yellow accents
- **Unified yellow palette** — no per-section color variation
- **5 horizontal band dashboard** — full-width rows, selected band fills solid yellow
- **Flat, clean, sharp** — no glow effects, no scanlines, no blur
- **181 PNG assets** generated via Python + Pillow at 3x supersample

## Install

Copy the `yellowjacket` folder to `/mmc/root/themes/` on your Pager, then select it from Settings > Display > Theme.

```bash
scp -r yellowjacket root@172.16.52.1:/mmc/root/themes/yellowjacket/
```

## Regenerate Assets

```bash
cd yellowjacket
python3 generate_yellowjacket_assets.py
```

Requires Python 3 and Pillow (`pip install Pillow`).

## Author

superbasicstudio

## License

MIT
