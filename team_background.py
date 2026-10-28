"""Dynamic per-team header artwork for SliderForge Tkinter desktop app."""
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from branding import get_asset, store_asset, remove_asset, stadium_label, initials, load_photo, is_custom_team

PREFS = Path.home() / ".sliderforge" / "background_settings.json"
COLORS = {
    "East Carolina": "#592A8A", "Charlotte": "#046A38",
    "Texas": "#BF5700", "Texas Tech": "#C8102E",
    "UTSA": "#0C2340", "Dallas Stars": "#006847",
    "Dallas Cowboys": "#003594", "Texas A&M": "#500000",
    "Tennessee": "#FF8200", "Arkansas": "#9D2235",
    "Sam Houston": "#F76900", "North Texas": "#00843D",
}
DEFAULT = {"enabled": True, "side": "YOUR TEAM", "opacity": 15}

def _read_prefs():
    try:
        data = json.loads(PREFS.read_text(encoding="utf-8"))
        return {**DEFAULT, **{k: v for k, v in data.items() if k in DEFAULT}}
    except (OSError, ValueError, TypeError):
        return dict(DEFAULT)

class TeamBackground:
    def __init__(self, parent, game, home, away, venue):
        self.game, self.home, self.away, self.venue = game, home, away, venue
        self.prefs = _read_prefs()
        self.enabled = tk.BooleanVar(value=bool(self.prefs["enabled"]))
        self.side = tk.StringVar(value=self.prefs["side"] if self.prefs["side"] in ("YOUR TEAM", "OPPONENT", "HOME", "AWAY") else "YOUR TEAM")
        self.opacity = tk.IntVar(value=max(5, min(40, int(self.prefs["opacity"]))))
        self.frame = ttk.Frame(parent)
        self.frame.pack(fill="x", pady=(0, 8))
        self.canvas = tk.Canvas(self.frame, height=118, bg="#18251d", highlightthickness=0)
        self.canvas.pack(fill="x")
        self.photo = None
        controls = ttk.Frame(self.frame)
        controls.pack(fill="x", pady=(5, 0))
        ttk.Label(controls, text="Background:").pack(side="left")
        ttk.Checkbutton(controls, text="On", variable=self.enabled, command=self.changed).pack(side="left", padx=5)
        ttk.Combobox(controls, textvariable=self.side, state="readonly", width=13,
                     values=["YOUR TEAM", "OPPONENT", "HOME", "AWAY"]).pack(side="left", padx=5)
        ttk.Label(controls, text="Opacity").pack(side="left", padx=(10, 3))
        tk.Scale(controls, from_=5, to=40, orient="horizontal", variable=self.opacity,
                 length=125, bg="#17221d", fg="white", highlightthickness=0,
                 troughcolor="#3e5c48", showvalue=True, command=lambda _: self.changed()).pack(side="left")
        ttk.Button(controls, text="Import logo", command=self.import_logo).pack(side="left", padx=4)
        ttk.Button(controls, text="Import stadium", command=self.import_stadium).pack(side="left", padx=4)
        ttk.Button(controls, text="Reset stadium", command=self.reset_stadium).pack(side="left", padx=4)
        self.side.trace_add("write", lambda *_: self.changed())
        self.canvas.bind("<Configure>", lambda event: self.render())
        for var in (game, home, away, venue):
            var.trace_add("write", lambda *_: self.render())
        self.render()

    def selected_team(self):
        side = self.side.get()
        if side == "YOUR TEAM":
            return self.home.get()
        if side == "OPPONENT":
            return self.away.get()
        if side == "HOME":
            return self.home.get() if self.venue.get() == "HOME" else self.away.get()
        return self.away.get() if self.venue.get() == "HOME" else self.home.get()

    def changed(self):
        try:
            PREFS.parent.mkdir(parents=True, exist_ok=True)
            PREFS.write_text(json.dumps({"enabled": self.enabled.get(),
                                         "side": self.side.get(), "opacity": self.opacity.get()}), encoding="utf-8")
        except OSError:
            pass
        self.render()

    def import_logo(self):
        team = self.selected_team()
        source = filedialog.askopenfilename(title="Import logo for " + team,
                         filetypes=[("Images", "*.png *.jpg *.jpeg *.webp")])
        if not source:
            return
        try:
            store_asset(self.game.get(), team, "logo", source)
        except (OSError, ValueError) as exc:
            messagebox.showerror("Logo import", str(exc))
            return
        self.render()

    def import_stadium(self):
        team = self.selected_team()
        source = filedialog.askopenfilename(title="Choose stadium photo for " + team,
                         filetypes=[("Images", "*.png *.jpg *.jpeg *.webp")])
        if not source:
            return
        try:
            store_asset(self.game.get(), team, "stadium", source)
        except (OSError, ValueError) as exc:
            messagebox.showerror("Stadium import", str(exc))
            return
        self.render()

    def reset_stadium(self):
        remove_asset(self.game.get(), self.selected_team(), "stadium")
        self.render()

    def render(self):
        if not self.canvas.winfo_exists():
            return
        team = self.selected_team()
        width = max(350, self.canvas.winfo_width())
        height = 118
        accent = COLORS.get(team, "#264d42")
        self.canvas.configure(bg=accent if self.enabled.get() else "#17221d")
        self.canvas.delete("all")
        self.photo = None
        self.stadium_photo = None
        if self.enabled.get():
            stadium_path = get_asset(self.game.get(), team, "stadium")
            if stadium_path:
                try:
                    from PIL import Image, ImageTk, ImageEnhance
                    with Image.open(stadium_path) as raw:
                        img = raw.convert("RGB")
                        ratio = max(width / img.width, height / img.height)
                        nw, nh = int(img.width * ratio) + 1, int(img.height * ratio) + 1
                        img = img.resize((nw, nh), Image.Resampling.LANCZOS)
                        left, top = (nw - width) // 2, (nh - height) // 2
                        img = img.crop((left, top, left + width, top + height))
                        img = ImageEnhance.Brightness(img).enhance(0.34)
                        self.stadium_photo = ImageTk.PhotoImage(img)
                        self.canvas.create_image(0, 0, anchor="nw", image=self.stadium_photo)
                except (ImportError, OSError, ValueError):
                    self.stadium_photo = None
            if self.stadium_photo is None:
                self.canvas.create_rectangle(0, 0, width, height, fill="#19382e", outline="")
                for x in range(0, width, 50):
                    self.canvas.create_line(x, 0, x + 65, height, fill="#315d49", width=2)
                self.canvas.create_text(width * .5, height * .5, text="GENERIC STADIUM" if is_custom_team(team) else stadium_label(team, self.game.get()),
                                        fill="#729986", font=("Segoe UI", 13, "bold"))
            path = get_asset(self.game.get(), team, "logo")
            if path:
                try:
                    from PIL import Image, ImageTk
                    with Image.open(path) as raw:
                        image = raw.convert("RGBA")
                        image.thumbnail((int(width * .48), 106), Image.Resampling.LANCZOS)
                        alpha = image.getchannel("A").point(lambda a: int(a * self.opacity.get() / 100))
                        image.putalpha(alpha)
                        self.photo = ImageTk.PhotoImage(image)
                        self.canvas.create_image(width * .69, 59, image=self.photo)
                except (ImportError, OSError, ValueError):
                    self.photo = None
            if self.photo is None:
                self.canvas.create_text(width * .71, 57, text=initials(team),
                                        fill="#8f9b9b", font=("Segoe UI", 45, "bold"))
        self.canvas.create_text(22, 28, anchor="w", text="SLIDERFORGE",
                                fill="#ffffff", font=("Segoe UI", 23, "bold"))
        self.canvas.create_text(22, 67, anchor="w", text=team,
                                fill="#ffffff", font=("Segoe UI", 15, "bold"))
        self.canvas.create_text(22, 97, anchor="w", text=self.game.get() + " • " + stadium_label(team, self.game.get()),
                                fill="#e2e8ea", font=("Segoe UI", 10))
