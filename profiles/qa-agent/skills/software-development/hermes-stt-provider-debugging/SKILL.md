---
name: hermes-stt-provider-debugging
description: Debug Hermes voice transcription failures caused by provider/model mismatches between gateway callers and tools/transcription_tools.py.
triggers:
  - Hermes voice transcription fails
  - local whisper says invalid model size whisper-1
  - STT provider/model mismatch
  - gateway voice note transcription bug
---

# Hermes STT provider debugging

Use this when Hermes voice-note or Discord voice-channel transcription fails in the Hermes codebase, especially when the error mentions an invalid local Whisper model like `whisper-1`.

## Core lesson

Do not force a single global STT model from gateway code into `transcribe_audio()`.

`tools/transcription_tools.py` already contains provider-specific model selection logic:
- local/local_command -> `stt.local.model` or local defaults like `base`
- groq -> Groq model defaults
- openai -> OpenAI model defaults like `whisper-1`
- mistral -> Voxtral defaults

If gateway code passes a global `stt.model` override into `transcribe_audio(..., model=...)`, it can break local transcription by sending an API model name to a local backend.

## Symptoms

Common failure:
- `Local transcription failed: Invalid model size 'whisper-1'`

Likely cause:
- gateway caller reads `get_stt_model_from_config()`
- caller passes that value into `transcribe_audio(path, model=stt_model)`
- local provider receives OpenAI-only model name

## Investigation steps

1. Inspect the gateway caller paths:
   - `gateway/run.py` `_enrich_message_with_transcription()`
   - `gateway/platforms/discord.py` `_process_voice_input()`
2. Inspect `tools/transcription_tools.py`:
   - `transcribe_audio()`
   - `_get_provider()`
   - provider-specific branches for local/groq/openai/mistral
3. Confirm whether the caller is overriding model selection with `get_stt_model_from_config()`.
4. Verify whether the configured failing model belongs only to a cloud provider.

## Fix pattern

Prefer this:

```python
from tools.transcription_tools import transcribe_audio
result = await asyncio.to_thread(transcribe_audio, path)
```

Avoid this unless you are intentionally overriding the provider-specific model logic:

```python
from tools.transcription_tools import transcribe_audio, get_stt_model_from_config
stt_model = get_stt_model_from_config()
result = await asyncio.to_thread(transcribe_audio, path, model=stt_model)
```

## Why this works

`transcribe_audio()` already chooses the effective model after it knows the selected provider. Letting the tool own model selection prevents invalid cross-provider model names from leaking into local or alternative backends.

## Regression tests to add

### Gateway
In `tests/gateway/test_stt_config.py`, add a test that verifies `_enrich_message_with_transcription()` calls:

```python
transcribe_audio("/tmp/voice.ogg")
```

and not a forced `model=` override.

### Discord voice channel path
In `tests/gateway/test_voice_command.py`, assert that `_process_voice_input()` calls `transcribe_audio()` with only the WAV path and no extra model argument.

## Verification commands

Always activate the venv first:

```bash
source venv/bin/activate
python -m pytest tests/gateway/test_stt_config.py -q
python -m pytest tests/gateway/test_voice_command.py -q
```

For a smaller smoke test during iteration:

```bash
source venv/bin/activate
python -m pytest tests/gateway/test_stt_config.py tests/gateway/test_voice_command.py::TestDiscordVoiceChannelMethods::test_process_voice_input_success -q
```

## Pitfalls

- Do not assume `stt.model` is universally valid across providers.
- Do not “fix” local STT by translating `whisper-1` at the gateway layer; the right layer is `transcribe_audio()`.
- If a patch accidentally corrupts a large file, restore from git before reapplying a narrow edit.
- When running targeted tests, import errors or syntax errors elsewhere in the file can mask whether the STT fix actually worked.

## Success criteria

A good fix:
- removes gateway-level forced model overrides
- preserves provider-specific selection inside `transcribe_audio()`
- passes gateway STT tests
- passes Discord voice-command tests
- prevents local Whisper from receiving OpenAI-only model names
