import tkinter as tk
from tkinter import ttk, messagebox
import requests

# ── Groq API ───────────────────────────────────────────────────────────────
API_KEY = "key_here"

def ask_groq(messages):
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {API_KEY}"},
        json={
            "model": "llama-3.1-8b-instant",
            "messages": messages
        }
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

# ── Colour palette ─────────────────────────────────────────────────────────
BG       = "#1e1e2e"
CARD     = "#2a2a3e"
ACCENT   = "#7c6af7"
ACCENT2  = "#a78bfa"
TEXT     = "#e2e8f0"
MUTED    = "#94a3b8"
ENTRY_BG = "#13131f"
BTN_HVR  = "#6d5ce6"

# ── Chip options ───────────────────────────────────────────────────────────
CHIP_SKILLS    = ["Coding / programming","Drawing / design","Mathematics","Writing",
                  "Communication","Photography","Research","Leadership",
                  "Problem-solving","Languages"]
CHIP_HOBBIES   = ["Gaming","Reading","Painting / art","Music","Sports",
                  "Cooking","Blogging / vlogging","Building things",
                  "Helping others","Travel"]
CHIP_INTERESTS = ["Technology / AI","Healthcare","Business","Creative arts",
                  "Science","Education","Law / justice","Finance",
                  "Media / content","Social work"]
STUDIES = [
    "Matric",
    "Intermediate — Pre-Medical",
    "Intermediate — Pre-Engineering",
    "Intermediate — ICS (Computer Science)",
    "Intermediate — Commerce",
    "Bachelor's — CS / IT",
    "Bachelor's — Business",
    "Bachelor's — Engineering",
    "Bachelor's — Medical",
    "Bachelor's — Arts / Humanities",
    "Other"
]

# ── Helper: scrollable frame ───────────────────────────────────────────────
def make_scroll_frame(parent):
    canvas = tk.Canvas(parent, bg=BG, highlightthickness=0)
    sb = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
    frame = tk.Frame(canvas, bg=BG)
    frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=frame, anchor="nw")
    canvas.configure(yscrollcommand=sb.set)
    canvas.pack(side="left", fill="both", expand=True)
    sb.pack(side="right", fill="y")
    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    canvas.bind_all("<MouseWheel>", _on_mousewheel)
    return frame, canvas

