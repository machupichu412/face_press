"""Rebuild the photographic animal cutouts, eyewear and paper overlays.

Usage: python scripts/extract_specimens.py --cache /tmp/specimen-photos --download
Dependencies: Pillow, NumPy, OpenCV, and curl for optional downloads.
"""

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from urllib.parse import quote

import cv2
import numpy as np
import wildlife
from PIL import Image, ImageFilter, ImageOps

OUTPUT = Path(__file__).resolve().parents[1] / "assets" / "specimens"
SITE_PATH = "assets/specimens/"
SIDE = 512
LANCZOS = Image.Resampling.LANCZOS
# Filename, creator, license, and license URL for the exact source photograph.
SOURCES = {
    **wildlife.SOURCES,
    "ears": ("Cat-ears.jpg", "Jim Conrad", "Public domain (author release)", None),
    "rabbit": (
        "Cottontail_rabbits_-_37514488816_(portrait).jpg",
        "lwolfartist",
        "CC BY 2.0",
        "https://creativecommons.org/licenses/by/2.0/",
    ),
    "deer2": (
        "Red_deer_stag.jpg",
        "Mehmet Karatay",
        "CC BY-SA 3.0",
        "https://creativecommons.org/licenses/by-sa/3.0/",
    ),
    "cat": (
        "Cat_close-up_2004_b.jpg",
        "Cayambe",
        "CC BY-SA 3.0",
        "https://creativecommons.org/licenses/by-sa/3.0/",
    ),
    "shades": (
        "Clip-on_sunglasses.jpg",
        "Tiia Monto",
        "CC BY-SA 4.0",
        "https://creativecommons.org/licenses/by-sa/4.0/",
    ),
    "glasses": (
        "A_pair_of_Spectacles_Wellcome_L0044000.jpg",
        "Wellcome Library, London",
        "CC BY 4.0",
        "https://creativecommons.org/licenses/by/4.0/",
    ),
    "paper": ("Texture_paper.jpg", "Paolo Neo", "Public domain (author release)", None),
    "paper2": (
        "Paper002_4K_Color.jpg",
        "ambientCG.com / Lennart Demes",
        "CC0 1.0",
        "https://creativecommons.org/publicdomain/zero/1.0/",
    ),
}


def originals(cache, download):
    pictures, records = {}, {}
    for key, (filename, author, rights, license_url) in SOURCES.items():
        suffix = hashlib.md5(filename.encode()).hexdigest()
        raw = f"https://upload.wikimedia.org/wikipedia/commons/{suffix[0]}/{suffix[:2]}/{quote(filename)}"
        local = cache / (key + ".jpg")
        if not local.exists() and download:
            partial = local.with_suffix(".partial")
            subprocess.run(
                [
                    "curl",
                    "--fail",
                    "--location",
                    "--retry",
                    "2",
                    "--output",
                    str(partial),
                    raw,
                ],
                check=True,
            )
            partial.replace(local)
        original = ImageOps.exif_transpose(Image.open(local)).convert("RGB")
        pictures[key] = original
        records[key] = {
            "title": filename.replace("_", " "),
            "creator": author,
            "rights": rights,
            "url": "https://commons.wikimedia.org/wiki/File:" + quote(filename),
            "licenseUrl": license_url,
            "sha256": hashlib.sha256(local.read_bytes()).hexdigest(),
        }
    return pictures, records


def reference(photo, angle=0):
    if angle:
        photo = photo.rotate(angle, Image.Resampling.BICUBIC, expand=True)
    return photo.resize((800, round(photo.height * 800 / photo.width)), LANCZOS)


def matte(photo, loops):
    """Trace source contours on the 800px reference. Only the alpha is drawn."""
    mask = np.zeros((photo.height, photo.width), np.uint8)
    for points in loops:
        cv2.fillPoly(mask, [np.array(points, np.int32)], 255, lineType=cv2.LINE_AA)
    return mask


def cut(photo, mask, cutoff=1):
    gray = photo.convert("L")
    gray = gray.filter(ImageFilter.UnsharpMask(radius=1.1, percent=95, threshold=3))
    ink = gray.convert("RGBA")
    alpha = Image.fromarray(np.uint8(np.clip(mask, 0, 255)))
    ink.putalpha(alpha)
    bounds = alpha.point(lambda x: 255 if x >= cutoff else 0).getbbox()
    return ink.crop(bounds)


