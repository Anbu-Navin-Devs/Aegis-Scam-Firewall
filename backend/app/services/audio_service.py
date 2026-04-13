"""
Audio analysis service for deepfake voice liveness detection.

This module uses *librosa* to extract acoustic features from uploaded audio
and applies a heuristic scoring algorithm to estimate the likelihood that
the voice was AI-generated.

┌──────────────────────────────────────────────────────────────────────┐
│  HOW A REAL ML MODEL WOULD SLOT IN                                   │
│                                                                      │
│  1. Replace the heuristic block inside `analyze_voice_liveness`      │
│     with a call to a pre-trained classifier, e.g.:                   │
│                                                                      │
│         model = torch.jit.load("models/deepfake_detector.pt")        │
│         logits = model(mfcc_tensor)                                  │
│         probability = torch.sigmoid(logits).item()                   │
│                                                                      │
│  2. The rest of the pipeline (file I/O → librosa feature extraction  │
│     → response schema) stays exactly the same.                       │
│                                                                      │
│  3. For production, add a warm-up step in FastAPI's `on_startup`     │
│     event so the model weights are already in GPU/CPU memory         │
│     before the first request arrives.                                │
│                                                                      │
│  Recommended architectures:                                          │
│   • RawNet2 / RawNet3  (waveform-level CNN)                         │
│   • AASIST              (graph-attention + spectral features)        │
│   • Wav2Vec 2.0 fine-tuned on ASVspoof 2021                         │
└──────────────────────────────────────────────────────────────────────┘
"""

from __future__ import annotations

import io
import numpy as np
import librosa
import soundfile as sf

from app.models.schemas import DeepfakeResponse


# ---------------------------------------------------------------------------
# Configurable thresholds for the heuristic scorer
# ---------------------------------------------------------------------------
_SPECTRAL_FLATNESS_THRESHOLD = 0.45   # above → synthetic-sounding
_PITCH_STD_THRESHOLD         = 25.0   # below → unnaturally monotone (Hz)
_SILENCE_RATIO_THRESHOLD     = 0.08   # below → TTS rarely pauses naturally
_ZCR_STD_THRESHOLD           = 0.015  # below → too-smooth zero-crossing rate


