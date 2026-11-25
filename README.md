# Face Press

A free, browser-based cut-and-paste portrait studio. The editor loads its face parts, font, and print effects from local files. A static web server is the only runtime dependency.

[Open the studio on GitHub Pages](https://machupichu412.github.io/face_press/)

## Run locally

From this directory, run the following command and open [the studio](http://127.0.0.1:4371/).

```sh
python3 -m http.server 4371 --bind 127.0.0.1
```

## Make a print

1. Choose a photographic cutout from the library. **Reference mix** loads the white-background reference-style composition; **Undo** retrieves the previous draft.
2. Drag the selected cutout or use the position pad. **Size** scales it proportionally. **Width** and **Height** stretch or squash it independently. **Spacing** moves paired eyes, brows, or ears closer together or farther apart. For eyes, **Mirror left eye** and **Mirror right eye** duplicate the corresponding eye as viewed on the canvas. Type into any placement field for an exact value, or use the arrow keys or mouse wheel over the field to adjust one unit at a time.
3. Choose **Jaw** to adjust the lower-outline shadow. Opacity, lighting, and blend apply to that cutout. Facial hair has its own layer.
4. Animal eyes, ears, noses, and mouths share their anatomical categories with the human cutouts. Use **Show** to browse photographed people, synthetic portraits, or animals where available. The human collections show the highest-resolution crops first when filtered. Gills and fins each have a face-part slot, and antlers have a separate slot under **Extras**.
5. Under **Extras**, each click on a tattoo, piercing, or jewelry thumbnail adds an independent layer. Click the same thumbnail again to add another copy. The **Edit layer** menu selects the instance to drag, resize, rotate, or remove. Undo and redo also cover layer changes.
6. **Newsprint** uses an angled screen of variable-size ink dots. Dot size and ink density control both the print and the parts-library previews. Archive thumbnails use the saved settings of each portrait.
7. **Export PNG** downloads the displayed 800 × 880 print with its selected image credits embedded as PNG text metadata. **Save to archive** keeps an editable copy in this browser. Drafts survive reloads on the same origin. Historical drafts reopen with their saved facial choices. Retired illustrated extras reopen as empty slots for photo cutouts.

## Face library

The browser samples each cutout at its native resolution. All cutouts share a normalized 512 × 512 coordinate system for placement. The extraction pipeline runs separately from the app. See the [image credits and extraction guide](CREDITS.md) for sources and licenses. The [adornment credits](assets/adornments/CREDITS.md) and [animal, eyewear, and paper credits](assets/specimens/CREDITS.md) document the source photos and rebuild steps. Archivo Black is bundled under the [SIL Open Font License](assets/type/OFL.txt).
