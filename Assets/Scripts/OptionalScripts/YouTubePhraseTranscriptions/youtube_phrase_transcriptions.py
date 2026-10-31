#!/usr/bin/env python3
"""
Search YouTube for a phrase, save every found video URL and download the
transcripts into a single text file.

Examples:
    python3 youtube_phrase_transcriptions.py "why prezi is so good"
    python3 youtube_phrase_transcriptions.py "why prezi is so good" --languages en,pl
    python3 youtube_phrase_transcriptions.py --links-only "why prezi is so good"
    python3 youtube_phrase_transcriptions.py --transcripts-only "why prezi is so good"
    python3 youtube_phrase_transcriptions.py --links-file video_urls.txt --transcripts-only

Default output (run from the repository root):
    data/output/YouTubePhraseTranscriptions/<phrase-slug>/video_urls.txt
    data/output/YouTubePhraseTranscriptions/<phrase-slug>/transcriptions.txt
    data/output/YouTubePhraseTranscriptions/<phrase-slug>/resume_file.txt
    data/output/YouTubePhraseTranscriptions/<phrase-slug>/missing_transcripts.txt

transcriptions.txt keeps the same block format as the rest of the repository,
so it can be deduplicated later with
Assets/Scripts/09 extractAndRemoveDuplicates.py:

    URL: https://www.youtube.com/watch?v=XXXXXXXXXXX
    Transcription:
    line 1
    line 2

Requirements:
    pip install -r requirements.txt
"""

import argparse
import glob
import html
import json
import os
import re
import shutil
import socket
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

DEFAULT_OUTPUT_ROOT = os.path.join("data", "output", "YouTubePhraseTranscriptions")
DEFAULT_LANGUAGES = "en"
DEFAULT_HTTP_TIMEOUT = 30
MAX_ERROR_LENGTH = 500

# Errors which will not disappear after a retry (video simply has no transcript).
NON_RETRYABLE_ERRORS = {
    "AgeRestricted",
    "InvalidVideoId",
    "NoTranscriptFound",
    "TranscriptsDisabled",
    "VideoUnavailable",
}


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description=(
            "Collect YouTube video URLs for a search phrase and download "
            "their transcripts into one text file."
        )
    )
    parser.add_argument(
        "phrase",
        nargs="?",
        help='Search phrase, e.g. "why prezi is so good".',
    )
    parser.add_argument(
        "--max-results",
        type=int,
        default=0,
        help="Maximum number of videos to collect (0 = all results, default: 0).",
    )
    parser.add_argument(
        "--languages",
        default=DEFAULT_LANGUAGES,
        help=(
            "Comma-separated language preference order, "
            f"e.g. en,pl (default: {DEFAULT_LANGUAGES})."
        ),
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help=f"Output directory (default: {DEFAULT_OUTPUT_ROOT}/<phrase-slug>).",
    )
    parser.add_argument(
        "--links-file",
        default=None,
        help="Existing URL list to use instead of searching YouTube.",
    )
    parser.add_argument(
        "--links-only",
        action="store_true",
        help="Only collect video URLs, do not download transcripts.",
    )
    parser.add_argument(
        "--transcripts-only",
        action="store_true",
        help="Only download transcripts from an existing links file.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite previously collected links/transcripts instead of resuming.",
    )
    parser.add_argument(
        "--sleep",
        type=float,
        default=1.0,
        help="Seconds to wait between transcript requests (default: 1.0).",
    )
    parser.add_argument(
        "--retries",
        type=int,
        default=3,
        help="Number of attempts per video when YouTube rate-limits (default: 3).",
    )
    parser.add_argument(
        "--backend",
        choices=("auto", "api", "piped", "invidious", "ytdlp"),
        default="auto",
        help=(
            "Transcript backend: 'api' = youtube-transcript-api, "
            "'piped' = public Piped API, 'invidious' = public Invidious "
            "instance, 'ytdlp' = yt-dlp subtitles, 'auto' tries api, then "
            "Piped/Invidious (if configured), then yt-dlp (default: auto)."
        ),
    )
    parser.add_argument(
        "--piped-instance",
        default=os.environ.get("PIPED_INSTANCE"),
        help=(
            "Piped API base URL, e.g. https://api.piped.private.coffee. "
            "Used by --backend piped and as an auto fallback. "
            "Can also be set with PIPED_INSTANCE."
        ),
    )
    parser.add_argument(
        "--invidious-instance",
        default=os.environ.get("INVIDIOUS_INSTANCE"),
        help=(
            "Invidious base URL, e.g. https://yt.chocolatemoo53.com. "
            "Used by --backend invidious and as an auto fallback. "
            "Can also be set with INVIDIOUS_INSTANCE."
        ),
    )
    args = parser.parse_args(argv)

    if args.links_only and args.transcripts_only:
        parser.error("--links-only and --transcripts-only cannot be used together.")
    if not args.phrase and not args.links_file:
        parser.error("provide a search phrase or --links-file.")
    if args.max_results < 0:
        parser.error("--max-results must be >= 0.")
    if args.retries < 1:
        parser.error("--retries must be >= 1.")
    if args.backend == "invidious" and not args.invidious_instance:
        parser.error("--backend invidious requires --invidious-instance.")
    if args.backend == "piped" and not args.piped_instance:
        parser.error("--backend piped requires --piped-instance.")
    return args


