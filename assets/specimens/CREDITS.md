# Photographic animal parts, spectacles, and stock

Each layer contains pixels from a photographed object, animal, or physical surface. The [manifest](library.json) maps each option to its source photograph, creator, license, and original-file SHA-256 digest.

| Layers | Photograph and creator | License |
| --- | --- | --- |
| Cat ears | [Cat-ears.jpg](https://commons.wikimedia.org/wiki/File:Cat-ears.jpg) by Jim Conrad | Public-domain release by the photographer |
| Cottontail ears | [Cottontail rabbits](https://commons.wikimedia.org/wiki/File:Cottontail_rabbits_-_37514488816_%28portrait%29.jpg) by lwolfartist | [CC BY 2.0](https://creativecommons.org/licenses/by/2.0/) |
| Velvet antlers | [Red deer stag](https://commons.wikimedia.org/wiki/File:Red_deer_stag.jpg) by Mehmet Karatay | [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/) |
| Tabby eyes and tabby muzzle | [Cat close-up 2004 b](https://commons.wikimedia.org/wiki/File:Cat_close-up_2004_b.jpg) by Cayambe | [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/) |
| Clip-on shades | [Clip-on sunglasses](https://commons.wikimedia.org/wiki/File:Clip-on_sunglasses.jpg) by Tiia Monto | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) |
| Round spectacles | [A pair of Spectacles, circa 1936](https://commons.wikimedia.org/wiki/File:A_pair_of_Spectacles_Wellcome_L0044000.jpg), Wellcome Library, London | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) |
| Paper fibers | [Paper002 4K Color](https://commons.wikimedia.org/wiki/File:Paper002_4K_Color.jpg) by ambientCG / Lennart Demes | [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/) |
| Letterpress grain | [Texture paper](https://commons.wikimedia.org/wiki/File:Texture_paper.jpg) by Paolo Neo | Public-domain release by the photographer |

All photographic fragments have been cropped, isolated, converted to grayscale, and resized. The cat and cottontail ears, tabby eyes, and muzzle use reflected copies to make a matched pair. The muzzle retains the photographed whiskers with their tone reversed for black ink. The paper layers isolate variations in fiber and printed ink density from their source photographs. The ShareAlike cutouts are available under the same licenses as their respective photographs.

## Rebuild

Use the Python environment described in the [main credits](../../CREDITS.md). From the project root, run the following command. The extractor downloads the originals into the specified cache, then generates the transparent WebPs and source manifest.

```sh
/tmp/face-press-tools/bin/python scripts/extract_specimens.py --cache /tmp/face-press-specimens --download
```

With a populated cache, omit `--download` to rebuild offline.

## Fish and wildlife expansion

The following additions use the photographed structure of actual gills, fins, eyes, ears, bills, lips and antlers. The source color and illumination have been converted to grayscale. Matching eyes, side fins, cheek gills, ears and moose antlers use mirrored photographic fragments. The file for each ShareAlike adaptation retains its source license.

| Layers | Photograph and credit | License |
| --- | --- | --- |
| Perch eyes, gill covers, dorsal crest, forked tail fins | [Yellow perch at Gavins Point](https://commons.wikimedia.org/wiki/File:Yellow_Perch_%28Perca_flavescens%29_white_background.jpg) by Sam Stukel, U.S. Fish and Wildlife Service | U.S. government work, public domain in the U.S. |
| Bluegill eyes, opercula, lips, fan fins, dorsal spines and pectoral fins | [Blue gill](https://commons.wikimedia.org/wiki/File:Blue_gill_%2851238121687%29.jpg) by Sam Stukel, U.S. Fish and Wildlife Service | U.S. government work, public domain in the U.S. |
| Tuna gill fans | [Tuna Gills cut out](https://commons.wikimedia.org/wiki/File:Tuna_Gills_cut_out.jpg), Chris 73 / Wikimedia Commons | [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/) |
| Puffin eyes and bill | [Puffin on Skomer Island](https://commons.wikimedia.org/wiki/File:Puffin_%28Fratercula_arctica%29_head.jpg), Charles J. Sharp / Sharp Photography | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) |
| Goat eyes | [Horizontal Rectangular Pupil of a Goat](https://commons.wikimedia.org/wiki/File:Horizontal_Rectangular_Pupil_of_a_Goat.jpg) by Sumbria.vikramaditya | [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/) |
| Moose ears and paddle antlers | [Bull Moose](https://commons.wikimedia.org/wiki/File:Bull_Moose.jpg) by Kent Miller, U.S. National Park Service, Denali National Park and Preserve | U.S. government work, public domain in the U.S. |

The tuna fragment is adapted from a [Wikipedia](https://www.wikipedia.org/) and [Wikimedia Commons](https://commons.wikimedia.org/) image by [Chris 73](https://en.wikipedia.org/wiki/User:Chris_73). The [original photograph](https://commons.wikimedia.org/wiki/File:Tuna_Gills_cut_out.jpg) is available under [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/).

The same rebuild command above includes the new animals. The [source tracings and mounting positions](../../scripts/wildlife.py) are applied to full-resolution photographs. The new layers render to 1024 × 1024 transparent WebPs. Their manifest bounds use the shared 512-unit portrait frame.
