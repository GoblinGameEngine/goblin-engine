; Generates sky_day.png / sky_night.png -- tileable ceiling-panel sky
; textures for the station's day/night cycle (shaders/ceiling_sky.gdshader,
; scripts/world/DaySkySystem.gd). Requested directly: generated with GIMP
; (Script-Fu, GIMP's own batch scripting language), not PIL like this
; project's other procedural textures.
;
; Tiled every TILE_CEILING=60m (StationRingBuilder.gd) in BOTH directions
; -- large on purpose (requested directly: "large fluffy clouds... a
; mosaic," not a small pattern repeated so densely it reads as a fine
; texture). Each repeat still doubles as the "innumerable small screens"
; flavor text's own panel, just a bigger one; the fine grid baked in here
; is what gives the granular-up-close look, smoothed by ordinary mipmap
; minification from a distance -- no shader work needed for that part.
;
; Run: gimp-console -i --batch-interpreter=plug-in-script-fu-eval -b '(load "blender_scripts/gen_sky_textures.scm")' -b '(gimp-quit 0)'
; NOTE: this GIMP 3.0 install needs gimp-console specifically (not `gimp
; -i`, which still initializes GTK and hangs trying to open a display in
; a headless environment) and takes ~30-90s just to start -- not hung,
; just slow; give batch calls a generous (120s+) timeout.

(define size 1024)
(define out-dir "/home/nelahi/goblin-engine/.claude/worktrees/station-player-controls/godot_project/assets/textures/")

(define (draw-grid img drawable spacing color alpha)
  (gimp-context-set-foreground color)
  (gimp-context-set-opacity alpha)
  (gimp-context-set-paint-mode LAYER-MODE-NORMAL)
  (let loop ((i 0))
    (if (< i size)
        (begin
          (gimp-image-select-rectangle img CHANNEL-OP-REPLACE i 0 1 size)
          (gimp-drawable-edit-fill drawable FILL-FOREGROUND)
          (gimp-image-select-rectangle img CHANNEL-OP-REPLACE 0 i size 1)
          (gimp-drawable-edit-fill drawable FILL-FOREGROUND)
          (loop (+ i spacing)))))
  (gimp-selection-none img))

; One cloud's blob silhouette -- a cluster of overlapping ellipses,
; ADDed into the current selection (caller replaces first). Requested
; directly: LARGE fluffy clouds -- scale is applied to a bigger base
; footprint than the original small-tile version.
(define (select-cloud-blob img cx cy scale)
  (gimp-image-select-ellipse img CHANNEL-OP-REPLACE
    (- cx (* scale 130)) (- cy (* scale 55)) (* scale 240) (* scale 110))
  (gimp-image-select-ellipse img CHANNEL-OP-ADD
    (- cx (* scale 60)) (- cy (* scale 90)) (* scale 190) (* scale 130))
  (gimp-image-select-ellipse img CHANNEL-OP-ADD
    (+ cx (* scale 20)) (- cy (* scale 80)) (* scale 170) (* scale 115))
  (gimp-image-select-ellipse img CHANNEL-OP-ADD
    (+ cx (* scale 90)) (- cy (* scale 35)) (* scale 140) (* scale 95))
  (gimp-image-select-ellipse img CHANNEL-OP-ADD
    (- cx (* scale 100)) (- cy (* scale 20)) (* scale 130) (* scale 80)))

; Cel-shaded cloud: dark outline ring (grown selection minus body), then
; white body on top -- requested directly ("clouds need outlines like
; the cel shaded models").
(define (draw-cloud img drawable cx cy scale)
  (select-cloud-blob img cx cy scale)
  (gimp-selection-grow img (max 3 (round (* scale 9))))
  (gimp-context-set-opacity 100)
  (gimp-context-set-foreground '(55 63 76))
  (gimp-drawable-edit-fill drawable FILL-FOREGROUND)
  (select-cloud-blob img cx cy scale)
  (gimp-context-set-foreground '(255 255 253))
  (gimp-drawable-edit-fill drawable FILL-FOREGROUND)
  (gimp-selection-none img))

(define (gen-sky-day)
  (let* ((img (car (gimp-image-new size size RGB)))
         (layer (car (gimp-layer-new img "sky" size size RGB-IMAGE 100 LAYER-MODE-NORMAL))))
    (gimp-image-insert-layer img layer 0 -1)
    ; Brighter, more vivid blue than the first version -- requested
    ; directly ("the station is too dark in the daytime" fed back into
    ; this texture too, not just the ambient-light fix).
    (gimp-context-set-foreground '(140 190 240))
    (gimp-context-set-background '(205 228 250))
    (gimp-selection-none img)
    (gimp-context-set-gradient-fg-bg-rgb)
    (gimp-drawable-edit-gradient-fill layer GRADIENT-LINEAR 0 FALSE 1 0 TRUE 0 0 size 0)

    ; A few LARGE fluffy clouds, not many small ones -- requested
    ; directly.
    (draw-cloud img layer 200 260 2.0)
    (draw-cloud img layer 700 180 1.7)
    (draw-cloud img layer 470 700 2.2)

    (draw-grid img layer 48 '(100 145 195) 14)

    (gimp-image-flatten img)
    (gimp-file-save RUN-NONINTERACTIVE img (string-append out-dir "sky_day.png"))
    (gimp-image-delete img)))

(define (draw-star img drawable cx cy r color)
  (gimp-image-select-ellipse img CHANNEL-OP-REPLACE (- cx r) (- cy r) (* r 2) (* r 2))
  (gimp-context-set-opacity 100)
  (gimp-context-set-foreground color)
  (gimp-drawable-edit-fill drawable FILL-FOREGROUND)
  (gimp-selection-none img))

; A soft glowing galaxy/nebula blob -- several overlapping ellipses at
; DECREASING opacity from a bright core outward, faking a soft gradient
; glow without needing a real gaussian-blur plugin call (this GIMP 3.0
; install's PDB signatures were unreliable enough elsewhere -- see this
; file's own header note -- that avoiding an extra untested call here
; was worth it).
(define (draw-galaxy img drawable cx cy scale core-color mid-color outer-color)
  (gimp-context-set-paint-mode LAYER-MODE-NORMAL)
  (gimp-image-select-ellipse img CHANNEL-OP-REPLACE
    (- cx (* scale 140)) (- cy (* scale 55)) (* scale 280) (* scale 110))
  (gimp-context-set-opacity 35)
  (gimp-context-set-foreground outer-color)
  (gimp-drawable-edit-fill drawable FILL-FOREGROUND)
  (gimp-image-select-ellipse img CHANNEL-OP-REPLACE
    (- cx (* scale 85)) (- cy (* scale 34)) (* scale 170) (* scale 68))
  (gimp-context-set-opacity 45)
  (gimp-context-set-foreground mid-color)
  (gimp-drawable-edit-fill drawable FILL-FOREGROUND)
  (gimp-image-select-ellipse img CHANNEL-OP-REPLACE
    (- cx (* scale 40)) (- cy (* scale 16)) (* scale 80) (* scale 32))
  (gimp-context-set-opacity 65)
  (gimp-context-set-foreground core-color)
  (gimp-drawable-edit-fill drawable FILL-FOREGROUND)
  (gimp-image-select-ellipse img CHANNEL-OP-REPLACE
    (- cx (* scale 14)) (- cy (* scale 6)) (* scale 28) (* scale 12))
  (gimp-context-set-opacity 85)
  (gimp-drawable-edit-fill drawable FILL-FOREGROUND)
  (gimp-selection-none img)
  (gimp-context-set-opacity 100))

(define (gen-sky-night)
  (let* ((img (car (gimp-image-new size size RGB)))
         (layer (car (gimp-layer-new img "sky" size size RGB-IMAGE 100 LAYER-MODE-NORMAL))))
    (gimp-image-insert-layer img layer 0 -1)
    (gimp-context-set-foreground '(6 8 20))
    (gimp-context-set-background '(16 18 40))
    (gimp-selection-none img)
    (gimp-context-set-gradient-fg-bg-rgb)
    (gimp-drawable-edit-gradient-fill layer GRADIENT-LINEAR 0 FALSE 1 0 TRUE 0 0 size 0)

    ; Galaxies drawn BEFORE stars, so star points sit crisply on top of
    ; the soft glow instead of being dimmed by it.
    (draw-galaxy img layer 250 300 1.6 '(235 225 250) '(165 140 210) '(90 80 160))
    (draw-galaxy img layer 760 620 1.3 '(250 230 220) '(210 150 170) '(120 70 110))
    (draw-galaxy img layer 550 150 1.0 '(220 235 250) '(140 170 215) '(70 90 150))

    ; Fixed, deterministic star field -- same reasoning as this project's
    ; other generators preferring seeded/reproducible placement.
    ; Requested directly: differing SIZE and COLOR (white, pale blue,
    ; pale amber, pale red), not uniform dots.
    (draw-star img layer 80 120 3 '(255 255 255)) (draw-star img layer 260 60 2 '(200 215 255))
    (draw-star img layer 420 180 4 '(255 245 220)) (draw-star img layer 600 100 1 '(255 255 255))
    (draw-star img layer 760 240 3 '(255 210 190)) (draw-star img layer 920 140 2 '(210 225 255))
    (draw-star img layer 120 360 2 '(255 255 255)) (draw-star img layer 320 420 3 '(255 240 210))
    (draw-star img layer 500 380 1 '(200 215 255)) (draw-star img layer 680 440 4 '(255 255 255))
    (draw-star img layer 840 360 2 '(255 200 180)) (draw-star img layer 60 580 3 '(215 225 255))
    (draw-star img layer 240 640 2 '(255 255 255)) (draw-star img layer 400 560 1 '(255 245 215))
    (draw-star img layer 580 620 4 '(255 255 255)) (draw-star img layer 760 700 2 '(200 220 255))
    (draw-star img layer 940 580 3 '(255 220 200)) (draw-star img layer 140 800 2 '(255 255 255))
    (draw-star img layer 320 860 3 '(210 225 255)) (draw-star img layer 500 820 1 '(255 255 255))
    (draw-star img layer 680 880 4 '(255 240 215)) (draw-star img layer 860 820 2 '(255 210 195))
    (draw-star img layer 40 940 3 '(255 255 255)) (draw-star img layer 220 980 2 '(200 215 255))
    (draw-star img layer 460 950 1 '(255 255 255)) (draw-star img layer 700 960 3 '(255 245 220))
    (draw-star img layer 940 940 2 '(215 225 255)) (draw-star img layer 980 60 4 '(255 255 255))
    (draw-star img layer 180 220 1 '(255 210 195)) (draw-star img layer 900 460 3 '(255 255 255))

    (draw-grid img layer 48 '(28 32 58) 18)

    (gimp-image-flatten img)
    (gimp-file-save RUN-NONINTERACTIVE img (string-append out-dir "sky_night.png"))
    (gimp-image-delete img)))

(gen-sky-day)
(gen-sky-night)
