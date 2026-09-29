# Design: Chess Diagram Transcriber (Evaluation Form Version)

## System Overview
Image → 64 square crops → CNN classifier → FEN → python-chess → dual formatters → braille + audio transcriptions

**Pipeline**: BoardDetector extracts 64 32x32 crops → SquareClassifier (CNN) predicts 13 classes per square → FEN string → python-chess Board → BrailleFormatter (B8 order: R,D,T,C,A,pawns) + AudioFormatter (book order: Rey,Dama,Torres,Alfiles,Caballos,Peones) → highlighted squares by color analysis

## Core Components

**BoardDetector**: Grid-based 8x8 extraction from input image, normalize to 32x32, detect highlights by average square color (yellow/red thresholds)

**SquareClassifier (CNN)**: 13 classes (empty + 12 pieces). PyTorch: Conv2d(3→32) → Pool → Conv2d(32→64) → Pool → FC(4096→128) → FC(128→13). Fallback: sklearn MLPClassifier if PyTorch install >5min. Input 32x32x3, output class logits.

**BrailleFormatter**: Spanish initials (R,D,T,C,A,P), braille row encoding (1⠂ 2⠆ 3⠒ 4⠲ 5⠢ 6⠖ 7⠶ 8⠦), order R-D-T-C-A-pawns, pawns without P prefix. Format: `Blancas: Re⠂ Dd⠂ Ta⠂...` Highlights appended: `)Resaltadas en amarillo las casillas g⠒ y h⠲(`

**AudioFormatter**: Spanish names (Rey,Dama,Torre,Alfil,Caballo,Peón), singular/plural by count, conjunction "y" before last square, order Rey-Dama-Torres-Alfiles-Caballos-Peones. Format: `Blancas: Rey en E2, Dama en A4, Torres en C1 y H1...`

**DatasetGenerator**: Extract piece sprites from ejemplos/ (known positions from REFERENCIA.md) → composite synthetic boards with Pillow → 32x32 crops with perfect labels. CRITICAL: Two styles (modern color boards: tablero1-6, scanned B&W diagrams: diagrama01,02,05,23) → dataset MUST cover both or model fails on half.

## Recognition & Verification

**What we recognize**: Each of 64 squares classified independently (empty or 12 piece types). Highlighted squares by color. Board boundaries auto-detected.

**What we output**: 
- Braille (B8): exact character match including special row encoding
- Audio (libro adaptado): exact word order and grammar rules

**How we verify**: Character-by-character comparison against 10 transcriptions in REFERENCIA.md. Validation script reports: square accuracy (correct/640), perfect diagram count (of 10), per-piece confusion matrix.

## Tech Stack
Python 3.8+, Streamlit (UI), Pillow+OpenCV (image), python-chess (validation/queries), PyTorch/scikit-learn (CNN), boto3+Polly (audio, behind DEMO_MODE flag)

## Error Handling
Board detection failure → manual crop sliders. Invalid FEN → catch exception, show warning. Polly unavailable → text-only mode. No stack traces to user.

## Performance
CNN inference <2sec (64 squares CPU), total pipeline <5sec, training <10min on 10K synthetic samples
