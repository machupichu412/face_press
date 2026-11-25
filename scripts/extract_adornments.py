"""Rebuild photo adornments. Requires Python 3, Pillow, numpy, opencv-python.

Usage: python scripts/extract_adornments.py /path/to/source-image-cache
A missing original is downloaded from its museum. Source pixels and layout are
pinned; an upstream image change is reported before applying a mask to it.
"""
import argparse
import hashlib
import json
from pathlib import Path
from urllib.request import Request, urlopen

import cv2
import numpy as np
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets/adornments"
MET = "The Metropolitan Museum of Art"
MET_IIIF = "https://collectionapi.metmuseum.org/api/collection/v1/iiif"
TATLER = "The Tatler, 25 November 1903, p. 311. Wellcome Collection, 35574i"

SOURCES = {
    "1903": {
        "title": "Six arms showing different designs of tattoo, and two smaller views of tattoos",
        "credit": TATLER,
        "url": "https://wellcomecollection.org/works/kv9bw5f4",
        "rights": "Public Domain Mark 1.0", "licenseUrl": "https://creativecommons.org/publicdomain/mark/1.0/",
        "image": "https://iiif.wellcomecollection.org/image/V0040689/full/full/0/default.jpg",
        "sha256": "2504c0c64c02c893f69e0e043d085e8c7c96704319bba04b6118fd84e21c6916",
    }
}
for object_id, image_id, title, accession, digest in [
    ("312749", "2177867", "Nose ornament, Zenú, 1–1000 CE", "1979.206.545", "d693b31501e2e52a8c844b8e4ec3c458c4ea26c8b34916818728c46f2b45b921"),
    ("313514", "1651525", "Nose ornament, Venado Beach, 5th–8th century", "1979.206.1353", "bb546c31b67ea8df253f567fe6dda86effaed7477533715359d0cf89bb293e07"),
    ("243314", "535343", "Earring, crescent-shaped, decorated, Roman, 1st century CE", "74.51.3896", "c63066d4dbe4c33f7eedff3da0f4134a74ebd9baa22959e1212332f523ed0a92"),
    ("250992", "1393922", "Gold earring with pendant and garnet setting, Roman, 2nd century CE", "20.243", "170de4f8fb0ff67da7213192fc2fb3c3f59975a27a5016a49bc5704781b6d1ce"),
    ("446792", "2010963", "Earring, one of a pair, attributed to India, 19th century", "15.95.129", "0a39e92807afe3bfd95d5c1e04c33d822a3fac7bc890067760f02bb3dc2fb780"),
    ("242724", "535790", "Gold diadem, Cypriot, 4th century BCE", "74.51.3291", "97e886f59b6a538f44a028cb67498d0e526bd6ef797132251f271f553a740991"),
    ("251937", "1396126", "Necklace with pearls and beryl beads, Roman, 1st–2nd century CE", "25.192.1", "e704e97bd12ddbb8a2ef36beddf5f948da84eb6c7c53da892fb22939a4fe8a0a"),
    ("243103", "544624", "Hair pin", "74.51.3685", "cba7b6f2acfd99e0d04d24912e2fcfd0f5867d4989b6fa701662ddfcf14a12d0"),
    ("317800", "660349", "Nose Ornament, Moche, 1st–3rd century", "1996.372.1", "bf2269c9612500b8e4d3fcf0f373f21f0b6066e1ce844016e459a19d6087c663"),
    ("444954", "1640417", "Nose Ring, probably 19th century", "04.34.9", "e18603a0810d5d752ddcf57b7f797f7d61c585dee4c758a2f19f96e455b558e1"),
    ("446855", "862952", "Nose Ring, 19th century", "16.74.22", "9c0bc7f5e8fa45652c83a2cad7c814dd136861707f74a731b5efb5641038ba65"),
    ("751542", "1791607", "Snow goggles, Thule, Native American, ca. 800–1200", "2019.456.13", "d239fc27935e723459ec72359fed2e0c8cc6c334aa4f0da7fafa8396a0a1bf56"),
    ("250990", "1638831", "Gold and garnet strap diadem with Herakles knot, Greek, 3rd–2nd century BCE", "20.241", "e54200aa4f3afc2631d99ad5c47faf01b8321467ed8a3ff9ebbdb2f2668baaad"),
]:
    SOURCES[object_id] = {
        "title": title, "credit": f"{MET}, {accession}",
        "url": f"https://www.metmuseum.org/art/collection/search/{object_id}",
        "rights": "CC0-1.0", "licenseUrl": "https://creativecommons.org/publicdomain/zero/1.0/",
        "image": f"{MET_IIIF}/{object_id}/{image_id}/main-image", "sha256": digest,
    }


