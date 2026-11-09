#!/usr/bin/env python3
"""Retrieve speech in memory; download audio only when captions are absent."""
import argparse
import json
from pathlib import Path
import re
import signal
import sys
import tempfile
from urllib.parse import parse_qs, urlparse


class MissingCaptions(Exception):
    pass


def video_id(value):
    parsed = urlparse(value if "://" in value else "https://" + value)
    host = (parsed.hostname or "").lower()
    parts = parsed.path.strip("/").split("/")
    if parsed.scheme not in ("http", "https") or parsed.username or parsed.password:
        raise ValueError("Provide a public YouTube video URL.")
    if host in ("youtu.be", "www.youtu.be") and len(parts) == 1:
        result = parts[0]
    elif host in ("youtube.com", "www.youtube.com", "m.youtube.com", "music.youtube.com"):
        if parsed.path == "/watch":
            result = parse_qs(parsed.query).get("v", [""])[0]
        elif len(parts) == 2 and parts[0] in ("shorts", "embed", "live"):
            result = parts[1]
        else:
            result = ""
    else:
        result = ""
    if not re.fullmatch(r"[A-Za-z0-9_-]{11}", result):
        raise ValueError("URL must identify one YouTube video, not a channel or playlist.")
    return result


def captions(identifier, languages):
    from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
    try:
        tracks = list(YouTubeTranscriptApi().list(identifier))
        def rank(track):
            language = track.language_code
            preference = next((i for i, code in enumerate(languages)
                               if language == code or language.startswith(code + "-")), len(languages))
            return preference, track.is_generated
        for track in sorted(tracks, key=rank):
            rows = [{"start": s.start, "duration": s.duration, "text": s.text}
                    for s in track.fetch() if s.text.strip()]
            if rows:
                return {"source": "automatic_captions" if track.is_generated else "human_captions",
                        "language": track.language_code, "segments": rows}
    except (TranscriptsDisabled, NoTranscriptFound) as exc:
        raise MissingCaptions(type(exc).__name__) from exc
    raise MissingCaptions("No nonempty caption tracks available")


def local_audio(identifier, model_name, model_dir, audio_parent=None):
    from yt_dlp import YoutubeDL
    from faster_whisper import WhisperModel
    with tempfile.TemporaryDirectory(prefix="audio-", dir=audio_parent) as temporary:
        options = {"format": "bestaudio", "noplaylist": True, "cachedir": False,
                   "outtmpl": str(Path(temporary) / "audio.%(ext)s"),
                   "quiet": True, "noprogress": True, "socket_timeout": 30,
                   "retries": 2, "fragment_retries": 2}
        with YoutubeDL(options) as downloader:
            url = "https://www.youtube.com/watch?v=" + identifier
            metadata = downloader.extract_info(url, download=False)
            if metadata.get("is_live") or metadata.get("live_status") in ("is_live", "is_upcoming"):
                raise RuntimeError("Audio fallback requires a completed video, not a live/upcoming broadcast.")
            downloaded = downloader.extract_info(url, download=True)
            audio_path = Path(downloader.prepare_filename(downloaded))
        if not audio_path.is_file():
            raise RuntimeError("Audio download did not produce the expected file.")
        print("Transcribing audio locally; this may take several minutes.", file=sys.stderr, flush=True)
        model = WhisperModel(model_name, device="cpu", compute_type="int8", download_root=str(model_dir))
        segments, info = model.transcribe(str(audio_path), beam_size=5, vad_filter=True)
        rows = [{"start": s.start, "duration": s.end - s.start, "text": s.text.strip()}
                for s in segments if s.text.strip()]
        if not rows:
            raise RuntimeError("Local transcription found no intelligible speech.")
        return {"source": "local_whisper", "model": model_name, "language": info.language,
                "title": metadata.get("title"), "segments": rows}


def retrieve(identifier, languages, model_name, model_dir, audio_parent=None):
    try:
        result = captions(identifier, languages)
    except MissingCaptions as exc:
        print("Captions absent; downloading temporary audio for local transcription.", file=sys.stderr, flush=True)
        result = local_audio(identifier, model_name, model_dir, audio_parent)
        result["fallback_reason"] = str(exc)
    return {"video_id": identifier, "url": "https://www.youtube.com/watch?v=" + identifier, **result}


def emit(result, page_size):
    if not page_size:
        print(json.dumps({**result, "complete": True}, ensure_ascii=False), flush=True)
        return
    rows = result["segments"]
    metadata = {k: v for k, v in result.items() if k != "segments"}
    for offset in range(0, len(rows), page_size):
        complete = offset + page_size >= len(rows)
        print(json.dumps({**metadata, "offset": offset, "total_segments": len(rows),
                          "segments": rows[offset:offset + page_size], "complete": complete},
                         ensure_ascii=False), flush=True)
        if not complete:
            print("Enter for next page; q to stop:", file=sys.stderr, flush=True)
            answer = sys.stdin.readline()
            if not answer or answer.strip().lower() == "q":
                print("Stopped before full transcript coverage.", file=sys.stderr)
                return


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url")
    parser.add_argument("--languages", nargs="+", default=["en"])
    parser.add_argument("--model", choices=["tiny", "base", "small", "medium", "large-v3"], default="small")
    parser.add_argument("--page-size", type=int, default=0)
    args = parser.parse_args()
    if args.page_size < 0:
        parser.error("--page-size must be nonnegative")
    model_dir = Path(__file__).resolve().parents[1] / ".runtime" / "models"
    try:
        result = retrieve(video_id(args.url), args.languages, args.model, model_dir)
        emit(result, args.page_size)
        return 0
    except KeyboardInterrupt:
        print("Interrupted; temporary audio cleaned up.", file=sys.stderr)
        return 130
    except Exception as exc:
        print(json.dumps({"error": type(exc).__name__, "message": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    def interrupt(signum, frame):
        raise KeyboardInterrupt
    signal.signal(signal.SIGTERM, interrupt)
    sys.exit(main())
