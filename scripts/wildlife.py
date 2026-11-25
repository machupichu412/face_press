"""Masks and mounting positions for the photographed wildlife features.

Tracings use an upright source thumbnail fitted within 800 × 720. Masks are
rasterized on the original photograph; no low-resolution tracing preview is
used for the actual photographic pixels.
"""

from dataclasses import dataclass
from math import ceil

import cv2
import numpy as np
from PIL import Image, ImageFilter, ImageOps

US_PD = "Public domain (U.S. government work)"
SOURCES = {
    "perch": (
        "Yellow_Perch_(Perca_flavescens)_white_background.jpg",
        "Sam Stukel / U.S. Fish and Wildlife Service",
        US_PD,
        None,
    ),
    "sunfish": (
        "Blue_gill_(51238121687).jpg",
        "Sam Stukel / U.S. Fish and Wildlife Service",
        US_PD,
        None,
    ),
    "tuna": (
        "Tuna_Gills_cut_out.jpg",
        "Chris 73 / Wikimedia Commons",
        "CC BY-SA 3.0",
        "https://creativecommons.org/licenses/by-sa/3.0/",
    ),
    "puffin": (
        "Puffin_(Fratercula_arctica)_head.jpg",
        "Charles J. Sharp / Sharp Photography",
        "CC BY-SA 4.0",
        "https://creativecommons.org/licenses/by-sa/4.0/",
    ),
    "goat": (
        "Horizontal_Rectangular_Pupil_of_a_Goat.jpg",
        "Sumbria.vikramaditya",
        "CC0 1.0",
        "https://creativecommons.org/publicdomain/zero/1.0/",
    ),
    "moose": (
        "Bull_Moose.jpg",
        "Kent Miller / U.S. National Park Service, Denali National Park and Preserve",
        US_PD,
        None,
    ),
}


@dataclass(frozen=True)
class Tracing:
    source: str
    category: str
    key: str
    title: str
    # Left half of each pair is mounted here in the standard 512px frame.
    center: tuple[int, int]
    width: int
    boundary: str
    paired: bool = False
    flip: bool = False
    rotate: float = 0
    white_backdrop: bool = False


