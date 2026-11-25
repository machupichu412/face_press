"""Compile the browser library offline. See CREDITS.md for sources and commands."""

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from urllib.parse import quote

import cv2
import numpy as np
import onnxruntime as ort
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "parts"
SIDE = 512
SHAPE = (SIDE, SIDE)
SYN_VIS_REV = "100262732989e77f38cd831d70a376a93735006a"
MODEL_URL = "https://huggingface.co/PayamFard123/dermaintel-face-parsing/resolve/main/resnet18.onnx"
MODEL_SHA = "0d9bd318e46987c3bdbfacae9e2c0f461cae1c6ac6ea6d43bbe541a91727e33f"
PUBLIC_PORTRAITS = [
    "Donald_R._Pettit.jpg",
    "Aaron_Cohen_-_GPN-2002-000100.jpg",
    "Leland_Melvin.jpg",
    "Frank_Rubio_official_portrait.jpg",
    "Victor_J._Glover_official_portrait.jpg",
    "Ruth_Bader_Ginsburg_2016_portrait.jpg",
    "Ellison_Shoji_Onizuka_(NASA).jpg",
    "Katherine_Johnson_in_2008.jpg",
    "John_Glenn_Low_Res.jpg",
    "Charles_F._Bolden,_Jr.jpg",
    "Guion_Bluford.jpg",
    "Buzz_Aldrin_(S69-31743).jpg",
    "Chris_Hadfield.jpg",
    "John_Fetterman_US_Senate_portrait.jpg",
    "Ted_Cruz_official_116th_portrait.jpg",
    "Ketanji_Brown_Jackson_official_SCOTUS_portrait.jpg",
    "Rosa_DeLauro_118th_Congress.jpeg",
    "Thurgood-marshall-2.jpg",
]
CLASSES = {
    "chin": [1], "mouth": [11, 12, 13], "nose": [10], "eyes": [4, 5],
    "eyebrows": [2, 3], "ears": [7, 8], "hair": [17], "glasses": [6],
}
LABELS = {"chin": "Jaw", "mouth": "Lips", "nose": "Nose", "eyes": "Eyes",
          "eyebrows": "Brows", "ears": "Ears", "hair": "Hair", "glasses": "Frames", "beard": "Facial hair"}


# Visually reviewed front-facing subjects from the pinned headshot release.
CURATED = {6, 11, 26, 41, 46, 66, 81, 86, 106, 121, 126, 131, 141, 166,
           171, 191, 201, 206, 226, 231, 251, 266, 271, 301, 306, 326, 331,
           346, 361, 366, 381, 386, 421, 426, 431, 451, 461, 471}


# The 2048px base portraits are separately composed from the headshot series.
BASE_PORTRAITS = [19, 27, 35, 57, 79, 87, 97, 125, 143, 217, 248, 263, 319, 397]
HISTORIC = {
    "archive-lincoln": (
        "archive-lincoln.tif", "https://tile.loc.gov/storage-services/master/pnp/ppmsca/19300/19301u.tif",
        "https://www.loc.gov/pictures/item/96522529/"),
    "archive-douglass": (
        "archive-douglass.jpg", "https://www.archives.gov/files/research/still-pictures/fl-fl-022.jpg",
        "https://www.archives.gov/research/still-pictures/highlights/frederick-douglass"),
}


NASA_PORTRAITS = {
    "S92-40463": "Mae Jemison",
    "jsc2014e037863": "Ellen Ochoa",
    "JSC2001-03044": "Peggy Whitson",
    "jsc2025e078605_alt": "Jessica Meir",
    "S97-06573": "Franklin Chang-Diaz",
    "S85-36539": "Ronald McNair",
    "S82-36442": "Bruce McCandless",
    "NHQ202009160004": "Christina Koch",
    "s64-29926": "Michael Collins",
    "jsc2023e047050_alt": "Jeanette Epps",
}


def sources(synvis_ids):
    for n in sorted(synvis_ids):
        filename = f"001-{n:04d}.png"
        url = f"https://huggingface.co/datasets/retowyss/Syn-Vis-v0/resolve/{SYN_VIS_REV}/images/headshot/{filename}"
        yield filename, url
    for n in BASE_PORTRAITS:
        filename = f"001-{n:04d}.png"
        url = f"https://huggingface.co/datasets/retowyss/Syn-Vis-v0/resolve/{SYN_VIS_REV}/images/base/{filename}"
        yield "base-" + filename, url
    for nasa_id in NASA_PORTRAITS:
        url = f"https://images-assets.nasa.gov/image/{nasa_id}/{nasa_id}~orig.jpg"
        yield f"nasa-{nasa_id}.jpg", url
    for name, url, _ in HISTORIC.values():
        yield name, url
    for i, filename in enumerate(PUBLIC_PORTRAITS, 1):
        digest = hashlib.md5(filename.encode()).hexdigest()
        url = f"https://upload.wikimedia.org/wikipedia/commons/{digest[0]}/{digest[:2]}/{quote(filename)}"
        if i == 15:
            url = "https://www.cruz.senate.gov/files/images/STC%20HEADSHOT.jpg"
        yield f"gov-{i}.jpg", url