def _short_error(exc, limit=MAX_ERROR_LENGTH):
    """Return a one-line, length-limited error description."""
    text = " ".join(str(exc).split())
    if len(text) > limit:
        text = text[:limit] + "..."
    return "%s: %s" % (exc.__class__.__name__, text)


def slugify(text):
    """Create a filesystem-safe, human-readable directory name."""
    slug = re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")
    return slug[:80] or "search"


def ensure_parent_dir(path):
    parent = os.path.dirname(os.path.abspath(path))
    os.makedirs(parent, exist_ok=True)


def read_urls(path):
    """
    Read URLs from a plain list or from the format produced by
    Assets/Scripts/04 YouTubeChannelSearch.py (which adds "Search Query:" lines).
    """
    urls = []
    with open(path, "r", encoding="utf-8") as file:
        for raw_line in file:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            match = re.search(r"https?://\S+", line)
            if match:
                urls.append(match.group(0))
            elif not re.search(r"\s", line):
                urls.append(line)
    return urls


def write_urls(path, urls):
    ensure_parent_dir(path)
    with open(path, "w", encoding="utf-8") as file:
        for url in urls:
            file.write(url + "\n")


def collect_video_urls(phrase, max_results=0):
    """Search YouTube with yt-dlp and return unique video URLs."""
    try:
        import yt_dlp
    except ImportError:
        raise RuntimeError(
            "Missing dependency 'yt-dlp'. Install it with:\n"
            "    pip install -r requirements.txt"
        )

    if max_results == 0:
        search_target = "ytsearchall:" + phrase
    else:
        search_target = "ytsearch%d:%s" % (max_results, phrase)

    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": "in_playlist",
        "skip_download": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(search_target, download=False)
    except Exception as exc:
        raise RuntimeError("YouTube search failed: %s" % exc)

    entries = (info or {}).get("entries") or []
    urls = []
    seen_ids = set()

    for entry in entries:
        if not entry:
            continue
        video_id = entry.get("id")
        if not video_id:
            video_id = extract_video_id(entry.get("url") or "")
        if not video_id or video_id in seen_ids:
            continue
        seen_ids.add(video_id)
        urls.append("https://www.youtube.com/watch?v=%s" % video_id)

    return urls


def extract_video_id(url):
    """Extract an 11-character YouTube video id from common URL formats."""
    match = re.search(
        r"(?:v=|youtu\.be/|/shorts/|/embed/|/live/)([0-9A-Za-z_-]{11})",
        url,
    )
    return match.group(1) if match else None


def _pick_transcript(transcript_list, languages):
    """Prefer requested languages, then any manually created transcript."""
    try:
        return transcript_list.find_transcript(languages)
    except Exception:
        pass

    transcripts = list(transcript_list)
    if not transcripts:
        raise RuntimeError("no transcripts available")
    for transcript in transcripts:
        if not getattr(transcript, "is_generated", False):
            return transcript
    return transcripts[0]


def _snippets_to_text(fetched):
    snippets = getattr(fetched, "snippets", fetched)
    lines = []
    for snippet in snippets:
        if isinstance(snippet, dict):
            text = snippet.get("text", "")
        else:
            text = getattr(snippet, "text", "")
        if text:
            lines.append(text.strip())
    return "\n".join(line for line in lines if line)