TRACINGS = [
    Tracing(
        "perch",
        "eyes",
        "perch-eyes",
        "Perch eyes",
        (201, 236),
        55,
        "674,264 679,260 686,259 694,261 700,267 704,274 703,282 699,287 693,291 684,292 677,289 673,284 671,276",
        True,
    ),
    Tracing(
        "sunfish",
        "eyes",
        "bluegill-eyes",
        "Bluegill eyes",
        (201, 236),
        51,
        "577,433 582,428 589,425 596,426 602,430 608,437 610,445 608,453 603,461 595,465 586,464 578,459 574,453 573,445",
        True,
    ),
    Tracing(
        "goat",
        "eyes",
        "goat-eyes",
        "Goat eyes",
        (201, 236),
        69,
        "110,324 112,307 119,292 130,283 147,282 170,281 195,281 220,277 242,274 258,275 279,281 295,291 312,307 319,327 331,341 344,360 346,375 342,386 327,392 300,398 277,405 256,410 237,415 213,419 188,417 164,409 141,397 124,380 116,363",
        True,
    ),
    Tracing(
        "puffin",
        "eyes",
        "puffin-eyes",
        "Puffin eyes",
        (201, 236),
        47,
        "349,184 351,173 353,163 359,158 365,160 372,172 380,176 388,183 397,190 391,196 381,202 374,207 362,205 355,200 350,193",
        True,
    ),
    Tracing(
        "perch",
        "gills",
        "perch-opercula",
        "Perch gill covers",
        (170, 286),
        55,
        "629,224 644,232 659,245 672,259 670,276 662,289 651,301 636,311 619,318 603,323 592,322 585,316 587,300 593,284 605,266 614,245",
        True,
    ),
    Tracing(
        "sunfish",
        "gills",
        "bluegill-opercula",
        "Bluegill gill covers",
        (169, 284),
        67,
        "482,353 486,343 494,335 501,332 511,334 519,341 526,351 533,364 536,373 529,384 528,403 522,427 517,451 510,471 517,488 531,502 545,510 532,511 514,503 499,492 489,476 483,452 483,427 484,401 482,382",
        True,
    ),
    Tracing(
        "tuna",
        "gills",
        "tuna-gill-filaments",
        "Tuna gill fans",
        (170, 292),
        43,
        "136,165 151,146 174,127 198,112 226,96 259,83 282,76 269,98 250,128 235,157 222,182 205,218 196,244 187,272 176,307 167,340 158,377 157,406 163,430 178,446 197,450 215,439 209,469 194,505 181,539 167,565 153,579 134,588 114,576 98,551 86,519 73,488 64,453 56,415 53,368 54,336 62,309 70,280 76,257 86,247 107,235 130,230 143,224 134,211 128,197 128,181",
        True,
        True,
    ),
    Tracing(
        "sunfish",
        "fins",
        "bluegill-tail-fins",
        "Bluegill fan fins",
        (122, 255),
        93,
        "78,158 81,142 91,125 109,112 126,104 147,97 154,77 165,57 181,40 198,28 216,24 236,28 248,41 255,58 257,72 254,100 251,118 233,125 213,137 201,150 192,165 190,182 182,193 163,196 145,195 124,200 108,196 93,184 81,174",
        True,
        False,
        -15,
        True,
    ),
    Tracing(
        "perch",
        "fins",
        "perch-dorsal",
        "Perch dorsal crest",
        (256, 112),
        176,
        "350,118 365,107 387,87 414,72 442,65 471,60 506,56 538,63 565,75 585,82 589,122 581,147 571,161 557,158 542,153 522,151 500,148 476,144 451,142 424,139 395,137 372,136",
        False,
        False,
        0,
        True,
    ),
    Tracing(
        "sunfish",
        "fins",
        "sunfish-spines",
        "Sunfish dorsal spines",
        (256, 109),
        171,
        "286,143 287,117 293,100 308,87 332,81 364,82 405,87 425,91 450,106 476,124 501,143 528,169 553,197 576,234 589,260 577,250 559,233 534,214 508,198 482,184 448,173 418,166 384,160 359,158 334,158 310,160 297,158",
        False,
        False,
        15,
        True,
    ),
    Tracing(
        "perch",
        "fins",
        "perch-tail-fins",
        "Forked tail fins",
        (126, 259),
        94,
        "12,278 26,255 37,235 42,226 36,214 36,190 37,172 45,156 53,151 78,155 100,162 123,170 148,178 160,184 155,200 149,220 146,235 144,245 129,254 107,269 74,286 43,299 21,299",
        True,
        False,
        -12,
        True,
    ),
    Tracing(
        "sunfish",
        "fins",
        "sunfish-pectoral",
        "Pectoral fins",
        (131, 284),
        82,
        "279,349 290,344 309,345 329,350 351,357 375,368 397,379 420,392 438,406 454,420 466,432 469,439 464,449 447,453 424,454 402,454 378,458 356,464 339,472 342,455 338,435 333,416 324,399 312,379 298,364",
        True,
    ),
    Tracing(
        "puffin",
        "mouth",
        "puffin-bill",
        "Puffin bill",
        (256, 327),
        86,
        "196,357 193,345 192,320 194,295 200,270 209,248 220,227 235,206 255,184 275,167 281,162 282,189 283,215 287,237 298,251 310,252 324,251 335,256 345,264 350,275 345,283 332,287 318,286 330,311 337,319 332,326 320,331 297,338 266,347 233,356 207,362 198,362",
    ),
    Tracing(
        "sunfish",
        "mouth",
        "bluegill-lips",
        "Bluegill lips",
        (256, 332),
        77,
        "579,515 592,510 607,503 624,498 639,494 645,498 649,504 648,511 643,520 641,529 637,539 627,546 608,551 585,553 565,552 549,549 535,541 527,534 530,530 543,532 562,530",
        False,
        False,
        -8,
    ),
    Tracing(
        "moose",
        "ears",
        "moose-ears",
        "Moose ears",
        (153, 212),
        66,
        "332,135 333,126 338,120 345,121 355,126 366,134 379,143 392,157 402,171 414,185 430,195 422,201 411,206 401,215 391,222 377,218 361,211 350,199 342,182 337,165",
        True,
    ),
    Tracing(
        "moose",
        "antlers",
        "moose-antlers",
        "Moose paddles",
        (180, 107),
        119,
        "176,104 179,97 186,95 193,99 197,113 201,128 207,147 215,161 225,174 237,180 236,174 224,161 218,153 219,147 225,146 233,150 241,160 243,146 239,125 225,107 213,89 205,74 198,57 198,44 203,38 211,39 216,47 219,61 223,75 228,61 234,59 239,64 242,78 248,77 256,77 263,79 268,69 278,65 287,68 292,77 297,100 303,121 306,132 313,122 320,119 323,126 321,140 318,156 316,180 314,205 317,215 327,221 347,222 370,220 385,220 394,225 391,238 380,243 358,243 334,241 314,235 294,227 269,218 242,205 220,197 205,186 192,169 183,150 178,127",
        True,
    ),
]