def get_file(path, url):
    if not path.exists():
        tmp = path.with_suffix(".partial")
        subprocess.run(["curl", "--fail", "--location", "--retry", "2",
                        "--output", str(tmp), url], check=True)
        tmp.replace(path)


def parse(session, face):
    rgb = cv2.cvtColor(face, cv2.COLOR_BGR2RGB) / np.float32(255)
    rgb -= np.array([.485, .456, .406], np.float32)
    rgb /= np.array([.229, .224, .225], np.float32)
    x = np.ascontiguousarray(rgb.transpose(2, 0, 1)[None])
    logits = session.run(["output"], {"input": x})[0]
    return logits[0].argmax(0).astype(np.uint8)


def centroid(mask):
    y, x = np.where(mask)
    if len(y) < 20:
        raise ValueError("missing landmark")
    return np.array([np.mean(x), np.mean(y)])


def refine_glasses(face, labels):
    # In this front-facing 2016 portrait, the parser labels both transparent
    # lenses as solid glasses. Keep only dark frame pixels near the traced rims.
    paths = [
        [(146,228),(160,231),(173,233)],
        [(166,230),(184,229),(206,229),(226,232),(244,238),(241,254),(235,269),(224,276),(207,278),(188,277),(178,271),(174,261),(172,245),(171,235)],
        [(240,239),(249,241),(260,239)],
        [(259,239),(272,233),(291,229),(313,227),(334,228),(331,243),(330,256),(326,268),(316,275),(297,278),(280,277),(270,272),(265,264),(260,250),(257,240)],
        [(329,232),(338,229),(343,227)],
    ]
    frame = np.zeros_like(labels)
    for points in paths:
        cv2.polylines(frame, [np.array(points, np.int32)], False, 255, 8, cv2.LINE_AA)
    dark = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY) < 144
    labels[labels == 6] = 1
    labels[(frame > 80) & dark] = 6
    cv2.ellipse(labels, (208,245), (18,7), 0, 0, 360, 4, -1)
    cv2.ellipse(labels, (293,243), (17,7), 0, 0, 360, 5, -1)


# Traced contours are in the parser's 512-square face crop. They enclose the
# photographed frame and leave both lenses open. Widths are in crop pixels.
# Each eye pair supplies landmarks where BiSeNet groups the lens and eye.
FRAME_DETAILS = {
    "gov-16": ("Upswept browline", [(195,245),(304,235)], [
        (7, [(145,238),(157,233),(174,230),(192,228),(210,229),(225,233),(234,240)]),
        (3, [(145,235),(150,244),(154,265),(161,279),(173,288),(188,292),(202,292),(217,286),(227,276),(233,261),(236,245),(233,237)]),
        (3, [(236,241),(244,238),(253,238),(262,240)]),
        (7, [(264,238),(275,228),(294,222),(314,219),(335,219),(353,222),(360,226)]),
        (3, [(264,234),(262,245),(267,262),(274,274),(286,281),(302,285),(319,284),(333,278),(339,269),(345,250),(346,233),(353,224)]),
    ]),
    "gov-18": ("Heavy keyhole", [(219,237),(321,251)], [
        (10, [(119,201),(138,204),(159,208),(181,213),(205,214),(230,218),(248,222),(264,230),(280,235),(293,234),(307,232),(327,232),(353,236),(375,242)]),
        (6, [(182,215),(187,237),(190,253),(197,264),(211,270),(232,272),(244,268),(252,260),(256,248),(262,231)]),
        (6, [(289,237),(289,254),(292,269),(299,281),(312,286),(329,286),(343,281),(352,271),(361,250),(367,242)]),
        (4, [(123,201),(115,202),(107,209)]),
    ]),
    "gov-8": ("Slim rectangle", [(221,234),(304,233)], [
        (3, [(178,246),(178,237),(184,232),(204,229),(228,228),(239,230),(242,235),(239,254),(234,267),(223,273),(201,277),(188,276),(184,267),(178,246)]),
        (4, [(176,250),(185,249),(202,246),(210,246)]),
        (3, [(239,242),(248,239),(257,238),(264,239)]),
        (3, [(263,230),(272,225),(292,220),(314,217),(330,218),(338,221),(342,231),(341,254),(338,262),(320,267),(299,270),(282,268),(273,262),(268,251),(263,234)]),
        (6, [(342,232),(356,233),(370,233),(389,234),(407,234)]),
    ]),
}


