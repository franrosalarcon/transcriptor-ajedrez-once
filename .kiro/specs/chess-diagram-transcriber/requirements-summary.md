# Requirements: Chess Diagram Transcriber (Evaluation Form Version)

## 1. Output Format (Critical)
**R1.1 Braille B8**: Piece order R,D,T,C,A,pawns. Row numbers braille low position (⠂⠆⠒⠲⠢⠖⠶⠦ not ASCII). Pawns column+row only (a⠆ not Pa⠆). Format: `Blancas: Re⠂ Dd⠂...` Highlights at end with color.

**R1.2 Audio Book**: Piece order Rey,Dama,Torres,Alfiles,Caballos,Peones (different from braille). Singular/plural by count. Conjunction "y" before last. Format: `Blancas: Rey en E2, Dama en A4, Torres en C1 y H1...`

**R1.3 Accuracy**: 100% character match against REFERENCIA.md transcriptions. No format invention.

## 2. Recognition
**R2.1 Square Classification**: CNN classifies 64 squares independently. 13 classes: empty, wP,wN,wB,wR,wQ,wK, bP,bN,bB,bR,bQ,bK. Input 32x32 crops. Target >95% accuracy.

**R2.2 Board Detection**: Auto-detect boundaries, extract 64 crops in a1-h8 order, normalize 32x32. Handle modern color boards AND scanned B&W diagrams.

**R2.3 Highlights**: Detect by average square color (yellow/red), not CNN. Detection failure doesn't block transcription.

## 3. Dataset
**R3.1 Synthetic Generation**: Extract sprites from ejemplos/, compose thousands of boards with Pillow, perfect labels from REFERENCIA.md ground truth.

**R3.2 Dual Styles**: MUST cover modern color (tablero1-6: green/cream, coordinates) AND scanned book (diagrama01,02,05,23: B&W, hatched, antique print). Model trained on one fails on other.

## 4. Chess Logic
**R4.1 Validation**: Convert CNN output to FEN, load into python-chess Board, catch invalid positions. No chess rule reimplementation.

**R4.2 Queries**: Use python-chess to find pieces by type/color, return squares in order.

## 5. Interface
**R5.1 Upload**: Streamlit file uploader, PNG/JPG validation, clear errors.

**R5.2 Display**: Show braille (Unicode) + audio text, both copyable, always visible regardless of audio availability.

**R5.3 Audio**: Amazon Polly Spanish neural voice, behind DEMO_MODE flag, graceful degradation offline.

## 6. Validation
**R6.1 Reference Set**: Automated script compares output to 10 diagrams in REFERENCIA.md character-by-character.

**R6.2 Metrics**: Square accuracy (correct/640), diagram accuracy (perfect/10), per-piece breakdown, confusion matrix.

## 7. Model
**R7.1 Architecture**: Small CNN (2 conv, 2 FC, <100K params). PyTorch preferred, sklearn fallback if install >5min.

**R7.2 Training**: Train once on synthetic data, save weights, load at startup. Never train during operation. Complete <10min CPU.

## 8. Performance
Process diagram <5sec total (detection <1sec, inference <2sec, formatting <0.1sec). CPU-only, <2GB memory.

## 9. Engineering
Python 3.8+ only. Streamlit UI, Pillow+OpenCV image, python-chess logic, PyTorch/sklearn ML, boto3 audio optional. One file one responsibility, files <200 lines. No auth/DB/Docker/CI/tests. Every commit keeps app runnable.

## 10. Demo
Launch without errors, end-to-end in <5min, no internet for core functionality, graceful error handling (no stack traces), fallback for missing services.