def derive(photo, spec):
    frame = photo.copy()
    frame.thumbnail((800, 720))
    scale_x, scale_y = photo.width / frame.width, photo.height / frame.height
    outline = np.asarray(
        [tuple(map(int, p.split(","))) for p in spec.boundary.split()], float
    )
    # Soften joins between annotation points while retaining the measured silhouette.
    next_point = np.roll(outline, -1, axis=0)
    outline = np.stack(
        (outline * 0.84 + next_point * 0.16, outline * 0.16 + next_point * 0.84), axis=1
    ).reshape(-1, 2)
    outline[:, 0] *= scale_x
    outline[:, 1] *= scale_y
    # Work inside each fragment's rect rather than allocating a whole photo-sized mask.
    x, y = np.floor(outline.min(axis=0)).astype(int)
    right, bottom = np.ceil(outline.max(axis=0)).astype(int) + 1
    patch = photo.crop((x, y, right, bottom))
    alpha = np.zeros((patch.height, patch.width), np.uint8)
    cv2.fillPoly(
        alpha,
        [np.round((outline - [x, y]) * 16).astype(np.int32)],
        255,
        cv2.LINE_AA,
        shift=4,
    )
    if spec.white_backdrop:
        darkest = np.asarray(patch).min(axis=2).astype(float)
        alpha = np.uint8(alpha * np.clip((253 - darkest) / 27, 0, 1))
    gray = np.asarray(patch.convert("L"), np.float32)
    # Preserve specular reflections and recover contrast in very translucent fins.
    lo, hi = np.percentile(gray[alpha > 170], [2, 98])
    if hi - lo > 15:
        gray = 0.32 * gray + 0.68 * np.clip(25 + (gray - lo) * 215 / (hi - lo), 10, 255)
    piece = (
        Image.fromarray(gray.clip(0, 255).astype(np.uint8))
        .filter(
            ImageFilter.UnsharpMask(
                radius=max(1, scale_x * 0.5), percent=85, threshold=3
            )
        )
        .convert("RGBA")
    )
    piece.putalpha(Image.fromarray(alpha))
    if spec.rotate:
        piece = piece.rotate(spec.rotate, Image.Resampling.BICUBIC, expand=True)
        piece = piece.crop(piece.getbbox())
    if spec.flip:
        piece = ImageOps.mirror(piece)
    width = 2 * spec.width
    piece = piece.resize(
        (width, round(width * piece.height / piece.width)), Image.Resampling.LANCZOS
    )
    image = Image.new("RGBA", (1024, 1024))
    x = round(spec.center[0] * 2 - piece.width / 2)
    y = round(spec.center[1] * 2 - piece.height / 2)
    image.alpha_composite(piece, (x, y))
    if spec.paired:
        image.alpha_composite(ImageOps.mirror(piece), (1024 - x - piece.width, y))
    return image


def normalized_bounds(image):
    left, top, right, bottom = image.getchannel("A").getbbox()
    scale = image.width / 512
    x, y = int(left // scale), int(top // scale)
    return [x, y, ceil(right / scale) - x, ceil(bottom / scale) - y]
