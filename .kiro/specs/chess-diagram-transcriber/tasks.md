# Tasks: Chess Diagram Transcriber for ONCE

## Sprint 1: Spec Creation (Complete by 13:30)

### Phase 1: Specification Documents ✓
- [x] 1.1 Create design.md (DONE)
- [x] 1.2 Create requirements.md (DONE)
- [x] 1.3 Create tasks.md (DONE)

**Deliverable**: Three spec documents under 4,000 characters each, ready to paste into evaluation form.

---

## Sprint 2: Core Implementation (13:30 - 14:45)

### Phase 2: Dataset Generation (Required, 30 min)
- [ ] 2.1 Parse REFERENCIA.md to extract ground truth positions
  - Read 10 transcriptions
  - Parse braille format to FEN strings
  - Map image paths to positions
  - **Time**: 10 min

- [ ] 2.2 Extract piece sprites from reference images
  - Load tablero1-6.png (modern style)
  - Load diagrama01,02,05,23.png (book style)
  - Crop individual pieces using known positions
  - Save sprites organized by piece type and style
  - **Time**: 15 min

- [ ] 2.3 Generate synthetic training dataset
  - Create random valid chess positions (1000 per style)
  - Composite boards using extracted sprites
  - Generate 32x32 crops with labels
  - Save as numpy arrays
  - **Time**: 5 min

### Phase 3: Model Training (Required, 15 min)
- [ ] 3.1 Implement CNN architecture
  - Define ChessSquareCNN class
  - 2 conv layers + 2 FC layers
  - 13-class output
  - **Time**: 5 min
  - **Fallback**: If PyTorch install >5 min, use sklearn MLPClassifier

- [ ] 3.2 Train classifier
  - Load synthetic dataset
  - Train/val split 80/20
  - Train for 10-20 epochs
  - Save best weights to disk
  - **Time**: 10 min

### Phase 4: Board Processing (Required, 20 min)
- [ ] 4.1 Implement board detection and cropping
  - Find board boundaries in image
  - Grid-based 8x8 extraction
  - Normalize each crop to 32x32
  - Handle both visual styles
  - **Time**: 10 min

- [ ] 4.2 Implement square classification
  - Load trained model weights
  - Batch inference on 64 crops
  - Convert predictions to FEN
  - Validate with python-chess
  - **Time**: 10 min

### Phase 5: Transcription Formatters (Required, 20 min)
- [ ] 5.1 Implement BrailleFormatter
  - Define braille row encoding constants
  - Implement piece ordering: R, D, T, C, A, pawns
  - Format each color's pieces
  - Add highlight notation
  - **Time**: 10 min

- [ ] 5.2 Implement AudioFormatter
  - Define piece name mappings (Spanish)
  - Implement piece ordering: Rey, Dama, Torres, Alfiles, Caballos, Peones
  - Handle singular/plural
  - Add conjunction "y" before last square
  - **Time**: 10 min

### Phase 6: Validation Script (Required, 10 min)
- [ ] 6.1 Create validation script
  - Load 10 reference images
  - Run pipeline on each
  - Compare output to REFERENCIA.md character-by-character
  - Report square accuracy and perfect match count
  - **Time**: 10 min

### Phase 7: Streamlit UI (Required, 20 min)
- [ ] 7.1 Basic UI with image upload
  - File uploader widget
  - Display uploaded image
  - Run transcription pipeline
  - Show braille output
  - Show audio output
  - **Time**: 15 min

- [ ] 7.2 Amazon Polly integration
  - Configure boto3 client
  - Synthesize audio from text
  - Add playback widget
  - Wrap in DEMO_MODE check
  - Graceful fallback to text-only
  - **Time**: 5 min

**Sprint 2 Deliverable**: Working end-to-end pipeline. Upload diagram → see braille + audio transcriptions → hear audio playback.

---

## Sprint 3: Robustness & Polish (14:45 - 17:15)

### Phase 8: Handle Novel Diagrams (Priority 1, 40 min)
- [ ] 8.1 Manual crop adjustment controls
  - Add sliders for board boundary adjustment
  - Preview cropped region
  - Re-run classification on adjusted crop
  - **Time**: 20 min

- [ ] 8.2 Board rotation support
  - Add "Rotate 180°" button for black's perspective
  - Re-detect board after rotation
  - **Time**: 10 min

- [ ] 8.3 Reserve test diagrams
  - Set aside 2 examples not used in development
  - Document which examples were held out
  - **Time**: 5 min

- [ ] 8.4 Robust error handling
  - Wrap all processing in try-catch
  - Show user-friendly messages
  - Never display stack traces
  - Log errors to file for debugging
  - **Time**: 5 min

### Phase 9: Accessibility (Priority 2, 30 min)
- [ ] 9.1 Keyboard navigation
  - Add labels to all controls
  - Set logical tab order
  - Test keyboard-only operation
  - **Time**: 10 min

