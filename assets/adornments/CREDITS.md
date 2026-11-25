# Photographic adornments

## Tattoos

Game bird, Messenger bird, Lion on the prowl, Stag head, Winged dolphin, Stalking cat and Coiled dragon are cutouts of tattoos photographed on people's skin. The photographs appeared in *The Tatler* on 25 November 1903, page 311. The game bird is identified in the original as a design after Archibald Thorburn. The Messenger bird appeared under the caption “A Message of Peace.”

Wellcome Collection, reference 35574i, marks the complete illustrated work as public domain. The source sheet depicts the tattoo designs themselves. Stag head, Winged dolphin, Stalking cat and Coiled dragon come from four separate photographed arms on that sheet. The extraction masks the surrounding skin, removes uneven lighting and encodes ink density as transparency. [Collection record and rights statement](https://wellcomecollection.org/works/kv9bw5f4) · [Public Domain Mark](https://creativecommons.org/publicdomain/mark/1.0/) · [Source image](https://iiif.wellcomecollection.org/image/V0040689/full/full/0/default.jpg)

## Piercings

- **Zenú septum bar.** Zenú nose ornament, Colombia, 1–1000 CE. The Metropolitan Museum of Art, The Michael C. Rockefeller Memorial Collection, Bequest of Nelson A. Rockefeller, 1979, accession 1979.206.545. [Collection record](https://www.metmuseum.org/art/collection/search/312749)
- **Cast nose ornament.** Gold nose ornament, Venado Beach, Panama, 5th–8th century. The Metropolitan Museum of Art, The Michael C. Rockefeller Memorial Collection, Bequest of Nelson A. Rockefeller, 1979, accession 1979.206.1353. [Collection record](https://www.metmuseum.org/art/collection/search/313514)

- **Open gold hoop.** Gold nose ring, attributed to Ethiopia, probably 19th century. The Metropolitan Museum of Art, Gift of Meredith Howland, 1904, accession 04.34.9. The mask removes the display stand. [Collection record](https://www.metmuseum.org/art/collection/search/444954)
- **Moche crescent.** Gold nose ornament, Moche, 1st–3rd century. The Metropolitan Museum of Art, Rogers Fund, 1996, accession 1996.372.1. [Collection record](https://www.metmuseum.org/art/collection/search/317800)
- **Silver coin chain.** Silver nose ring, attributed to India, 19th century. The Metropolitan Museum of Art, Gift of Margaret Olivia Sage, 1916, accession 16.74.22. The layer isolates the ring, hanging coins and attached chain from the catalogue photograph. [Collection record](https://www.metmuseum.org/art/collection/search/446855)

## Jewelry

- **Crescent hoops.** The left and right cutouts are individually clipped from the catalogue photograph of gold crescent earrings, Roman, 1st century CE. The Metropolitan Museum of Art, The Cesnola Collection, Purchased by subscription, 1874–76, accession 74.51.3896. [Collection record](https://www.metmuseum.org/art/collection/search/243314)
- **Garnet drop.** Gold earring with pendant and garnet setting, Roman, 2nd century CE. The Metropolitan Museum of Art, Rogers Fund, 1920, accession 20.243. [Collection record](https://www.metmuseum.org/art/collection/search/250992)
- **Jhumka earring.** Gold and glass-bead earring, attributed to India, 19th century. The Metropolitan Museum of Art, John Stewart Kennedy Fund, 1915, accession 15.95.129. Mirrored for the left earlobe. [Collection record](https://www.metmuseum.org/art/collection/search/446792)

- **Embossed diadem.** Cypriot gold diadem, 4th century BCE. The Metropolitan Museum of Art, The Cesnola Collection, Purchased by subscription, 1874–76, accession 74.51.3291. [Collection record](https://www.metmuseum.org/art/collection/search/242724)
- **Herakles knot band.** Greek gold and garnet strap diadem, 3rd–2nd century BCE. The Metropolitan Museum of Art, Rogers Fund, 1920, accession 20.241. The original catalogue photograph is monochrome. [Collection record](https://www.metmuseum.org/art/collection/search/250990)
- **Beryl necklace.** Roman necklace with pearls and beryl beads, 1st–2nd century CE. The Metropolitan Museum of Art, Gift of George D. Pratt, 1925, accession 25.192.1. The front arc is clipped to hang at the neckline. [Collection record](https://www.metmuseum.org/art/collection/search/251937)
- **Onyx hairpin.** Silver, glass paste and onyx hairpin. The Metropolitan Museum of Art, The Cesnola Collection, Purchased by subscription, 1874–76, accession 74.51.3685. [Collection record](https://www.metmuseum.org/art/collection/search/243103)

## Eyewear

**Thule snow goggles.** Carved walrus-ivory goggles, Thule, ca. 800–1200. The Metropolitan Museum of Art, The Charles and Valerie Diker Collection of Native American Art, Gift of Charles and Valerie Diker, 2019, accession 2019.456.13. The cutout removes the display stand and backdrop. [Collection record](https://www.metmuseum.org/art/collection/search/751542)

The Met labels each of these object images public domain and makes its Open Access images available under CC0. Each cutout retains the color and surface detail from the museum photograph. The editor converts the layers to the selected print treatment. [The Met Open Access policy](https://www.metmuseum.org/about-the-met/policies-and-documents/open-access) · [CC0 dedication](https://creativecommons.org/publicdomain/zero/1.0/)

## Textures

Each texture uses a crop from the material’s 2048-pixel photographic diffuse map. Local light and dark detail are transferred to translucent pixels so facial features show through. Poly Haven distributes these textures under CC0. [Poly Haven license](https://polyhaven.com/license)

- **Furrowed bark.** *Bark Brown 01*, Rob Tuytel. [Source and license](https://polyhaven.com/a/bark_brown_01)
- **Hessian weave.** *Hessian 380*, photographed by colormass and processed by Rico Cilliers. [Source and license](https://polyhaven.com/a/hessian_380)
- **Denim twill.** *Denim Fabric 06*, photographed by Greg Zaal and processed by Rico Cilliers. [Source and license](https://polyhaven.com/a/denim_fabric_06)

## Rebuilding

Run `python scripts/extract_adornments.py /path/to/image-cache` from the project with Pillow, NumPy and OpenCV installed. The extractor downloads missing originals, verifies their SHA-256 hashes and writes the transparent WebP layers and catalog. The new layers are rendered on 1024-pixel canvases from their source photographs. All catalog bounds use the editor’s 512-pixel coordinate system. The catalog includes each source page, image URL, rights statement and hash.
