
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sqlite3, csv, json
import sys
from pathlib import Path

ROOT=Path.home()/".sliderforge"
ROOT.mkdir(exist_ok=True)
DB=sqlite3.connect(ROOT/"sliderforge.db")
DB.execute("CREATE TABLE IF NOT EXISTS ratings(game TEXT,mode TEXT,career TEXT,season TEXT,team TEXT,ovr INTEGER,off INTEGER,defense INTEGER,source TEXT,PRIMARY KEY(game,mode,career,season,team))")
DB.execute("CREATE TABLE IF NOT EXISTS results(id INTEGER PRIMARY KEY,game TEXT,mode TEXT,career TEXT,season TEXT,home TEXT,away TEXT,home_score INTEGER,away_score INTEGER)")
DB.commit()
TEAMS=sorted(set("""East Carolina|UTSA|Charlotte|North Texas|Tulane|Sam Houston|Rice|UAB|Memphis|Navy|Army|Tulsa|South Florida|Temple|Florida Atlantic|Texas|Texas A&M|Texas Tech|Baylor|TCU|Houston|SMU|Arkansas|Tennessee|Vanderbilt|Alabama|Georgia|Florida|LSU|Oklahoma|Ole Miss|Mississippi State|Auburn|Kentucky|Missouri|South Carolina|Ohio State|Michigan|Penn State|Notre Dame|USC|UCLA|Oregon|Washington|Boise State|Fresno State|San Diego State|Colorado State|Air Force|Wyoming|New Mexico|New Mexico State|UTEP|Texas State|Troy|Appalachian State|Coastal Carolina|Georgia State|Georgia Southern|Marshall|Old Dominion|James Madison|Liberty|Louisiana|UL Monroe|Southern Miss|Western Kentucky|Middle Tennessee|FIU|Louisiana Tech|Jacksonville State|Kennesaw State|UConn|UMass|Buffalo|Toledo|Ohio|Miami (OH)|Bowling Green|Akron|Kent State|Ball State|Central Michigan|Eastern Michigan|Western Michigan|Northern Illinois|California|Stanford|Florida State|Miami (FL)|Clemson|NC State|Duke|Wake Forest|Virginia|Virginia Tech|Louisville|Pittsburgh|Syracuse|Boston College|Georgia Tech|North Carolina|Kansas|Kansas State|Iowa State|Oklahoma State|Colorado|Utah|BYU|Arizona|Arizona State|Cincinnati|West Virginia|UCF|Nebraska|Iowa|Wisconsin|Minnesota|Illinois|Indiana|Purdue|Michigan State|Maryland|Rutgers|Northwestern|Hawaii|Nevada|UNLV|San Jose State|Utah State|Oregon State|Washington State""".split("|")))
def asset_path(name):
 return Path(getattr(sys,"_MEIPASS",Path(__file__).resolve().parent))/name

def seed_official():
 path=asset_path("cfb27_official_ratings.csv")
 if not path.exists():return
 with path.open(encoding="utf-8-sig",newline="") as f:
  for row in csv.DictReader(f):
   team=row["team"];nums=[int(row[k]) for k in ("ovr","off","def")]
   # Preserve existing manual edits and imports.
   DB.execute("INSERT OR IGNORE INTO ratings VALUES(?,?,?,?,?,?,?,?,?)",("27","Exhibition","Default Roster","Current",team,*nums,"EA official June 23 2026"))
 DB.commit()
