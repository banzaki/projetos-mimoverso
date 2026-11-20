# Estudio STL: instructions for Bia's AI

Bia is a DevOps engineer, new to building products with AI. Talk to her in Portuguese. Code, file names and commit messages stay in English. Keep steps small, show the result, and say what you checked.

## What this project is
A tool where Bia asks for a creature in words ("um sapinho com chifre, 6 cm") and gets a printable **STL** file. First step: text to STL. Later step: open an existing STL and change its size and parts.

## How it works (no API key needed)
You (the AI) write a short Python script that builds the creature from rounded shapes, using `studio/shapes.py`. The script has `SIZE_MM` on its first line, so "bigger/smaller" is one edit. Then you run it, check it, and preview it.

Commands (from this folder, after `pip install -r requirements.txt` inside a venv):
- Build: `python examples/<name>.py` (writes `out/<name>.stl`)
- Check: `python -m studio.check out/<name>.stl`  (must say closed mesh True, bodies 1)
- Preview: `python studio/preview.py out/<name>.stl out/preview` (front, side, three-quarter PNGs)

## Rules
- The deliverable is the `.stl`. A PNG preview is not proof the model prints.
- "Done" = check passes AND Bia opened the STL in her slicer (Bambu Studio) without errors. Say what you checked and what you did not.
- Original designs only. Never copy an existing character or someone else's model.
- Nothing is published, pushed or sent to anyone without Bia's OK. Never ask for passwords or keys.
- Reference creature: `examples/sapinho.py`. Copy it for a new creature, keep the same structure.
- Known weak points of the first frog: very thin horn tips, a shallow smile groove, the head overhanging the body. Not yet sliced or printed.
