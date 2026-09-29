# Requirements: Chess Diagram Transcriber for ONCE

## 1. Output Format Requirements

### 1.1 Braille Transcription (B8 Technical Document)
The system MUST produce braille notation exactly matching the Documento Técnico B8 format.

**Acceptance Criteria**:
- Piece order within each color: R (rey), D (dama), T (torre), C (caballo), A (alfil), then pawns
- Row numbers use braille low position exclusively: 1⠂ 2⠆ 3⠒ 4⠲ 5⠢ 6⠖ 7⠶ 8⠦
- Pawns show only column and row (e.g., `a⠆`), never with 'P' prefix
- Format: `Blancas: Re⠂ Dd⠂ Ta⠂ Th⠂ ...`
- Highlighted squares listed separately at end with color indication

### 1.2 Audio Transcription (Adapted Book Format)
The system MUST produce audio description matching ONCE's adapted book format.

**Acceptance Criteria**:
- Piece order within each color: Rey, Dama, Torres, Alfiles, Caballos, Peones (different from braille)
- Singular or plural noun based on piece count (e.g., "Torre" vs "Torres")
- Conjunction "y" before last square in each piece group
- Format: `Blancas: Rey en E2, Dama en A4, Torres en C1 y H1, ...`
- Sentence ends with period

### 1.3 Character-by-Character Accuracy
The system MUST produce output matching reference transcriptions exactly.

**Acceptance Criteria**:
- 100% character match on braille transcription against REFERENCIA.md
- 100% character match on audio transcription against REFERENCIA.md
- No invented format variations or "helpful" modifications

## 2. Image Recognition Requirements

### 2.1 Square Classification
The system MUST classify each of 64 board squares independently using a trained CNN.

**Acceptance Criteria**:
- 13 classes: empty, wP, wN, wB, wR, wQ, wK, bP, bN, bB, bR, bQ, bK
- Input: 32x32 pixel crop of each square
- Output: class label and confidence score
- Model achieves >95% accuracy on validation set

### 2.2 Board Detection and Cropping
The system MUST extract 64 individual square images from input diagram.