for texture, title, credit, digest in [
    ("bark_brown_01", "Bark Brown 01", "Rob Tuytel", "0cdd066f34d357fdbf7eb99159e668a6dc346bb7fd093a9e27058eb827d09b9a"),
    ("denim_fabric_06", "Denim Fabric 06", "Greg Zaal (photography), Rico Cilliers (processing)", "ddeaa6edd75e9bb8f01764a3cf591a88cf260b89dadc1ac9ab6185c03ff0cecf"),
    ("hessian_380", "Hessian 380", "colormass (photography), Rico Cilliers (processing)", "14a21d84cdd20cb3c64457b070d1ce220496e25652de063709ceed2ab453ee09"),
]:
    SOURCES[texture] = {
        "title": title, "credit": f"{credit}, Poly Haven",
        "url": f"https://polyhaven.com/a/{texture}", "rights": "CC0-1.0",
        "licenseUrl": "https://creativecommons.org/publicdomain/zero/1.0/",
        "image": f"https://dl.polyhaven.org/file/ph-assets/Textures/jpg/2k/{texture}/{texture}_diff_2k.jpg",
        "sha256": digest,
    }


def original(cache, source):
    path = cache / f"{source}.jpg"
    record = SOURCES[source]
    if not path.exists():
        request = Request(record["image"], headers={"User-Agent": "FacePress-Artwork-Extraction/1.0"})
        with urlopen(request, timeout=90) as response:
            data = response.read()
        if hashlib.sha256(data).hexdigest() != record["sha256"]:
            raise ValueError(f"Unexpected source, please review the photograph at {record['url']}")
        path.write_bytes(data)
    if hashlib.sha256(path.read_bytes()).hexdigest() != record["sha256"]:
        raise ValueError(f"Source file changed: {path}")
    return Image.open(path).convert("RGB")


def tattoo(photo, points, threshold=2.5):
    # The outlines select the photographed tattoo. Local white-point estimation
    # separates ink from curved, unevenly lit skin on the 1903 halftone page.
    gray = np.asarray(photo.convert("L"))
    coords = np.rint(np.array(points) * photo.height / 1200).astype(np.int32)
    x, y, w, h = cv2.boundingRect(coords)
    gray = gray[y:y+h, x:x+w]
    selection = np.zeros_like(gray)
    cv2.fillPoly(selection, [coords - [x, y]], 255)
    selection = cv2.GaussianBlur(selection, (0, 0), 2.3)
    smooth = cv2.GaussianBlur(gray, (0, 0), 1.55)
    # Closing estimates the tone around both large ink fields and fine details.
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (101, 101))
    skin = cv2.morphologyEx(smooth, cv2.MORPH_CLOSE, kernel)
    contrast = (skin.astype(float) - smooth - threshold) * 3.1
    alpha = (np.clip(contrast, 0, 245) * (selection / 255)).astype("uint8")
    # Encoding ink density in alpha lets the face show through pale regions.
    cut = Image.new("RGBA", (w, h), (21, 21, 21, 0))
    cut.putalpha(Image.fromarray(alpha))
    return cut.crop(cut.getbbox())


