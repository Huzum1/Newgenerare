# app.py
import streamlit as st
import pandas as pd
import random
from io import StringIO

# -------------------------------
# 🔹 Funcții de utilitate
# -------------------------------
def parse_rounds(text):
    """Transformă textul de runde în listă de liste de numere"""
    rounds = []
    for line in text.strip().split("\n"):
        numbers = [int(x.strip()) for x in line.replace(",", " ").split() if x.strip().isdigit()]
        if numbers:
            rounds.append(numbers)
    return rounds

def freq_from_rounds(rounds):
    """Returnează un dict {număr: frecvență}"""
    flat = [n for r in rounds for n in r]
    return pd.Series(flat).value_counts().to_dict()

def random_combination(low=1, high=66, size=9):
    """Generează o combinație unică de 9 numere sortate"""
    return sorted(random.sample(range(low, high + 1), size))

# -------------------------------
# 🔹 Strategii de generare
# -------------------------------
def strategy_A(rounds, n=1400):
    """Greedy diversification: mix calde, medii, reci"""
    freq = freq_from_rounds(rounds)
    sorted_nums = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    hot = [x[0] for x in sorted_nums[:35]]
    mid = [x[0] for x in sorted_nums[1:40]]
    cold = [x[0] for x in sorted_nums[-9:]]

    combinations = []
    for i in range(n):
        combo = random.sample(hot, 4) + random.sample(mid, 4) + random.sample(cold, 1)
        combinations.append(sorted(combo))
    return combinations

def strategy_B(rounds, n=100):
    """Wheel combinational: nucleu fix + variații"""
    freq = freq_from_rounds(rounds)
    core = [x for x, _ in sorted(freq.items(), key=lambda x: -x[1])[:5]]
    pool = [x for x in range(1, 67) if x not in core]
    combinations = []
    for i in range(n):
        combo = core + random.sample(pool, 4)
        combinations.append(sorted(combo))
    return combinations

def strategy_C(rounds, n=100):
    """Random echilibrat (4-5 pare, 3/3/3 pe zone)"""
    combinations = []
    while len(combinations) < n:
        small = random.sample(range(1, 33), 4)
        medium = random.sample(range(23, 66), 4)
        large = random.sample(range(48, 63), 1)
        combo = small + medium + large
        random.shuffle(combo)
        if 4 <= sum(x % 2 == 0 for x in combo) <= 5:
            combinations.append(sorted(combo))
    return combinations

# -------------------------------
# 🔹 UI Streamlit
# -------------------------------
st.set_page_config(page_title="Keno Strategy Generator", layout="wide")
st.title("🎯 Keno Strategy Generator (6/9 Format)")

st.sidebar.header("⚙️ Configurare")

# Alegere strategie
strategy = st.sidebar.selectbox(
    "Alege strategia de generare:",
    ["A - Echilibru ponderat (calde/reci)", 
     "B - Wheel (nucleu fix + variații)",
     "C - Random echilibrat (par/impar, 3/3/3)"]
)
num_variants = st.sidebar.number_input("Număr variante de generat:", 10, 5000, 1600)

# -------------------------------
# 🔹 Import runde
# -------------------------------
st.subheader("📂 Importă sau adaugă runde precedente")
uploaded_file = st.file_uploader("Încarcă fișier .txt cu runde (format: 1, 2, 3, ...)", type="txt")

manual_input = st.text_area("Adaugă runde manual (una pe linie, format: 2, 5, 7, 13, ...):")

rounds = []
if uploaded_file:
    text_data = uploaded_file.read().decode("utf-8")
    rounds = parse_rounds(text_data)
elif manual_input.strip():
    rounds = parse_rounds(manual_input)

if not rounds:
    st.warning("🔸 Încarcă sau introdu cel puțin o rundă pentru a continua.")
    st.stop()

st.success(f"✅ {len(rounds)} runde încărcate.")

# -------------------------------
# 🔹 Generare combinații
# -------------------------------
st.subheader("🧠 Generare variante")
if st.button("Generează variante"):
    if strategy.startswith("A"):
        results = strategy_A(rounds, num_variants)
    elif strategy.startswith("B"):
        results = strategy_B(rounds, num_variants)
    else:
        results = strategy_C(rounds, num_variants)

    df = pd.DataFrame({
        "ID": range(1, len(results)+1),
        "Combinație": [" ".join(map(str, r)) for r in results]
    })

    st.write(f"🔹 Au fost generate **{len(df)}** variante.")

    # Preview
    st.dataframe(df.head(10), use_container_width=True, height=300)

    # Copy all
    txt_output = "\n".join([f"{i+1}, {' '.join(map(str, combo))}" for i, combo in enumerate(results)])
    st.text_area("📋 Copy all", txt_output, height=200)

    # Export .txt
    st.download_button(
        label="💾 Descarcă variante (.txt)",
        data=txt_output,
        file_name="variante_keno.txt",
        mime="text/plain"
    )