def _fetch_transcript_api(video_id, languages):
    """
    Fetch one transcript with youtube-transcript-api and return
    (text, language_code). Supports 0.6.x and 1.x.
    """
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
    except ImportError:
        raise RuntimeError(
            "Missing dependency 'youtube-transcript-api'. Install it with:\n"
            "    pip install -r requirements.txt"
        )

    if hasattr(YouTubeTranscriptApi, "get_transcript"):
        # youtube-transcript-api < 1.0
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        transcript = _pick_transcript(transcript_list, languages)
        fetched = transcript.fetch()
    else:
        # youtube-transcript-api >= 1.0
        api = YouTubeTranscriptApi()
        transcript_list = api.list(video_id)
        transcript = _pick_transcript(transcript_list, languages)
        fetched = transcript.fetch()

    text = _snippets_to_text(fetched)
    if not text.strip():
        raise RuntimeError("empty transcript")
    return text, getattr(transcript, "language_code", "")


def _pick_ytdlp_subtitle_language(info, languages):
    """Choose a subtitle key from yt-dlp metadata and report if it is automatic."""
    sources = (
        (info.get("subtitles") or {}, False),
        (info.get("automatic_captions") or {}, True),
    )

    for preferred in languages:
        for available, is_automatic in sources:
            if preferred in available:
                return preferred, is_automatic
        for available, is_automatic in sources:
            for key in available:
                if key.startswith(preferred + "-") or key.startswith(preferred + "_"):
                    return key, is_automatic

    for available, is_automatic in sources:
        if available:
            return next(iter(available)), is_automatic

    raise RuntimeError("no subtitles available")


def _invidious_base_url(instance):
    base = (instance or "").strip().rstrip("/")
    if not base:
        raise RuntimeError(
            "Invidious backend requires --invidious-instance "
            "(e.g. https://yt.chocolatemoo53.com)."
        )
    if not base.startswith(("http://", "https://")):
        base = "https://" + base
    return base


def _http_get_text(url, timeout=DEFAULT_HTTP_TIMEOUT):
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/131.0.0.0 Safari/537.36"
            )
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        raise RuntimeError("HTTP %s for %s" % (exc.code, url))
    except urllib.error.URLError as exc:
        raise RuntimeError("request failed for %s: %s" % (url, exc.reason))


def _pick_invidious_caption(captions, languages):
    by_code = {}
    for caption in captions:
        code = (caption.get("languageCode") or "").strip()
        if code:
            by_code.setdefault(code, caption)

    for preferred in languages:
        if preferred in by_code:
            return preferred, by_code[preferred]
    for preferred in languages:
        for code, caption in by_code.items():
            if code.startswith(preferred + "-") or code.startswith(preferred + "_"):
                return code, caption

    if by_code:
        code = sorted(by_code)[0]
        return code, by_code[code]

    raise RuntimeError("no captions available on Invidious")


def _fetch_transcript_invidious(video_id, languages, instance):
    """
    Fetch captions through an Invidious instance. Useful when YouTube blocks
    this machine's IP but another server can still reach the timedtext API.
    """
    base = _invidious_base_url(instance)
    list_url = "%s/api/v1/captions/%s" % (
        base,
        urllib.parse.quote(video_id, safe=""),
    )

    try:
        payload = json.loads(_http_get_text(list_url))
    except json.JSONDecodeError:
        raise RuntimeError("Invidious returned invalid JSON for %s" % video_id)

    captions = payload.get("captions") or []
    if not captions:
        raise RuntimeError("no captions available on Invidious")

    language, caption = _pick_invidious_caption(captions, languages)
    label = caption.get("label") or language
    candidate_urls = [
        "%s/api/v1/captions/%s?%s"
        % (
            base,
            urllib.parse.quote(video_id, safe=""),
            urllib.parse.urlencode({"label": label}),
        )
    ]
    if language:
        candidate_urls.append(
            "%s/api/v1/captions/%s?%s"
            % (
                base,
                urllib.parse.quote(video_id, safe=""),
                urllib.parse.urlencode({"lang": language}),
            )
        )

    content = None
    last_error = None
    for vtt_url in candidate_urls:
        try:
            candidate = _http_get_text(vtt_url)
        except RuntimeError as exc:
            last_error = exc
            continue
        if candidate.lstrip("\ufeff \t\r\n").startswith("WEBVTT"):
            content = candidate
            break
        last_error = RuntimeError(
            "Invidious did not return WebVTT for %s" % video_id
        )

    if content is None:
        raise last_error or RuntimeError("Invidious returned no captions")

    text = _vtt_text_to_text(content)
    if not text.strip():
        raise RuntimeError("empty transcript")
    return text, language


