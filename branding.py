"""Per-game team branding: locally imported images, no bundled third-party marks."""
import hashlib, json, shutil
from pathlib import Path
from tkinter import PhotoImage
ROOT=Path.home()/".sliderforge"/"branding"
INDEX=ROOT/"index.json"
STADIUMS={
"Texas Tech":"Jones AT&T Stadium","East Carolina":"Dowdy–Ficklen Stadium",
"Texas":"Darrell K Royal–Texas Memorial Stadium","Texas A&M":"Kyle Field",
"Baylor":"McLane Stadium","TCU":"Amon G. Carter Stadium",
"SMU":"Gerald J. Ford Stadium","Houston":"TDECU Stadium",
"Notre Dame":"Notre Dame Stadium","Ohio State":"Ohio Stadium",
"Michigan":"Michigan Stadium","Penn State":"Beaver Stadium",
"Alabama":"Bryant–Denny Stadium","Georgia":"Sanford Stadium",
"Tennessee":"Neyland Stadium","LSU":"Tiger Stadium",
"Florida":"Ben Hill Griffin Stadium","Oklahoma":"Gaylord Family–Oklahoma Memorial Stadium",
"USC":"Los Angeles Memorial Coliseum","UCLA":"Rose Bowl",
"Boise State":"Albertsons Stadium","UTSA":"Alamodome",
"Charlotte":"Jerry Richardson Stadium","North Texas":"DATCU Stadium"
}
def is_custom_team(team):
 return team.startswith("TeamBuilder") or team.startswith("Custom:") or team not in OFFICIAL
# official roster loaded by app during startup; unknown names treated as custom
OFFICIAL=set()
def stadium_label(team,game):
 if game.startswith("College Football"):
  if is_custom_team(team):return "Generic Stadium • import a TeamBuilder stadium screenshot"
  return STADIUMS.get(team,"Home Stadium • import a photo")
 return "Home venue • import a photo"
def initials(team):
 words=[w for w in team.split() if w.lower() not in ("teambuilder","team","custom")]
 return "".join(w[0] for w in words[:3]).upper() or "SF"
def _read():
 try:return json.loads(INDEX.read_text(encoding="utf-8"))
 except (OSError,ValueError):return {}
def _key(game,team):return game+"|"+team
def get_asset(game,team,kind):
 name=_read().get(_key(game,team),{}).get(kind)
 if not name:return None
 path=ROOT/name
 return path if path.is_file() else None
def store_asset(game,team,kind,source):
 if kind not in ("logo","stadium"):raise ValueError("Invalid asset type")
 src=Path(source)
 if src.suffix.lower() not in (".png",".jpg",".jpeg",".webp"):raise ValueError("Unsupported image format")
 if src.stat().st_size>15*1024*1024:raise ValueError("Image exceeds 15 MB")
 try:
  from PIL import Image
  with Image.open(src) as im:
   im.verify()
 except ImportError:
  if src.suffix.lower()!=".png":raise ValueError("Install Pillow for JPG/WEBP images, or import PNG")
 except Exception as e:raise ValueError("Invalid image: "+str(e))
 ROOT.mkdir(parents=True,exist_ok=True)
 name=hashlib.sha256(_key(game,team).encode()).hexdigest()[:20]+"_"+kind+src.suffix.lower()
 shutil.copyfile(src,ROOT/name)
 data=_read();data.setdefault(_key(game,team),{})[kind]=name
 INDEX.write_text(json.dumps(data,indent=2),encoding="utf-8")
 return ROOT/name
def remove_asset(game,team,kind):
 data=_read()
 if _key(game,team) in data:data[_key(game,team)].pop(kind,None)
 ROOT.mkdir(parents=True,exist_ok=True)
 INDEX.write_text(json.dumps(data,indent=2),encoding="utf-8")
def load_photo(path,size):
 if not path:return None
 try:
  from PIL import Image,ImageTk
  with Image.open(path) as im:
   im=im.convert("RGBA")
   im.thumbnail(size,Image.Resampling.LANCZOS)
   return ImageTk.PhotoImage(im)
 except ImportError:
  try:return PhotoImage(file=str(path)) if path.suffix.lower()==".png" else None
  except Exception:return None
 except Exception:return None
