import sympy as sp
import tkinter as tk
from tkinter import ttk, scrolledtext
from sympy import symbols, cos, sin, simplify



def dh_transform(a, alpha, d, theta):
    C, S = cos(theta), sin(theta)
    return sp.Matrix([
        [C, -S * cos(alpha), S * sin(alpha), a * C],
        [S, C * cos(alpha), -C * sin(alpha), a * S],
        [0, sin(alpha), cos(alpha), d],
        [0, 0, 0, 1]
    ])



def deg_to_rad(deg):
    return deg * sp.pi / 180



class DHCalculatorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Calculateur Cinématique DH")
        self.geometry("900x700")
        self.configure(bg="#f0f0f0")
        self.dh_params = []
        self.create_widgets()

    def create_widgets(self):
        input_frame = ttk.LabelFrame(self, text="Paramètres DH")
        input_frame.pack(pady=10, padx=10, fill="x")

        ttk.Label(input_frame, text="Nombre de liens:").grid(row=0, column=0)
        self.num_links = ttk.Entry(input_frame)
        self.num_links.grid(row=0, column=1)

        ttk.Button(input_frame, text="Générer les champs", command=self.generate_fields).grid(row=0, column=2)
        ttk.Button(input_frame, text="Réinitialiser", command=self.reset).grid(row=0, column=3)

        result_frame = ttk.LabelFrame(self, text="Résultats")
        result_frame.pack(pady=10, padx=10, fill="both", expand=True)

        self.result_area = scrolledtext.ScrolledText(result_frame, wrap=tk.WORD, font=("Courier", 12))
        self.result_area.pack(fill="both", expand=True)

    def generate_fields(self):
        for widget in self.winfo_children():
            if isinstance(widget, ttk.LabelFrame) and widget.winfo_name().endswith("_params"):
                widget.destroy()

        param_frame = ttk.LabelFrame(self, text="Saisie des paramètres")
        param_frame.pack(pady=10, padx=10, fill="x")

        n = int(self.num_links.get())
        self.entries = []

        for i in range(n):
            frame = ttk.Frame(param_frame)
            frame.pack(fill="x", pady=2)

            ttk.Label(frame, text=f"Lien {i + 1}").pack(side="left")
            entries = []

            for j, param in enumerate(["a (longueur)", "α (°)", "d", "θ (angle)"]):
                ttk.Label(frame, text=param).pack(side="left", padx=2)
                entry = ttk.Entry(frame, width=10)
                entry.pack(side="left", padx=2)
                entries.append(entry)

            self.entries.append(entries)

        ttk.Button(param_frame, text="Calculer", command=self.calculate).pack(pady=5)

    def calculate(self):
        self.result_area.delete(1.0, tk.END)
        T_total = sp.eye(4)

        try:
            for i, entries in enumerate(self.entries):
                a = entries[0].get()
                alpha = deg_to_rad(float(entries[1].get()))
                d = float(entries[2].get())
                theta = entries[3].get()

                if a.lower().startswith("l"):
                    a = symbols(a)
                else:
                    a = float(a)

                if theta.lower().startswith("t"):
                    theta = symbols(theta)
                else:
                    theta = float(theta)

                T_i = dh_transform(a, alpha, d, theta)
                self.result_area.insert(tk.END, f"\nMatrice T_{i}->{i + 1}:\n")
                self.result_area.insert(tk.END, self.pretty_matrix(T_i) + "\n")
                T_total = T_total * T_i

            self.result_area.insert(tk.END, "\n\nMatrice totale T_0->n:\n")
            self.result_area.insert(tk.END, self.pretty_matrix(simplify(T_total)) + "\n")
        except Exception as e:
            self.result_area.insert(tk.END, f"\nErreur: {str(e)}\n")

    def pretty_matrix(self, matrix):
        rep = {symbols(f"cos(t{i + 1})"): f"C{i + 1}" for i in range(10)}
        rep.update({symbols(f"sin(t{i + 1})"): f"S{i + 1}" for i in range(10)})
        rep.update({symbols(f"cos(t{i + 1} + t{i + 2})"): f"C{i + 1}{i + 2}" for i in range(9)})
        rep.update({symbols(f"sin(t{i + 1} + t{i + 2})"): f"S{i + 1}{i + 2}" for i in range(9)})
        return sp.pretty(matrix.subs(rep))

    def reset(self):
        self.result_area.delete(1.0, tk.END)
        self.num_links.delete(0, tk.END)
        for widget in self.winfo_children():
            if isinstance(widget, ttk.LabelFrame) and widget.winfo_name().endswith("_params"):
                widget.destroy()


if __name__ == "__main__":
    app = DHCalculatorApp()
    app.mainloop()