def _piped_base_url(instance):
    base = (instance or "").strip().rstrip("/")
    if not base:
        raise RuntimeError(
            "Piped backend requires --piped-instance "
            "(e.g. https://api.piped.private.coffee)."
        )
    if not base.startswith(("http://", "https://")):
        base = "https://" + base
    return base


def _pick_piped_caption(captions, languages):
    by_code = {}
    for caption in captions:
        code = (caption.get("code") or "").strip()
        if code:
            by_code.setdefault(code, []).append(caption)

    for preferred in languages:
        candidates = list(by_code.get(preferred, []))
        for code, items in by_code.items():
            if code.startswith(preferred + "-") or code.startswith(preferred + "_"):
                candidates.extend(items)
        if candidates:
            for caption in candidates:
                if not caption.get("autoGenerated"):
                    return caption
            return candidates[0]

    for caption in captions:
        if caption.get("code"):
            return caption

    raise RuntimeError("no captions available on Piped")


def _ttml_to_text(content):
    """Convert Piped's TTML subtitle content to plain text."""
    content = re.sub(r"<br\s*/?>", "\n", content, flags=re.IGNORECASE)
    try:
        root = ET.fromstring(content)
    except ET.ParseError:
        text = re.sub(r"<[^>]+>", " ", content)
        return "\n".join(
            line
            for line in (html.unescape(text).replace("\xa0", " ").splitlines())
            if line.strip()
        )

    paragraphs = []
    for element in root.iter():
        if element.tag.rsplit("}", 1)[-1] != "p":
            continue
        text = " ".join("".join(element.itertext()).split())
        if text and (not paragraphs or paragraphs[-1] != text):
            paragraphs.append(text)
    return "\n".join(paragraphs)


def _fetch_transcript_piped(video_id, languages, instance):
    """Fetch captions through a Piped API instance (uses Piped's timedtext proxy)."""
    base = _piped_base_url(instance)
    stream_url = "%s/streams/%s" % (base, urllib.parse.quote(video_id, safe=""))

    try:
        payload = json.loads(_http_get_text(stream_url))
    except json.JSONDecodeError:
        raise RuntimeError("Piped returned invalid JSON for %s" % video_id)

    captions = payload.get("subtitles") or []
    if not captions:
        raise RuntimeError("no captions available on Piped")

    caption = _pick_piped_caption(captions, languages)
    language = caption.get("code") or ""
    subtitle_url = caption.get("url")
    if not subtitle_url:
        raise RuntimeError("Piped did not provide a subtitle URL")

    content = _http_get_text(subtitle_url)
    text = _ttml_to_text(content)
    if not text.strip():
        raise RuntimeError("empty transcript")
    return text, language


def _vtt_text_to_text(content):
    """Convert WebVTT content to plain text."""
    timestamp = re.compile(r"^\d{2}:\d{2}:\d{2}[.,]\d{3}\s+-->")
    tag = re.compile(r"<[^>]+>")
    lines = []

    for raw_line in content.splitlines():
        line = raw_line.strip().lstrip("\ufeff")
        if not line or line.isdigit():
            continue
        if line == "WEBVTT" or line.startswith(
            ("NOTE", "Kind:", "Language:", "STYLE", "REGION")
        ):
            continue
        if timestamp.match(line):
            continue
        line = html.unescape(tag.sub("", line)).replace("\xa0", " ").strip()
        if line and (not lines or lines[-1] != line):
            lines.append(line)

    return "\n".join(lines)


def _vtt_to_text(path):
    """Convert a WebVTT subtitle file to plain text."""
    with open(path, "r", encoding="utf-8-sig", errors="replace") as file:
        return _vtt_text_to_text(file.read())