# ── Main App ───────────────────────────────────────────────────────────────
class CareerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("")
        self.root.geometry("720x680")
        self.root.configure(bg=BG)
        self.root.resizable(False, False)

        self.name     = tk.StringVar()
        self.age      = tk.StringVar()
        self.career   = tk.StringVar()
        self.study    = tk.StringVar(value=STUDIES[0])
        self.sel_skills    = []
        self.sel_hobbies   = []
        self.sel_interests = []
        self.skills_text_extra = ""
        self.chat_history = []  # stores full conversation for Groq

        self._build_header()
        self._build_step_bar()
        self.content = tk.Frame(self.root, bg=BG)
        self.content.pack(fill="both", expand=True)
        self.show_step1()

    def _build_header(self):
        h = tk.Frame(self.root, bg=ACCENT, pady=12)
        h.pack(fill="x")
        tk.Label(h, text="🎓  AI Career Counsellor",
                 font=("Segoe UI", 16, "bold"), bg=ACCENT, fg="white").pack()
        self.sub_lbl = tk.Label(h, text="Step 1 of 3 — tell us about yourself",
                 font=("Segoe UI", 9), bg=ACCENT, fg="#ddd6fe")
        self.sub_lbl.pack(pady=(2, 0))

    def _build_step_bar(self):
        bar_frame = tk.Frame(self.root, bg=BG, pady=8)
        bar_frame.pack(fill="x", padx=30)
        self.dots = []
        for i in range(3):
            d = tk.Frame(bar_frame, bg=MUTED, height=4)
            d.pack(side="left", fill="x", expand=True, padx=3)
            self.dots.append(d)

    def set_step(self, n, subtitle):
        self.sub_lbl.config(text=subtitle)
        for i, d in enumerate(self.dots):
            d.config(bg=ACCENT if i < n else MUTED)

    def clear(self):
        for w in self.content.winfo_children():
            w.destroy()

    def _lbl_entry(self, parent, label, var, placeholder="", width=38):
        tk.Label(parent, text=label, font=("Segoe UI", 9),
                 bg=BG, fg=MUTED).pack(anchor="w")
        f = tk.Frame(parent, bg=CARD, highlightbackground=ACCENT, highlightthickness=1)
        f.pack(fill="x", pady=(2, 10))
        e = tk.Entry(f, textvariable=var, font=("Segoe UI", 11),
                     bg=ENTRY_BG, fg=TEXT, relief="flat",
                     insertbackground=TEXT, width=width)
        e.pack(fill="x", padx=10, pady=7)
        if placeholder and not var.get():
            e.insert(0, placeholder)
            e.config(fg=MUTED)
            def on_focus_in(ev):
                if e.get() == placeholder:
                    e.delete(0, "end")
                    e.config(fg=TEXT)
            def on_focus_out(ev):
                if not e.get():
                    e.insert(0, placeholder)
                    e.config(fg=MUTED)
            e.bind("<FocusIn>", on_focus_in)
            e.bind("<FocusOut>", on_focus_out)
        return e

    def _chips(self, parent, label, options, selected_list):
        tk.Label(parent, text=label, font=("Segoe UI", 10, "bold"),
                 bg=BG, fg=ACCENT2).pack(anchor="w", pady=(8, 3))
        wrap = tk.Frame(parent, bg=BG)
        wrap.pack(fill="x")
        row = tk.Frame(wrap, bg=BG)
        row.pack(fill="x")
        col_count = 0
        for opt in options:
            is_sel = [opt in selected_list]
            btn = tk.Button(row, text=opt,
                            font=("Segoe UI", 9),
                            bg=ACCENT if opt in selected_list else CARD,
                            fg="white" if opt in selected_list else MUTED,
                            relief="flat", cursor="hand2",
                            padx=8, pady=4)
            btn.pack(side="left", padx=3, pady=2)
            col_count += 1
            if col_count % 4 == 0:
                row = tk.Frame(wrap, bg=BG)
                row.pack(fill="x")
            def toggle(o=opt, b=btn, sl=selected_list, issel=is_sel):
                if issel[0]:
                    sl.remove(o)
                    b.config(bg=CARD, fg=MUTED)
                    issel[0] = False
                else:
                    sl.append(o)
                    b.config(bg=ACCENT, fg="white")
                    issel[0] = True
            btn.config(command=toggle)

    # ── STEP 1 ─────────────────────────────────────────────────────────────
    def show_step1(self):
        self.clear()
        self.set_step(1, "Step 1 of 3 — tell us about yourself")
        sf, _ = make_scroll_frame(self.content)
        pad = tk.Frame(sf, bg=BG, padx=30)
        pad.pack(fill="x", pady=10)

        self._lbl_entry(pad, "Full name", self.name, "Your full name")
        self._lbl_entry(pad, "Age", self.age, "e.g. 17", width=10)

        tk.Label(pad, text="Any career in mind?  (optional)",
                 font=("Segoe UI", 9), bg=BG, fg=MUTED).pack(anchor="w")
        f = tk.Frame(pad, bg=CARD, highlightbackground=ACCENT, highlightthickness=1)
        f.pack(fill="x", pady=(2, 10))
        tk.Entry(f, textvariable=self.career, font=("Segoe UI", 11),
                 bg=ENTRY_BG, fg=TEXT, relief="flat",
                 insertbackground=TEXT).pack(fill="x", padx=10, pady=7)

        btn_row = tk.Frame(pad, bg=BG)
        btn_row.pack(fill="x", pady=6)
        tk.Button(btn_row, text="Next  →",
                  font=("Segoe UI", 11, "bold"),
                  bg=ACCENT, fg="white",
                  activebackground=BTN_HVR,
                  relief="flat", cursor="hand2",
                  padx=18, pady=8,
                  command=self._next1).pack(side="right")

    def _next1(self):
        if not self.name.get().strip() or self.name.get().strip() == "Your full name":
            messagebox.showwarning("Missing info", "Please enter your name.")
            return
        if not self.age.get().strip() or self.age.get().strip() == "e.g. 17":
            messagebox.showwarning("Missing info", "Please enter your age.")
            return
        self.show_step2()

    # ── STEP 2 ─────────────────────────────────────────────────────────────
    def show_step2(self):
        self.clear()
        self.set_step(2, "Step 2 of 3 — your education")
        sf, _ = make_scroll_frame(self.content)
        pad = tk.Frame(sf, bg=BG, padx=30)
        pad.pack(fill="x", pady=10)

        tk.Label(pad, text="What are you currently studying?",
                 font=("Segoe UI", 10, "bold"), bg=BG, fg=ACCENT2).pack(anchor="w", pady=(4, 6))
        cb = ttk.Combobox(pad, textvariable=self.study,
                          values=STUDIES, state="readonly",
                          font=("Segoe UI", 11), width=44)
        cb.pack(anchor="w", pady=(0, 16))

        btn_row = tk.Frame(pad, bg=BG)
        btn_row.pack(fill="x", pady=6)
        tk.Button(btn_row, text="← Back",
                  font=("Segoe UI", 10), bg=CARD, fg=MUTED,
                  relief="flat", cursor="hand2",
                  padx=12, pady=6,
                  command=self.show_step1).pack(side="left")
        tk.Button(btn_row, text="Next  →",
                  font=("Segoe UI", 11, "bold"),
                  bg=ACCENT, fg="white",
                  activebackground=BTN_HVR,
                  relief="flat", cursor="hand2",
                  padx=18, pady=8,
                  command=self.show_step3).pack(side="right")

    # ── STEP 3 ─────────────────────────────────────────────────────────────
    def show_step3(self):
        self.clear()
        self.set_step(3, "Step 3 of 3 — your skills & interests")
        sf, canvas = make_scroll_frame(self.content)
        pad = tk.Frame(sf, bg=BG, padx=30)
        pad.pack(fill="x", pady=10)

        self._chips(pad, "Skills  (tap to select)", CHIP_SKILLS, self.sel_skills)

        tk.Label(pad, text="Anything else? (optional)",
                 font=("Segoe UI", 9), bg=BG, fg=MUTED).pack(anchor="w", pady=(6, 2))
        f = tk.Frame(pad, bg=CARD, highlightbackground=ACCENT, highlightthickness=1)
        f.pack(fill="x", pady=(0, 8))
        self.extra_skills_box = tk.Text(f, height=2, font=("Segoe UI", 10),
                                        bg=ENTRY_BG, fg=TEXT, relief="flat",
                                        padx=8, pady=6, insertbackground=TEXT)
        self.extra_skills_box.pack(fill="x")

        self._chips(pad, "Hobbies", CHIP_HOBBIES, self.sel_hobbies)
        self._chips(pad, "Interests", CHIP_INTERESTS, self.sel_interests)

        btn_row = tk.Frame(pad, bg=BG)
        btn_row.pack(fill="x", pady=12)
        tk.Button(btn_row, text="← Back",
                  font=("Segoe UI", 10), bg=CARD, fg=MUTED,
                  relief="flat", cursor="hand2",
                  padx=12, pady=6,
                  command=self.show_step2).pack(side="left")
        tk.Button(btn_row, text="✨  Get My Results",
                  font=("Segoe UI", 11, "bold"),
                  bg=ACCENT, fg="white",
                  activebackground=BTN_HVR,
                  relief="flat", cursor="hand2",
                  padx=18, pady=8,
                  command=self._submit).pack(side="right")

    # ── SUBMIT — sends to AI ─────────────────────────────────────────────
    def _submit(self):
        extra = self.extra_skills_box.get("1.0", "end").strip()
        if not self.sel_skills and not extra:
            messagebox.showwarning("Missing info", "Please select at least one skill.")
            return
        self.skills_text_extra = extra
        all_skills = self.sel_skills + ([extra] if extra else [])

        # Build the first prompt with all user info
        system_msg = {
            "role": "system",
            "content": (
            "You are a friendly Pakistani career counsellor. "
            "Suggest careers relevant to Pakistan's job market. "
            "Be warm, encouraging, and concise."
            )
        }
        user_msg = {
    "role": "user",
    "content": (
        f"My name is {self.name.get()}, I am {self.age.get()} years old, "
        f"currently studying {self.study.get()}. "

        f"My skills are: {', '.join(all_skills)}. "
        f"My hobbies are: {', '.join(self.sel_hobbies)}. "
        f"My interests are: {', '.join(self.sel_interests)}. "
        f"Career I have in mind: {self.career.get() or 'none'}. "

        "Please suggest ONLY 3 careers.\n\n"
        "For each career:\n"
        "Career Name:\n"
        "Why it suits me:\n"
        "Next Step:\n"
        "Motivation:\n"
    )
}
        

        # Store chat history starting with system + first user message
        self.chat_history = [system_msg, user_msg]

        # Show loading
        self.clear()
        self.set_step(3, f"Results for {self.name.get()}")
        sf, _ = make_scroll_frame(self.content)
        pad = tk.Frame(sf, bg=BG, padx=24)
        pad.pack(fill="x", pady=10)
        tk.Label(pad, text="⏳ Getting your personalised results...",
                 font=("Segoe UI", 11), bg=BG, fg=MUTED).pack(pady=40)
        self.root.update()

        try:
            reply = ask_groq(self.chat_history)
            # Add assistant reply to history so chat remembers context
            self.chat_history.append({"role": "assistant", "content": reply})
            self._show_results(reply)
        except Exception as e:
            messagebox.showerror("API Error", f"Could not reach Groq:\n{e}")

    # ── RESULTS + CHAT ─────────────────────────────────────────────────────
    def _show_results(self, initial_reply):
        self.clear()
        self.set_step(3, f"Results for {self.name.get()}")
        sf, _ = make_scroll_frame(self.content)
        pad = tk.Frame(sf, bg=BG, padx=24)
        pad.pack(fill="x", pady=10)

        tk.Label(pad,
                 text=f"Hi {self.name.get()}! Here are your personalised career suggestions 🌟",
                 font=("Segoe UI", 10, "bold"), bg=BG, fg=TEXT,
                 wraplength=640).pack(pady=(0, 8))

        # Show AI career suggestions in a text box
        result_box = tk.Text(pad, font=("Segoe UI", 10), bg=CARD, fg=TEXT,
                             relief="flat", wrap="word", padx=12, pady=10,
                             height=14, insertbackground=TEXT)
        clean_reply = initial_reply.replace("Career Name:", "\n🌟 Career Name:")
        clean_reply = clean_reply.replace("Why it suits me:", "\n💡 Why it suits me:")
        clean_reply = clean_reply.replace("Next Step:", "\n🎯 Next Step:")
        clean_reply = clean_reply.replace("Motivation:", "\n✨ Motivation:")

        result_box.insert("1.0", clean_reply)
        result_box.config(state="disabled")
        result_box.pack(fill="x", pady=(0, 10))

        # ── Chat section ───────────────────────────────────────────────────
        tk.Label(pad, text="💬 Ask a follow-up question",
                 font=("Segoe UI", 10, "bold"), bg=BG, fg=ACCENT2).pack(anchor="w", pady=(6, 3))

        # Chat display box
        self.chat_box = tk.Text(pad, font=("Segoe UI", 10), bg=ENTRY_BG, fg=TEXT,
                                relief="flat", wrap="word", padx=10, pady=8,
                                height=8, insertbackground=TEXT, state="disabled")
        self.chat_box.pack(fill="x", pady=(0, 6))

        # Input row
        input_row = tk.Frame(pad, bg=BG)
        input_row.pack(fill="x", pady=(0, 6))

        self.chat_input = tk.Entry(input_row, font=("Segoe UI", 10),
                                   bg=ENTRY_BG, fg=TEXT, relief="flat",
                                   insertbackground=TEXT)
        self.chat_input.pack(side="left", fill="x", expand=True, padx=(0, 6), ipady=7)
        self.chat_input.bind("<Return>", lambda e: self._send_chat())

        tk.Button(input_row, text="Send",
                  font=("Segoe UI", 10, "bold"),
                  bg=ACCENT, fg="white",
                  activebackground=BTN_HVR,
                  relief="flat", cursor="hand2",
                  padx=14, pady=6,
                  command=self._send_chat).pack(side="right")

        # Footer
        btn_row = tk.Frame(pad, bg=BG)
        btn_row.pack(pady=8)
        tk.Button(btn_row, text="🔄  Start Over",
                  font=("Segoe UI", 10), bg=CARD, fg=MUTED,
                  relief="flat", cursor="hand2",
                  command=self._reset).pack()

    def _send_chat(self):
        user_text = self.chat_input.get().strip()
        if not user_text:
            return

        # Show user message in chat box
        self.chat_box.config(state="normal")
        self.chat_box.insert("end", f"You: {user_text}\n")
        self.chat_box.config(state="disabled")
        self.chat_input.delete(0, "end")
        self.root.update()

        # Add to history and call AI
        self.chat_history.append({"role": "user", "content": user_text})

        try:
            reply = ask_groq(self.chat_history)
            self.chat_history.append({"role": "assistant", "content": reply})
            self.chat_box.config(state="normal")
            self.chat_box.insert("end", f"AI: {reply}\n\n")
            self.chat_box.config(state="disabled")
            self.chat_box.see("end")
        except Exception as e:
            self.chat_box.config(state="normal")
            self.chat_box.insert("end", f"❌ Error: {e}\n\n")
            self.chat_box.config(state="disabled")

    def _reset(self):
        self.name.set("")
        self.age.set("")
        self.career.set("")
        self.study.set(STUDIES[0])
        self.sel_skills.clear()
        self.sel_hobbies.clear()
        self.sel_interests.clear()
        self.skills_text_extra = ""
        self.chat_history = []
        self.show_step1()

# ── Run ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    app = CareerApp(root)
    root.mainloop()