def stamp(piece, width, center, paired=False, mirror_first=False, angle=0):
    """Place photographic fragments in the same frame as the aligned faces."""
    if angle:
        piece = piece.rotate(angle, Image.Resampling.BICUBIC, expand=True)
        piece = piece.crop(piece.getbbox())
    piece = piece.resize((width, round(width * piece.height / piece.width)), LANCZOS)
    if mirror_first:
        piece = ImageOps.mirror(piece)
    canvas = Image.new("RGBA", (SIDE, SIDE))
    x, y = center
    left = round(x - piece.width / 2)
    top = round(y - piece.height / 2)
    canvas.alpha_composite(piece, (left, top))
    if paired:
        canvas.alpha_composite(ImageOps.mirror(piece), (SIDE - left - piece.width, top))
    return canvas


def cat_ears(photo):
    ref = reference(photo)
    edge = [
        (93, 492),
        (152, 413),
        (238, 340),
        (326, 252),
        (410, 183),
        (461, 129),
        (502, 93),
        (541, 69),
        (575, 61),
        (602, 66),
        (621, 86),
        (638, 122),
        (644, 169),
        (641, 237),
        (632, 284),
        (624, 338),
        (609, 388),
        (596, 432),
        (583, 477),
        (572, 527),
        (560, 591),
        (556, 660),
        (495, 674),
        (404, 661),
        (309, 635),
        (210, 592),
        (134, 542),
    ]
    return stamp(cut(ref, matte(ref, [edge])), 91, (163, 132), True, mirror_first=True)


def rabbit_ears(photo):
    ref = reference(photo)
    edge = [
        (496, 268),
        (505, 218),
        (525, 178),
        (549, 154),
        (580, 137),
        (611, 125),
        (635, 122),
        (651, 128),
        (668, 145),
        (681, 168),
        (693, 202),
        (703, 249),
        (714, 292),
        (720, 339),
        (721, 391),
        (714, 424),
        (703, 454),
        (686, 476),
        (663, 495),
        (647, 526),
        (641, 562),
        (620, 601),
        (580, 614),
        (547, 607),
        (530, 576),
        (522, 530),
        (524, 481),
        (523, 442),
        (517, 397),
        (509, 360),
        (501, 318),
    ]
    return stamp(cut(ref, matte(ref, [edge])), 64, (203, 94), True, True, angle=-11)


def antlers(photo):
    ref = reference(photo)
    # The trailing stag in the background is outside both masks.
    left = [
        (64, 30),
        (69, 28),
        (76, 31),
        (80, 43),
        (82, 58),
        (88, 72),
        (93, 80),
        (101, 79),
        (112, 68),
        (125, 51),
        (141, 35),
        (156, 23),
        (163, 23),
        (164, 29),
        (154, 37),
        (141, 54),
        (132, 67),
        (127, 78),
        (128, 91),
        (129, 106),
        (131, 120),
        (136, 137),
        (142, 151),
        (155, 163),
        (170, 176),
        (195, 194),
        (225, 212),
        (250, 228),
        (264, 241),
        (262, 223),
        (258, 199),
        (254, 170),
        (252, 143),
        (251, 117),
        (251, 92),
        (256, 86),
        (262, 88),
        (265, 98),
        (267, 118),
        (269, 145),
        (272, 175),
        (276, 203),
        (280, 230),
        (284, 250),
        (292, 258),
        (299, 258),
        (301, 266),
        (289, 278),
        (271, 279),
        (253, 264),
        (233, 251),
        (209, 234),
        (187, 218),
        (160, 196),
        (138, 175),
        (116, 154),
        (100, 134),
        (88, 115),
        (80, 96),
        (73, 75),
        (67, 53),
    ]
    right = [
        (332, 264),
        (347, 262),
        (363, 253),
        (380, 237),
        (407, 219),
        (426, 202),
        (442, 186),
        (450, 175),
        (451, 167),
        (444, 170),
        (439, 168),
        (438, 161),
        (447, 159),
        (454, 151),
        (461, 150),
        (467, 157),
        (463, 137),
        (459, 119),
        (450, 98),
        (441, 79),
        (437, 68),
        (440, 62),
        (447, 64),
        (455, 73),
        (466, 89),
        (478, 113),
        (485, 140),
        (486, 163),
        (482, 180),
        (491, 171),
        (498, 159),
        (500, 145),
        (496, 133),
        (490, 123),
        (491, 116),
        (497, 112),
        (503, 113),
        (507, 122),
        (510, 135),
        (515, 151),
        (514, 166),
        (507, 179),
        (494, 190),
        (479, 198),
        (470, 198),
        (459, 209),
        (444, 226),
        (431, 240),
        (412, 251),
        (389, 262),
        (366, 272),
        (349, 281),
        (335, 280),
        (328, 275),
    ]
    return stamp(cut(ref, matte(ref, [left, right])), 268, (256, 85))