**Acceptance Criteria**:
- Automatic detection of board boundaries
- Crops exactly 64 squares in a1-h8 order (white's perspective)
- Each crop normalized to 32x32 pixels
- Handles both modern color boards and scanned B&W diagrams

### 2.3 Highlight Detection
The system MUST detect highlighted squares by color analysis.

**Acceptance Criteria**:
- Detects yellow-highlighted squares
- Detects red-highlighted squares
- Detection by average square color, not CNN classification
- Absence of highlights doesn't block transcription

## 3. Dataset Requirements

### 3.1 Synthetic Dataset Generation
The system MUST generate training data from reference diagram sprites.

**Acceptance Criteria**:
- Extract piece sprites from ejemplos/ images
- Generate thousands of synthetic boards with Pillow
- Perfect labels (no manual annotation required)
- Ground truth verified against REFERENCIA.md transcriptions

### 3.2 Dual Visual Style Coverage
The dataset MUST cover both visual styles present in reference diagrams.

**Acceptance Criteria**:
- Style 1: Modern color boards (green/cream, standard pieces, coordinates)
- Style 2: Scanned book diagrams (B&W, hatched dark squares, antique print)
- Training set includes representative samples from both styles
- Model trained on both styles, not just one

## 4. Chess Logic Requirements

### 4.1 Position Validation
The system MUST use python-chess for position representation and validation.

**Acceptance Criteria**:
- CNN output converted to valid FEN string
- FEN loaded into python-chess Board object
- Invalid positions caught and reported
- No reimplementation of chess rules (use python-chess)

### 4.2 Piece Querying
The system MUST query position for piece locations and types.

**Acceptance Criteria**:
- Query all pieces of given type and color
- Return squares in consistent order
- Support both algebraic notation (e2) and numeric indexing

## 5. Interface Requirements

### 5.1 Image Upload
The system MUST accept chess diagram images through Streamlit UI.

**Acceptance Criteria**:
- Upload PNG or JPG images
- Display uploaded image
- Validate image format before processing
- Clear error messages for unsupported formats

### 5.2 Transcription Display
The system MUST display both transcription formats clearly.

**Acceptance Criteria**:
- Braille text shown with proper Unicode rendering
- Audio text shown in readable format
- Both transcriptions copyable to clipboard
- Text always visible regardless of audio availability

### 5.3 Audio Playback
The system MUST synthesize and play audio transcription using Amazon Polly.

**Acceptance Criteria**:
- Use Spanish neural voice
- Playback control visible in UI
- Behind DEMO_MODE flag: works offline without credentials
- Graceful degradation: show text if Polly unavailable

## 6. Validation Requirements

### 6.1 Reference Validation
The system MUST verify accuracy against 10 reference diagrams in REFERENCIA.md.

**Acceptance Criteria**:
- Automated validation script
- Character-by-character comparison of braille output
- Character-by-character comparison of audio output
- Report: square accuracy, perfect diagram match count

### 6.2 Metrics Reporting
The system MUST provide quantitative accuracy metrics.

**Acceptance Criteria**:
- Square-level accuracy: correct classifications / 640 total
- Diagram-level accuracy: perfect matches / 10 total
- Per-piece-type accuracy breakdown
- Confusion matrix for CNN classifier

## 7. Model Requirements

### 7.1 CNN Architecture
The system MUST use small CNN for square classification.

**Acceptance Criteria**:
- PyTorch implementation (fallback: scikit-learn MLPClassifier)
- Input: 32x32x3 RGB images
- Output: 13-class logits
- Architecture: 2 conv layers, 2 fully connected layers
- Total parameters <100K

### 7.2 Training and Persistence
The system MUST train model once and load weights at runtime.

**Acceptance Criteria**:
- Model trains on synthetic dataset
- Weights saved to disk after training
- App loads pre-trained weights at startup
- App never trains during normal operation
- Training completes in <10 minutes on CPU

## 8. Performance Requirements

### 8.1 Processing Speed
The system MUST process diagrams quickly for demo purposes.

**Acceptance Criteria**:
- Board detection and cropping: <1 second
- CNN inference (64 squares): <2 seconds
- Transcription formatting: <0.1 seconds
- Total pipeline: <5 seconds per diagram

### 8.2 Resource Constraints
The system MUST run on modest hardware without GPU.

**Acceptance Criteria**:
- CPU-only inference
- Memory usage <2GB
- No internet required for core functionality (DEMO_MODE)
- PyTorch installation fallback if takes >5 minutes

## 9. Engineering Constraints

### 9.1 Technology Stack
The system MUST use specified technologies exclusively.

**Acceptance Criteria**:
- Python 3.8+ for all components
- Streamlit for UI
- Pillow and OpenCV for image processing
- python-chess for chess logic
- PyTorch for ML (fallback: scikit-learn)
- boto3 for AWS Polly (optional)

### 9.2 Code Organization
The system MUST maintain clear separation of concerns.

**Acceptance Criteria**:
- One file, one responsibility
- Files kept under 200 lines
- No authentication, database, Docker, CI/CD, or unit tests
- No unnecessary refactoring or new dependencies
- Each commit must keep app runnable

## 10. Demo Requirements

### 10.1 Demo Readiness
The system MUST be demonstrable at each checkpoint.

**Acceptance Criteria**:
- App launches without errors
- Demo runs end-to-end on example diagrams
- All functionality testable in <5 minutes
- No internet dependency for core demo

### 10.2 Error Handling
The system MUST handle errors gracefully during demo.

**Acceptance Criteria**:
- No stack traces shown to user
- Clear error messages for all failure modes
- App continues functioning after non-fatal errors
- Fallback behaviors for missing services (Polly)
