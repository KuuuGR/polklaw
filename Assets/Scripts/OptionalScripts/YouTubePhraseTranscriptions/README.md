# YouTube phrase -> URLs -> transcripts

One command that:

1. searches YouTube for a phrase with `yt-dlp`,
2. stores every found video URL in `video_urls.txt`,
3. downloads a transcript for every video and writes all of them to a single
   `transcriptions.txt` file.

This is a combined, updated version of the existing scripts:

- `Assets/Scripts/04 YouTubeChannelSearch.py` (collects YouTube URLs),
- `Assets/Scripts/06 ExtractYouTubeTranscriptions.py` and
  `Assets/Scripts/07 MultiprocessYouTubeTranscriptions.py` (downloads
  transcripts; those use the old `youtube_transcript_api` API and hardcode
  Polish).

## Installation

Python 3.9-3.14 is recommended (`youtube-transcript-api` does not support
Python 3.15 yet). On Python 3.15 the script still works by automatically
falling back to yt-dlp subtitle downloads or an Invidious instance.

Run from the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r Assets/Scripts/OptionalScripts/YouTubePhraseTranscriptions/requirements.txt
```

If `python3` points to Python 3.15, create the environment with an older
interpreter, for example:

```bash
python3.14 -m venv .venv
```

## Usage

Default run (search + transcripts; collects all search results):

```bash
python3 Assets/Scripts/OptionalScripts/YouTubePhraseTranscriptions/youtube_phrase_transcriptions.py "why prezi is so good"
```

Limit the number of videos and prefer English, then Polish transcripts:

```bash
python3 Assets/Scripts/OptionalScripts/YouTubePhraseTranscriptions/youtube_phrase_transcriptions.py \
  "why prezi is so good" --max-results 50 --languages en,pl
```

Only collect URLs:

```bash
python3 Assets/Scripts/OptionalScripts/YouTubePhraseTranscriptions/youtube_phrase_transcriptions.py \
  "why prezi is so good" --links-only
```

Only download transcripts using the previously saved URL list:

```bash
python3 Assets/Scripts/OptionalScripts/YouTubePhraseTranscriptions/youtube_phrase_transcriptions.py \
  "why prezi is so good" --transcripts-only
```

Use a custom URL list and output directory:

```bash
python3 Assets/Scripts/OptionalScripts/YouTubePhraseTranscriptions/youtube_phrase_transcriptions.py \
  --links-file my_links.txt --transcripts-only --output-dir data/output/my_run
```

Start from scratch instead of resuming:

```bash
python3 Assets/Scripts/OptionalScripts/YouTubePhraseTranscriptions/youtube_phrase_transcriptions.py \
  "why prezi is so good" --overwrite
```

If YouTube blocks this machine's IP (`429` / `IpBlocked`), use a public Piped
API or Invidious instance as a proxy. Piped is usually faster:

```bash
python3 Assets/Scripts/OptionalScripts/YouTubePhraseTranscriptions/youtube_phrase_transcriptions.py \
  "why prezi is so good" --transcripts-only \
  --backend piped --piped-instance https://api.piped.private.coffee
```

```bash
python3 Assets/Scripts/OptionalScripts/YouTubePhraseTranscriptions/youtube_phrase_transcriptions.py \
  "why prezi is so good" --transcripts-only \
  --backend invidious --invidious-instance https://yt.chocolatemoo53.com
```

You can also add `--piped-instance ...` and/or `--invidious-instance ...` to the
default `auto` backend, so the script tries the API first, then Piped, then
Invidious, then yt-dlp.

## Output

By default, files are written to:

```text
data/output/YouTubePhraseTranscriptions/<phrase-slug>/
├── video_urls.txt
├── transcriptions.txt
├── resume_file.txt
└── missing_transcripts.txt
```

- `video_urls.txt` - one video URL per line.
- `transcriptions.txt` - all transcripts in one file, in the format expected by
  `Assets/Scripts/09 extractAndRemoveDuplicates.py`:

  ```text
  URL: https://www.youtube.com/watch?v=XXXXXXXXXXX
  Transcription:
  first caption line
  second caption line
  ```

- `resume_file.txt` - successfully processed URLs; re-running the command skips
  them (unless `--overwrite` is used).
- `missing_transcripts.txt` - videos without an available transcript, with the
  reason returned by the transcript source.

## Options

| Option | Description |
| --- | --- |
| `phrase` | Search phrase (positional argument). |
| `--max-results N` | Maximum number of videos, `0` means all results (default: `0`). |
| `--languages en,pl` | Transcript language preference order (default: `en`). If none of the requested languages exists, the script falls back to any manually created transcript, then to any available transcript. |
| `--output-dir PATH` | Output directory. |
| `--links-file PATH` | Use an existing URL list instead of searching. |
| `--links-only` | Only collect URLs. |
| `--transcripts-only` | Only download transcripts from an existing URL list. |
| `--overwrite` | Delete previous links/transcripts and start fresh. |
| `--sleep SECONDS` | Delay between transcript requests (default: `1.0`). |
| `--retries N` | Retry attempts for rate-limited requests (default: `3`). |
| `--backend auto\|api\|piped\|invidious\|ytdlp` | Transcript source. `auto` (default) tries `youtube-transcript-api`, then Piped and Invidious (if configured), then yt-dlp subtitles. |
| `--piped-instance URL` | Piped API base URL used by `--backend piped` or as an `auto` fallback. Can also be set with `PIPED_INSTANCE`. |
| `--invidious-instance URL` | Invidious base URL used by `--backend invidious` or as an `auto` fallback. Can also be set with `INVIDIOUS_INSTANCE`. |

## Notes

- `youtube-transcript-api` supports both the old `0.6.x` API and the new `1.x`
  API. If it is missing, too old, or blocked, `--backend auto` falls back to a
  configured Piped/Invidious instance and then to downloading subtitles with
  `yt-dlp` (converting the VTT file to text).
- YouTube may block transcript requests coming from cloud/VPN IP addresses
  (`RequestBlocked` / `IpBlocked`). Such videos are listed in
  `missing_transcripts.txt`; re-running later may succeed. If three videos in a
  row are blocked, the script stops instead of hammering YouTube, and you can
  resume the same command later.
- When YouTube blocks the local IP, `--backend piped` or
  `--backend invidious` can fetch captions through a public proxy service.
  These are third-party services and may rate-limit, disappear, or not have
  every caption track. If a Piped instance starts returning HTTP 500
  `SignInConfirmNotBotException`, switch to `--backend invidious` or another
  instance.
- Age-restricted or region-restricted videos may have no transcript available
  without cookies/authentication.
- The search step collects public search results only; YouTube search does not
  return literally every video on the platform.