def jewel(photo, box, jhumka=False):
    # Crop to the catalogued object. Positive seeds distinguish warm metal from
    # museum backdrops. GrabCut retains highlights and removes enclosed holes.
    rgb = np.ascontiguousarray(np.asarray(photo.crop(box)))
    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
    if jhumka:
        red, green, blue = np.moveaxis(rgb.astype(float), -1, 0)
        positive = ((red - blue > 59) | (green > red) | (red < 70))
    else:
        positive = hsv[:, :, 1] > 56
    seed = positive.astype(np.uint8)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    # Ring apertures stay transparent; only a narrow neighborhood can grow.
    candidate = cv2.dilate(seed, kernel, iterations=4).astype(bool)
    mask = np.zeros(positive.shape, np.uint8)
    mask[candidate] = cv2.GC_PR_BGD
    mask[positive] = cv2.GC_PR_FGD
    mask[cv2.erode(seed, kernel).astype(bool)] = cv2.GC_FGD
    cv2.grabCut(rgb, mask, None, np.zeros((1, 65)), np.zeros((1, 65)), 5, cv2.GC_INIT_WITH_MASK)
    matte = ((mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD)).astype(np.uint8)
    count, labels, stats, _ = cv2.connectedComponentsWithStats(matte)
    largest = 1 + int(np.argmax(stats[1:count, cv2.CC_STAT_AREA]))
    alpha = cv2.GaussianBlur((labels == largest).astype(np.uint8) * 255, (3, 3), 0.6)
    cut = Image.fromarray(rgb).convert("RGBA")
    cut.putalpha(Image.fromarray(alpha))
    return cut.crop(cut.getbbox())


def place(layer, part, width, center, top):
    scale = layer.width // 512
    width, center, top = width * scale, center * scale, top * scale
    height = round(part.height * width / part.width)
    part = part.resize((width, height), Image.Resampling.LANCZOS)
    layer.alpha_composite(part, (round(center - width / 2), top))


def tonal_piece(photo, matte):
    """Trim a source photograph to its supplied opacity map."""
    cut = photo.convert("RGBA")
    alpha = np.clip(matte, 0, 255).astype(np.uint8)
    cut.putalpha(Image.fromarray(alpha))
    return cut.crop(cut.getbbox())


def region(photo, reference_width, points, cutouts=()):
    """Antialiased source contour, with optional interior holes."""
    alpha = np.zeros((photo.height, photo.width), np.uint8)
    for boundary, value in [(points, 255), *((hole, 0) for hole in cutouts)]:
        outline = np.rint(np.array(boundary) * (photo.width / reference_width)).astype(np.int32)
        cv2.fillPoly(alpha, [outline], value)
    return cv2.GaussianBlur(alpha, (3, 3), 0.6)


def textile(photo, box):
    """Keep the contrast of a photographed material as a translucent print."""
    gray = np.asarray(photo.crop(box).resize((1024, 1024), Image.Resampling.LANCZOS).convert("L"), float)
    detail = gray - cv2.GaussianBlur(gray, (0, 0), 46)
    lo, hi = np.percentile(detail, [2, 98])
    value = (detail - lo) / max(1, hi - lo) * 2 - 1
    value = np.clip(value, -1, 1)
    # Pale fibers remain visible over hair while dark fibers print onto paper.
    rgba = np.empty((*gray.shape, 4), dtype=np.uint8)
    rgba[:, :, :3] = np.where(value[:, :, None] < 0, 22, 238)
    rgba[:, :, 3] = np.round(np.abs(value) * 100)
    return Image.fromarray(rgba)