- [ ] 9.2 Screen reader compatibility
  - Add ARIA labels where needed
  - Ensure transcriptions are copyable
  - Test with Windows Narrator or NVDA
  - **Time**: 10 min

- [ ] 9.3 Plain text mode
  - Provide text-only output option
  - Ensure nothing depends solely on color
  - Add "Copy to clipboard" buttons
  - **Time**: 10 min

### Phase 10: Documentation & Metrics (Priority 3, 30 min)
- [ ] 10.1 Final accuracy measurement
  - Run validation script on all 10 references
  - Document exact numbers for form
  - Generate confusion matrix
  - **Time**: 10 min

- [ ] 10.2 Create README.md
  - Project overview
  - Why it matters
  - Technical approach
  - Innovation highlights
  - How to run
  - **Time**: 10 min

- [ ] 10.3 Finalize spec documents
  - Update with any design changes
  - Trim to 4,000 character limit if needed
  - Proofread for clarity
  - **Time**: 5 min

- [ ] 10.4 Document custom Kiro enhancements
  - List any hooks created
  - List any skills created
  - Explain how they accelerated development
  - **Time**: 5 min

### Phase 11: Demo Prep (16:15 - 17:15, 60 min)
- [ ] 11.1 Test complete demo flow
  - Load app
  - Upload each example
  - Verify transcriptions
  - Test audio playback
  - **Time**: 20 min

- [ ] 11.2 Test with held-out diagrams
  - Upload the 2 reserved examples
  - Verify transcriptions match expectations
  - Document accuracy
  - **Time**: 10 min

- [ ] 11.3 Fill evaluation form
  - Paste specs into form fields
  - Add accuracy metrics
  - Add innovation notes
  - **Time**: 15 min

- [ ] 11.4 Final freeze
  - No code changes after 16:15
  - Only documentation updates
  - Commit final state
  - **Time**: 5 min

- [ ] 11.5 Practice demo presentation
  - Prepare 2-minute walkthrough
  - Identify key highlights
  - Prepare for questions
  - **Time**: 10 min

---

## Task Dependencies

```
Phase 1 (Specs) → DONE

Phase 2 (Dataset) → Phase 3 (Training)
Phase 3 (Training) → Phase 4 (Processing)
Phase 4 (Processing) → Phase 5 (Formatters)
Phase 5 (Formatters) → Phase 6 (Validation)
Phase 5 (Formatters) → Phase 7 (UI)

Phase 7 (UI) → Phase 8 (Robustness)
Phase 8 (Robustness) → Phase 9 (Accessibility)
Phase 9 (Accessibility) → Phase 10 (Docs)
Phase 10 (Docs) → Phase 11 (Demo Prep)
```

---

## Critical Path

**Must Complete by 14:45**:
- Dataset generation (2.1-2.3)
- Model training (3.1-3.2)
- Board processing (4.1-4.2)
- Formatters (5.1-5.2)
- Validation script (6.1)
- Basic UI (7.1-7.2)

**Must Complete by 16:15**:
- Manual crop controls (8.1-8.2)
- Error handling (8.4)
- Accessibility basics (9.1-9.3)
- Final metrics (10.1)
- README (10.2)

**After 16:15 - No Code Changes**:
- Demo testing (11.1-11.2)
- Form submission (11.3)
- Practice (11.5)

---

## Time Budget Summary

| Sprint | Phase | Total Time | Priority |
|--------|-------|------------|----------|
| 1 | Specs | 30 min | DONE |
| 2 | Dataset | 30 min | Required |
| 2 | Training | 15 min | Required |
| 2 | Processing | 20 min | Required |
| 2 | Formatters | 20 min | Required |
| 2 | Validation | 10 min | Required |
| 2 | UI | 20 min | Required |
| 3 | Novel Diagrams | 40 min | P1 |
| 3 | Accessibility | 30 min | P2 |
| 3 | Docs | 30 min | P3 |
| 3 | Demo Prep | 60 min | P3 |

**Total**: 305 minutes (5 hours 5 minutes)
**Available**: Sprint 2 (75 min) + Sprint 3 (150 min) = 225 minutes

**Risk Mitigation**:
- PyTorch install fallback to sklearn (saves 10+ min)
- Dataset size adjustable (500 samples minimum)
- Training epochs adjustable (5 minimum)
- Polly optional (DEMO_MODE fallback)

---

## Success Criteria

**Sprint 1 (13:30)**: ✓ Specs complete
**Sprint 2 (14:45)**: End-to-end demo works on reference diagrams
**Sprint 3 (17:15)**: Robust demo on novel diagrams with accessibility

**Final Deliverable**: App transcribes novel chess diagrams to exact ONCE formats with measured accuracy, accessible interface, and complete documentation.
