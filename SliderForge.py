
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sqlite3, csv, json
import sys
import threading
import webbrowser
import updater
import branding
from pathlib import Path

ROOT=Path.home()/".sliderforge"
ROOT.mkdir(exist_ok=True)
DB=sqlite3.connect(ROOT/"sliderforge.db")
DB.execute("CREATE TABLE IF NOT EXISTS ratings(game TEXT,mode TEXT,career TEXT,season TEXT,team TEXT,ovr INTEGER,off INTEGER,defense INTEGER,source TEXT,PRIMARY KEY(game,mode,career,season,team))")
DB.execute("CREATE TABLE IF NOT EXISTS results(id INTEGER PRIMARY KEY,game TEXT,mode TEXT,career TEXT,season TEXT,home TEXT,away TEXT,home_score INTEGER,away_score INTEGER)")
DB.execute("CREATE TABLE IF NOT EXISTS season_profiles(game TEXT,mode TEXT,career TEXT,season TEXT,controlled_team TEXT,difficulty TEXT,sliders_json TEXT,PRIMARY KEY(game,mode,career,season))")
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
   DB.execute("INSERT OR IGNORE INTO ratings VALUES(?,?,?,?,?,?,?,?,?)",("C27","Exhibition","Default Roster","Current",team,*nums,"EA official June 23 2026"))
 DB.commit()
seed_official()
TEAMS=sorted(set(TEAMS)|{r[0] for r in csv.reader(asset_path("cfb27_official_ratings.csv").open(encoding="utf-8")) if r and r[0]!="team"})
SLIDERS=["QB Accuracy","Pass Blocking","WR Catching","Run Blocking","Ball Security","Pass Defense Reaction Time","Interceptions","Pass Coverage","Tackling","FG Power","FG Accuracy","Punt Power","Punt Accuracy","Kickoff Power","Offside","False Start","Holding","Facemask","Defensive Pass Interference","Offensive Pass Interference","Illegal Block in the Back","Roughing the Passer","Roughing the Kicker","Running into the Kicker"]
NFL_TEAMS=sorted("""Arizona Cardinals|Atlanta Falcons|Baltimore Ravens|Buffalo Bills|Carolina Panthers|Chicago Bears|Cincinnati Bengals|Cleveland Browns|Dallas Cowboys|Denver Broncos|Detroit Lions|Green Bay Packers|Houston Texans|Indianapolis Colts|Jacksonville Jaguars|Kansas City Chiefs|Las Vegas Raiders|Los Angeles Chargers|Los Angeles Rams|Miami Dolphins|Minnesota Vikings|New England Patriots|New Orleans Saints|New York Giants|New York Jets|Philadelphia Eagles|Pittsburgh Steelers|San Francisco 49ers|Seattle Seahawks|Tampa Bay Buccaneers|Tennessee Titans|Washington Commanders""".split("|"))
CFB_TEAMS=TEAMS[:]
GAME_CHOICES=["College Football 25","College Football 26","College Football 27","Madden NFL 25","Madden NFL 26","Madden NFL 27","NHL 25","NHL 26","NHL 27"]
def game_key(label):
 return ("N" if label.startswith("NHL") else "M" if label.startswith("Madden") else "C")+label[-2:]
def game_family(label):
 return "NHL" if label.startswith("NHL") else "Madden" if label.startswith("Madden") else "College Football"
def game_modes(label):
 return ("Franchise","Be a Pro","Play Now") if game_family(label)=="NHL" else ("Franchise","Superstar","Exhibition") if game_family(label)=="Madden" else ("Dynasty","Road to Glory","Exhibition")

NHL_TEAMS=sorted("""Anaheim Ducks|Boston Bruins|Buffalo Sabres|Calgary Flames|Carolina Hurricanes|Chicago Blackhawks|Colorado Avalanche|Columbus Blue Jackets|Dallas Stars|Detroit Red Wings|Edmonton Oilers|Florida Panthers|Los Angeles Kings|Minnesota Wild|Montreal Canadiens|Nashville Predators|New Jersey Devils|New York Islanders|New York Rangers|Ottawa Senators|Philadelphia Flyers|Pittsburgh Penguins|San Jose Sharks|Seattle Kraken|St. Louis Blues|Tampa Bay Lightning|Toronto Maple Leafs|Vancouver Canucks|Vegas Golden Knights|Washington Capitals|Winnipeg Jets|Utah Hockey Club|Utah Mammoth""".split("|"))
# PWHL lists reflect the league's teams by season, not guaranteed in-game roster availability.
PWHL_ORIGINAL=["Boston Fleet","Minnesota Frost","Montréal Victoire","New York Sirens","Ottawa Charge","Toronto Sceptres"]
PWHL_2026=["Seattle Torrent","Vancouver Goldeneyes"]
PWHL_2027=["PWHL Detroit","PWHL Hamilton","PWHL Las Vegas","PWHL San Jose"]
def pwhl_teams_for_game(game):
 teams=PWHL_ORIGINAL[:]
 if game in ("NHL 26","NHL 27"):teams+=PWHL_2026
 if game=="NHL 27":teams+=PWHL_2027
 return sorted(teams)
