import contextlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("analyze_youtube", Path(__file__).parents[1] / "scripts/analyze_youtube.py")
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)
ID = "dQw4w9WgXcQ"


class Tests(unittest.TestCase):
    def test_urls(self):
        for url in [f"https://youtu.be/{ID}?t=3", f"https://www.youtube.com/watch?v={ID}&list=foo",
                    f"youtube.com/shorts/{ID}", f"https://m.youtube.com/live/{ID}"]:
            self.assertEqual(tool.video_id(url), ID)
        for url in ["https://evil.com/watch?v=" + ID, "https://youtube.com/playlist?list=123",
                    "https://youtube.com.evil.com/watch?v=" + ID, "file://youtube.com/watch?v=" + ID]:
            with self.assertRaises(ValueError):
                tool.video_id(url)

    def test_fallback_only_for_absence(self):
        with patch.object(tool, "captions", side_effect=tool.MissingCaptions("empty")), \
             patch.object(tool, "local_audio", return_value={"segments": []}) as audio:
            result = tool.retrieve(ID, ["en"], "small", Path("unused"))
            audio.assert_called_once()
            self.assertEqual(result["fallback_reason"], "empty")
        with patch.object(tool, "captions", side_effect=RuntimeError("blocked")), \
             patch.object(tool, "local_audio") as audio:
            with self.assertRaisesRegex(RuntimeError, "blocked"):
                tool.retrieve(ID, ["en"], "small", Path("unused"))
            audio.assert_not_called()

    def test_caption_language_and_manual_preference(self):
        class Disabled(Exception): pass
        class NotFound(Exception): pass
        def track(language, generated, text):
            return types.SimpleNamespace(language_code=language, is_generated=generated,
                fetch=lambda: [types.SimpleNamespace(start=1, duration=2, text=text)])
        tracks = [track("es", False, "Spanish"), track("en", True, "auto"), track("en", False, "manual")]
        module = types.SimpleNamespace(YouTubeTranscriptApi=lambda: types.SimpleNamespace(list=lambda _: tracks),
                                       TranscriptsDisabled=Disabled, NoTranscriptFound=NotFound)
        with patch.dict(sys.modules, {"youtube_transcript_api": module}):
            self.assertEqual(tool.captions(ID, ["en"])["segments"][0]["text"], "manual")
            tracks[:] = [tracks[0]]
            self.assertEqual(tool.captions(ID, ["en"])["language"], "es")
            tracks.clear()
            with self.assertRaises(tool.MissingCaptions): tool.captions(ID, ["en"])

    def test_pagination_complete_and_quit(self):
        result = {"segments": [{"text": str(i)} for i in range(3)]}
        output = io.StringIO()
        with contextlib.redirect_stdout(output), patch("sys.stdin", io.StringIO("\n\n")):
            tool.emit(result, 1)
        pages = [json.loads(line) for line in output.getvalue().splitlines()]
        self.assertEqual([p["complete"] for p in pages], [False, False, True])
        output = io.StringIO()
        with contextlib.redirect_stdout(output), patch("sys.stdin", io.StringIO("q\n")):
            tool.emit(result, 1)
        self.assertFalse(json.loads(output.getvalue())["complete"])

    def test_audio_cleanup_on_success_and_failure(self):
        paths = []
        class Downloader:
            def __init__(self, options): self.path = Path(options["outtmpl"].replace("%(ext)s", "webm"))
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def extract_info(self, url, download):
                if download:
                    self.path.write_bytes(b"audio")
                    paths.append(self.path)
                return {"title": "test"}
            def prepare_filename(self, _): return str(self.path)
        class Model:
            def __init__(self, *args, **kwargs): pass
            def transcribe(self, path, **kwargs):
                return iter([types.SimpleNamespace(start=0, end=1, text="hello")]), types.SimpleNamespace(language="en")
        with patch.dict(sys.modules, {"yt_dlp": types.SimpleNamespace(YoutubeDL=Downloader),
                                     "faster_whisper": types.SimpleNamespace(WhisperModel=Model)}):
            self.assertEqual(tool.local_audio(ID, "small", Path("unused"))["segments"][0]["text"], "hello")
            self.assertFalse(paths[-1].parent.exists())
            with patch.object(Model, "transcribe", side_effect=RuntimeError("failed")):
                with self.assertRaises(RuntimeError): tool.local_audio(ID, "small", Path("unused"))
            self.assertFalse(paths[-1].parent.exists())


if __name__ == "__main__":
    unittest.main()
