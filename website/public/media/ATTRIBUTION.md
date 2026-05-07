# Media attribution

Royalty-free sources used on the LocalGrocery marketing site. Update contact and repo links in [`website/src/site-config.ts`](../../src/site-config.ts) before publishing.

## Video

- **Hero background** — [Mixkit](https://mixkit.co/license/) — stock preview “Woman bags groceries at the supermarket” (free for commercial use per Mixkit terms). Served from the Mixkit CDN in `website/index.html`.

## Photography (Unsplash)

Images are loaded from `images.unsplash.com` with crop/size query parameters. [Unsplash License](https://unsplash.com/license).

**Note:** Only valid photo IDs are used (invalid or removed IDs return **404** and show as broken images in the browser). Replace any image by picking a photo on [unsplash.com](https://unsplash.com) and copying its **Image URL** from the download/share UI.

Current photo ids in use include:

`photo-1542838132-92c53300491e`, `1604719312566-8912e9227c6a`, `1556742049-0cfed4f6a45d`, `1516738901171-8eb4fc13bd20`, `1534723452862-4c874018d66d`, `1558618666-fcd25c85cd64`, `1571771894821-ce9b6c11b08e`, `1546435770-a3e426bf472b`, `1524661135-423995f22d0b` (journey: nearby / map pins), `1556742111-a301076d9d18` (journey: secure payment), `1464226184884-fa280b87c399`, `1512941937669-90a1b58e7e9c` (journey: map & live tracking), `1504674900247-0877df9cc836`, `1490818387583-1baba5e638af`.

To avoid hotlinking entirely, download JPEGs from Unsplash and place them under `website/public/media/`, then point `src` to `./media/your-file.jpg` (paths stay relative to the deployed site root).