def feline_parts(photo):
    ref = reference(photo, -29)
    eye = [
        (431, 302),
        (434, 286),
        (443, 276),
        (456, 264),
        (478, 252),
        (490, 247),
        (511, 247),
        (523, 246),
        (523, 259),
        (520, 280),
        (509, 301),
        (497, 312),
        (481, 320),
        (460, 322),
        (445, 321),
        (434, 318),
    ]
    yield (
        "tabby-eyes",
        "Tabby eyes",
        stamp(cut(ref, matte(ref, [eye])), 55, (201, 236), True, True),
    )
    muzzle = [
        (381, 429),
        (398, 428),
        (423, 428),
        (441, 423),
        (460, 418),
        (476, 421),
        (486, 429),
        (491, 444),
        (490, 464),
        (483, 482),
        (470, 497),
        (454, 507),
        (435, 513),
        (414, 517),
        (394, 518),
        (381, 514),
    ]
    mask = matte(ref, [muzzle])
    # Extract photographed whisker highlights against the darker background;
    # their angle, curvature and spacing come directly from the photographed fur.
    whisker_zone = matte(
        ref,
        [
            [
                (463, 422),
                (664, 373),
                (643, 405),
                (670, 434),
                (668, 477),
                (648, 518),
                (618, 574),
                (527, 515),
                (463, 476),
            ]
        ],
    )
    gray = np.array(ref.convert("L"), np.float32)
    bright = np.maximum(0, gray - cv2.GaussianBlur(gray, (0, 0), 2.6) - 10)
    lines = np.minimum(255, bright * 5) * whisker_zone / 255
    mask = np.maximum(mask, lines.astype(np.uint8))
    ink = np.array(ref.convert("L"))
    ink[(lines > 0) & (matte(ref, [muzzle]) == 0)] = (
        50  # Invert the isolated pale hairs for dark ink.
    )
    right = Image.fromarray(ink).convert("RGBA")
    right.putalpha(Image.fromarray(mask))
    right = right.crop((381, 370, 672, 577))
    whole = Image.new("RGBA", (right.width * 2, right.height))
    whole.alpha_composite(ImageOps.mirror(right), (0, 0))
    whole.alpha_composite(right, (right.width, 0))
    yield "tabby-muzzle", "Tabby muzzle", stamp(whole, 210, (256, 300))


def shades(photo):
    ref = reference(photo)
    gray = np.asarray(ref.convert("L"), dtype=np.float32)
    mask = np.clip((248 - gray) * 10, 0, 255)
    return stamp(cut(ref, mask), 242, (256, 236))


