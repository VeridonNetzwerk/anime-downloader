#!/usr/bin/env python3
"""Native AniWatch downloader (no WSL, no bash script).

Designed for the local AniWatch UI server:
- fetch anime/episode metadata from local aniwatch-api
- resolve stream URL via episode servers/sources endpoints
- download with ffmpeg
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)


def info(msg: str) -> None:
    print(f"[INFO] {msg}")


def warn(msg: str) -> None:
    print(f"[WARN] {msg}")


def error(msg: str) -> None:
    print(f"[ERROR] {msg}", file=sys.stderr)


def sanitize_filename(name: str) -> str:
    clean = re.sub(r"[^\w\-.() ,@+#%&=]", "_", name, flags=re.ASCII)
    clean = re.sub(r"_+", "_", clean).strip(" ._")
    return clean or "unknown"


def api_get(base_url: str, path: str, params: dict[str, str] | None = None, referer: str | None = None) -> dict:
    base_url = base_url.rstrip("/")
    query = ""
    if params:
        query = "?" + urllib.parse.urlencode(params)
    url = f"{base_url}{path}{query}"

    headers = {
        "Accept": "application/json",
        "User-Agent": USER_AGENT,
    }
    if referer:
        headers["Referer"] = referer

    req = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
    except urllib.error.URLError as exc:
        raise RuntimeError(f"API request failed for {url}: {exc}") from exc

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Invalid JSON from {url}: {raw[:250]}") from exc

    if isinstance(payload, dict) and "data" in payload:
        return payload["data"]
    return payload


def choose_server(servers_data: dict, audio: str, preferred_keyword: str | None) -> tuple[str, str]:
    pool = servers_data.get(audio) or []
    chosen_audio = audio
    if not pool and audio == "dub":
        warn("No dub servers available; falling back to sub")
        pool = servers_data.get("sub") or []
        chosen_audio = "sub"

    if not pool:
        raise RuntimeError("No episode servers available")

    names: list[str] = []
    for item in pool:
        name = str(item.get("serverName") or "").strip()
        if name:
            names.append(name)

    if preferred_keyword:
        filtered = [n for n in names if preferred_keyword.lower() in n.lower()]
        if filtered:
            names = filtered

    if not names:
        raise RuntimeError("No usable server names found")

    def map_server(name: str) -> str | None:
        lc = name.lower()
        if lc in {"hd-1", "hd1", "vidstreaming"}:
            return "hd-1"
        if lc in {"hd-2", "hd2", "vidcloud", "megacloud", "rapidcloud"}:
            return "hd-2"
        return None

    for name in names:
        mapped = map_server(name)
        if mapped:
            return chosen_audio, mapped

    raise RuntimeError(f"No supported server found (hd-1/hd-2). Available: {', '.join(names)}")


def parse_episode_selection(selection: str, all_eps: list[dict]) -> list[dict]:
    if not all_eps:
        return []

    by_num: dict[str, dict] = {str(ep["number"]): ep for ep in all_eps if "number" in ep}
    numbers = sorted(by_num.keys(), key=lambda x: int(x))
    if not selection or selection.strip() == "*":
        return [by_num[n] for n in numbers]

    selection = selection.strip()
    if selection.lower().startswith("l") and selection[1:].isdigit():
        count = int(selection[1:])
        if count <= 0:
            return []
        return [by_num[n] for n in numbers[-count:]]

    picked: set[str] = set()
    for token in [t.strip() for t in selection.split(",") if t.strip()]:
        if "-" in token:
            a, b = token.split("-", 1)
            if a.isdigit() and b.isdigit():
                lo, hi = sorted((int(a), int(b)))
                for n in range(lo, hi + 1):
                    key = str(n)
                    if key in by_num:
                        picked.add(key)
            continue
        if token.isdigit() and token in by_num:
            picked.add(token)

    return [by_num[n] for n in numbers if n in picked]


def run_ffmpeg(video_url: str, referer: str, output_file: Path) -> None:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("ffmpeg not found in PATH")

    output_file.parent.mkdir(parents=True, exist_ok=True)
    headers = f"User-Agent: {USER_AGENT}\r\nReferer: {referer}\r\n"

    cmd = [
        ffmpeg,
        "-y",
        "-loglevel",
        "warning",
        "-headers",
        headers,
        "-i",
        video_url,
        "-c",
        "copy",
        str(output_file),
    ]
    res = subprocess.run(cmd)
    if res.returncode != 0:
        raise RuntimeError(f"ffmpeg exited with code {res.returncode}")


def download_subtitles(subs: list[dict], pref: str, output_base: Path, referer: str) -> None:
    if pref == "none" or not subs:
        return

    selected: list[dict] = []
    if pref == "all":
        selected = subs
    elif pref == "default":
        eng = [s for s in subs if "english" in str(s.get("lang", "")).lower()]
        selected = [eng[0] if eng else subs[0]]
    else:
        wanted = [x.strip().lower() for x in pref.split(",") if x.strip()]
        for w in wanted:
            for s in subs:
                lang = str(s.get("lang", "")).lower()
                if w in lang:
                    selected.append(s)
                    break

    seen = set()
    uniq: list[dict] = []
    for s in selected:
        url = str(s.get("url", ""))
        if not url or url in seen:
            continue
        seen.add(url)
        uniq.append(s)

    for sub in uniq:
        lang = sanitize_filename(str(sub.get("lang") or "sub"))
        url = str(sub.get("url") or "")
        if not url:
            continue
        out = output_base.with_suffix(f".{lang}.vtt")
        req = urllib.request.Request(
            url,
            headers={"User-Agent": USER_AGENT, "Referer": referer},
            method="GET",
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                out.write_bytes(resp.read())
            info(f"Subtitle saved: {out.name}")
        except Exception as exc:  # noqa: BLE001
            warn(f"Subtitle download failed ({lang}): {exc}")


def main() -> int:
    parser = argparse.ArgumentParser(description="AniWatch native downloader")
    parser.add_argument("--api-url", required=True)
    parser.add_argument("--anime-id", default="")
    parser.add_argument("--anime-name", default="")
    parser.add_argument("--episodes", default="*")
    parser.add_argument("--audio", default="sub", choices=["sub", "dub"])
    parser.add_argument("--resolution", default="")
    parser.add_argument("--server", default="")
    parser.add_argument("--subtitles", default="default")
    parser.add_argument("--threads", default="4")
    parser.add_argument("--output-dir", default="")
    parser.add_argument("--separate-langs", default="0")
    args = parser.parse_args()

    output_root = Path(args.output_dir or Path.home() / "Downloads" / "AniWatch")
    output_root.mkdir(parents=True, exist_ok=True)

    anime_id = args.anime_id.strip()
    anime_name = args.anime_name.strip()

    if not anime_id and not anime_name:
        raise RuntimeError("anime-id or anime-name is required")

    if not anime_id:
        info(f"Searching anime: {anime_name}")
        data = api_get(args.api_url, "/api/v2/hianime/search", {"q": anime_name})
        candidates = data.get("animes") or []
        if not candidates:
            raise RuntimeError(f"No anime found for query: {anime_name}")
        first = candidates[0]
        anime_id = str(first.get("id") or "").strip()
        anime_name = str(first.get("name") or anime_id)

    info_data = api_get(args.api_url, f"/api/v2/hianime/anime/{urllib.parse.quote(anime_id)}")
    anime_title = (
        ((info_data.get("anime") or {}).get("info") or {}).get("name")
        or anime_name
        or anime_id
    )
    anime_title = sanitize_filename(str(anime_title))

    eps_data = api_get(args.api_url, f"/api/v2/hianime/anime/{urllib.parse.quote(anime_id)}/episodes")
    episodes = eps_data.get("episodes") or []
    selected = parse_episode_selection(args.episodes, episodes)
    if not selected:
        raise RuntimeError("No episodes selected")

    info(f"Anime: {anime_title} ({anime_id})")
    info(f"Episodes selected: {len(selected)}")

    success = 0
    fail = 0

    for idx, ep in enumerate(selected, start=1):
        ep_num = str(ep.get("number"))
        ep_stream_id = str(ep.get("episodeId") or "")
        ep_title = sanitize_filename(str(ep.get("title") or f"Episode {ep_num}"))
        if not ep_stream_id:
            warn(f"Episode {ep_num}: missing stream id")
            fail += 1
            continue

        info(f"[{idx}/{len(selected)}] Resolving episode {ep_num}: {ep_title}")

        try:
            servers = api_get(
                args.api_url,
                "/api/v2/hianime/episode/servers",
                {"animeEpisodeId": ep_stream_id},
            )
            audio_cat, server = choose_server(servers, args.audio, args.server or None)
            sources = api_get(
                args.api_url,
                "/api/v2/hianime/episode/sources",
                {
                    "animeEpisodeId": ep_stream_id,
                    "server": server,
                    "category": audio_cat,
                },
                referer="https://megacloud.blog/",
            )

            src_list = sources.get("sources") or []
            if not src_list:
                raise RuntimeError("No sources returned")
            first_src = src_list[0]
            video_url = str(first_src.get("url") or "").strip()
            if not video_url:
                raise RuntimeError("Empty video URL")

            referer = str((sources.get("headers") or {}).get("Referer") or "https://megacloud.blog/")
            tracks = [t for t in (sources.get("tracks") or []) if str(t.get("lang", "")).lower() != "thumbnails"]

            lang_dir = f"english-{audio_cat}" if str(args.separate_langs) == "1" else ""
            target_dir = output_root / lang_dir / anime_title if lang_dir else output_root / anime_title
            out_file = target_dir / f"Episode_{int(ep_num):02d}_{ep_title}.mp4"

            if out_file.exists():
                info(f"Episode {ep_num} already exists: {out_file.name}")
                success += 1
                continue

            run_ffmpeg(video_url, referer, out_file)
            download_subtitles(tracks, args.subtitles, out_file.with_suffix(""), referer)
            info(f"Downloaded episode {ep_num}: {out_file}")
            success += 1
        except Exception as exc:  # noqa: BLE001
            error(f"Episode {ep_num} failed: {exc}")
            fail += 1

    info(f"Done. success={success} failed={fail}")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