def trace_frame(key, labels):
    _, eyes, paths = FRAME_DETAILS[key]
    support = np.zeros_like(labels)
    for width, path in paths:
        cv2.polylines(support, [np.array(path, np.int32)], False, 255, width, cv2.LINE_AA)
    labels[labels == 6] = 1
    labels[support >= 120] = 6
    for index, (x, y) in enumerate(eyes, 4):
        cv2.ellipse(labels, (x, y), (17, 6), 0, 0, 360, index, -1)


def align(path, detector, session):
    original = cv2.imread(str(path))
    if original is None:
        raise ValueError("undecodable portrait")
    detector_scale = 800 / max(original.shape[:2])
    img = cv2.resize(original, None, fx=detector_scale, fy=detector_scale, interpolation=cv2.INTER_AREA)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = detector.detectMultiScale(cv2.equalizeHist(gray), 1.09, 4, minSize=(36, 36))
    if len(faces) == 0:
        raise ValueError("no front view")
    if path.stem == "gov-3":
        # Logos on the suit trigger the frontal-face cascade in this particular photo.
        x, y, w, h = min(faces, key=lambda b: b[1])
    else:
        x, y, w, h = max(faces, key=lambda b: b[2] * b[3])
    crop_side = max(w, h) * 1.85
    scale = SIDE / crop_side
    crop = np.array([[scale, 0, 256-scale*(x+w*.5)], [0, scale, 256-scale*(y+h*.45)]])
    face = cv2.warpAffine(img, crop, SHAPE, borderMode=cv2.BORDER_REPLICATE)
    labels = parse(session, face)
    if path.stem == "gov-6":
        refine_glasses(face, labels)
    if path.stem in FRAME_DETAILS:
        trace_frame(path.stem, labels)
    # The network occasionally assigns the same right/left class to both eyes.
    connected, _, stats, centers = cv2.connectedComponentsWithStats(mask_for(labels, [4, 5]))
    plausible = [i for i in range(1, connected) if stats[i, cv2.CC_STAT_AREA] > 25]
    best = sorted(plausible, key=lambda i: stats[i, cv2.CC_STAT_AREA], reverse=True)[:2]
    if len(best) != 2:
        raise ValueError("missing eyes")
    eyes = sorted((centers[best[0]], centers[best[1]]), key=lambda c: c[0])
    mid = (eyes[0] + eyes[1]) / 2
    delta = eyes[1] - eyes[0]
    dist = np.linalg.norm(delta)
    # Reject profiles and severely asymmetric detections.
    nose = centroid(labels == 10)
    sides = [stats[i, cv2.CC_STAT_AREA] for i in best]
    if path.stem not in FRAME_DETAILS and (dist < 45 or abs(nose[0]-mid[0]) > dist*.16 or min(sides)/max(sides) < .45):
        raise ValueError("oblique view")
    matrix = cv2.getRotationMatrix2D(tuple(mid), np.degrees(np.arctan2(*delta[::-1])), 110/dist)
    matrix[:, 2] += np.array([256., 236.]) - mid
    labels = cv2.warpAffine(labels, matrix, SHAPE, flags=cv2.INTER_NEAREST)
    mouth = centroid(np.isin(labels, CLASSES["mouth"]))
    # Standardize the vertical distance between features, retaining lip shape and jawline.
    # The parser always operates on 512 pixels. Sample the photo directly at
    # twice that density only if its mapped source footprint supports it.
    to_aligned = matrix @ np.vstack([crop, [0, 0, 1]])
    inverse = cv2.invertAffineTransform(to_aligned)
    native_footprint = np.hypot(inverse[0, 0], inverse[1, 0]) / detector_scale
    new_source = path.stem.startswith(("base-", "archive-", "nasa-")) or path.stem in {"gov-8","gov-13","gov-14","gov-15","gov-16","gov-17","gov-18"}
    detail = 2 if new_source and native_footprint >= 2 else 1
    side = SIDE * detail
    axis = (np.arange(side, dtype=np.float32)+.5)/detail-.5
    src_rows = np.interp(axis, [0, 236, 331, 511], [0, 236, mouth[1], 511])
    map_y = np.broadcast_to(src_rows[:, None], (side, side)).astype(np.float32)
    map_x = np.broadcast_to(axis, (side, side))
    photo_x = (inverse[0, 0]*map_x + inverse[0, 1]*map_y + inverse[0, 2]) / detector_scale
    photo_y = (inverse[1, 0]*map_x + inverse[1, 1]*map_y + inverse[1, 2]) / detector_scale
    gray = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
    # Prefilter high-resolution photos before decimation to retain real hair
    # texture without aliasing subpixel hairs into false checkerboard patterns.
    footprint = native_footprint / detail
    if footprint > 1.25:
        gray = cv2.GaussianBlur(gray, (0, 0), .42*footprint)
    lum = cv2.remap(gray, photo_x.astype(np.float32), photo_y.astype(np.float32),
                    cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REPLICATE)
    lum = cv2.addWeighted(lum, 1.58, cv2.GaussianBlur(lum, (0, 0), 1.0), -.58, 0)
    labels = cv2.remap(labels, map_x, map_y, cv2.INTER_NEAREST)
    return lum, labels


