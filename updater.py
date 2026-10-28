
"""GitHub Releases updater for SliderForge. Standard library only."""
import json, re, urllib.request, urllib.error, zipfile, hashlib
from pathlib import Path

VERSION="1.3.0"
APP_DIR=Path.home()/".sliderforge"
CONFIG=APP_DIR/"updates.json"
MAX_BYTES=100*1024*1024

def settings():
    try:
        return json.loads(CONFIG.read_text(encoding="utf-8"))
    except (OSError,ValueError):
        return {"repo":"Becksploder2/SliderForge","channel":"beta"}

def save_settings(repo,channel):
    repo=repo.strip().removeprefix("https://github.com/").strip("/")
    if repo.endswith(".git"):repo=repo[:-4]
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+",repo):
        raise ValueError("Enter owner/repository, e.g. yourname/SliderForge")
    if channel not in ("stable","beta"):raise ValueError("Invalid channel")
    APP_DIR.mkdir(exist_ok=True)
    CONFIG.write_text(json.dumps({"repo":repo,"channel":channel},indent=2),encoding="utf-8")

def version_tuple(v):
    m=re.search(r"(\d+)\.(\d+)\.(\d+)",v)
    if not m:raise ValueError("Release tag must include a version like v1.2.1")
    return tuple(map(int,m.groups()))

def _json(url):
    req=urllib.request.Request(url,headers={"User-Agent":"SliderForge-Updater/1.2","Accept":"application/vnd.github+json"})
    with urllib.request.urlopen(req,timeout=12) as r:
        return json.load(r)

def check():
    cfg=settings()
    repo=cfg.get("repo","")
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+",repo):
        raise ValueError("Configure a GitHub repository first.")
    endpoint=f"https://api.github.com/repos/{repo}/releases"
    releases=_json(endpoint+"?per_page=30")
    for release in releases:
        if release.get("draft") or (cfg.get("channel")=="stable" and release.get("prerelease")):continue
        try: newer=version_tuple(release["tag_name"])>version_tuple(VERSION)
        except (KeyError,ValueError):continue
        if not newer: return {"newer":False,"release":release,"asset":None}
        assets=[a for a in release.get("assets",[]) if a.get("name","").lower().endswith(".zip") and "sliderforge" in a.get("name","").lower()]
        if not assets: return {"newer":True,"release":release,"asset":None}
        return {"newer":True,"release":release,"asset":assets[0]}
    return {"newer":False,"release":None,"asset":None}

def download_asset(asset):
    name=asset["name"]
    if Path(name).name!=name or not name.lower().endswith(".zip"):raise ValueError("Invalid release filename")
    if asset.get("size",0)>MAX_BYTES:raise ValueError("Update exceeds 100 MB safety limit")
    url=asset["browser_download_url"]
    if not url.startswith("https://github.com/"):raise ValueError("Expected GitHub release download URL")
    directory=APP_DIR/"downloads";directory.mkdir(parents=True,exist_ok=True)
    target=directory/name
    temp=directory/(name+".partial")
    try:
        req=urllib.request.Request(url,headers={"User-Agent":"SliderForge-Updater/1.2"})
        with urllib.request.urlopen(req,timeout=30) as r, temp.open("wb") as out:
            size=0
            while True:
                chunk=r.read(65536)
                if not chunk:break
                size+=len(chunk)
                if size>MAX_BYTES:raise ValueError("Update exceeds 100 MB safety limit")
                out.write(chunk)
        with zipfile.ZipFile(temp) as z:
            if z.testzip() is not None:raise ValueError("Corrupt ZIP")
            for entry in z.infolist():
                path=Path(entry.filename.replace("\\","/"))
                if path.is_absolute() or ".." in path.parts:raise ValueError("Unsafe ZIP path")
        # GitHub asset digest when provided (sha256:hex)
        digest=asset.get("digest") or ""
        if digest.startswith("sha256:"):
            actual=hashlib.sha256(temp.read_bytes()).hexdigest()
            if actual.lower()!=digest[7:].lower():raise ValueError("SHA256 checksum mismatch")
        temp.replace(target)
        return target
    finally:
        temp.unlink(missing_ok=True)