def add_photographs(photos, save):
    def layer(category, slug, name, source, cut, width, center, top):
        save(category, slug, name, source, [(cut, width, center, top)], size=1024)

    more_tattoos = [
        ("stag", "Stag head", 53, 195, 254,
         [(354,920),(361,918),(369,938),(376,948),(371,923),(370,908),(376,908),(385,932),
          (383,912),(374,902),(373,887),(379,888),(388,905),(389,891),(398,878),(404,880),
          (398,898),(399,914),(402,907),(406,880),(413,879),(413,889),(407,911),(414,906),
          (425,880),(433,880),(429,894),(417,916),(410,938),(409,958),(416,976),(415,955),
          (420,949),(426,960),(431,976),(447,957),(443,937),(452,946),(459,961),(460,945),
          (454,919),(443,899),(447,890),(459,901),(465,911),(465,893),(471,895),(477,918),
          (476,901),(483,893),(485,914),(489,903),(497,898),(495,931),(491,955),(495,984),
          (496,1054),(478,1053),(451,1044),(441,1052),(427,1045),(415,1057),(409,1070),
          (399,1072),(391,1068),(390,1058),(396,1033),(398,1000),(379,994),(367,988),
          (361,977),(362,968),(377,981),(389,982),(372,969),(359,954)]),
        ("winged-dolphin", "Winged dolphin", 47, 311, 254,
         [(97,889),(103,879),(116,872),(130,872),(148,876),(155,886),(161,892),(148,899),
          (147,904),(159,909),(184,910),(202,905),(208,907),(227,919),(239,931),(251,952),
          (254,973),(243,968),(250,1009),(258,1043),(273,1065),(281,1078),(265,1086),
          (245,1079),(239,1095),(246,1112),(237,1110),(227,1099),(219,1080),(215,1047),
          (211,1010),(201,989),(196,1016),(194,1041),(183,1021),(170,995),(161,977),
          (156,959),(151,944),(143,945),(136,931),(121,930),(114,919),(102,915),(99,907)]),
        ("stalking-cat", "Stalking cat", 38, 198, 254,
         [(111,446),(128,433),(144,419),(160,411),(178,410),(197,423),(201,442),(199,458),
          (214,473),(230,490),(239,515),(241,544),(236,571),(226,599),(220,625),(210,646),
          (198,650),(181,646),(176,634),(183,621),(172,614),(166,621),(168,647),(173,671),
          (184,685),(179,697),(162,696),(146,691),(137,661),(134,627),(125,579),(121,542),
          (128,507),(133,473),(139,447),(127,453),(112,458)]),
        ("coiled-dragon", "Coiled dragon", 35, 313, 251,
         [(604,398),(615,382),(632,376),(652,377),(664,386),(677,379),(689,380),
          (700,394),(708,414),(700,427),(690,430),(701,438),(706,452),(702,471),
          (698,492),(702,512),(701,533),(696,555),(695,582),(691,611),(684,644),
          (680,678),(672,699),(636,698),(641,681),(626,674),(616,658),(607,660),
          (600,675),(591,683),(593,662),(587,672),(591,653),(592,633),(594,615),
          (608,599),(608,590),(601,584),(593,581),(600,560),(592,565),(594,550),
          (601,540),(592,536),(597,527),(605,524),(594,506),(590,482),(588,449),
          (594,431),(601,439),(605,435),(598,418)]),
    ]
    for slug, name, width, center, top, polygon in more_tattoos:
        cut = tattoo(photos["1903"], polygon)
        # These motifs wrap around the photographed arm. Taper their cropped
        # outlines into the underlying portrait at the source photograph's edge.
        if slug in {"stag", "coiled-dragon"}:
            opacity = np.array(cut.getchannel("A"), float)
            right = np.linspace(1, 0, max(2, round(cut.width * 0.16)))
            opacity[:, -len(right):] *= right
            if slug == "coiled-dragon":
                bottom = np.linspace(1, 0, max(2, round(cut.height * 0.06)))
                opacity[-len(bottom):, :] *= bottom[:, None]
            cut.putalpha(Image.fromarray(opacity.astype("uint8")))
        layer("tattoo", slug, name, "1903", cut, width, center, top)

    photo = photos["444954"]
    hoop_mask = region(photo, 330, [
        (83,209),(84,195),(90,180),(100,168),(114,157),(129,151),(147,147),
        (169,149),(186,152),(201,160),(218,170),(230,184),(238,199),(242,214),
        (243,228),(239,242),(232,253),(220,261),(208,266),(195,271),(185,271),
        (183,263),(189,256),(202,252),(211,246),(217,236),(221,224),(221,213),
        (218,202),(208,190),(196,183),(185,178),(166,173),(149,173),(134,177),
        (122,183),(114,192),(109,204),(107,216),(111,228),(118,239),(128,247),
        (141,253),(146,254),(147,263),(157,268),(161,274),(141,270),(127,265),
        (113,258),(99,244),(90,230),(85,218)
    ])
    hoop = tonal_piece(photo, hoop_mask).rotate(162, Image.Resampling.BICUBIC, expand=True)
    hoop = hoop.crop(hoop.getbbox())
    layer("piercing", "open-hoop", "Open gold hoop", "444954", hoop, 30, 238, 282)

    plate = jewel(photos["317800"], (65, 25, 1163, 696))
    layer("piercing", "moche-crescent", "Moche crescent", "317800", plate, 66, 256, 282)

    photo = photos["446855"]
    # The museum photographed the long hook folded back above the chain.
    # Isolate its hanging run and the ring in their worn orientation.
    mask = region(photo, 700, [(0,95),(49,83),(82,63),(94,69),(98,99),(124,122),
        (192,129),(237,134),(268,137),(333,147),(375,155),(417,150),(466,137),
        (501,129),(501,87),(515,39),(545,10),(589,0),(649,0),(699,33),
        (699,279),(0,279)])
    gray = np.asarray(photo.convert("L"), float)
    cut = tonal_piece(photo, np.clip((244-gray)*3.1, 0, 255) * (mask/255))
    layer("piercing", "coin-chain", "Silver coin chain", "446855", cut, 123, 192, 270)

    circlet = jewel(photos["242724"], (42, 311, 1171, 549))
    layer("jewelry", "foliate-diadem", "Embossed diadem", "242724", circlet, 181, 256, 164)

    photo = photos["250990"]
    gray = np.asarray(photo.convert("L"), float)
    mask = region(photo,1200,[(73,153),(102,115),(489,111),(520,106),(549,99),
         (595,92),(626,106),(645,113),(716,109),(1079,116),(1117,132),
         (1137,159),(1120,198),(1103,210),(672,215),(637,223),(603,229),
         (549,226),(500,217),(109,217),(76,197)])
    # The grayscale catalogue negative includes a diffuse studio shadow.
    band = tonal_piece(photo, np.clip((195-gray)*3,0,255)*(mask/255))
    layer("jewelry", "herakles", "Herakles knot band", "250990", band, 193, 255, 153)

    photo = photos["251937"]
    rgb = np.asarray(photo, dtype=float)
    # Preserve the necklace's lower arc and its separate light-blue pendant.
    necklace_mask = region(photo,400,[(82,203),(88,199),(98,201),(101,217),(106,235),
        (127,251),(154,268),(179,273),(195,272),(206,277),(243,266),(264,250),
        (281,236),(289,216),(291,200),(306,199),(305,223),(293,245),(270,266),
        (246,281),(221,286),(207,293),(177,295),(148,285),(124,275),(100,252),(86,239)])
    tone = np.max(rgb,axis=2)-np.min(rgb,axis=2)
    intensity = np.maximum((tone-12)*13,(155-np.max(rgb,axis=2))*4.5)
    pearls = tonal_piece(photo,np.clip(intensity,0,255)*(necklace_mask/255))
    layer("jewelry", "beryl-strand", "Beryl necklace", "251937", pearls, 134, 256, 409)

    photo = photos["243103"]
    gray = np.asarray(photo.convert("L"), float)
    onyx = tonal_piece(photo,np.clip((209-gray)*6,0,255)*
        (region(photo,300,[(116,89),(137,74),(139,58),(159,58),(162,81),(183,90),
          (186,149),(164,157),(160,287),(132,287),(131,157),(116,145)])/255))
    onyx = onyx.rotate(42,Image.Resampling.BICUBIC,expand=True)
    layer("jewelry", "onyx-pin", "Onyx hairpin", "243103", onyx.crop(onyx.getbbox()), 57, 170, 129)

    goggles = jewel(photos["751542"], (244, 233, 970, 500))
    layer("glasses", "thule-goggles", "Thule snow goggles", "751542", goggles, 215, 256, 211)

    for source, slug, name, box in [
        ("bark_brown_01", "bark", "Furrowed bark", (160, 140, 1840, 1820)),
        ("hessian_380", "hessian", "Hessian weave", (414, 486, 1246, 1318)),
        ("denim_fabric_06", "denim", "Denim twill", (248, 300, 1256, 1308)),
    ]:
        layer("texture", slug, name, source, textile(photos[source],box), 512, 256, 0)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("cache", type=Path)
    args = parser.parse_args()
    args.cache.mkdir(parents=True, exist_ok=True)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    photos = {key: original(args.cache, key) for key in SOURCES}
    library = {"size": 512, "parts": {"tattoo": [], "piercing": [], "jewelry": [], "texture": [], "glasses": []}, "sources": SOURCES}
    cv2.setRNGSeed(1)

    def save(category, slug, name, source, placements, size=512):
        layer = Image.new("RGBA", (size, size))
        for part, width, center, top in placements:
            place(layer, part, width, center, top)
        identifier = f"{category}-{slug}"
        path = OUTPUT / f"{identifier}.webp"
        layer.save(path, lossless=True, method=6, exact=True)
        x, y, right, bottom = layer.getbbox()
        scale = size // 512
        x, y = x // scale, y // scale
        right, bottom = (right+scale-1) // scale, (bottom+scale-1) // scale
        library["parts"][category].append({
            "id": identifier, "name": name, "src": path.relative_to(ROOT).as_posix(),
            "bounds": [x,y,right-x,bottom-y], "source": source
        })

    tattoo_specs = [
        ("gamebird","Game bird",52,310,257,
         [(66,210),(73,200),(89,188),(110,179),(132,175),(155,176),(162,166),(167,153),(176,146),(195,139),(203,140),(199,151),(190,158),(185,175),(185,189),(197,204),(214,235),(224,258),(216,273),(205,272),(175,257),(158,245),(145,232),(133,239),(122,254),(115,240),(111,244),(97,284),(90,285),(91,262),(94,244),(97,230),(82,233),(64,224)]),
        ("messenger","Messenger bird",43,196,259,
         [(613,166),(623,173),(640,200),(652,219),(656,213),(657,197),(646,174),(635,157),(640,154),(660,176),(672,184),(688,153),(694,156),(685,178),(679,199),(679,215),(698,188),(703,187),(698,213),(683,237),(662,255),(655,265),(665,259),(682,251),(677,276),(667,281),(655,275),(650,268),(641,271),(638,266),(639,251),(630,240),(624,212)]),
        ("lion","Lion on the prowl",34,307,257,
         [(404,385),(410,391),(409,413),(426,428),(439,419),(445,405),(459,401),(477,404),(481,423),(486,439),(479,459),(469,487),(455,525),(445,560),(417,615),(398,636),(394,659),(407,669),(410,678),(407,684),(397,682),(389,677),(385,668),(384,650),(387,632),(373,639),(350,649),(347,643),(356,626),(364,617),(368,606),(378,565),(381,546),(376,545),(378,528),(386,519),(387,495),(386,475),(393,449),(390,428),(395,404)]),
    ]
    for slug, name, width, center, top, points in tattoo_specs:
        part = tattoo(photos["1903"], points)
        save("tattoo", slug, name, "1903", [(part, width, center, top)])

    bar = jewel(photos["312749"], (65, 40, 1140, 295))
    save("piercing", "zenu-bar", "Zenú septum bar", "312749", [(bar, 98, 256, 287)])
    crown = jewel(photos["313514"], (340, 239, 878, 688))
    save("piercing", "filigree", "Cast nose ornament", "313514", [(crown, 37, 256, 286)])
    left = jewel(photos["243314"], (173, 235, 570, 662))
    right = jewel(photos["243314"], (599, 237, 1045, 661))
    save("jewelry", "crescents", "Crescent hoops", "243314", [(left, 30, 145, 274), (right, 30, 367, 274)])
    drop = jewel(photos["250992"], (307, 292, 634, 940))
    save("jewelry", "garnet", "Garnet drop", "250992", [(drop, 27, 365, 272)])
    jhumka = jewel(photos["446792"], (72, 224, 655, 937), jhumka=True)
    save("jewelry", "jhumka", "Jhumka earring", "446792", [(ImageOps.mirror(jhumka), 55, 148, 269)])
    add_photographs(photos, save)
    (OUTPUT / "library.json").write_text(json.dumps(library, ensure_ascii=False, indent=2) + "\n")
    print({key: len(parts) for key, parts in library["parts"].items()})


if __name__ == "__main__":
    main()