def _fetch_transcript_ytdlp(video_id, languages):
    """
    Fallback backend: download subtitles with yt-dlp and parse the VTT file.
    Works on Python versions where youtube-transcript-api 1.x is unavailable.
    """
    try:
        import yt_dlp
    except ImportError:
        raise RuntimeError(
            "Missing dependency 'yt-dlp'. Install it with:\n"
            "    pip install -r requirements.txt"
        )

    url = "https://www.youtube.com/watch?v=%s" % video_id
    probe_opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "socket_timeout": DEFAULT_HTTP_TIMEOUT,
    }

    with yt_dlp.YoutubeDL(probe_opts) as ydl:
        info = ydl.extract_info(url, download=False)

    language, is_automatic = _pick_ytdlp_subtitle_language(info, languages)
    temp_dir = tempfile.mkdtemp(prefix="yt_transcript_")

    try:
        download_opts = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
            "writesubtitles": not is_automatic,
            "writeautomaticsub": is_automatic,
            "subtitleslangs": [language],
            "subtitlesformat": "vtt",
            "outtmpl": os.path.join(temp_dir, "%(id)s.%(ext)s"),
            "overwrites": True,
            "retries": 2,
            "socket_timeout": DEFAULT_HTTP_TIMEOUT,
        }
        with yt_dlp.YoutubeDL(download_opts) as ydl:
            ydl.download([url])

        files = glob.glob(os.path.join(temp_dir, "*.vtt"))
        if not files:
            raise RuntimeError("yt-dlp did not write a subtitle file")

        preferred = [f for f in files if f.endswith(".%s.vtt" % language)]
        text = _vtt_to_text((preferred or files)[0])
        if not text.strip():
            raise RuntimeError("empty transcript")
        return text, language
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def fetch_transcript(
    video_id,
    languages,
    backend="auto",
    invidious_instance=None,
    piped_instance=None,
):
    """Fetch a transcript using the selected backend (auto/api/piped/invidious/ytdlp)."""
    api_error = None
    piped_error = None
    invidious_error = None

    if backend == "invidious":
        return _fetch_transcript_invidious(video_id, languages, invidious_instance)
    if backend == "piped":
        return _fetch_transcript_piped(video_id, languages, piped_instance)

    if backend in ("auto", "api"):
        try:
            return _fetch_transcript_api(video_id, languages)
        except Exception as exc:
            if backend == "api":
                raise
            api_error = exc

    if (
        backend == "auto"
        and api_error.__class__.__name__ in NON_RETRYABLE_ERRORS
        and not piped_instance
        and not invidious_instance
    ):
        raise api_error

    if backend == "auto" and piped_instance:
        try:
            return _fetch_transcript_piped(video_id, languages, piped_instance)
        except Exception as exc:
            piped_error = exc

    if backend == "auto" and invidious_instance:
        try:
            return _fetch_transcript_invidious(video_id, languages, invidious_instance)
        except Exception as exc:
            invidious_error = exc

    try:
        return _fetch_transcript_ytdlp(video_id, languages)
    except Exception as exc:
        if backend == "ytdlp":
            raise
        parts = ["youtube-transcript-api failed (%s)" % _short_error(api_error, 160)]
        if piped_error is not None:
            parts.append("Piped failed (%s)" % _short_error(piped_error, 160))
        if invidious_error is not None:
            parts.append("Invidious failed (%s)" % _short_error(invidious_error, 160))
        parts.append("yt-dlp failed (%s)" % _short_error(exc, 160))
        raise RuntimeError("; ".join(parts))


def fetch_transcript_with_retry(
    video_id,
    languages,
    retries,
    sleep,
    backend="auto",
    invidious_instance=None,
    piped_instance=None,
):
    last_error = None
    for attempt in range(1, retries + 1):
        try:
            return fetch_transcript(
                video_id,
                languages,
                backend,
                invidious_instance=invidious_instance,
                piped_instance=piped_instance,
            )
        except Exception as exc:
            last_error = exc
            if (
                exc.__class__.__name__ in NON_RETRYABLE_ERRORS
                or "no subtitles available" in str(exc)
                or "no captions available" in str(exc)
                or attempt >= retries
            ):
                break
            wait = max(sleep, 1.0) * attempt
            print(
                "    retry %d/%d in %.1fs (%s)"
                % (attempt, retries - 1, wait, _short_error(exc, 300))
            )
            time.sleep(wait)
    raise last_error


