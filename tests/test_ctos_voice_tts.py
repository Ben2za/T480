from __future__ import annotations

import importlib.machinery
import importlib.util
import io
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "ctos-voice"
LOADER = importlib.machinery.SourceFileLoader("ctos_voice_tts_test", str(SCRIPT))
SPEC = importlib.util.spec_from_loader(LOADER.name, LOADER)
assert SPEC is not None
VOICE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = VOICE
LOADER.exec_module(VOICE)


class PiperRenderTests(unittest.TestCase):
    def test_render_piper_wav_writes_without_playback(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            model = root / "voice.onnx"
            config = root / "voice.onnx.json"
            output = root / "answer.wav"
            model.write_bytes(b"model")
            config.write_text("{}", encoding="utf-8")

            def render(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
                self.assertEqual(kwargs["input"], "Bonjour depuis Piper.\n")
                target = Path(command[command.index("--output_file") + 1])
                target.write_bytes(b"RIFF" + (b"\0" * 36) + b"WAVE" + (b"\0" * 32))
                return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

            with (
                mock.patch.object(VOICE, "piper_binary", return_value="/usr/bin/piper"),
                mock.patch.object(VOICE, "PIPER_MODEL", model),
                mock.patch.object(VOICE, "PIPER_CONFIG", config),
                mock.patch.object(VOICE.subprocess, "run", side_effect=render) as run,
                mock.patch.object(VOICE, "play_wav") as play,
            ):
                rc = VOICE.render_piper_wav(" Bonjour   depuis Piper. ", output)

            self.assertEqual(rc, 0)
            self.assertGreater(output.stat().st_size, 44)
            run.assert_called_once()
            play.assert_not_called()

    def test_render_rejects_symlink_output(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "target.wav"
            target.write_bytes(b"keep")
            link = root / "link.wav"
            link.symlink_to(target)
            with (
                mock.patch.object(VOICE, "piper_binary", return_value="/usr/bin/piper"),
                mock.patch.object(VOICE, "PIPER_MODEL", target),
                mock.patch.object(VOICE, "PIPER_CONFIG", target),
                mock.patch.object(VOICE.subprocess, "run") as run,
            ):
                rc = VOICE.render_piper_wav("test", link)
            self.assertEqual(rc, 2)
            self.assertEqual(target.read_bytes(), b"keep")
            run.assert_not_called()

    def test_render_command_reads_text_from_stdin_not_argv(self) -> None:
        args = VOICE.argparse.Namespace(
            stdin=True,
            text=[],
            engine="piper",
            output="/tmp/test-browser-piper.wav",
        )
        with (
            mock.patch.object(VOICE.sys, "stdin", io.StringIO("Réponse locale")),
            mock.patch.object(VOICE, "render_piper_wav", return_value=0) as render,
        ):
            rc = VOICE.cmd_render_wav(args)
        self.assertEqual(rc, 0)
        render.assert_called_once_with("Réponse locale", Path("/tmp/test-browser-piper.wav"))


if __name__ == "__main__":
    unittest.main()
