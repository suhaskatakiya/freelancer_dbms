"""
FREELANCER PLATFORM — Python Tkinter GUI
Restored original logic, removing ONLY the review section.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from datetime import date

# ── DB CONFIG ──
DB_CONFIG = dict(host="localhost", user="root",
                 password="suhas123", database="freelancer_db")


def get_conn():
    return mysql.connector.connect(**DB_CONFIG)


# ── COLOURS & FONTS ──
BG = "#F0F4FF"
SIDEBAR = "#1E3A5F"
ACCENT = "#2563EB"
WHITE = "#FFFFFF"
TEXT = "#1F2937"
MUTED = "#6B7280"
SUCCESS = "#10B981"
DANGER = "#EF4444"
FONT_H1 = ("Segoe UI", 20, "bold")
FONT_H2 = ("Segoe UI", 14, "bold")
FONT_BODY = ("Segoe UI", 11)
FONT_SM = ("Segoe UI", 9)


def styled_btn(parent, text, cmd, bg=ACCENT, fg=WHITE, **kw):
    return tk.Button(parent, text=text, command=cmd, bg=bg, fg=fg,
                     font=("Segoe UI", 10, "bold"), relief="flat",
                     padx=14, pady=6, cursor="hand2", **kw)


def entry_field(parent, placeholder="", show=""):
    frame = tk.Frame(parent, bg=WHITE, bd=1, relief="solid")
    e = tk.Entry(frame, font=FONT_BODY, bg=WHITE,
                 fg=TEXT, relief="flat", show=show)
    e.pack(fill="x", padx=6, pady=5)
    if placeholder:
        e.insert(0, placeholder)
        e.config(fg=MUTED)

        def fi(ev):
            if e.get() == placeholder:
                e.delete(0, "end")
                e.config(fg=TEXT)

        def fo(ev):
            if not e.get():
                e.insert(0, placeholder)
                e.config(fg=MUTED)
        e.bind("<FocusIn>", fi)
        e.bind("<FocusOut>", fo)
    return frame, e

# ═══════════════════════════════════════
#  LOGIN / REGISTER
# ═══════════════════════════════════════


class AuthWindow:
    def __init__(self, root):
        self.root = root
        root.title("FreelanceHub — Login")
        root.geometry("420x520")
        root.configure(bg=BG)
        root.resizable(False, False)
        self._build()

    def _build(self):
        hdr = tk.Frame(self.root, bg=SIDEBAR, height=90)
        hdr.pack(fill="x")
        tk.Label(hdr, text="FreelanceHub", font=("Segoe UI", 22, "bold"),
                 bg=SIDEBAR, fg=WHITE).pack(expand=True, pady=24)

        body = tk.Frame(self.root, bg=BG)
        body.pack(fill="both", expand=True, padx=36, pady=20)

        tab = tk.Frame(body, bg=BG)
        tab.pack(fill="x", pady=(0, 16))
        self.lt = tk.Button(tab, text="Login", font=("Segoe UI", 11, "bold"),
                            bg=ACCENT, fg=WHITE, relief="flat", padx=20, pady=6,
                            command=lambda: self._show("login"))
        self.lt.pack(side="left", padx=(0, 4))
        self.rt = tk.Button(tab, text="Register", font=("Segoe UI", 11),
                            bg=WHITE, fg=TEXT, relief="flat", padx=20, pady=6,
                            command=lambda: self._show("register"))
        self.rt.pack(side="left")

        self.lf = self._build_login(body)
        self.rf = self._build_register(body)
        self._show("login")

    def _build_login(self, p):
        f = tk.Frame(p, bg=BG)
        tk.Label(f, text="Email", font=FONT_BODY,
                 bg=BG, fg=TEXT).pack(anchor="w")
        ef, self.le = entry_field(f, "your@email.com")
        ef.pack(fill="x", pady=(2, 10))
        tk.Label(f, text="Password", font=FONT_BODY,
                 bg=BG, fg=TEXT).pack(anchor="w")
        pf, self.lp = entry_field(f, "password", show="*")
        pf.pack(fill="x", pady=(2, 16))
        styled_btn(f, "Login", self._login).pack(fill="x", ipady=4)
        return f

    def _build_register(self, p):
        f = tk.Frame(p, bg=BG)
        tk.Label(f, text="Full Name", font=FONT_BODY,
                 bg=BG, fg=TEXT).pack(anchor="w")
        nf, self.rn = entry_field(f, "John Doe")
        nf.pack(fill="x", pady=(2, 8))
        tk.Label(f, text="Email", font=FONT_BODY,
                 bg=BG, fg=TEXT).pack(anchor="w")
        ef, self.re = entry_field(f, "your@email.com")
        ef.pack(fill="x", pady=(2, 8))
        tk.Label(f, text="Password", font=FONT_BODY,
                 bg=BG, fg=TEXT).pack(anchor="w")
        pf, self.rp = entry_field(f, "Min 6 chars", show="*")
        pf.pack(fill="x", pady=(2, 8))
        tk.Label(f, text="Role", font=FONT_BODY,
                 bg=BG, fg=TEXT).pack(anchor="w")
        self.rr = ttk.Combobox(
            f, values=["client", "freelancer"], state="readonly", font=FONT_BODY)
        self.rr.set("client")
        self.rr.pack(fill="x", pady=(2, 14))
        styled_btn(f, "Create Account", self._register,
                   bg=SUCCESS).pack(fill="x", ipady=4)
        return f

    def _show(self, tab):
        self.lf.pack_forget()
        self.rf.pack_forget()
        if tab == "login":
            self.lt.config(bg=ACCENT, fg=WHITE, font=("Segoe UI", 11, "bold"))
            self.rt.config(bg=WHITE, fg=TEXT, font=("Segoe UI", 11))
            self.lf.pack(fill="both", expand=True)
        else:
            self.rt.config(bg=ACCENT, fg=WHITE, font=("Segoe UI", 11, "bold"))
            self.lt.config(bg=WHITE, fg=TEXT, font=("Segoe UI", 11))
            self.rf.pack(fill="both", expand=True)

    def _login(self):
        try:
            conn = get_conn()
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT * FROM users WHERE email=%s AND password=%s",
                        (self.le.get().strip(), self.lp.get().strip()))
            user = cur.fetchone()
            conn.close()
            if user:
                self.root.destroy()
                MainApp(user)
            else:
                messagebox.showerror("Error", "Invalid email or password.")
        except Exception as e:
            messagebox.showerror("DB Error", str(e))

    def _register(self):
        name = self.rn.get().strip()
        email = self.re.get().strip()
        pwd = self.rp.get().strip()
        if not all([name, email, pwd]):
            messagebox.showwarning("Missing", "Fill all fields.")
            return
        try:
            conn = get_conn()
            cur = conn.cursor()
            cur.execute("INSERT INTO users (full_name,email,password,role) VALUES (%s,%s,%s,%s)",
                        (name, email, pwd, self.rr.get()))
            conn.commit()
            conn.close()
            messagebox.showinfo("Done", "Account created! Please login.")
            self._show("login")
        except mysql.connector.IntegrityError:
            messagebox.showerror("Error", "Email already exists.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

# ═══════════════════════════════════════
#  MAIN APPLICATION
# ═══════════════════════════════════════


class MainApp:
    def __init__(self, user):
        self.user = user
        self.root = tk.Tk()
        self.root.title(f"FreelanceHub — {user['full_name']}")
        self.root.geometry("1100x680")
        self.root.configure(bg=BG)
        self._layout()
        self.root.mainloop()

    def _layout(self):
        sb = tk.Frame(self.root, bg=SIDEBAR, width=200)
        sb.pack(side="left", fill="y")
        sb.pack_propagate(False)
        tk.Label(sb, text="FreelanceHub", font=("Segoe UI", 14, "bold"),
                 bg=SIDEBAR, fg=WHITE).pack(pady=(24, 2), padx=12)
        tk.Label(sb, text=self.user['full_name'], font=FONT_SM,
                 bg=SIDEBAR, fg="#93C5FD").pack()
        tk.Label(sb, text=f"[{self.user['role'].upper()}]",
                 font=("Segoe UI", 8), bg=SIDEBAR, fg="#64748B").pack(pady=(0, 16))
        ttk.Separator(sb, orient="horizontal").pack(fill="x", padx=16)

        for label, cmd in self._nav():
            tk.Button(sb, text=label, command=cmd, bg=SIDEBAR, fg="#CBD5E1",
                      font=("Segoe UI", 11), relief="flat", anchor="w",
                      padx=20, pady=10, cursor="hand2",
                      activebackground="#2D4E7A",
                      activeforeground=WHITE).pack(fill="x")

        tk.Frame(sb, bg=SIDEBAR).pack(expand=True, fill="y")
        styled_btn(sb, "Logout", self._logout, bg="#374151").pack(
            fill="x", padx=16, pady=16)

        self.content = tk.Frame(self.root, bg=BG)
        self.content.pack(side="right", fill="both", expand=True)
        self._dashboard()

    def _nav(self):
        r = self.user['role']
        items = [("  Dashboard", self._dashboard)]
        if r == 'client':
            items += [("  Post Project", self._post_project),
                      ("  My Projects",  self._my_projects),
                      ("  Payments",     self._payments)]
        else:
            items += [("  Browse Projects", self._browse),
                      ("  My Bids",         self._my_bids),
                      ("  My Contracts",    self._my_contracts),
                      ("  Earnings",        self._earnings)]
        return items

    def _clear(self):
        for w in self.content.winfo_children():
            w.destroy()

    def _hdr(self, title, sub=""):
        h = tk.Frame(self.content, bg=WHITE,
                     highlightbackground="#E5E7EB", highlightthickness=1)
        h.pack(fill="x")
        tk.Label(h, text=title, font=FONT_H1, bg=WHITE,
                 fg=TEXT).pack(side="left", padx=28, pady=20)
        if sub:
            tk.Label(h, text=sub, font=FONT_BODY,
                     bg=WHITE, fg=MUTED).pack(side="left")

    def _treeview(self, parent, cols, height=10):
        f = tk.Frame(parent, bg=BG)
        f.pack(fill="both", expand=True)
        tree = ttk.Treeview(f, columns=cols, show="headings", height=height)
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=140, anchor="center")
        sb2 = ttk.Scrollbar(f, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb2.set)
        tree.pack(side="left", fill="both", expand=True)
        sb2.pack(side="right", fill="y")
        return tree

    def _dashboard(self):
        self._clear()
        self._hdr("Dashboard", f"  Welcome, {self.user['full_name']}!")
        body = tk.Frame(self.content, bg=BG)
        body.pack(fill="both", expand=True, padx=28, pady=20)
        try:
            conn = get_conn()
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM projects WHERE status='open'")
            open_p = cur.fetchone()[0]
            if self.user['role'] == 'client':
                cur.execute(
                    "SELECT COUNT(*) FROM projects WHERE client_id=%s", (self.user['user_id'],))
                mine = cur.fetchone()[0]
                cur.execute(
                    "SELECT COUNT(*) FROM bids b JOIN projects p ON b.project_id=p.project_id WHERE p.client_id=%s AND b.status='pending'", (self.user['user_id'],))
                pend = cur.fetchone()[0]
                cards = [("Open Projects", open_p, "#DBEAFE"), ("My Projects",
                                                                mine, "#D1FAE5"), ("Pending Bids", pend, "#FEF3C7")]
            else:
                cur.execute(
                    "SELECT COUNT(*) FROM bids WHERE freelancer_id=%s", (self.user['user_id'],))
                mine = cur.fetchone()[0]
                cur.execute(
                    "SELECT COUNT(*) FROM contracts WHERE freelancer_id=%s AND status='active'", (self.user['user_id'],))
                active_contracts = cur.fetchone()[0]
                cur.execute(
                    "SELECT COALESCE(SUM(pay.amount),0) FROM payments pay JOIN contracts c ON pay.contract_id=c.contract_id WHERE c.freelancer_id=%s AND pay.status='completed'", (self.user['user_id'],))
                earned = cur.fetchone()[0]
                cards = [("Open Projects", open_p, "#DBEAFE"), ("My Bids", mine, "#D1FAE5"), ("Active Contracts",
                                                                                              active_contracts, "#D1FAE5"), (f"Total Earned", f"Rs.{earned:,.0f}", "#F3E8FF")]
            conn.close()
        except:
            cards = [("Open Projects", 0, "#DBEAFE"),
                     ("Mine", 0, "#D1FAE5"), ("Other", 0, "#FEF3C7")]

        row = tk.Frame(body, bg=BG)
        row.pack(fill="x", pady=(0, 20))
        for lbl, val, color in cards:
            c = tk.Frame(
                row, bg=color, highlightbackground="#E5E7EB", highlightthickness=1)
            c.pack(side="left", expand=True, fill="x", padx=8, ipady=16)
            tk.Label(c, text=str(val), font=(
                "Segoe UI", 28, "bold"), bg=color, fg=TEXT).pack()
            tk.Label(c, text=lbl, font=FONT_BODY, bg=color, fg=MUTED).pack()

        tk.Label(body, text="Recent Open Projects", font=FONT_H2,
                 bg=BG, fg=ACCENT).pack(anchor="w", pady=(8, 4))
        self._load_projects_tree(body, limit=5)

    def _load_projects_tree(self, parent, limit=None, client_id=None):
        cols = ("ID", "Title", "Budget", "Deadline", "Status", "Client")
        tree = self._treeview(parent, cols, height=7)
        tree.column("Title", width=220, anchor="w")
        try:
            conn = get_conn()
            cur = conn.cursor()
            q = "SELECT p.project_id,p.title,p.budget,p.deadline,p.status,u.full_name FROM projects p JOIN users u ON p.client_id=u.user_id"
            params = []
            if client_id:
                q += " WHERE p.client_id=%s"
                params.append(client_id)
            else:
                q += " WHERE p.status='open'"
            q += " ORDER BY p.created_at DESC"
            if limit:
                q += f" LIMIT {limit}"
            cur.execute(q, params)
            for r in cur.fetchall():
                tree.insert("", "end", values=(
                    r[0], r[1], f"Rs.{r[2]:,.0f}", str(r[3]) if r[3] else "-", r[4], r[5]))
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", str(e))
        return tree

    def _post_project(self):
        self._clear()
        self._hdr("Post a New Project")
        body = tk.Frame(self.content, bg=BG)
        body.pack(fill="both", expand=True, padx=28, pady=20)
        frm = tk.Frame(body, bg=WHITE, highlightbackground="#E5E7EB",
                       highlightthickness=1, padx=24, pady=16)
        frm.pack(fill="x")
        fields = {}
        for lbl, ph in [("Title", "e.g. Build a mobile app"), ("Budget", "e.g. 5000"), ("Deadline", "YYYY-MM-DD")]:
            tk.Label(frm, text=lbl, font=FONT_BODY, bg=WHITE,
                     fg=TEXT).pack(anchor="w", pady=(8, 2))
            fr, ent = entry_field(frm, ph)
            fr.pack(fill="x")
            fields[lbl] = ent
        tk.Label(frm, text="Description", font=FONT_BODY,
                 bg=WHITE, fg=TEXT).pack(anchor="w", pady=(8, 2))
        desc = tk.Text(frm, height=4, font=FONT_BODY, relief="solid", bd=1)
        desc.pack(fill="x")

        def submit():
            try:
                conn = get_conn()
                cur = conn.cursor()
                cur.execute("INSERT INTO projects (client_id,title,description,budget,deadline) VALUES (%s,%s,%s,%s,%s)",
                            (self.user['user_id'], fields["Title"].get(), desc.get("1.0", "end").strip(),
                             float(fields["Budget"].get()), fields["Deadline"].get() or None))
                conn.commit()
                conn.close()
                messagebox.showinfo("Done", "Project posted!")
                self._my_projects()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        styled_btn(frm, "Post Project", submit).pack(anchor="w", pady=(14, 0))

    def _my_projects(self):
        self._clear()
        self._hdr("My Projects")
        body = tk.Frame(self.content, bg=BG)
        body.pack(fill="both", expand=True, padx=28, pady=20)
        tree = self._load_projects_tree(body, client_id=self.user['user_id'])

        def view_bids():
            sel = tree.selection()
            if not sel:
                messagebox.showinfo("Select", "Select a project.")
                return
            self._bids_for(tree.item(sel[0])['values'][0])

        styled_btn(body, "View Bids", view_bids).pack(anchor="w", pady=8)

    def _bids_for(self, pid):
        self._clear()
        self._hdr(f"Bids on Project #{pid}")
        body = tk.Frame(self.content, bg=BG)
        body.pack(fill="both", expand=True, padx=28, pady=20)
        cols = ("BidID", "Freelancer", "Amount", "Status", "Proposal")
        tree = self._treeview(body, cols)
        tree.column("Proposal", width=300, anchor="w")
        try:
            conn = get_conn()
            cur = conn.cursor()
            cur.execute(
                "SELECT b.bid_id,u.full_name,b.amount,b.status,b.proposal FROM bids b JOIN users u ON b.freelancer_id=u.user_id WHERE b.project_id=%s", (pid,))
            for r in cur.fetchall():
                tree.insert("", "end", values=(
                    r[0], r[1], f"Rs.{r[2]:,.0f}", r[3], r[4]))
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", str(e))

        def accept():
            sel = tree.selection()
            if not sel:
                return
            bid_id = tree.item(sel[0])['values'][0]
            if messagebox.askyesno("Confirm", f"Accept bid #{bid_id}?"):
                try:
                    conn = get_conn()
                    cur = conn.cursor()
                    cur.callproc("accept_bid", [bid_id])
                    conn.commit()
                    conn.close()
                    messagebox.showinfo(
                        "Done", "Bid accepted! Contract created.")
                    self._my_projects()
                except Exception as e:
                    messagebox.showerror("Error", str(e))

        styled_btn(body, "Accept Selected Bid", accept,
                   bg=SUCCESS).pack(anchor="w", pady=8)

    def _browse(self):
        self._clear()
        self._hdr("Browse Open Projects")
        body = tk.Frame(self.content, bg=BG)
        body.pack(fill="both", expand=True, padx=28, pady=20)
        tree = self._load_projects_tree(body)
        tree.column("ID",       width=40,  anchor="center")
        tree.column("Title",    width=250, anchor="w")
        tree.column("Budget",   width=100, anchor="center")
        tree.column("Deadline", width=100, anchor="center")
        tree.column("Status",   width=90,  anchor="center")
        tree.column("Client",   width=150, anchor="w")

        frm = tk.Frame(body, bg=WHITE, highlightbackground="#E5E7EB",
                       highlightthickness=1, padx=20, pady=12)
        frm.pack(fill="x", pady=10)
        tk.Label(frm, text="Place a Bid", font=FONT_H2,
                 bg=WHITE, fg=ACCENT).pack(anchor="w")
        row = tk.Frame(frm, bg=WHITE)
        row.pack(fill="x", pady=6)
        tk.Label(row, text="Amount:", font=FONT_BODY,
                 bg=WHITE, fg=TEXT).pack(side="left")
        _, amt = entry_field(row, "e.g. 4500")
        amt.master.pack(side="left", padx=8)
        tk.Label(frm, text="Your Proposal:", font=FONT_BODY,
                 bg=WHITE, fg=TEXT).pack(anchor="w", pady=(4, 2))
        prop = tk.Text(frm, height=3, font=FONT_BODY, relief="solid", bd=1)
        prop.pack(fill="x")

        def bid():
            sel = tree.selection()
            if not sel:
                messagebox.showinfo("Select", "Select a project first.")
                return
            pid = tree.item(sel[0])['values'][0]
            try:
                conn = get_conn()
                cur = conn.cursor()
                cur.callproc("place_bid", [pid, self.user['user_id'], float(
                    amt.get()), prop.get("1.0", "end").strip()])
                conn.commit()
                conn.close()
                messagebox.showinfo("Done", "Bid placed successfully!")
                amt.delete(0, "end")
                prop.delete("1.0", "end")
            except Exception as e:
                messagebox.showerror("Error", str(e))

        styled_btn(frm, "Submit Bid", bid).pack(anchor="w", pady=(10, 0))

    def _my_bids(self):
        self._clear()
        self._hdr("My Bids")
        body = tk.Frame(self.content, bg=BG)
        body.pack(fill="both", expand=True, padx=28, pady=20)
        cols = ("BidID", "Project", "Client", "Amount", "Status", "Date")
        tree = self._treeview(body, cols)
        try:
            conn = get_conn()
            cur = conn.cursor()
            cur.execute("""SELECT b.bid_id,p.title,u.full_name,b.amount,b.status,b.created_at
                           FROM bids b JOIN projects p ON b.project_id=p.project_id
                           JOIN users u ON p.client_id=u.user_id
                           WHERE b.freelancer_id=%s ORDER BY b.created_at DESC""", (self.user['user_id'],))
            for r in cur.fetchall():
                tree.insert("", "end", values=(
                    r[0], r[1], r[2], f"Rs.{r[3]:,.0f}", r[4], str(r[5])[:10]))
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _my_contracts(self):
        self._clear()
        self._hdr("My Contracts", "  Bids you won")
        body = tk.Frame(self.content, bg=BG)
        body.pack(fill="both", expand=True, padx=28, pady=20)

        cols = ("ContractID", "Project Title", "Client",
                "Agreed Amount", "Start Date", "Status")
        tree = self._treeview(body, cols, height=8)
        try:
            conn = get_conn()
            cur = conn.cursor()
            cur.execute("""SELECT c.contract_id, p.title, u.full_name, c.agreed_amount, c.start_date, c.status
                FROM contracts c JOIN projects p ON c.project_id = p.project_id
                JOIN users u ON c.client_id = u.user_id WHERE c.freelancer_id = %s""", (self.user['user_id'],))
            for r in cur.fetchall():
                tree.insert("", "end", values=(
                    r[0], r[1], r[2], f"Rs.{r[3]:,.0f}", str(r[4]), r[5]))
            conn.close()
        except Exception as e:
            messagebox.showerror("DB Error", str(e))

    def _payments(self):
        self._clear()
        self._hdr("Payments")
        body = tk.Frame(self.content, bg=BG)
        body.pack(fill="both", expand=True, padx=28, pady=20)
        cols = ("ContractID", "Project", "Freelancer", "Amount", "Status")
        tree = self._treeview(body, cols, height=7)
        try:
            conn = get_conn()
            cur = conn.cursor()
            cur.execute(
                "SELECT c.contract_id,p.title,u.full_name,c.agreed_amount,c.status FROM contracts c JOIN projects p ON c.project_id=p.project_id JOIN users u ON c.freelancer_id=u.user_id WHERE c.client_id=%s", (self.user['user_id'],))
            for r in cur.fetchall():
                tree.insert("", "end", values=(
                    r[0], r[1], r[2], f"Rs.{r[3]:,.0f}", r[4]))
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", str(e))

        frm = tk.Frame(body, bg=WHITE, highlightbackground="#E5E7EB",
                       highlightthickness=1, padx=20, pady=12)
        frm.pack(fill="x", pady=10)
        tk.Label(frm, text="Make Payment", font=FONT_H2,
                 bg=WHITE, fg=ACCENT).pack(anchor="w")
        row = tk.Frame(frm, bg=WHITE)
        row.pack(fill="x", pady=6)
        tk.Label(row, text="Method:", font=FONT_BODY,
                 bg=WHITE).pack(side="left")
        method = ttk.Combobox(
            row, values=["credit_card", "bank_transfer", "wallet"], state="readonly")
        method.set("wallet")
        method.pack(side="left", padx=8)

        def pay():
            sel = tree.selection()
            if not sel:
                return
            cid = tree.item(sel[0])['values'][0]
            amt = str(tree.item(sel[0])['values'][3]).replace(
                "Rs.", "").replace(",", "")
            try:
                conn = get_conn()
                cur = conn.cursor()
                cur.callproc("make_payment", [cid, float(amt), method.get()])
                conn.commit()
                conn.close()
                messagebox.showinfo("Done", "Payment successful!")
                self._payments()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        styled_btn(frm, "Pay Now", pay, bg=SUCCESS).pack(
            anchor="w", pady=(10, 0))

    def _earnings(self):
        self._clear()
        self._hdr("My Earnings")
        body = tk.Frame(self.content, bg=BG)
        body.pack(fill="both", expand=True, padx=28, pady=20)
        cols = ("PaymentID", "Project", "Amount", "Method", "Date", "Status")
        tree = self._treeview(body, cols)
        total = 0
        try:
            conn = get_conn()
            cur = conn.cursor()
            cur.execute("""SELECT pay.payment_id,p.title,pay.amount,pay.method,pay.payment_date,pay.status
                           FROM payments pay JOIN contracts c ON pay.contract_id=c.contract_id
                           JOIN projects p ON c.project_id=p.project_id
                           WHERE c.freelancer_id=%s""", (self.user['user_id'],))
            for r in cur.fetchall():
                tree.insert("", "end", values=(
                    r[0], r[1], f"Rs.{r[2]:,.0f}", r[3], str(r[4])[:10], r[5]))
                if r[5] == 'completed':
                    total += float(r[2])
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", str(e))
        tk.Label(body, text=f"Total Earned: Rs.{total:,.2f}",
                 font=FONT_H2, bg=BG, fg=SUCCESS).pack(anchor="e")

    def _logout(self):
        self.root.destroy()
        root = tk.Tk()
        AuthWindow(root)
        root.mainloop()


if __name__ == "__main__":
    root = tk.Tk()
    AuthWindow(root)
    root.mainloop()