def wire_frames(photo):
    ref = reference(photo)
    gray = np.asarray(ref.convert("L"), dtype=np.float32)
    band = np.zeros_like(gray, np.uint8)
    # Fit each real rim to five measured points. Retain the photograph's
    # local density inside the narrow bands and remove folded temple arms.
    left = [
        (170, 101),
        (191, 59),
        (246, 26),
        (312, 32),
        (357, 61),
        (381, 111),
        (379, 159),
        (354, 199),
        (310, 226),
        (264, 230),
        (215, 214),
        (179, 175),
        (168, 137),
    ]
    right = [
        (495, 192),
        (506, 155),
        (535, 122),
        (577, 107),
        (623, 106),
        (667, 121),
        (699, 148),
        (719, 186),
        (723, 224),
        (711, 261),
        (681, 294),
        (644, 310),
        (603, 314),
        (555, 304),
        (523, 282),
        (503, 247),
    ]
    for points in [left, right]:
        ellipse = cv2.fitEllipse(np.array(points, np.int32))
        cv2.ellipse(band, ellipse, 255, 7, lineType=cv2.LINE_AA)
    bridge = [
        (378, 183),
        (384, 159),
        (389, 119),
        (393, 106),
        (400, 98),
        (417, 94),
        (443, 96),
        (472, 102),
        (491, 115),
        (507, 132),
        (508, 141),
        (501, 149),
        (497, 171),
        (494, 205),
        (487, 215),
        (483, 191),
        (484, 155),
        (489, 140),
        (498, 133),
        (487, 120),
        (467, 110),
        (439, 102),
        (414, 101),
        (403, 106),
        (400, 123),
        (403, 143),
        (392, 166),
    ]
    hinge_l = [(145, 96), (164, 97), (177, 100), (173, 115), (158, 116), (144, 107)]
    hinge_r = [(717, 230), (735, 232), (754, 239), (750, 251), (732, 250), (715, 244)]
    band |= matte(ref, [bridge, hinge_l, hinge_r])
    alpha = np.minimum(255, (255 - gray) * 2.6) * band.astype(np.float32) / 255
    return stamp(cut(ref, alpha), 236, (256, 236), angle=13.5)


def grain(photo, box, ink_range):
    # Crop actual stock with a relatively constant local light; remove
    # the illumination gradient while keeping the paper and ink structure.
    gray = np.asarray(
        photo.crop(box).resize((SIDE, SIDE), LANCZOS).convert("L"), np.float32
    )
    detail = gray - cv2.GaussianBlur(gray, (0, 0), 24)
    low, high = np.percentile(detail, [2, 98])
    opacity = np.clip((high - detail) / max(1, high - low), 0, 1) * ink_range
    ink = Image.new("RGBA", (SIDE, SIDE), (33, 33, 33, 0))
    ink.putalpha(Image.fromarray(opacity.astype(np.uint8)))
    return ink


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", type=Path, required=True)
    parser.add_argument("--download", action="store_true")
    args = parser.parse_args()
    args.cache.mkdir(parents=True, exist_ok=True)
    photos, sources = originals(args.cache, args.download)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    parts = {
        key: []
        for key in (
            "ears",
            "eyes",
            "nose",
            "mouth",
            "gills",
            "fins",
            "antlers",
            "glasses",
            "texture",
        )
    }

    def add(group, key, label, source, image):
        name = key + ".webp"
        image.save(OUTPUT / name, lossless=True, method=5)
        parts[group].append(
            {
                "id": key,
                "name": label,
                "src": SITE_PATH + name,
                "bounds": wildlife.normalized_bounds(image),
                **({"origin": "animal"} if group not in ("texture", "glasses") else {}),
                "source": source,
            }
        )

    add("ears", "cat-ears", "Cat ears", "ears", cat_ears(photos["ears"]))
    add(
        "ears",
        "cottontail-ears",
        "Cottontail ears",
        "rabbit",
        rabbit_ears(photos["rabbit"]),
    )
    add("antlers", "stag-antlers", "Velvet antlers", "deer2", antlers(photos["deer2"]))
    for key, label, image in feline_parts(photos["cat"]):
        add("eyes" if key == "tabby-eyes" else "nose", key, label, "cat", image)
    for spec in wildlife.TRACINGS:
        add(
            spec.category,
            spec.key,
            spec.title,
            spec.source,
            wildlife.derive(photos[spec.source], spec),
        )
    add(
        "glasses",
        "clip-on-shades",
        "Clip-on shades",
        "shades",
        shades(photos["shades"]),
    )
    add(
        "glasses",
        "round-spectacles",
        "Round spectacles",
        "glasses",
        wire_frames(photos["glasses"]),
    )
    add(
        "texture",
        "rag-stock",
        "Paper fibers",
        "paper2",
        grain(photos["paper2"], (600, 900, 1624, 1924), 65),
    )
    add(
        "texture",
        "ink-grain",
        "Letterpress grain",
        "paper",
        grain(photos["paper"], (720, 968, 1072, 1320), 96),
    )
    (OUTPUT / "library.json").write_text(
        json.dumps({"size": SIDE, "parts": parts, "sources": sources}, indent=2) + "\n"
    )


if __name__ == "__main__":
    main()