def mask_for(labels, classes):
    return np.uint8(np.isin(labels, classes)) * 255


def expand(mask, radius):
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (radius*2+1, radius*2+1))
    return cv2.dilate(mask, kernel)


def skin_reference(lum, labels):
    detail = lum.shape[0] // SIDE
    erase = expand(mask_for(labels, [2, 3, 4, 5, 6, 10, 11, 12, 13]), 9*detail)
    valid = np.uint8((labels == 1) & (erase == 0))
    weights = cv2.GaussianBlur(valid.astype(np.float32), (0, 0), 17*detail)
    values = cv2.GaussianBlur(valid*lum.astype(np.float32), (0, 0), 17*detail)
    smooth = np.divide(values, weights, out=np.full_like(values, np.median(lum[labels==1])), where=weights>.002)
    return smooth


def jaw_layer(lum, labels, reference):
    face = mask_for(labels, [1, 2, 3, 4, 5, 6, 10, 11, 12, 13])
    contours, _ = cv2.findContours(face, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    shape = np.zeros_like(face)
    cv2.drawContours(shape, [max(contours, key=cv2.contourArea)], 0, 255, -1)
    detail = lum.shape[0] // SIDE
    shape = cv2.medianBlur(shape, 4*detail+1)
    inside = cv2.distanceTransform(shape, cv2.DIST_L2, 5)
    outside = cv2.distanceTransform(255-shape, cv2.DIST_L2, 5)
    distance = (inside - outside)/detail
    rows = np.arange(lum.shape[0])[:, None]/detail
    # Follow the source's lower silhouette, ending the side strokes beside the mouth.
    side_fade = np.clip((rows-309)/26., 0, 1)
    band = side_fade * np.clip((17-distance)/9., 0, 1) * np.clip((distance+3.5)/2., 0, 1)
    chin_pixels = lum.astype(np.float32)
    relative = (chin_pixels+4) / np.maximum(reference+4, 10)
    shadows = np.clip(1.08-relative, 0, 1)
    edge = np.exp(-np.abs(distance-1)/2.4)
    ink = np.clip(.17*np.exp(-np.maximum(distance, 0)/6) + .46*edge + shadows*1.2, 0, 1)
    alpha = np.uint8(255*band*ink)
    return np.zeros_like(lum), alpha


def tonal_cutout(pixels, support):
    # Deposit the shadows on the paper. Midtones retain continuous opacity, so
    # a moved feature never carries an opaque rectangular patch of skin.
    ink = 1-pixels.astype(np.float32)/255
    pigment = np.minimum(1, ink/.70)
    alpha = np.uint8(np.rint(support.astype(np.float32)*pigment))
    gray = 255*(1-np.divide(ink, pigment, out=np.zeros_like(ink), where=pigment>0))
    return np.uint8(np.clip(gray, 0, 255)), alpha


def recover_crown(lum):
    # The short parser crop cuts through the top of this high-top hairstyle.
    # This loose trace seeds GrabCut; the matte boundary follows the original
    # hair texture in the full-resolution aligned photograph.
    outline = [(116,186),(120,157),(129,128),(142,107),(160,90),(183,77),
               (211,66),(238,60),(263,58),(290,59),(323,67),(350,79),
               (373,97),(388,119),(399,150),(407,184),(411,216),(403,245),
               (393,258),(376,262),(374,232),(367,201),(361,164),(351,133),
               (337,117),(320,111),(299,111),(276,111),(253,115),(227,116),
               (202,117),(183,120),(168,128),(159,151),(152,178),(150,203),
               (145,231),(141,259),(134,275),(128,250),(122,228),(118,205)]
    detail = lum.shape[0] // SIDE
    prior = np.zeros_like(lum)
    cv2.fillPoly(prior, [np.array(outline,np.int32)*detail], 255)
    margin = 7*detail
    outer, inner = expand(prior, margin), 255-expand(255-prior, margin)
    x,y,w,h = cv2.boundingRect(outer)
    roi = np.s_[y-1:y+h+1, x-1:x+w+1]
    seed = np.full(outer[roi].shape, cv2.GC_BGD, np.uint8)
    seed[outer[roi]>0] = cv2.GC_PR_BGD
    seed[prior[roi]>0] = cv2.GC_PR_FGD
    seed[inner[roi]>0] = cv2.GC_FGD
    cv2.setRNGSeed(11)
    cv2.grabCut(cv2.cvtColor(lum[roi], cv2.COLOR_GRAY2BGR), seed, None,
                np.zeros((1,65)), np.zeros((1,65)), 2, cv2.GC_INIT_WITH_MASK)
    matte = np.zeros_like(prior)
    matte[roi] = np.uint8((seed%2)*255)
    return matte


def extract_layers(lum, labels, source=""):
    side = lum.shape[0]
    detail = side // SIDE
    reference = skin_reference(lum, labels)
    yield "chin", *jaw_layer(lum, labels, reference)
    ratio = (lum.astype(np.float32)+4) / np.maximum(reference+4, 12)
    # Local skin is paper white; the deeper tones keep their optical contrast.
    feature = np.uint8(np.clip(255*((ratio-.035)/.90).clip(0, 1)**1.5, 0, 255))
    frames = expand(mask_for(labels, CLASSES["glasses"]), 2*detail)
    for kind, classes in CLASSES.items():
        if kind == "chin":
            continue
        mask = mask_for(labels, classes)
        if kind == "hair" and source == "nasa-S85-36539":
            mask = recover_crown(lum)
        if kind == "hair" and source == "nasa-S82-36442":
            # Remove disconnected bits of the dark suit from this short haircut.
            _, components, stats, _ = cv2.connectedComponentsWithStats(mask)
            mask = np.uint8(components == np.argmax(stats[1:,cv2.CC_STAT_AREA])+1)*255
        if kind == "ears":
            # A matched pair from the more visible ear avoids half-obscured variants.
            left = mask.copy()
            left[:, side//2:] = 0
            right = mask.copy()
            right[:, :side//2] = 0
            ear = left if left.sum() > right.sum() else right
            if np.count_nonzero(ear) < 240*detail**2:
                continue
            light = feature
            if source.startswith(("nasa-", "base-", "archive-")) or source in {"gov-13", "gov-14", "gov-15", "gov-16", "gov-17"}:
                low, high = np.percentile(lum[ear>0], [4, 95])
                inner_tones = np.clip(22 + 222*(lum.astype(np.float32)-low)/max(48, high-low), 0, 255)
                light = np.uint8(.8*inner_tones+.2*feature)
            if ear is right:
                ear, light = ear[:, ::-1], light[:, ::-1]
            x, y, w, h = cv2.boundingRect(ear)
            if w < 5*detail or h < 13*detail:
                continue
            # Seat each ear slightly inside the silhouette at the typical tragus height.
            scale = float(np.clip(53*detail/h, .65, 2.2))
            matrix = np.array([[scale, 0., 153*detail-scale*(x+w)], [0., scale, 264*detail-scale*(y+h*.52)]])
            ear = cv2.warpAffine(ear, matrix, (side, side))
            light = cv2.warpAffine(light, matrix, (side, side))
            light = np.where(ear > 0, light, light[:, ::-1])
            yield kind, *tonal_cutout(light, cv2.GaussianBlur(ear | ear[:, ::-1], (3, 3), .65))
            continue
        if np.count_nonzero(mask) < (150 if kind == "glasses" else 45)*detail**2:
            continue
        if kind == "hair":
            # Remove clothing misclassified as hair near the edge of the source.
            if np.count_nonzero(mask[0]) > 55*detail:
                continue
            # Trim the lower hair as a gently curved paper cut.
            rows, cols = np.ogrid[:side, :side]
            rows, cols = rows/detail, cols/detail
            bottom = 476 - (cols-256)**2 / 1700 + 4*np.sin(cols/17)
            mask[rows > bottom] = 0
            mask[:2*detail] = mask[:, :2*detail] = mask[:, -2*detail:] = 0
        if kind in ("eyes", "eyebrows", "nose", "mouth"):
            core = mask.copy()
            radius = {"eyes": 7, "eyebrows": 2, "nose": 5, "mouth": 2}[kind]
            mask = expand(mask, radius*detail)
            sigma = {"eyes": 1.8, "eyebrows": .65, "nose": 2.1, "mouth": .9}[kind]
        else:
            sigma = .7
        if kind == "hair":
            # Preserve highlights in dark hair, which carry its structure in monochrome.
            p5 = np.percentile(lum[mask > 0], 5)
            hair = (lum.astype(float)-p5)*1.30+24
            pixels = np.uint8(np.clip(hair, 0, 255))
        elif kind == "glasses":
            pixels = lum
        else:
            pixels = feature
        support = cv2.GaussianBlur(mask, (0, 0), sigma*detail)
        if kind in ("eyes", "eyebrows", "nose", "mouth"):
            support[frames > 0] = 0
            if kind in ("eyes", "eyebrows", "mouth"):
                # Preserve lip color, eyelids, and individual brow hairs even on
                # portraits where direct light makes them brighter than the cheek.
                low, high = np.percentile(lum[core > 0], [3, 94])
                contrast = 16 + 226*(lum.astype(np.float32)-low)/max(55, high-low)
                blend = cv2.GaussianBlur(core.astype(np.float32)/255, (0, 0), 1.0)
                blend *= {"eyes": .53, "eyebrows": .22, "mouth": .82}[kind]
                pixels = np.uint8(np.clip(pixels*(1-blend) + np.clip(contrast, 8, 255)*blend, 0, 255))
            yield kind, *tonal_cutout(pixels, support)
        else:
            yield kind, pixels, support


# The semantic model has no facial-hair class. These hand-traced boundaries
# constrain the photographic extraction on the same eye/mouth-aligned grid.
FACIAL_HAIR = {
    "nasa-S85-36539": ("Tapered moustache", [
        (187,324),(195,316),(207,311),(218,307),(230,302),(243,301),(255,302),
        (266,303),(277,303),(290,307),(303,311),(317,313),(326,318),(325,324),
        (317,329),(303,331),(297,325),(283,318),(268,315),(255,315),(241,316),
        (225,318),(211,323),(205,329),(198,333),(191,329),
    ]),
    "gov-18": ("Pencil moustache", [
        (207,324),(214,315),(224,305),(235,302),(246,306),(259,309),(272,304),
        (283,303),(291,307),(301,314),(307,323),(295,319),(284,317),(273,318),
        (263,319),(251,319),(239,317),(226,317),(216,321),
    ]),
    "archive-lincoln": ("Chin curtain", [
        (132,269),(140,270),(148,283),(158,295),(170,304),(181,315),(186,330),
        (186,343),(198,349),(211,352),(219,350),(233,356),(251,360),(278,354),
        (294,348),(313,341),(327,333),(338,316),(349,306),(359,286),(369,273),
        (377,264),(374,287),(372,307),(378,323),(370,338),(376,351),(368,364),
        (365,383),(355,404),(347,407),(340,418),(331,420),(323,432),(315,438),
        (293,443),(277,447),(257,464),(242,469),(220,465),(199,463),(187,452),
        (182,433),(178,420),(172,410),(171,394),(159,377),(153,359),(152,345),
        (147,331),(150,316),(145,302),(139,291),
    ]),
    "archive-douglass": ("Silver fork beard", [
        (169,305),(182,302),(196,303),(204,294),(216,287),(229,294),(245,299),
        (254,298),(266,288),(278,289),(294,297),(306,310),(316,324),(329,330),
        (346,323),(360,309),(374,295),(387,279),(395,271),(403,282),(409,299),
        (416,313),(414,329),(423,347),(425,366),(410,378),(405,388),(388,403),
        (368,415),(347,425),(323,438),(306,450),(291,461),(277,473),(260,486),
        (240,484),(225,481),(208,469),(198,461),(194,450),(181,442),(173,425),
        (176,414),(171,402),(179,390),(172,374),(174,359),(169,346),(173,337),
    ]),
    "gov-13": ("Chevron moustache", [
        (191,325),(199,308),(212,301),(232,295),(250,298),(260,299),(274,295),
        (290,297),(307,302),(319,310),(327,326),(315,325),(302,329),(285,331),
        (269,330),(258,327),(244,327),(233,330),(216,327),(203,322),
    ]),
    "gov-14": ("Goatee", [
        (197,354),(214,350),(233,347),(247,348),(256,350),(271,346),(289,345),
        (301,349),(307,361),(311,378),(307,393),(298,408),(283,423),(267,432),
        (244,439),(225,435),(211,428),(201,417),(196,403),(193,385),(194,368),
    ]),
    "gov-15": ("Full beard", [
        (125,266),(135,262),(142,286),(148,311),(160,329),(179,336),(190,330),
        (201,318),(215,310),(232,306),(248,306),(256,308),(273,301),(287,304),
        (302,311),(315,323),(326,336),(339,342),(353,334),(369,314),(375,290),
        (380,266),(391,264),(390,295),(385,313),(378,338),(368,365),(356,384),
        (338,398),(318,406),(297,419),(272,429),(247,433),(224,428),(198,421),
        (176,410),(155,392),(143,373),(135,350),(128,318),(123,296),
    ]),
}


def facial_hair_layer(key, lum, labels):
    _, points = FACIAL_HAIR[key]
    support = np.zeros_like(lum)
    detail = lum.shape[0] // SIDE
    cv2.fillPoly(support, [np.array(points, np.int32)*detail], 255, lineType=cv2.LINE_AA)
    # The full beard encloses exposed skin around the mouth.
    if key == "gov-15":
        opening = [(199,332),(213,327),(237,324),(260,325),(278,322),(295,325),
                   (308,330),(316,344),(320,362),(311,381),(297,382),(282,369),
                   (276,360),(255,363),(242,362),(231,373),(216,378),(202,372),
                   (197,357)]
        cv2.fillPoly(support, [np.array(opening, np.int32)*detail], 0, lineType=cv2.LINE_AA)
    support[mask_for(labels, CLASSES["mouth"])>0] = 0
    support = cv2.GaussianBlur(support, (0, 0), 1.3*detail)
    rows = np.arange(lum.shape[0])[:, None]/detail
    cheek = (labels == 1) & (rows > 245) & (rows < 302)
    skin_light = np.percentile(lum[cheek], 70)
    ratio = lum.astype(np.float32) / max(1, skin_light)
    pixels = np.uint8(255*np.clip((ratio-.05)/.91, 0, 1)**1.4)
    if key in {"archive-douglass", "gov-18"}:
        # Pale facial hair has little broad shadow. Extract the local strand
        # contrast against the lighter illumination within the traced region.
        smooth = cv2.GaussianBlur(lum, (0, 0), 4*detail).astype(np.float32)
        strand = np.clip(245 - (smooth-lum)*4.8, 0, 255).astype(np.uint8)
        pixels = np.minimum(pixels, strand)
    return tonal_cutout(pixels, support)


def save_layer(kind, lum, mask, key, number):
    box = cv2.boundingRect(np.uint8(mask > 15))
    detail = lum.shape[0] // SIDE
    x, y = box[0] // detail, box[1] // detail
    w = (box[0]+box[2]+detail-1)//detail-x
    h = (box[1]+box[3]+detail-1)//detail-y
    if not w or not h:
        return None
    filename = f"{kind}-{key}.webp"
    rgba = np.dstack([lum, lum, lum, mask])
    rgba[mask == 0] = 0
    pending = OUT / (filename + ".partial")
    Image.fromarray(rgba).save(pending, format="WEBP", lossless=True, method=4)
    pending.replace(OUT / filename)
    return {"id": f"{kind}-{key}", "name": f"{LABELS[kind]} {number:02d}",
            "src": f"assets/parts/{filename}", "bounds": [x, y, w, h], "source": key, "pixels": int(lum.shape[0])}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", type=Path, required=True)
    parser.add_argument("--model", type=Path)
    parser.add_argument("--download", action="store_true")
    selection = parser.add_mutually_exclusive_group()
    selection.add_argument("--all", action="store_true", help="Screen all 480 Syn-Vis candidates")
    selection.add_argument("--add-ids", type=int, nargs="+", metavar="ID",
                           help="Add Syn-Vis headshot numbers (1–480) to the curated set")
    args = parser.parse_args()
    args.cache.mkdir(parents=True, exist_ok=True)
    model = args.model or args.cache / "resnet18.onnx"
    if args.download:
        get_file(model, MODEL_URL)
    if hashlib.sha256(model.read_bytes()).hexdigest() != MODEL_SHA:
        raise SystemExit("Unexpected model checksum")
    ort.disable_telemetry_events()
    setting = ort.SessionOptions()
    setting.intra_op_num_threads = 3
    session = ort.InferenceSession(str(model), sess_options=setting, providers=["CPUExecutionProvider"])
    detector = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    OUT.mkdir(parents=True, exist_ok=True)
    parts = {kind: [] for kind in (*CLASSES, "beard")}
    if any(n < 1 or n > 480 for n in args.add_ids or []):
        parser.error("Syn-Vis IDs must be between 1 and 480")
    ids = range(1, 481) if args.all else (CURATED | set(args.add_ids or []))
    records = {}
    for name, url in sources(ids):
        path = args.cache / name
        if args.download:
            get_file(path, url)
        if not path.exists():
            raise SystemExit(f"Missing {path}. Supply --download to fetch the source files.")
        try:
            lum, labels = align(path, detector, session)
            key = path.stem
            mouth = centroid(mask_for(labels, CLASSES["mouth"]))
            if key.startswith("001-") and int(key[4:]) not in CURATED and abs(mouth[0]-256) > 10:
                raise ValueError("off-center mouth")
            synthetic = key.startswith(("001-", "base-"))
            if synthetic:
                source_link = url.replace("/resolve/", "/blob/")
            elif key.startswith("nasa-"):
                source_link = f"https://images.nasa.gov/details/{key[5:]}"
            elif key in HISTORIC:
                source_link = HISTORIC[key][2]
            else:
                source_link = "https://commons.wikimedia.org/wiki/File:" + quote(PUBLIC_PORTRAITS[int(key[4:])-1])
            records[key] = {"url": source_link, "kind": "synthetic" if synthetic else "photo",
                            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                            "rights": "CC0-1.0" if synthetic else "Public domain (United States)"}
            if key in FACIAL_HAIR:
                pixels, alpha = facial_hair_layer(key, lum, labels)
                item = save_layer("beard", pixels, alpha, key, len(parts["beard"])+1)
                if item:
                    item["name"] = FACIAL_HAIR[key][0]
                    parts["beard"].append(item)
            for kind, pixels, alpha in extract_layers(lum, labels, key):
                if kind == "hair" and key in {"base-001-0217", "base-001-0248"}:
                    # One scarf hides the crown and one double-bun extends past the crop.
                    continue
                if key == "archive-douglass" and kind != "hair":
                    # The visible beard and hair are usable in this angled portrait.
                    continue
                if key in {"gov-8", "gov-18"} and kind != "glasses":
                    # Use the traced eyewear from these angled portraits only.
                    continue
                if key in {"archive-douglass", "archive-lincoln", "gov-15"} and kind in {"chin", "mouth"}:
                    # These areas are partly covered by the source hair.
                    continue
                if (key in {"gov-13", "nasa-S85-36539"} and kind == "mouth") or (key == "gov-14" and kind == "chin"):
                    continue
                if key == "gov-8" and kind == "glasses":
                    # Reuse the unobscured lens from this three-quarter view.
                    right = alpha.copy()
                    center = right.shape[1]//2
                    right[:, :center] = 0
                    right[:, int(center*1.54):] = 0
                    pixels = np.where(right > 0, pixels, pixels[:, ::-1])
                    alpha = right | right[:, ::-1]
                if key == "gov-18" and kind == "glasses":
                    # The arm running back to the near ear projects past the
                    # frontal silhouette. Retain just the photographed hinge.
                    alpha[:, :int(145*alpha.shape[0]/SIDE)] = 0
                item = save_layer(kind, pixels, alpha, path.stem, len(parts[kind])+1)
                if item:
                    if kind == "glasses" and key in FRAME_DETAILS:
                        item["name"] = FRAME_DETAILS[key][0]
                    parts[kind].append(item)
        except ValueError as exc:
            print(f"Skipping {name}: {exc}")
    # Place key silhouettes and expressions together on the first browsing pages.
    featured = ["001-0011", "gov-7", "001-0166", "gov-6", "001-0251", "gov-3",
                "001-0426", "gov-2", "001-0126", "gov-11", "001-0381", "gov-10"]
    priority = {key: i for i, key in enumerate(featured)}
    original_faces = {f"001-{n:04d}" for n in CURATED} | {f"gov-{i}" for i in range(1,13) if i != 8}
    for kind, entries in parts.items():
        # Existing printed fragment numbers remain stable when donors are added.
        original = {"gov-13","gov-14","gov-15"} if kind == "beard" else original_faces
        entries.sort(key=lambda e: (e["source"] not in original, priority.get(e["source"], len(featured))))
        for index, entry in enumerate(entries, 1):
            if kind != "beard" and not (kind == "glasses" and entry["source"] in FRAME_DETAILS):
                entry["name"] = f"{LABELS[kind]} {index:02d}"
    manifest = {"size": SIDE, "parts": parts, "sources": records}
    next_manifest = OUT / "library.json.partial"
    next_manifest.write_text(json.dumps(manifest, indent=2) + "\n")
    next_manifest.replace(OUT / "library.json")
    print({k: len(v) for k, v in parts.items()})


if __name__ == "__main__":
    main()
