# app.py
import streamlit as st
import pandas as pd
import random
from io import StringIO
import matplotlib.pyplot as plt

st.set_page_config(page_title="🎯 Keno Strategy Generator + Simulator", layout="wide")

# ----------------------------
# Funcții utilitare
# ----------------------------
def parse_rounds(text):
    rounds = []
    for line in text.strip().splitlines():
        nums = [int(x) for x in line.replace(",", " ").split() if x.isdigit()]
        if nums:
            rounds.append(nums)
    return rounds

def freq_from_rounds(rounds):
    flat = [n for r in rounds for n in r]
    s = pd.Series(flat).value_counts().to_dict()
    for i in range(1, 67):
        s.setdefault(i, 0)
    return dict(sorted(s.items()))

def strategy_diverse(n=800):
    """3/3/3 + echilibru par/impar"""
    tickets = []
    while len(tickets) < n:
        small = random.sample(range(1, 23), 3)
        medium = random.sample(range(23, 45), 3)
        large = random.sample(range(45, 67), 3)
        combo = sorted(small + medium + large)
        if 4 <= sum(x % 2 == 0 for x in combo) <= 5:
            tickets.append(combo)
    return tickets

def strategy_wheel(rounds, n=480):
    """Wheel cu mai multe nuclee diferite."""
    freq = freq_from_rounds(rounds)
    sorted_nums = sorted(freq, key=freq.get, reverse=True)
    core_sets = [
        sorted_nums[:5],
        sorted_nums[5:10],
        sorted_nums[10:15],
        sorted_nums[-10:-5],
        sorted_nums[-5:],
        random.sample(sorted_nums, 5)
    ]
    pool = list(range(1, 67))
    tickets = []
    per_core = n // len(core_sets)
    for core in core_sets:
        for _ in range(per_core):
            extra = random.sample([x for x in pool if x not in core], 4)
            combo = sorted(core + extra)
            tickets.append(combo)
    return tickets

def strategy_random_equilibrat(n=320):
    """Random echilibrat simplu."""
    tickets = []
    while len(tickets) < n:
        combo = random.sample(range(1, 67), 9)
        if 4 <= sum(x % 2 == 0 for x in combo) <= 5:
            tickets.append(sorted(combo))
    return tickets

# ----------------------------
# Interfață
# ----------------------------
st.title("🎯 Keno 6/9 Strategy Generator + Monte-Carlo Simulator")

st.sidebar.header("⚙️ Configurare")
num_variants = st.sidebar.number_input("Număr total variante", 100, 5000, 1600)
sim_rounds = st.sidebar.number_input("Simulări Monte-Carlo", 1000, 50000, 10000, step=1000)
seed = st.sidebar.number_input("Seed (0 = aleator)", 0, 999999, 0)
if seed != 0:
    random.seed(seed)

# Import runde
st.subheader("📂 Importă runde anterioare")
uploaded = st.file_uploader("Încarcă fișier .txt (format: 1, 2, 3, ...)", type=["txt"])
manual = st.text_area("Adaugă manual runde (una pe linie, format: 2, 5, 7, 13, ...):")

rounds = []
if uploaded:
    content = uploaded.read().decode("utf-8")
    rounds = parse_rounds(content)
if manual.strip():
    rounds += parse_rounds(manual)

if not rounds:
    st.warning("⚠️ Nu ai încărcat runde. Se va genera cu distribuție uniformă.")
else:
    st.success(f"{len(rounds)} runde încărcate pentru analiză frecvență.")

# ----------------------------
# Generare variante
# ----------------------------
st.subheader("🧩 Generare 1600 variante (50% Diverse, 30% Wheel, 20% Random)")
if st.button("Generează variante"):
    diverse = strategy_diverse(n=int(num_variants * 0.5))
    wheel = strategy_wheel(rounds, n=int(num_variants * 0.3))
    rand = strategy_random_equilibrat(n=int(num_variants * 0.2))

    all_tickets = diverse + wheel + rand
    df = pd.DataFrame({
        "ID": range(1, len(all_tickets) + 1),
        "Combinație": [" ".join(map(str, c)) for c in all_tickets]
    })

    st.success(f"S-au generat {len(df)} variante.")
    st.dataframe(df.head(10), height=300)
    st.download_button("💾 Descarcă .txt", "\n".join([f"{i+1}, {c}" for i, c in enumerate(df['Combinație'])]),
                       file_name="variante_keno.txt", mime="text/plain")

    st.session_state["tickets"] = all_tickets