Generate a polished HTML slide presentation. Work through the following phases in order.

---

## Phase 1 — Gather Requirements

Ask the user these questions (all at once, not one by one):

1. **Topic / title** — What is the presentation about?
2. **Audience & purpose** — Who is it for, and what should they walk away feeling or knowing?
3. **Slide count** — How many slides? (suggest 8–12 if unsure)
4. **Style** — Show the numbered list below and ask them to pick one, or describe their own vibe:
   1. Bold Signal — confident, bold, modern (dark/orange)
   2. Electric Studio — professional, high contrast (split white/blue)
   3. Creative Voltage — energetic, retro-modern (blue/neon yellow)
   4. Dark Botanical — elegant, sophisticated (dark/warm accents)
   5. Notebook Tabs — editorial, tactile (cream paper, colorful tabs)
   6. Pastel Geometry — friendly, organized (soft pastels, pill accents)
   7. Split Pastel — playful, creative (peach/lavender split)
   8. Vintage Editorial — witty, editorial (cream, bold serif)
   9. Neon Cyber — futuristic, techy (navy/cyan/magenta)
   10. Terminal Green — hacker aesthetic (dark/green mono)
   11. Swiss Modern — Bauhaus, grid-precise (black/white/red)
   12. Paper & Ink — literary, thoughtful (warm cream, crimson)
5. **Content** — Do they have bullet points, an outline, or raw notes to include? (paste here, or say "generate it")
6. **Images** — Any image files to include? If yes, list the paths.
7. **Inline editing** — Do they want an edit mode so they can tweak text directly in the browser? (yes/no)

Wait for the user's answers before continuing.

---

## Phase 2 — Generate the Presentation

Use the plugin reference files from `.claude/plugins/frontend-slides/` as your implementation guide:

- **`html-template.md`** — base HTML structure, JS class architecture, inline editing implementation, image pipeline
- **`STYLE_PRESETS.md`** — exact colors, fonts, and signature elements for each preset
- **`viewport-base.css`** — mandatory base CSS (paste the entire file's contents into the `<style>` block)
- **`animation-patterns.md`** — entrance animations, background effects, interactive patterns

### Generation rules

**Structure:**
- Single self-contained `.html` file — all CSS and JS inline, no external dependencies except fonts
- Images referenced by file path (not base64), placed in an `assets/` folder beside the HTML
- Follow `SlidePresentation` class pattern from `html-template.md` exactly

**Design:**
- Apply the chosen preset's colors, fonts, and signature elements faithfully
- Use `clamp()` for all font sizes and spacing — never hard-coded px values for layout
- Paste the full contents of `viewport-base.css` into the `<style>` block (do not link it)
- Add `.reveal` entrance animations on slide content; stagger children with `transition-delay`
- Match animation intensity to the preset's vibe (see `animation-patterns.md`)

**Content:**
- Every slide needs a clear purpose — no filler
- Title slide, content slides, and a closing/CTA slide minimum
- Large section numbers (01, 02…) where the preset calls for them

**Inline editing (only if user said yes):**
- Follow the JS-based hover pattern from `html-template.md` exactly — do NOT use CSS `~` sibling selector
- Implement `exportFile()` with the edit-state-stripping pattern from `html-template.md`

**Images (only if provided):**
- Process with Pillow if needed (circular crop, resize > 1MB)
- Use semantic CSS classes: `.logo`, `.screenshot`
- Never repeat the same image on multiple slides (except logos on title + closing)

**CSS gotchas:**
- Negate `clamp()`/`min()`/`max()` with `calc(-1 * ...)` — never a bare leading `-`

### Output

Write the file directly to disk as `presentation.html` (or `[topic-slug].html` if a more descriptive name makes sense). If images need processing, run the Python Pillow script first and save results to `assets/`.

After writing the file, tell the user:
- The filename
- How to open it (drag into browser, or `open presentation.html`)
- One sentence on what style was applied and why it fits their topic