def nhl_teams_for_game(game):
 teams=[team for team in NHL_TEAMS if team not in ("Utah Hockey Club", "Utah Mammoth")]
 teams.append("Utah Hockey Club" if game == "NHL 25" else "Utah Mammoth")
 return sorted(teams)+["──── PWHL (league teams; game availability unverified) ────"]+pwhl_teams_for_game(game)

# Candidate hockey slider labels; confirm the exact in-game labels and availability per edition.
NHL_SLIDER_GROUPS={
 "General":["Game Speed","Fatigue Effect","Fatigue Recovery","Injury Occurrence"],
 "Skating":["Skating Speed","Player Acceleration","Skating Agility","Back Skating"],
 "Shooting":["Slap Shot Accuracy","Slap Shot Power","Wrist Shot Accuracy","Wrist Shot Power","One Timer Accuracy"],
 "Passing":["Pass Accuracy","Pass Speed","Pass Reception Ease","Pass Interceptions"],
 "Puck Control":["Puck Control","Puck Pickups","Deking Impact"],
 "Goalies":["Goalie Reaction Time","Goalie Cross Crease Reaction Time","Goalie Screen Effect","Goalie Save Reaction Time"],
 "Checking":["Hitting Power","Aggression","Poke Checking Accuracy","Stick Lift Effectiveness"],
 "Penalties":["Tripping","Slashing","Interference","Hooking","High Sticking","Boarding"],
 "AI":["CPU Difficulty Adjustment","CPU Strategy Adjustment"]
}
FOOTBALL_SLIDER_GROUPS={"Offense":SLIDERS[:5],"Defense":SLIDERS[5:9],"Special Teams":SLIDERS[9:14],"Penalties":SLIDERS[14:]}

