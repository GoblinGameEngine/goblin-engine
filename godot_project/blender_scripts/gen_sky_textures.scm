; Generates sky_day.png / sky_night.png -- tileable ceiling-panel sky
; textures for the station's day/night cycle (shaders/ceiling_sky.gdshader,
; scripts/world/DaySkySystem.gd). Requested directly: generated with GIMP
; (Script-Fu, GIMP's own batch scripting language), not PIL like this
; project's other procedural textures.
;
; Tiled every TILE_CEILING=8m (StationRingBuilder.gd) in BOTH directions --
; the "innumerable small screens" flavor text is satisfied for free by
; this: each repeat IS one small screen panel. The moving/color-cycling
; sun BAND is a separate, non-tiled feature computed from world position
; in the shader itself (a single band spanning the whole width would
; repeat every 8m if baked into this tile), not part of this texture.
;
; Run: gimp -i --batch-interpreter=plug-in-script-fu-eval -b '(load "blender_scripts/gen_sky_textures.scm")' -b '(gimp-quit 0)'

(define size 512)
(define out-dir "/home/nelahi/goblin-engine/.claude/worktrees/station-player-controls/godot_project/assets/textures/")

; A thin seamless grid -- always tiles since `size` divides evenly by
; `spacing` -- reads as faint panel seams between "screens."
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
; ADDed into the current selection (caller replaces first).
(define (select-cloud-blob img cx cy scale)
  (gimp-image-select-ellipse img CHANNEL-OP-REPLACE
    (- cx (* scale 55)) (- cy (* scale 22)) (* scale 100) (* scale 46))
  (gimp-image-select-ellipse img CHANNEL-OP-ADD
    (- cx (* scale 25)) (- cy (* scale 36)) (* scale 75) (* scale 52))
  (gimp-image-select-ellipse img CHANNEL-OP-ADD
    (+ cx (* scale 8)) (- cy (* scale 32)) (* scale 68) (* scale 46))
  (gimp-image-select-ellipse img CHANNEL-OP-ADD
    (+ cx (* scale 38)) (- cy (* scale 14)) (* scale 58) (* scale 38)))

; Cel-shaded cloud: dark outline ring (grown selection minus body), then
; white body on top -- requested directly ("clouds need outlines like
; the cel shaded models"). Two selection passes (outer then inner)
; instead of gimp-selection-border, which replaces rather than composes.
(define (draw-cloud img drawable cx cy scale)
  (select-cloud-blob img cx cy scale)
  (gimp-selection-grow img (max 2 (round (* scale 5))))
  (gimp-context-set-foreground '(58 66 78))
  (gimp-context-set-opacity 100)
  (gimp-drawable-edit-fill drawable FILL-FOREGROUND)
  (select-cloud-blob img cx cy scale)
  (gimp-context-set-foreground '(250 250 248))
  (gimp-drawable-edit-fill drawable FILL-FOREGROUND)
  (gimp-selection-none img))

(define (gen-sky-day)
  (let* ((img (car (gimp-image-new size size RGB)))
         (layer (car (gimp-layer-new img "sky" size size RGB-IMAGE 100 LAYER-MODE-NORMAL))))
    (gimp-image-insert-layer img layer 0 -1)
    ; Base gradient -- deliberately fairly neutral/mid blue (not heavily
    ; saturated) so the shader's day->dusk->night tint multiply has room
    ; to swing toward orange/red without looking muddy.
    (gimp-context-set-foreground '(120 172 226))
    (gimp-context-set-background '(184 214 240))
    (gimp-selection-none img)
    (gimp-context-set-gradient-fg-bg-rgb)
    (gimp-drawable-edit-gradient-fill layer GRADIENT-LINEAR 0 FALSE 1 0 TRUE 0 0 size 0)

    (draw-cloud img layer 96 140 1.0)
    (draw-cloud img layer 340 100 0.8)
    (draw-cloud img layer 220 340 1.15)
    (draw-cloud img layer 430 400 0.7)

    (draw-grid img layer 32 '(90 130 175) 18)

    (gimp-image-flatten img)
    (gimp-file-save RUN-NONINTERACTIVE img (string-append out-dir "sky_day.png"))
    (gimp-image-delete img)))

(define (draw-star img drawable cx cy r brightness)
  (gimp-image-select-ellipse img CHANNEL-OP-REPLACE (- cx r) (- cy r) (* r 2) (* r 2))
  (gimp-context-set-foreground (list brightness brightness (min 255 (+ brightness 10))))
  (gimp-context-set-opacity 100)
  (gimp-drawable-edit-fill drawable FILL-FOREGROUND)
  (gimp-selection-none img))

(define (gen-sky-night)
  (let* ((img (car (gimp-image-new size size RGB)))
         (layer (car (gimp-layer-new img "sky" size size RGB-IMAGE 100 LAYER-MODE-NORMAL))))
    (gimp-image-insert-layer img layer 0 -1)
    (gimp-context-set-foreground '(8 10 24))
    (gimp-context-set-background '(20 22 46))
    (gimp-selection-none img)
    (gimp-context-set-gradient-fg-bg-rgb)
    (gimp-drawable-edit-gradient-fill layer GRADIENT-LINEAR 0 FALSE 1 0 TRUE 0 0 size 0)

    ; Fixed, deterministic star field -- same reasoning as this project's
    ; other generators preferring seeded/reproducible placement.
    (draw-star img layer 40 60 2 235) (draw-star img layer 130 30 1 210)
    (draw-star img layer 210 90 2 245) (draw-star img layer 300 50 1 200)
    (draw-star img layer 380 120 2 225) (draw-star img layer 460 70 1 215)
    (draw-star img layer 60 180 1 195) (draw-star img layer 160 210 2 240)
    (draw-star img layer 250 170 1 205) (draw-star img layer 340 230 2 230)
    (draw-star img layer 420 190 1 210) (draw-star img layer 490 250 2 220)
    (draw-star img layer 30 290 2 235) (draw-star img layer 110 330 1 200)
    (draw-star img layer 190 300 2 245) (draw-star img layer 270 350 1 210)
    (draw-star img layer 350 310 2 225) (draw-star img layer 440 350 1 195)
    (draw-star img layer 70 420 1 215) (draw-star img layer 150 450 2 240)
    (draw-star img layer 230 400 1 205) (draw-star img layer 310 460 2 230)
    (draw-star img layer 390 430 1 220) (draw-star img layer 470 480 2 235)
    (draw-star img layer 20 480 1 200) (draw-star img layer 480 20 2 245)

    (draw-grid img layer 32 '(30 34 60) 22)

    (gimp-image-flatten img)
    (gimp-file-save RUN-NONINTERACTIVE img (string-append out-dir "sky_night.png"))
    (gimp-image-delete img)))

(gen-sky-day)
(gen-sky-night)
