# Face Press image credits

The facial library contains 530 cutouts. Camera photographs from 30 subjects contribute 189 cutouts, and 52 synthetic portraits contribute 341. Every facial category includes photographed options. Each entry in the [library manifest](assets/parts/library.json) links to its source record, which identifies the source type, original image and SHA-256 digest.

## Synthetic headshots

Reto Wyss created **Syn-Vis-v0** in 2025, a repository of 480 synthetic subjects with a separate headshot series. Face Press uses 38 images from the headshot series and 14 additional subjects from the 2048-pixel base series, selected for pose, exposure and variety in facial features, skin tone and hair. The original collection depicts female-presenting subjects, mostly young adults. Wyss dedicated the individual images to CC0 and licensed the dataset compilation, documentation and original metadata under CC BY-SA 4.0. The headshot source revision used here is `100262732989e77f38cd831d70a376a93735006a`. [Original dataset and license statement](https://huggingface.co/datasets/retowyss/Syn-Vis-v0) · [CC0](https://creativecommons.org/publicdomain/zero/1.0/) · [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)

## Photographic portraits

The camera sources include official portraits and historical photographs. Face Press cropped, aligned, segmented and tonally adjusted the images. The four photographed spectacle cutouts retain open lenses. For the slim rectangular frames, the visible lens and hinge from the Katherine Johnson photograph are mirrored into a front-facing pair. The source records below describe the original images and credits.

### U.S. public-domain portraits

| Source ID | Photograph | Credit |
| --- | --- | --- |
| gov-1 | [Donald R. Pettit](https://commons.wikimedia.org/wiki/File:Donald_R._Pettit.jpg) | NASA |
| gov-2 | [Aaron Cohen](https://commons.wikimedia.org/wiki/File:Aaron_Cohen_-_GPN-2002-000100.jpg) | NASA |
| gov-3 | [Leland Melvin](https://commons.wikimedia.org/wiki/File:Leland_Melvin.jpg) | NASA / Robert Markowitz |
| gov-4 | [Frank Rubio](https://commons.wikimedia.org/wiki/File:Frank_Rubio_official_portrait.jpg) | NASA / Bill Stafford |
| gov-5 | [Victor J. Glover](https://commons.wikimedia.org/wiki/File:Victor_J._Glover_official_portrait.jpg) | NASA / Robert Markowitz |
| gov-6 | [Ruth Bader Ginsburg](https://commons.wikimedia.org/wiki/File:Ruth_Bader_Ginsburg_2016_portrait.jpg) | Steve Petteway, Supreme Court of the United States |
| gov-7 | [Ellison Onizuka](https://commons.wikimedia.org/wiki/File:Ellison_Shoji_Onizuka_%28NASA%29.jpg) | NASA |
| gov-8 | [Katherine Johnson](https://commons.wikimedia.org/wiki/File:Katherine_Johnson_in_2008.jpg) | NASA / Sean Smith |
| gov-9 | [John Glenn](https://commons.wikimedia.org/wiki/File:John_Glenn_Low_Res.jpg) | U.S. Senate Historical Office |
| gov-10 | [Charles Bolden](https://commons.wikimedia.org/wiki/File:Charles_F._Bolden%2C_Jr.jpg) | NASA / Bill Ingalls |
| gov-11 | [Guion Bluford](https://commons.wikimedia.org/wiki/File:Guion_Bluford.jpg) | NASA, with restoration by Wikimedia Commons contributor Coffeeandcrumbs |
| gov-12 | [Buzz Aldrin](https://commons.wikimedia.org/wiki/File:Buzz_Aldrin_%28S69-31743%29.jpg) | NASA |
| gov-13 | [Chris Hadfield](https://commons.wikimedia.org/wiki/File:Chris_Hadfield.jpg) | NASA |
| gov-14 | [John Fetterman](https://commons.wikimedia.org/wiki/File:John_Fetterman_US_Senate_portrait.jpg) | United States Senate |
| gov-15 | [Ted Cruz](https://commons.wikimedia.org/wiki/File:Ted_Cruz_official_116th_portrait.jpg) | U.S. Senate Photographic Studio |
| gov-16 | [Ketanji Brown Jackson](https://commons.wikimedia.org/wiki/File:Ketanji_Brown_Jackson_official_SCOTUS_portrait.jpg) | Fred Schilling, Collection of the Supreme Court of the United States |
| gov-17 | [Rosa DeLauro](https://commons.wikimedia.org/wiki/File:Rosa_DeLauro_118th_Congress.jpeg) | House Creative Services |
| gov-18 | [Thurgood Marshall](https://commons.wikimedia.org/wiki/File:Thurgood-marshall-2.jpg) | Robert S. Oakes, Library of Congress |

### NASA Image and Video Library

These ten portraits were sampled from the original camera files in NASA’s Image and Video Library. Credit lines follow the NASA catalog records. [NASA image and media guidelines](https://www.nasa.gov/nasa-brand-center/images-and-media/)

| Subject | NASA catalog record | Photography credit |
| --- | --- | --- |
| Mae Jemison | [S92-40463](https://images.nasa.gov/details/S92-40463) | NASA |
| Ellen Ochoa | [JSC2014E037863](https://images.nasa.gov/details/jsc2014e037863) | NASA / Bill Stafford |
| Peggy Whitson | [JSC2001-03044](https://images.nasa.gov/details/JSC2001-03044) | NASA / Bill Stafford |
| Jessica Meir | [JSC2025E078605](https://images.nasa.gov/details/jsc2025e078605_alt) | NASA / Josh Valcarcel |
| Franklin Chang-Díaz | [S97-06573](https://images.nasa.gov/details/S97-06573) | NASA |
| Ronald McNair | [S85-36539](https://images.nasa.gov/details/S85-36539) | NASA |
| Bruce McCandless II | [S82-36442](https://images.nasa.gov/details/S82-36442) | NASA |
| Christina Koch | [NHQ202009160004](https://images.nasa.gov/details/NHQ202009160004) | NASA / Bill Ingalls |
| Michael Collins | [S64-29926](https://images.nasa.gov/details/s64-29926) | NASA |
| Jeanette Epps | [JSC2023E047050](https://images.nasa.gov/details/jsc2023e047050_alt) | NASA / Bill Stafford |

### Historical photographs

The chin curtain comes from a nineteenth-century portrait of Abraham Lincoln by Alexander Gardner, sampled from the Library of Congress TIFF. The silver fork beard comes from George K. Warren’s portrait of Frederick Douglass, circa 1879, in the Frank W. Legg Photographic Collection. Both works are in the public domain in the United States. [Library of Congress portrait of Lincoln](https://www.loc.gov/pictures/item/96522529/) · [National Archives portrait of Douglass](https://www.archives.gov/research/still-pictures/highlights/frederick-douglass)

## Rebuild or expand the library

The editor runs entirely from the bundled assets. Rebuilding the library is optional. The [Python extractor](scripts/extract_parts.py) runs OpenCV's frontal-face detector, segments each head with a BiSeNet ResNet-18 model, and aligns the result by the eyes and mouth. It samples the original photograph at the aligned coordinates. Local tonal masks isolate eyelids, brows, lips and nasal shadows on transparent paper. The jaw layer follows a narrow band of skin and shadow beside and below the mouth. Seven hand-traced masks isolate photographic facial hair. Each fragment is exported as a lossless WebP on a shared 512-unit placement grid. For the expanded sources, the extractor measures how many original pixels map to the grid at the eye landmarks. Where the source supplies at least two pixels per grid unit, it samples the original directly onto a 1024 × 1024 canvas with antialiasing. The other assets use a 512 × 512 canvas. Each manifest entry records its pixel size and bounds in grid units. Occluded ears and clipped hairstyles are omitted where detected. The model runs locally during extraction. [Face-parsing implementation](https://github.com/yakhyo/face-parsing) · [ONNX weights](https://huggingface.co/PayamFard123/dermaintel-face-parsing)

These commands rebuild the curated set with a Python 3.11 environment and `curl`. Run them from the project directory. The cache belongs outside the public site. It keeps downloaded headshots and the checksum-verified model for later runs.

```sh
python3.11 -m venv /tmp/face-press-tools
/tmp/face-press-tools/bin/pip install numpy==2.4.4 pillow==12.3.0 opencv-python-headless==4.11.0.86 onnxruntime==1.29.0
/tmp/face-press-tools/bin/python scripts/extract_parts.py --cache /tmp/face-press-sources --download
```

Append `--all` to screen all 480 synthetic headshots plus the featured base-series and photographic sources, or append `--add-ids 24 75 390` to screen specific additional Syn-Vis subjects. Additional portraits pass automatic checks for frontal pose, eye visibility and mouth position. Inspect their thumbnails before distribution. A run rewrites the manifest and active layers in `assets/parts/`. Any preexisting exports from an earlier, broader selection are ignored by the editor.

Tattoo, piercing, and jewelry cutouts are documented in the [adornment credits](assets/adornments/CREDITS.md). The [specimen credits](assets/specimens/CREDITS.md) cover photographed animal parts, additional glasses, and paper textures. The bundled Archivo Black typeface carries the [SIL Open Font License](assets/type/OFL.txt).