async def analyze_voice_liveness(file_bytes: bytes) -> DeepfakeResponse:
    """
    Analyse raw audio bytes for deepfake / AI-generated voice indicators.

    The function extracts four acoustic feature groups with *librosa* and
    combines them into a weighted heuristic score (0-100).  Each feature
    group adds up to 25 points of "deepfake suspicion".

    Args:
        file_bytes: Raw bytes of an uploaded audio file (WAV, MP3, FLAC, OGG …).

    Returns:
        DeepfakeResponse with ``is_deepfake``, ``confidence_score``, and
        a detailed ``analysis_details`` string.
    """

    # ------------------------------------------------------------------
    # 1.  Load audio into a numpy array via soundfile → librosa
    #     We read through an in-memory buffer so nothing touches disk.
    # ------------------------------------------------------------------
    buf = io.BytesIO(file_bytes)
    try:
        audio_data, sample_rate = sf.read(buf, dtype="float32")
    except Exception:
        # Fallback: let librosa try its own decoder (mp3, ogg …)
        buf.seek(0)
        audio_data, sample_rate = librosa.load(buf, sr=None, mono=True)

    # Ensure mono
    if audio_data.ndim > 1:
        audio_data = np.mean(audio_data, axis=1)

    # Ensure float32 & normalise peak to 1.0
    audio_data = audio_data.astype(np.float32)
    peak = np.max(np.abs(audio_data))
    if peak > 0:
        audio_data = audio_data / peak

    duration = len(audio_data) / sample_rate
    details: list[str] = []
    score = 0.0  # accumulates 0-100

    # ------------------------------------------------------------------
    # 2.  Feature Group A – Spectral Flatness
    #     Deepfake / TTS audio tends to have *very uniform* spectral
    #     energy (flatness → 1.0), whereas real speech has more
    #     variation across frames.
    #
    #     ► In production, a CNN would learn this pattern automatically
    #       from mel-spectrogram inputs.
    # ------------------------------------------------------------------
    spectral_flatness = librosa.feature.spectral_flatness(y=audio_data)
    mean_flatness = float(np.mean(spectral_flatness))

    if mean_flatness > _SPECTRAL_FLATNESS_THRESHOLD:
        contribution = min(25.0, (mean_flatness - _SPECTRAL_FLATNESS_THRESHOLD) / (1.0 - _SPECTRAL_FLATNESS_THRESHOLD) * 25)
        score += contribution
        details.append(
            f"Spectral flatness is high ({mean_flatness:.3f} > {_SPECTRAL_FLATNESS_THRESHOLD}) "
            f"suggesting synthesised / uniform spectral energy (+{contribution:.1f} pts)."
        )
    else:
        details.append(
            f"Spectral flatness is normal ({mean_flatness:.3f}), consistent with natural speech."
        )

    # ------------------------------------------------------------------
    # 3.  Feature Group B – Pitch (F0) Stability
    #     Natural human speech has considerable pitch variation.
    #     Many TTS engines produce an unnaturally *stable* F0 contour.
    #
    #     ► A real model (e.g. AASIST) encodes F0 trajectories via
    #       graph-attention layers instead of a simple std threshold.
    # ------------------------------------------------------------------
    f0, voiced_flag, _ = librosa.pyin(
        audio_data,
        fmin=librosa.note_to_hz("C2"),
        fmax=librosa.note_to_hz("C7"),
        sr=sample_rate,
    )
    voiced_f0 = f0[voiced_flag] if voiced_flag is not None else f0[~np.isnan(f0)]

    if len(voiced_f0) > 0:
        pitch_std = float(np.std(voiced_f0))
        if pitch_std < _PITCH_STD_THRESHOLD:
            contribution = min(25.0, (_PITCH_STD_THRESHOLD - pitch_std) / _PITCH_STD_THRESHOLD * 25)
            score += contribution
            details.append(
                f"Pitch variability is low (std={pitch_std:.1f} Hz < {_PITCH_STD_THRESHOLD} Hz), "
                f"indicating monotone delivery typical of TTS (+{contribution:.1f} pts)."
            )
        else:
            details.append(
                f"Pitch variability is healthy (std={pitch_std:.1f} Hz), consistent with a real human voice."
            )
    else:
        details.append("Could not extract reliable pitch — audio may be too short or noisy.")

    # ------------------------------------------------------------------
    # 4.  Feature Group C – Silence / Pause Ratio
    #     Real speakers breathe, hesitate, and pause.  TTS output
    #     rarely contains natural silence gaps.
    #
    #     ► A production pipeline might use a Voice Activity Detector
    #       (e.g. Silero VAD) for more accurate segmentation.
    # ------------------------------------------------------------------
    rms = librosa.feature.rms(y=audio_data)[0]
    silence_threshold = 0.02
    silence_ratio = float(np.mean(rms < silence_threshold))

    if silence_ratio < _SILENCE_RATIO_THRESHOLD:
        contribution = min(25.0, (_SILENCE_RATIO_THRESHOLD - silence_ratio) / _SILENCE_RATIO_THRESHOLD * 25)
        score += contribution
        details.append(
            f"Silence ratio is very low ({silence_ratio:.3f} < {_SILENCE_RATIO_THRESHOLD}), "
            f"suggesting continuous TTS output without natural pauses (+{contribution:.1f} pts)."
        )
    else:
        details.append(
            f"Silence ratio is normal ({silence_ratio:.3f}), natural breathing pauses detected."
        )

    # ------------------------------------------------------------------
    # 5.  Feature Group D – Zero-Crossing Rate Smoothness
    #     Real vocal-tract excitation creates irregular ZCR patterns.
    #     Neural vocoders tend to produce smoother ZCR curves.
    #
    #     ► RawNet2 captures this implicitly in its first sinc-conv layer.
    # ------------------------------------------------------------------
    zcr = librosa.feature.zero_crossing_rate(y=audio_data)[0]
    zcr_std = float(np.std(zcr))

    if zcr_std < _ZCR_STD_THRESHOLD:
        contribution = min(25.0, (_ZCR_STD_THRESHOLD - zcr_std) / _ZCR_STD_THRESHOLD * 25)
        score += contribution
        details.append(
            f"Zero-crossing rate is unusually smooth (std={zcr_std:.4f} < {_ZCR_STD_THRESHOLD}), "
            f"consistent with neural vocoder output (+{contribution:.1f} pts)."
        )
    else:
        details.append(
            f"Zero-crossing rate variance is normal (std={zcr_std:.4f}), indicating natural excitation."
        )

    # ------------------------------------------------------------------
    # 6.  Final verdict
    # ------------------------------------------------------------------
    score = round(min(score, 100.0), 2)
    is_deepfake = score >= 50.0

    summary = (
        f"Audio duration: {duration:.2f}s | Sample rate: {sample_rate} Hz. "
        + " ".join(details)
    )

    return DeepfakeResponse(
        is_deepfake=is_deepfake,
        confidence_score=score,
        analysis_details=summary,
    )


# ---------------------------------------------------------------------------
# Rolling-window / streaming helper
# ---------------------------------------------------------------------------