seed_official()
TEAMS=sorted(set(TEAMS)|{r[0] for r in csv.reader(asset_path("cfb27_official_ratings.csv").open(encoding="utf-8")) if r and r[0]!="team"})
SLIDERS=["QB Accuracy","Pass Blocking","WR Catching","Run Blocking","Ball Security","Pass Defense Reaction Time","Interceptions","Pass Coverage","Tackling","FG Power","FG Accuracy","Punt Power","Punt Accuracy","Kickoff Power"]
class App:
 def __init__(self,root):
  self.root=root;root.title("SliderForge — Prototype 0.1");root.geometry("1060x790");root.configure(bg="#17221d")
  self.game=tk.StringVar(value="27");self.mode=tk.StringVar(value="Dynasty");self.career=tk.StringVar(value="My Dynasty");self.season=tk.StringVar(value="2026")
  self.home=tk.StringVar(value="East Carolina");self.away=tk.StringVar(value="Charlotte");self.status=tk.StringVar(value="Ready — ratings require verified import or manual entry")
  self.sliders={}
  style=ttk.Style();style.theme_use("clam")
  style.configure("TFrame",background="#17221d");style.configure("TLabel",background="#17221d",foreground="#edf5ed",font=("Segoe UI",10))
  style.configure("Title.TLabel",font=("Segoe UI",22,"bold"),foreground="#8df3a2")
  style.configure("TButton",padding=7)
  frame=ttk.Frame(root,padding=16);frame.pack(fill="both",expand=True)
  ttk.Label(frame,text="SLIDERFORGE",style="Title.TLabel").pack(anchor="w")
  ttk.Label(frame,text="YOUR GAME. YOUR DIFFICULTY. YOUR RULES.  •  Recommendations only; apply in-game manually").pack(anchor="w",pady=(0,15))
  top=ttk.Frame(frame);top.pack(fill="x")
  self.field(top,"College Football",self.game,["25","26","27"])
  self.field(top,"Mode",self.mode,["Exhibition","Dynasty","Road to Glory"])
  self.field(top,"Save / Career",self.career,None)
  self.field(top,"Season",self.season,None)
  teams=ttk.Frame(frame);teams.pack(fill="x",pady=14)
  self.field(teams,"HOME",self.home,TEAMS,width=34)
  self.field(teams,"AWAY",self.away,TEAMS,width=34)
  self.ratings_labels={}
  for side in ("HOME","AWAY"):
   column=ttk.Frame(teams);column.pack(side="left",padx=20)
   ttk.Label(column,text=side+"  OVR / OFF / DEF").pack(anchor="w")
   label=ttk.Label(column,text="— / — / —",font=("Segoe UI",15,"bold"));label.pack(anchor="w")
   self.ratings_labels[side]=label
   ttk.Button(column,text="Edit "+side+" ratings",command=lambda s=side:self.edit_ratings(s)).pack(anchor="w",pady=4)
  tools=ttk.Frame(frame);tools.pack(fill="x",pady=5)
  for name,fn in [("Import ratings CSV",self.import_csv),("Export ratings CSV",self.export_csv),("New season (copy prior)",self.new_season),("Log game result",self.log_result),("Export slider preset",self.export_preset)]:
   ttk.Button(tools,text=name,command=fn).pack(side="left",padx=3)
  ttk.Label(frame,text="Suggested gameplay sliders — editable USER and CPU values (0–100)").pack(anchor="w",pady=(15,4))
  notebook=ttk.Notebook(frame);notebook.pack(fill="both",expand=True)
  for title,indices in [("Offense",range(0,5)),("Defense",range(5,9)),("Special Teams",range(9,14))]:
   pane=ttk.Frame(notebook,padding=12);notebook.add(pane,text=title)
   for i in indices:
    name=SLIDERS[i];row=ttk.Frame(pane);row.pack(fill="x",pady=4)
    ttk.Label(row,text=name,width=30).pack(side="left")
    self.sliders[name]=[]
    for side in ("USER","CPU"):
     v=tk.IntVar(value=50);self.sliders[name].append(v)
     ttk.Label(row,text=side).pack(side="left",padx=5)
     tk.Scale(row,from_=0,to=100,orient="horizontal",variable=v,length=190,bg="#17221d",fg="white",highlightthickness=0,troughcolor="#3e5c48").pack(side="left")
  ttk.Label(frame,textvariable=self.status,wraplength=1000).pack(anchor="w",pady=10)
  for var in (self.game,self.mode,self.career,self.season,self.home,self.away):var.trace_add("write",lambda *_:self.refresh())
  self.refresh()
 def field(self,parent,label,var,choices,width=18):
  f=ttk.Frame(parent);f.pack(side="left",padx=(0,13))
  ttk.Label(f,text=label).pack(anchor="w")
  if choices:ttk.Combobox(f,textvariable=var,values=choices,width=width,state="readonly").pack()
  else:ttk.Entry(f,textvariable=var,width=width).pack()
 def key(self):
  mode=self.mode.get()
  return (self.game.get(),mode,self.career.get().strip() if mode!="Exhibition" else "Default Roster",self.season.get().strip() if mode!="Exhibition" else "Current")
 def lookup(self,team):
  row=DB.execute("SELECT ovr,off,defense,source FROM ratings WHERE game=? AND mode=? AND career=? AND season=? AND team=?",(*self.key(),team)).fetchone()
  if row:return row
  # Baseline EA ratings are a fallback, never masquerading as confirmed career ratings.
  if self.game.get()=="27":
   base=DB.execute("SELECT ovr,off,defense,source FROM ratings WHERE game='27' AND mode='Exhibition' AND career='Default Roster' AND season='Current' AND team=?",(team,)).fetchone()
   if base:return (*base[:3],"BASELINE ONLY — "+base[3])
  return None
 def refresh(self):
  for side,var in [("HOME",self.home),("AWAY",self.away)]:
   r=self.lookup(var.get());self.ratings_labels[side].config(text=(f"{r[0]} / {r[1]} / {r[2]}" + ("  (baseline)" if r and str(r[3]).startswith("BASELINE ONLY") else "")) if r else "— / — / —")
 def edit_ratings(self,side):
  team=(self.home if side=="HOME" else self.away).get()
  win=tk.Toplevel(self.root);win.title(f"{team} ratings");win.geometry("320x240")
  old=self.lookup(team);values=[]
  for i,label in enumerate(("OVR","OFF","DEF")):
   ttk.Label(win,text=label).pack();v=tk.StringVar(value=str(old[i]) if old else "");ttk.Entry(win,textvariable=v).pack();values.append(v)
  def save():
   try:
    nums=[int(v.get()) for v in values]
    if any(n<0 or n>99 for n in nums):raise ValueError()
   except ValueError:messagebox.showerror("Invalid ratings","Enter three whole numbers from 0 to 99.");return
   DB.execute("INSERT OR REPLACE INTO ratings VALUES(?,?,?,?,?,?,?,?,?)",(*self.key(),team,*nums,"manual"))
   DB.commit();self.refresh();win.destroy()
  ttk.Button(win,text="Save ratings",command=save).pack(pady=10)
 def import_csv(self):
  path=filedialog.askopenfilename(filetypes=[("CSV","*.csv")])
  if not path:return
  try:
   count=0
   with open(path,encoding="utf-8-sig",newline="") as f:
    for row in csv.DictReader(f):
     team=row["team"].strip();nums=[int(row[k]) for k in ("ovr","off","def")]
     if not team or any(n<0 or n>99 for n in nums):raise ValueError("Invalid team or ratings")
     DB.execute("INSERT OR REPLACE INTO ratings VALUES(?,?,?,?,?,?,?,?,?)",(*self.key(),team,*nums,"imported"));count+=1
   DB.commit();self.refresh();self.status.set(f"Imported {count} ratings for active game/mode/save/season")
  except Exception as e:DB.rollback();messagebox.showerror("Import error",str(e))
 def export_csv(self):
  path=filedialog.asksaveasfilename(defaultextension=".csv",filetypes=[("CSV","*.csv")])
  if not path:return
  rows=DB.execute("SELECT team,ovr,off,defense,source FROM ratings WHERE game=? AND mode=? AND career=? AND season=? ORDER BY team",self.key()).fetchall()
  with open(path,"w",encoding="utf-8",newline="") as f:
   w=csv.writer(f);w.writerow(["team","ovr","off","def","source"]);w.writerows(rows)
  self.status.set(f"Exported {len(rows)} teams")
 def new_season(self):
  if self.mode.get()=="Exhibition":messagebox.showinfo("Season","Use Dynasty or Road to Glory.");return
  old=self.season.get()
  try:new=str(int(old)+1)
  except ValueError:messagebox.showerror("Season","Enter a numeric season year.");return
  rows=DB.execute("SELECT team,ovr,off,defense FROM ratings WHERE game=? AND mode=? AND career=? AND season=?",self.key()).fetchall()
  for team,ovr,off,defense in rows:
   DB.execute("INSERT OR IGNORE INTO ratings VALUES(?,?,?,?,?,?,?,?,?)",(self.game.get(),self.mode.get(),self.career.get(),new,team,ovr,off,defense,"carried-forward-unverified"))
  DB.commit();self.season.set(new);self.status.set(f"Season {new} created; {len(rows)} ratings carried forward UNVERIFIED")
 def log_result(self):
  win=tk.Toplevel(self.root);win.title("Game result")
  vals=[]
  for team in (self.home.get(),self.away.get()):
   ttk.Label(win,text=team+" score").pack();v=tk.StringVar();ttk.Entry(win,textvariable=v).pack();vals.append(v)
  def save():
   try:a,b=map(lambda v:int(v.get()),vals);assert a>=0 and b>=0
   except (ValueError,AssertionError):messagebox.showerror("Invalid","Enter valid nonnegative scores");return
   DB.execute("INSERT INTO results(game,mode,career,season,home,away,home_score,away_score) VALUES(?,?,?,?,?,?,?,?)",(*self.key(),self.home.get(),self.away.get(),a,b));DB.commit()
   self.status.set(f"Saved result: {self.home.get()} {a}–{b} {self.away.get()}");win.destroy()
  ttk.Button(win,text="Save",command=save).pack(pady=10)
 def export_preset(self):
  path=filedialog.asksaveasfilename(defaultextension=".json",filetypes=[("JSON","*.json")])
  if not path:return
  data={"game":self.game.get(),"mode":self.mode.get(),"career":self.career.get(),"season":self.season.get(),"home":self.home.get(),"away":self.away.get(),"ratings":{"home":self.lookup(self.home.get()),"away":self.lookup(self.away.get())},"sliders":{name:{"user":v[0].get(),"cpu":v[1].get()} for name,v in self.sliders.items()}}
  Path(path).write_text(json.dumps(data,indent=2),encoding="utf-8");self.status.set("Preset exported")
if __name__=="__main__":
 root=tk.Tk();App(root);root.mainloop()
