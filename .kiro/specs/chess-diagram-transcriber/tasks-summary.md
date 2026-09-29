# Tasks: Chess Diagram Transcriber (Evaluation Form Version)

## Sprint 1: Specs (Complete ✓)
✓ Design, requirements, tasks documents created

## Sprint 2: Core Implementation (13:30-14:45, 115min)

**Phase 2: Dataset (30min, Required)**
- 2.1 Parse REFERENCIA.md ground truth (10min)
- 2.2 Extract sprites from ejemplos/ both styles (15min)
- 2.3 Generate 1000+ synthetic boards per style (5min)

**Phase 3: Model (15min, Required)**
- 3.1 CNN architecture (2 conv, 2 FC) or sklearn fallback (5min)
- 3.2 Train 10-20 epochs, save weights (10min)

**Phase 4: Processing (20min, Required)**
- 4.1 Board detection, 8x8 grid crop, normalize 32x32 (10min)
- 4.2 Load weights, batch inference, FEN output, validate (10min)

**Phase 5: Formatters (20min, Required)**
- 5.1 BrailleFormatter: braille rows, R-D-T-C-A-pawn order, highlights (10min)
- 5.2 AudioFormatter: Spanish names, singular/plural, Rey-Dama-Torres-Alfiles-Caballos-Peones order, "y" conjunction (10min)

**Phase 6: Validation (10min, Required)**
- 6.1 Script: run 10 references, character-by-character compare, report accuracy (10min)

**Phase 7: UI (20min, Required)**
- 7.1 Streamlit upload, display image, show braille+audio text (15min)
- 7.2 Polly integration behind DEMO_MODE, fallback (5min)

**Sprint 2 Goal**: Working pipeline, upload → braille + audio + playback

## Sprint 3: Robustness (14:45-17:15, 150min)

**Phase 8: Novel Diagrams (40min, Priority 1)**
- 8.1 Manual crop sliders, preview, re-classify (20min)
- 8.2 Rotate 180° button for black perspective (10min)
- 8.3 Reserve 2 test diagrams (5min)
- 8.4 Robust error handling, no stack traces (5min)

**Phase 9: Accessibility (30min, Priority 2)**
- 9.1 Labels, tab order, keyboard navigation (10min)
- 9.2 ARIA labels, test screen reader (10min)
- 9.3 Plain text mode, copy buttons, no color-only info (10min)

**Phase 10: Documentation (30min, Priority 3)**
- 10.1 Run validation, document exact accuracy (10min)
- 10.2 README: overview, why, approach, innovation, run instructions (10min)
- 10.3 Finalize specs, trim to 4K chars if needed (5min)
- 10.4 Document Kiro hooks/skills if created (5min)

**Phase 11: Demo Prep (60min, Priority 3, NO CODE after 16:15)**
- 11.1 Test complete flow all examples (20min)
- 11.2 Test held-out diagrams (10min)
- 11.3 Fill evaluation form (15min)
- 11.4 Final freeze, commit (5min)
- 11.5 Practice 2-min presentation (10min)

## Dependencies
Phases 2→3→4→5→(6,7)→8→9→10→11

## Critical Path
By 14:45: Dataset, model, processing, formatters, validation, UI (all required)
By 16:15: Manual controls, error handling, accessibility, metrics, README
After 16:15: Test, submit, practice (no code changes)

## Time Budget
Sprint 2 required: 115min. Sprint 3 P1-P3: 160min. Total 275min available (14:45-17:15 = 150min tight).

**Risk Mitigation**: PyTorch→sklearn fallback saves 10+min. Dataset 500 samples minimum. Training 5 epochs minimum. Polly optional.

## Success Criteria
Sprint 2: Demo works on references. Sprint 3: Works on novel diagrams, accessible, documented, ready to present.