def analyze_audio_chunk(audio_data: np.ndarray, sample_rate: int) -> DeepfakeResponse:
    """
    Synchronous heuristic scorer for a pre-decoded audio chunk.

    Designed for use by the WebSocket streaming router, which accumulates
    raw float32 PCM samples and calls this function each time the rolling
    window reaches a minimum threshold (e.g. 1-2 seconds of audio).
    Because librosa's ``pyin`` requires a minimum signal length, chunks
    shorter than 2048 samples skip pitch analysis gracefully.

    The four feature groups (spectral flatness, pitch stability, silence
    ratio, ZCR smoothness) are identical to ``analyze_voice_liveness`` so
    the heuristic thresholds stay consistent across both REST and WebSocket
    code paths.

    Args:
        audio_data:  1-D float32 numpy array of normalised PCM samples.
        sample_rate: Sample rate of the audio (Hz).

    Returns:
        DeepfakeResponse — same schema as the REST endpoint.
    """
    details: list[str] = []
    score = 0.0
    duration = len(audio_data) / sample_rate

    # -- Feature A: Spectral Flatness ----------------------------------------
    mean_flatness = float(np.mean(librosa.feature.spectral_flatness(y=audio_data)))
    if mean_flatness > _SPECTRAL_FLATNESS_THRESHOLD:
        contribution = min(
            25.0,
            (mean_flatness - _SPECTRAL_FLATNESS_THRESHOLD)
            / (1.0 - _SPECTRAL_FLATNESS_THRESHOLD)
            * 25,
        )
        score += contribution
        details.append(
            f"Spectral flatness high ({mean_flatness:.3f}) → synthetic energy (+{contribution:.1f})."
        )
    else:
        details.append(f"Spectral flatness normal ({mean_flatness:.3f}).")

    # -- Feature B: Pitch Stability ------------------------------------------
    # pyin needs >= 2048 samples (~0.13 s at 16 kHz); skip if chunk is too short.
    if len(audio_data) >= 2048:
        try:
            f0, voiced_flag, _ = librosa.pyin(
                audio_data,
                fmin=librosa.note_to_hz("C2"),
                fmax=librosa.note_to_hz("C7"),
                sr=sample_rate,
            )
            voiced_f0 = f0[voiced_flag] if voiced_flag is not None else f0[~np.isnan(f0)]
            if len(voiced_f0) > 0:
                pitch_std = float(np.std(voiced_f0))
                if pitch_std < _PITCH_STD_THRESHOLD:
                    contribution = min(
                        25.0,
                        (_PITCH_STD_THRESHOLD - pitch_std) / _PITCH_STD_THRESHOLD * 25,
                    )
                    score += contribution
                    details.append(
                        f"Pitch std={pitch_std:.1f} Hz (low → TTS +{contribution:.1f})."
                    )
                else:
                    details.append(f"Pitch std={pitch_std:.1f} Hz (healthy).")
            else:
                details.append("No voiced frames — too noisy/short for pitch.")
        except Exception:
            details.append("Pitch extraction skipped.")
    else:
        details.append("Chunk too short for pitch analysis.")

    # -- Feature C: Silence Ratio --------------------------------------------
    rms = librosa.feature.rms(y=audio_data)[0]
    silence_ratio = float(np.mean(rms < 0.02))
    if silence_ratio < _SILENCE_RATIO_THRESHOLD:
        contribution = min(
            25.0,
            (_SILENCE_RATIO_THRESHOLD - silence_ratio) / _SILENCE_RATIO_THRESHOLD * 25,
        )
        score += contribution
        details.append(f"Silence ratio {silence_ratio:.3f} (low → TTS +{contribution:.1f}).")
    else:
        details.append(f"Silence ratio {silence_ratio:.3f} (normal).")

    # -- Feature D: Zero-Crossing Rate Smoothness ----------------------------
    zcr_std = float(np.std(librosa.feature.zero_crossing_rate(y=audio_data)[0]))
    if zcr_std < _ZCR_STD_THRESHOLD:
        contribution = min(
            25.0,
            (_ZCR_STD_THRESHOLD - zcr_std) / _ZCR_STD_THRESHOLD * 25,
        )
        score += contribution
        details.append(f"ZCR std={zcr_std:.4f} (smooth → vocoder +{contribution:.1f}).")
    else:
        details.append(f"ZCR std={zcr_std:.4f} (natural).")

    # -- Final verdict -------------------------------------------------------
    score = round(min(score, 100.0), 2)
    summary = (
        f"[chunk {duration:.2f}s @ {sample_rate} Hz] " + " | ".join(details)
    )

    return DeepfakeResponse(
        is_deepfake=score >= 50.0,
        confidence_score=score,
        analysis_details=summary,
    )