def save_transcripts(
    urls,
    output_file,
    resume_file,
    missing_file,
    languages,
    sleep,
    retries,
    backend="auto",
    invidious_instance=None,
    piped_instance=None,
):
    """Download transcripts for urls and append them to output_file."""
    ensure_parent_dir(output_file)
    ensure_parent_dir(resume_file)
    ensure_parent_dir(missing_file)

    processed = set()
    if os.path.exists(resume_file):
        processed = set(read_urls(resume_file))

    pending = [url for url in urls if url not in processed]
    total = len(pending)
    saved = 0
    failed = 0
    consecutive_blocks = 0

    print("Videos to process: %d (already done: %d)" % (total, len(processed)))

    with open(output_file, "a", encoding="utf-8") as out_file, open(
        resume_file, "a", encoding="utf-8"
    ) as resume_out, open(missing_file, "a", encoding="utf-8") as missing_out:
        for index, url in enumerate(pending, start=1):
            video_id = extract_video_id(url)
            if not video_id:
                print("[%d/%d] invalid URL: %s" % (index, total, url))
                missing_out.write("%s\tinvalid URL\n" % url)
                missing_out.flush()
                failed += 1
                continue

            print("[%d/%d] %s" % (index, total, url))
            try:
                text, language = fetch_transcript_with_retry(
                    video_id,
                    languages,
                    retries,
                    sleep,
                    backend,
                    invidious_instance=invidious_instance,
                    piped_instance=piped_instance,
                )
                if not text:
                    raise RuntimeError("empty transcript")

                out_file.write("URL: %s\nTranscription:\n%s\n\n" % (url, text))
                out_file.flush()

                resume_out.write(url + "\n")
                resume_out.flush()
                saved += 1
                print("    saved (language: %s)" % (language or "unknown"))
            except Exception as exc:
                failed += 1
                message = _short_error(exc)
                print("    no transcript (%s)" % message)
                missing_out.write("%s\t%s\n" % (url, message))
                missing_out.flush()

                is_block = (
                    exc.__class__.__name__ in ("IpBlocked", "RequestBlocked")
                    or "429" in message
                    or "Too Many Requests" in message
                )
                consecutive_blocks = consecutive_blocks + 1 if is_block else 0
                if consecutive_blocks >= 3:
                    print(
                        "\nYouTube is rate-limiting this IP (429/IpBlocked). "
                        "Stopping so the script does not hammer the API.\n"
                        "Re-run the same command later to resume from %s."
                        % resume_file
                    )
                    break

            if sleep and index < total:
                time.sleep(sleep)

    print(
        "\nDone. Saved: %d, failed/skipped: %d, output: %s"
        % (saved, failed, output_file)
    )
    if failed:
        print("Details about skipped videos: %s" % missing_file)
    return saved, failed


def resolve_output_dir(args):
    if args.output_dir:
        return args.output_dir
    if args.phrase:
        return os.path.join(DEFAULT_OUTPUT_ROOT, slugify(args.phrase))
    return os.path.dirname(os.path.abspath(args.links_file))


def main(argv=None):
    args = parse_args(argv)
    socket.setdefaulttimeout(DEFAULT_HTTP_TIMEOUT)
    languages = [
        language.strip()
        for language in args.languages.split(",")
        if language.strip()
    ]
    if not languages:
        languages = [DEFAULT_LANGUAGES]

    output_dir = resolve_output_dir(args)
    links_file = args.links_file or os.path.join(output_dir, "video_urls.txt")
    transcripts_file = os.path.join(output_dir, "transcriptions.txt")
    resume_file = os.path.join(output_dir, "resume_file.txt")
    missing_file = os.path.join(output_dir, "missing_transcripts.txt")

    run_search = not args.transcripts_only
    run_transcripts = not args.links_only

    if args.overwrite and run_search:
        if os.path.exists(links_file):
            os.remove(links_file)
    if args.overwrite and run_transcripts:
        for path in (transcripts_file, resume_file, missing_file):
            if os.path.exists(path):
                os.remove(path)

    urls = []
    if run_search:
        print('Searching YouTube for: "%s"' % args.phrase)
        urls = collect_video_urls(args.phrase, args.max_results)
        if not urls:
            print("No videos found.")
            return 1
        write_urls(links_file, urls)
        print("Found %d unique video URLs." % len(urls))
        print("Saved URLs to: %s" % links_file)
    else:
        if not os.path.exists(links_file):
            print("Links file not found: %s" % links_file)
            return 1
        urls = read_urls(links_file)
        print("Loaded %d URLs from: %s" % (len(urls), links_file))

    if not run_transcripts:
        return 0

    if not urls:
        print("No URLs to process.")
        return 1

    print("Transcript language preference: %s" % ", ".join(languages))
    print("Transcript backend: %s" % args.backend)
    if args.piped_instance:
        print("Piped instance: %s" % args.piped_instance)
    if args.invidious_instance:
        print("Invidious instance: %s" % args.invidious_instance)
    print("Output file: %s\n" % transcripts_file)
    save_transcripts(
        urls=urls,
        output_file=transcripts_file,
        resume_file=resume_file,
        missing_file=missing_file,
        languages=languages,
        sleep=args.sleep,
        retries=args.retries,
        backend=args.backend,
        invidious_instance=args.invidious_instance,
        piped_instance=args.piped_instance,
    )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nInterrupted. Run the same command again to resume.")
        sys.exit(130)
    except RuntimeError as exc:
        print("Error: %s" % exc)
        sys.exit(1)