class App:
 def __init__(self,root):
  self.root=root;root.title("SliderForge v1.3 Beta — Stadium Branding");root.geometry("1180x810");root.configure(bg="#17221d")
  self.game=tk.StringVar(value="College Football 27");self.mode=tk.StringVar(value="Dynasty");self.career=tk.StringVar(value="My Dynasty");self.season=tk.StringVar(value="2026")
  self.home=tk.StringVar(value="East Carolina");self.away=tk.StringVar(value="Charlotte");self.primary_team=tk.StringVar(value="East Carolina");self.opponent=tk.StringVar(value="Charlotte");self.venue=tk.StringVar(value="HOME");self.status=tk.StringVar(value="Ready — ratings require verified import or manual entry")
  branding.OFFICIAL=set(CFB_TEAMS)
  self.sliders={}
  self._branding_photo=None
  self._loading_profile=False
  self.lock_status=tk.StringVar(value="Season profile not locked")
  self.controlled=tk.StringVar(value="HOME")
  self.auto_sliders=tk.BooleanVar(value=True)
  self.difficulty=tk.StringVar(value="All-American")
  style=ttk.Style();style.theme_use("clam")
  style.configure("TFrame",background="#17221d");style.configure("TLabel",background="#17221d",foreground="#edf5ed",font=("Segoe UI",10))
  style.configure("Title.TLabel",font=("Segoe UI",22,"bold"),foreground="#8df3a2")
  style.configure("TButton",padding=7)
  frame=ttk.Frame(root,padding=16);frame.pack(fill="both",expand=True)
  header=ttk.Frame(frame);header.pack(fill="x")
  ttk.Label(header,text="SLIDERFORGE",style="Title.TLabel").pack(side="left")
  ttk.Button(header,text="Check for Updates",command=self.check_updates).pack(side="right",padx=4)
  ttk.Button(header,text="Update Settings",command=self.update_settings).pack(side="right",padx=4)
  self.branding_panel=ttk.Frame(frame)
  self.branding_panel.pack(fill="x",pady=(4,10))
  self.branding_canvas=tk.Canvas(self.branding_panel,height=165,bg="#142b25",highlightthickness=0)
  self.branding_canvas.pack(fill="x")
  branding_actions=ttk.Frame(self.branding_panel);branding_actions.pack(fill="x",pady=(3,0))
  ttk.Button(branding_actions,text="New TeamBuilder Team",command=self.new_teambuilder).pack(side="left",padx=3)
  ttk.Button(branding_actions,text="Import Team Logo",command=self.import_team_logo).pack(side="left",padx=3)
  ttk.Button(branding_actions,text="Import Stadium Photo",command=self.import_stadium).pack(side="left",padx=3)
  ttk.Button(branding_actions,text="Reset Stadium",command=self.reset_stadium).pack(side="left",padx=3)
  ttk.Button(branding_actions,text="Remove Logo",command=self.remove_logo).pack(side="left",padx=3)
  ttk.Label(branding_actions,text="Custom team → generic stadium by default").pack(side="right")
  self.branding_canvas.bind("<Configure>",lambda e:self.refresh_branding())
  self.primary_team.trace_add("write",lambda *_:self.refresh_branding())
  self.game.trace_add("write",lambda *_:self.refresh_branding())
  ttk.Label(frame,text="YOUR GAME. YOUR DIFFICULTY. YOUR RULES.  •  Recommendations only; apply in-game manually").pack(anchor="w",pady=(0,10))
  top=ttk.Frame(frame);top.pack(fill="x")
  self.field(top,"Game",self.game,GAME_CHOICES,width=22)
  self.mode_tabs=ttk.Notebook(frame)
  self.mode_tabs.pack(fill="x",pady=(12,5))
  self.mode_frames={}
  for label in ("Dynasty","Road to Glory","Exhibition","Franchise","Superstar","Be a Pro","Play Now"):
   tab=ttk.Frame(self.mode_tabs,padding=9)
   self.mode_tabs.add(tab,text=label)
   self.mode_frames[label]=tab
   ttk.Label(tab,text={"Dynasty":"Your program • one consistent slider profile per season","Road to Glory":"Your player's team • independent career and season lock","Exhibition":"Your team first • optional opponent for matchup reference","Franchise":"Your NFL team • one locked slider profile per season","Superstar":"Your NFL career • independent season profile","Be a Pro":"Your hockey career • independent season profile","Play Now":"Single game • no season lock"}[label]).pack(anchor="w")
  self.mode_tabs.bind("<<NotebookTabChanged>>",self.on_mode_tab)
  self._visible_family=None
  setup=ttk.Frame(frame);setup.pack(fill="x",pady=6)
  self.field(setup,"Save / Career",self.career,None,width=23)
  self.field(setup,"Season",self.season,None,width=10)
  self.field(setup,"YOUR TEAM",self.primary_team,CFB_TEAMS,width=27)
  self.field(setup,"Venue",self.venue,["HOME","AWAY"],width=8)
  self.exhibition_extra=ttk.Frame(frame)
  self.field(self.exhibition_extra,"Opponent (reference only)",self.opponent,CFB_TEAMS,width=27)
  self.ratings_labels={}
  rating_row=ttk.Frame(frame);rating_row.pack(fill="x",pady=(5,8))
  ttk.Label(rating_row,text="YOUR TEAM  OVR / OFF / DEF").pack(side="left",padx=(0,10))
  self.ratings_labels["HOME"]=ttk.Label(rating_row,text="— / — / —",font=("Segoe UI",13,"bold"))
  self.ratings_labels["HOME"].pack(side="left")
  ttk.Button(rating_row,text="Edit my team's ratings",command=lambda:self.edit_ratings(self.controlled.get())).pack(side="left",padx=12)
  self.opponent_rating=ttk.Label(self.exhibition_extra,text="Opponent rating: — / — / —")
  self.opponent_rating.pack(side="left",padx=12)
  self.ratings_labels["AWAY"]=ttk.Label(frame,text="")
  tools=ttk.Frame(frame);tools.pack(fill="x",pady=5)
  for name,fn in [("Import ratings CSV",self.import_csv),("Export ratings CSV",self.export_csv),("New season (copy prior)",self.new_season),("Log game result",self.log_result),("Export slider preset",self.export_preset),("Capture card / ratings",self.capture_window)]:
   ttk.Button(tools,text=name,command=fn).pack(side="left",padx=3)
  tune=ttk.Frame(frame);tune.pack(fill="x",pady=(10,4))
  ttk.Label(tune,text="Difficulty:").pack(side="left")
  self.difficulty_box=ttk.Combobox(tune,textvariable=self.difficulty,values=["Freshman","Varsity","All-American","Heisman"],width=15,state="readonly")
  self.difficulty_box.pack(side="left",padx=6)
  ttk.Checkbutton(tune,text="Auto-apply True Balance",variable=self.auto_sliders,command=self.refresh).pack(side="left",padx=10)
  ttk.Button(tune,text="Recalculate",command=lambda:self.recommend(force=True)).pack(side="left")
  self.lock_button=ttk.Button(tune,text="Lock season",command=self.lock_season)
  self.lock_button.pack(side="left",padx=4)
  self.unlock_button=ttk.Button(tune,text="Unlock",command=self.unlock_season)
  self.unlock_button.pack(side="left")
  ttk.Label(frame,textvariable=self.lock_status).pack(anchor="w")
  ttk.Label(frame,text="Game-specific experimental slider profiles. Ratings do not alter sliders. Apply settings in-game manually.").pack(anchor="w",pady=(8,4))
  self.slider_notebook=ttk.Notebook(frame);self.slider_notebook.pack(fill="both",expand=True)
  self.render_sliders()
  ttk.Label(frame,textvariable=self.status,wraplength=1000).pack(anchor="w",pady=10)
  for var in (self.game,self.career,self.season,self.primary_team,self.opponent,self.venue,self.difficulty):var.trace_add("write",lambda *_:self.refresh())
  self.mode_tabs.select(self.mode_frames["Dynasty"])
  self.game.trace_add("write",lambda *_:self.on_game_changed())
  self.on_game_changed()
 def new_teambuilder(self):
  if game_family(self.game.get())!="College Football":
   messagebox.showinfo("TeamBuilder", "TeamBuilder customization is available for College Football editions.");return
  from tkinter import simpledialog
  name=simpledialog.askstring("TeamBuilder Team","Enter a TeamBuilder team name:",parent=self.root)
  if name and name.strip():self.primary_team.set("Custom: "+name.strip().removeprefix("Custom: "))
 def branding_team(self):
  return self.primary_team.get().strip()
 def import_team_logo(self):
  team=self.branding_team()
  if not team:return messagebox.showwarning("Choose team","Select or enter a team first.")
  path=filedialog.askopenfilename(title="Choose team logo",filetypes=[("Image files","*.png *.jpg *.jpeg *.webp")])
  if path:
   try:branding.store_asset(self.game.get(),team,"logo",path)
   except Exception as e:return messagebox.showerror("Import failed",str(e))
   self.refresh_branding()
 def import_stadium(self):
  team=self.branding_team()
  if not team:return messagebox.showwarning("Choose team","Select or enter a team first.")
  path=filedialog.askopenfilename(title="Choose stadium photo or TeamBuilder screenshot",filetypes=[("Image files","*.png *.jpg *.jpeg *.webp")])
  if path:
   try:branding.store_asset(self.game.get(),team,"stadium",path)
   except Exception as e:return messagebox.showerror("Import failed",str(e))
   self.refresh_branding()
 def reset_stadium(self):
  branding.remove_asset(self.game.get(),self.branding_team(),"stadium")
  self.refresh_branding()
 def remove_logo(self):
  branding.remove_asset(self.game.get(),self.branding_team(),"logo")
  self.refresh_branding()
 def refresh_branding(self):
  if not hasattr(self,"branding_canvas"):return
  c=self.branding_canvas
  w=max(600,c.winfo_width());h=165
  c.delete("all")
  team=self.branding_team()
  game=self.game.get()
  custom=branding.is_custom_team(team)
  stadium=branding.stadium_label(team,game)
  img=branding.load_photo(branding.get_asset(game,team,"stadium"),(w,h))
  self._branding_photo=img
  if img:
   c.create_image(w//2,h//2,image=img)
   c.create_rectangle(0,0,w,h,fill="#07130f",stipple="gray50",outline="")
  else:
   c.create_rectangle(0,0,w,h,fill="#183d30",outline="")
   for i in range(0,w,45):c.create_line(i,0,i+80,h,fill="#285342",width=2)
   c.create_rectangle(w*.07,20,w*.93,h-18,outline="#7fa18e",width=2)
   c.create_line(w*.5,20,w*.5,h-18,fill="#7fa18e",width=2)
   c.create_oval(w*.5-32,h*.5-32,w*.5+32,h*.5+32,outline="#7fa18e",width=2)
  c.create_rectangle(12,15,w*.55,148,fill="#0c1b18",outline="#597468")
  c.create_text(27,38,anchor="w",text=team[:43] or "Select a team",font=("Segoe UI",18,"bold"),fill="white")
  c.create_text(27,71,anchor="w",text=stadium[:58],font=("Segoe UI",11),fill="#b6e2c8")
  c.create_text(27,103,anchor="w",text=("TeamBuilder / Custom team" if custom else game),font=("Segoe UI",10),fill="#e5e5e5")
  logo=branding.load_photo(branding.get_asset(game,team,"logo"),(130,130))
  self._branding_logo=logo
  if logo:c.create_image(w-92,h//2,image=logo)
  else:
   c.create_oval(w-151,15,w-24,142,fill="#123127",outline="#83bd9b",width=3)
   c.create_text(w-87,78,text=branding.initials(team),font=("Segoe UI",26,"bold"),fill="white")
 def update_settings(self):
  win=tk.Toplevel(self.root);win.title("GitHub Update Settings");win.geometry("490x205");win.transient(self.root)
  win.grab_set()
  cfg=updater.settings()
  repo=tk.StringVar(value=cfg.get("repo",""))
  channel=tk.StringVar(value=cfg.get("channel","stable"))
  ttk.Label(win,text="GitHub repository (owner/SliderForge)").pack(anchor="w",padx=12,pady=(12,2))
  ttk.Entry(win,textvariable=repo,width=55).pack(fill="x",padx=12)
  ttk.Label(win,text="Release channel").pack(anchor="w",padx=12,pady=(10,2))
  ttk.Combobox(win,textvariable=channel,values=["stable","beta"],state="readonly").pack(fill="x",padx=12)
  def save():
   try:updater.save_settings(repo.get(),channel.get())
   except ValueError as e:messagebox.showerror("Invalid repository",str(e),parent=win);return
   win.destroy()
   self.status.set("GitHub updater configured. Use Check for Updates.")
  ttk.Button(win,text="Save",command=save).pack(pady=10)
 def check_updates(self):
  self.status.set("Checking GitHub Releases…")
  def worker():
   try:result=updater.check()
   except Exception as e:
    self.root.after(0,lambda msg=str(e):self._update_error(msg))
    return
   self.root.after(0,lambda:self._update_result(result))
  threading.Thread(target=worker,daemon=True).start()
 def _update_error(self,msg):
  self.status.set("Update check failed: "+msg)
  messagebox.showerror("GitHub update check",msg,parent=self.root)
 def _update_result(self,result):
  release=result["release"]
  if not result["newer"]:
   messagebox.showinfo("SliderForge updates","You're up to date (v"+updater.VERSION+")." if release else "No eligible GitHub releases found.",parent=self.root)
   self.status.set("Update check complete.")
   return
  asset=result["asset"]
  tag=release.get("tag_name","new release")
  if not asset:
   if messagebox.askyesno("New release",tag+" is available, but has no SliderForge ZIP. Open release page?",parent=self.root):
    webbrowser.open(release["html_url"])
   return
  if not messagebox.askyesno("Update available",tag+" is available. Download "+asset["name"]+" to your SliderForge downloads folder?\n\nThe app will NOT replace files while running.",parent=self.root):
   return
  self.status.set("Downloading "+asset["name"]+"…")
  def worker():
   try:target=updater.download_asset(asset)
   except Exception as e:self.root.after(0,lambda msg=str(e):self._update_error(msg));return
   self.root.after(0,lambda:self._update_downloaded(target))
  threading.Thread(target=worker,daemon=True).start()
 def _update_downloaded(self,target):
  self.status.set("Downloaded verified ZIP: "+str(target))
  messagebox.showinfo("Update downloaded","Update saved to:\n"+str(target)+"\n\nClose SliderForge, extract the ZIP into a NEW folder, and launch the updated START_WINDOWS.bat. Your profiles are stored separately in ~/.sliderforge.\n\nAutomatic installation is not enabled yet.",parent=self.root)
 def render_sliders(self):
  if not hasattr(self,"slider_notebook"):return
  for tab in self.slider_notebook.tabs():self.slider_notebook.forget(tab)
  self.sliders={}
  hockey=game_family(self.game.get())=="NHL"
  groups=NHL_SLIDER_GROUPS if hockey else FOOTBALL_SLIDER_GROUPS
  for title,names in groups.items():
   pane=ttk.Frame(self.slider_notebook,padding=10);self.slider_notebook.add(pane,text=title)
   for name in names:
    row=ttk.Frame(pane);row.pack(fill="x",pady=3)
    ttk.Label(row,text=name,width=32).pack(side="left")
    self.sliders[name]=[]
    # NHL has many settings with edition-dependent USER/CPU availability.
    sides=("VALUE",) if hockey or title=="Penalties" else ("USER","CPU")
    for side in sides:
     v=tk.IntVar(value=50);self.sliders[name].append(v)
     ttk.Label(row,text=side).pack(side="left",padx=3)
     tk.Scale(row,from_=0,to=100,orient="horizontal",variable=v,length=180,bg="#17221d",fg="white",highlightthickness=0,troughcolor="#3e5c48").pack(side="left")
  self.recommend(force=True)
 def on_mode_tab(self,event=None):
  tab=self.mode_tabs.tab(self.mode_tabs.select(),"text")
  if tab not in self.mode_frames:return
  self.mode.set(tab)
  self.career.set({"Dynasty":"My Dynasty","Road to Glory":"My RTG Career","Exhibition":"Default Roster","Franchise":"My Franchise","Superstar":"My Superstar Career","Be a Pro":"My Be a Pro Career","Play Now":"Default Roster"}[tab])
  if tab in ("Exhibition","Play Now"):
   self.exhibition_extra.pack(fill="x",pady=4,after=self.mode_tabs)
   self.lock_button.state(["disabled"]);self.unlock_button.state(["disabled"])
  else:
   self.exhibition_extra.pack_forget()
   self.lock_button.state(["!disabled"]);self.unlock_button.state(["!disabled"])
  self.refresh()
 def on_game_changed(self):
  family=game_family(self.game.get())
  modes=game_modes(self.game.get())
  for i in range(self.mode_tabs.index("end")):
   label=self.mode_tabs.tab(i,"text")
   self.mode_tabs.tab(i,state="normal" if label in modes else "hidden")
  if self.mode.get() not in modes:
   self.mode_tabs.select(self.mode_frames[modes[0]])
   self.on_mode_tab()
  teams=nhl_teams_for_game(self.game.get()) if family=="NHL" else NFL_TEAMS if family=="Madden" else CFB_TEAMS
  self.primary_team.set("Dallas Stars" if family=="NHL" else "Dallas Cowboys" if family=="Madden" else "East Carolina")
  self.opponent.set("Colorado Avalanche" if family=="NHL" else "Philadelphia Eagles" if family=="Madden" else "Charlotte")
  # Refresh every team selector, including the Exhibition opponent.
  for widget in self.root.winfo_children():
   self._set_team_choices(widget,teams)
  self.difficulty_box.configure(values=["Rookie","Semi-Pro","Pro","All-Star","Superstar"] if family=="NHL" else ["Rookie","Pro","All-Pro","All-Madden"] if family=="Madden" else ["Freshman","Varsity","All-American","Heisman"])
  self.difficulty.set("Pro" if family in ("Madden","NHL") else "Varsity")
  self.render_sliders()
  self.status.set("Selected "+self.game.get()+". PWHL teams are included by league season; in-game availability unverified. Experimental sliders.")
  self.refresh()
 def _set_team_choices(self,widget,teams):
  if isinstance(widget,ttk.Combobox) and widget.cget("textvariable") in (str(self.primary_team),str(self.opponent)):
   widget.configure(values=teams)
  for child in widget.winfo_children():self._set_team_choices(child,teams)
 def sync_teams(self):
  if self.primary_team.get().startswith("────"):
   self.primary_team.set("Dallas Stars")
  if self.opponent.get().startswith("────"):
   self.opponent.set("Colorado Avalanche")
  # Home/away are retained solely for game-result logging and capture-card compatibility.
  if self.venue.get()=="HOME":
   self.home.set(self.primary_team.get());self.away.set(self.opponent.get())
   self.controlled.set("HOME")
  else:
   self.away.set(self.primary_team.get());self.home.set(self.opponent.get())
   self.controlled.set("AWAY")
 def recommend(self,force=False):
  if self.mode.get() not in ("Exhibition","Play Now"):
   saved=self.get_season_profile()
   if saved:
    for name,values in saved.items():
     if name in self.sliders:
      for var,value in zip(self.sliders[name],values):var.set(value)
    self.lock_status.set("LOCKED — " + self.mode.get() + " / " + self.career.get() + " / " + self.season.get())
    return
   self.lock_status.set("UNLOCKED — season profile not saved")
  else:self.lock_status.set("Single-game mode — gameplay-first True Balance")
  if not force and not self.auto_sliders.get():return
  # Gameplay-first True Balance: ratings and opponent selection do not change sliders.
  # Difficulty is handled by the game's own difficulty setting, not artificial CPU boosts.
  # These values are experimental starting points, not verified game calibration.
  baseline={
   "QB Accuracy":50,"Pass Blocking":50,"WR Catching":50,
   "Run Blocking":50,"Ball Security":50,
   "Pass Defense Reaction Time":50,"Interceptions":20,
   "Pass Coverage":50,"Tackling":50,
  }
  for name,vars in self.sliders.items():
   target=(50 if game_family(self.game.get())=="NHL" else baseline.get(name,50))
   for var in vars:var.set(target)
  self.status.set(self.game.get()+(" NHL PLACEHOLDER: all sliders 50, not validated; adjust manually after checking your game menu." if game_family(self.game.get())=="NHL" else " Football TEST baseline: interceptions 20/20; other core sliders 50/50.")+" Apply in-game manually.")
 def get_season_profile(self):
  if self.mode.get() in ("Exhibition","Play Now"):return None
  row=DB.execute("SELECT sliders_json FROM season_profiles WHERE game=? AND mode=? AND career=? AND season=?",self.key()).fetchone()
  return json.loads(row[0]) if row else None
 def lock_season(self):
  if self.mode.get() in ("Exhibition","Play Now"):
   messagebox.showinfo("Exhibition","Season Lock applies to career modes, not single games.");return
  data={name:[v.get() for v in vars] for name,vars in self.sliders.items()}
  controlled=self.home.get() if self.controlled.get()=="HOME" else self.away.get()
  DB.execute("INSERT OR REPLACE INTO season_profiles VALUES(?,?,?,?,?,?,?)",(*self.key(),controlled,self.difficulty.get(),json.dumps(data)))
  DB.commit();self.refresh();self.status.set("Season profile locked. Changing opponents or capturing ratings will NOT change sliders.")
 def unlock_season(self):
  if self.mode.get() in ("Exhibition","Play Now"):return
  if not messagebox.askyesno("Unlock season","Unlock and delete this season's saved slider profile? You can lock it again."):return
  DB.execute("DELETE FROM season_profiles WHERE game=? AND mode=? AND career=? AND season=?",self.key());DB.commit();self.refresh()
 def field(self,parent,label,var,choices,width=18):
  f=ttk.Frame(parent);f.pack(side="left",padx=(0,13))
  ttk.Label(f,text=label).pack(anchor="w")
  if choices:ttk.Combobox(f,textvariable=var,values=choices,width=width,state="normal" if var is self.primary_team else "readonly").pack()
  else:ttk.Entry(f,textvariable=var,width=width).pack()
 def key(self):
  mode=self.mode.get()
  return (game_key(self.game.get()),mode,self.career.get().strip() if mode not in ("Exhibition","Play Now") else "Default Roster",self.season.get().strip() if mode not in ("Exhibition","Play Now") else "Current")
 def lookup(self,team):
  row=DB.execute("SELECT ovr,off,defense,source FROM ratings WHERE game=? AND mode=? AND career=? AND season=? AND team=?",(*self.key(),team)).fetchone()
  if row:return row
  # Baseline EA ratings are a fallback, never masquerading as confirmed career ratings.
  if self.game.get()=="College Football 27":
   base=DB.execute("SELECT ovr,off,defense,source FROM ratings WHERE game='C27' AND mode='Exhibition' AND career='Default Roster' AND season='Current' AND team=?",(team,)).fetchone()
   if not base:
    base=DB.execute("SELECT ovr,off,defense,source FROM ratings WHERE game='27' AND mode='Exhibition' AND career='Default Roster' AND season='Current' AND team=?",(team,)).fetchone()
   if base:return (*base[:3],"BASELINE ONLY — "+base[3])
  return None
 def refresh(self):
  self.sync_teams()
  r=self.lookup(self.primary_team.get())
  self.ratings_labels["HOME"].config(text=(f"{r[0]} / {r[1]} / {r[2]}" + ("  (baseline)" if str(r[3]).startswith("BASELINE ONLY") else "")) if r else "— / — / —")
  r2=self.lookup(self.opponent.get())
  self.opponent_rating.config(text="Opponent rating: "+(f"{r2[0]} / {r2[1]} / {r2[2]}" if r2 else "— / — / —"))
  self.recommend()
 def edit_ratings(self,side):
  team=self.primary_team.get()
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
  if self.mode.get() in ("Exhibition","Play Now"):messagebox.showinfo("Season","Season Lock is available in Dynasty, Road to Glory, Franchise, Superstar, and Be a Pro.");return
  old=self.season.get()
  try:new=str(int(old)+1)
  except ValueError:messagebox.showerror("Season","Enter a numeric season year.");return
  rows=DB.execute("SELECT team,ovr,off,defense FROM ratings WHERE game=? AND mode=? AND career=? AND season=?",self.key()).fetchall()
  for team,ovr,off,defense in rows:
   DB.execute("INSERT OR IGNORE INTO ratings VALUES(?,?,?,?,?,?,?,?,?)",(game_key(self.game.get()),self.mode.get(),self.career.get(),new,team,ovr,off,defense,"carried-forward-unverified"))
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
 def capture_window(self):
  try:
   import cv2
   from PIL import Image, ImageTk
  except ImportError:
   messagebox.showerror("Missing dependency","Capture requires opencv-python and Pillow. Run INSTALL_CAPTURE.bat first.")
   return
  win=tk.Toplevel(self.root);win.title("SliderForge — Capture Card Ratings v0.5");win.geometry("940x760");win.minsize(850,620)
  camera=tk.StringVar(value="0");active=[None];last=[None];preview=[None]
  bar=ttk.Frame(win);bar.pack(fill="x",padx=12,pady=10)
  ttk.Label(bar,text="Capture device index (try 0, 1, 2...):").pack(side="left")
  ttk.Combobox(bar,textvariable=camera,values=[str(i) for i in range(8)],width=5).pack(side="left",padx=8)
  info=tk.StringVar(value="Select your capture card and click Connect. Close OBS if it has exclusive access.")
  preview_frame=tk.Frame(win,bg="black",width=800,height=360)
  preview_frame.pack(fill="x",padx=12,pady=6)
  preview_frame.pack_propagate(False)
  canvas=tk.Label(preview_frame,bg="black",text="Preview appears after Connect",fg="white")
  canvas.pack(fill="both",expand=True)
  ttk.Label(win,textvariable=info,wraplength=830).pack(pady=6)
  fields=ttk.Frame(win);fields.pack(pady=8)
  vals={}
  for side in ("HOME","AWAY"):
   f=ttk.LabelFrame(fields,text=side,padding=8);f.pack(side="left",padx=10)
   for field in ("OVR","OFF","DEF"):
    row=ttk.Frame(f);row.pack(fill="x",pady=2)
    ttk.Label(row,text=field,width=6).pack(side="left")
    v=tk.StringVar();ttk.Entry(row,textvariable=v,width=6).pack(side="left");vals[(side,field)]=v
  def disconnect():
   if active[0] is not None:active[0].release();active[0]=None
  def tick():
   if not win.winfo_exists():return
   if active[0] is not None:
    ok,frame=active[0].read()
    if ok:
     last[0]=frame
     rgb=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
     img=Image.fromarray(rgb);img.thumbnail((800,340))
     photo=ImageTk.PhotoImage(img);preview[0]=photo;canvas.configure(image=photo,text="")
    else:info.set("No video frames received. Try another device index or close OBS.")
   win.after(80,tick)
  def connect():
   disconnect()
   try:index=int(camera.get())
   except ValueError:messagebox.showerror("Device","Choose a numeric camera index.");return
   cap=cv2.VideoCapture(index,cv2.CAP_DSHOW if __import__('sys').platform=='win32' else cv2.CAP_ANY)
   if not cap.isOpened():cap.release();info.set(f"Device {index} unavailable. Try another index or close capture software.");return
   active[0]=cap;info.set(f"Live capture device {index} connected. Display the team ratings screen in CFB.")
  def snapshot():
   if last[0] is None:messagebox.showwarning("No image","Connect your capture card first.");return
   path=ROOT/"last_ratings_capture.png";cv2.imwrite(str(path),last[0]);info.set(f"Screenshot saved: {path}")
   try:
    import pytesseract,re
    raw=pytesseract.image_to_string(Image.fromarray(cv2.cvtColor(last[0],cv2.COLOR_BGR2RGB)),config="--psm 11")
    lines=[x.strip() for x in raw.splitlines() if x.strip()]
    # Experimental recognition: extract only clearly labeled rating values; do not silently save.
    pairs=re.findall(r"\b(OVR|OFF|DEF)\s*[:\-]?\s*(\d{2})\b",raw.upper())
    if len(pairs)>=6:
     for side,chunk in zip(("HOME","AWAY"),(pairs[:3],pairs[3:6])):
      for key,val in chunk:
       if (side,key) in vals:vals[(side,key)].set(val)
    info.set("Screenshot saved. Experimental OCR: "+("Review detected numbers carefully before saving." if pairs else "No reliably labeled ratings found. Enter numbers manually."))
   except (ImportError,Exception) as e:info.set("Screenshot saved. OCR unavailable or failed; enter numbers manually. "+str(e)[:90])
  def save():
   try:
    ratings={side:[int(vals[(side,k)].get()) for k in ("OVR","OFF","DEF")] for side in ("HOME","AWAY")}
    if any(n<0 or n>99 for arr in ratings.values() for n in arr):raise ValueError()
   except ValueError:messagebox.showerror("Check ratings","Enter valid 0–99 ratings for both teams before saving.");return
   if not messagebox.askyesno("Confirm detected ratings","Save these ratings to the CURRENT game, mode, career and season?\n\n"+"\n".join(f"{side} ({(self.home if side=='HOME' else self.away).get()}): {arr}" for side,arr in ratings.items())):return
   for side,arr in ratings.items():
    team=(self.home if side=="HOME" else self.away).get()
    DB.execute("INSERT OR REPLACE INTO ratings VALUES(?,?,?,?,?,?,?,?,?)",(*self.key(),team,*arr,"capture-card-confirmed"))
   DB.commit();self.refresh();info.set("Ratings saved for reference. Gameplay-first sliders do not depend on ratings. Screenshot retained locally.")
  buttons=ttk.Frame(bar);buttons.pack(side="left",padx=12)
  for label,cmd in [("Connect",connect),("Disconnect",disconnect),("Capture / OCR",snapshot),("Save Ratings",save)]:ttk.Button(buttons,text=label,command=cmd).pack(side="left",padx=4)
  ttk.Label(win,text="OCR is experimental. Confirm all six numbers and select the correct teams before saving. No automatic console modifications.",wraplength=820).pack(pady=8)
  def close():disconnect();win.destroy()
  win.protocol("WM_DELETE_WINDOW",close);tick()
 def export_preset(self):
  path=filedialog.asksaveasfilename(defaultextension=".json",filetypes=[("JSON","*.json")])
  if not path:return
  data={"game":self.game.get(),"mode":self.mode.get(),"career":self.career.get(),"season":self.season.get(),"home":self.home.get(),"away":self.away.get(),"ratings":{"home":self.lookup(self.home.get()),"away":self.lookup(self.away.get())},"primary_team":self.primary_team.get(),"venue":self.venue.get(),"sliders":{name:({"user":v[0].get(),"cpu":v[1].get()} if len(v)>1 else {"value":v[0].get()}) for name,v in self.sliders.items()}}
  Path(path).write_text(json.dumps(data,indent=2),encoding="utf-8");self.status.set("Preset exported")
if __name__=="__main__":
 root=tk.Tk();App(root);root.mainloop()
