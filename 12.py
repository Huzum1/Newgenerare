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
        if len(numbers) == 12:  # loteria 12/66
            rounds.append(numbers)
    return rounds

def freq_from_rounds(rounds):
    """Returnează frecvența numerelor"""
    flat = [n for r in rounds for n in r]
    return pd.Series(flat).value_counts().to_dict()

# -------------------------------
# 🔹 Strategii de generare 4/4
# -------------------------------
def strategy_A(rounds, n=100, low=1, high=66):
    """Echilibru: calde + medii + reci"""
    freq = freq_from_rounds(rounds)
    sorted_nums = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    hot = [x[0] for x in sorted_nums[:15]]
    mid = [x[0] for x in sorted_nums[15:40]]
    cold = [x[0] for x in sorted_nums[-15:]]

    combinations = []
    for _ in range(n):
        combo = random.sample(hot, 1) + random.sample(mid, 2) + random.sample(cold, 1)
        combinations.append(sorted(combo))
    return combinations

def strategy_B(rounds, n=100, low=1, high=66):
    """Wheel: nucleu fix + variații"""
    freq = freq_from_rounds(rounds)
    core = [x for x, _ in sorted(freq.items(), key=lambda x: -x[1])[:2]]
    pool = [x for x in range(low, high + 1) if x not in core]
    combinations = []
    for _ in range(n):
        combo = core + random.sample(pool, 2)
        combinations.append(sorted(combo))
    return combinations

def strategy_C(rounds, n=100, low=1, high=66):
    """Random echilibrat (2 pare + 2 impare)"""
    combinations = []
    while len(combinations) < n:
        even_nums = [x for x in range(low, high + 1) if x % 2 == 0]
        odd_nums = [x for x in range(low, high + 1) if x % 2 == 1]
        combo = random.sample(even_nums, 2) + random.sample(odd_nums, 2)
        combinations.append(sorted(combo))
    return combinations

# -------------------------------
# 🔹 Funcție verificare 4/4
# -------------------------------
def check_matches(generated, rounds):
    """Verifică câte combinații 4/4 se regăsesc în rundele istorice"""
    matches = []
    for idx, combo in enumerate(generated, start=1):
        for ridx, r in enumerate(rounds, start=1):
            if set(combo).issubset(set(r)):
                matches.append((idx, ridx, combo))
                break
    return matches

# -------------------------------
# 🔹 UI Streamlit
# -------------------------------
st.set_page_config(page_title="Strategii 4/4 Loteria 12/66", layout="wide")
st.title("🎯 Strategii 4/4 – Loteria 12/66")

st.sidebar.header("⚙️ Configurare")

strategy = st.sidebar.selectbox(
    "Alege strategia de generare:",
    ["A - Echilibru ponderat (calde/reci)",
     "B - Nucleu fix + variații",
     "C - Random echilibrat (2 pare, 2 impare)"]
)
num_variants = st.sidebar.number_input("Număr variante de generat:", 10, 5000, 1000)

# -------------------------------
# 🔹 Import runde
# -------------------------------
st.subheader("📂 Importă sau adaugă runde 12/66")
uploaded_file = st.file_uploader("Încarcă fișier .txt cu runde (ex: 12 numere pe linie)", type="txt")
manual_input = st.text_area("Adaugă runde manual (una pe linie, format: 1, 5, 14, 22, 33, ... 12 numere)")

rounds = []
if uploaded_file:
    text_data = uploaded_file.read().decode("utf-8")
    rounds = parse_rounds(text_data)
elif manual_input.strip():
    rounds = parse_rounds(manual_input)

if not rounds:
    st.warning("🔸 Încarcă sau introdu cel puțin o rundă (12 numere) pentru a continua.")
    st.stop()

st.success(f"✅ {len(rounds)} runde încărcate (format 12/66).")

# -------------------------------
# 🔹 Generare combinații
# -------------------------------
st.subheader("🧠 Generare variante 4/4")

if st.button("🚀 Generează și verifică 4/4"):
    # Generare
    if strategy.startswith("A"):
        results = strategy_A(rounds, num_variants)
    elif strategy.startswith("B"):
        results = strategy_B(rounds, num_variants)
    else:
        results = strategy_C(rounds, num_variants)

    df = pd.DataFrame({
        "ID": range(1, len(results) + 1),
        "Combinație": [" ".join(map(str, r)) for r in results]
    })

    # Verificare 4/4
    matches = check_matches(results, rounds)
    st.success(f"🎉 Din {len(results)} variante generate, **{len(matches)}** se potrivesc complet 4/4 cu rundele istorice!")

    if matches:
        matched_df = pd.DataFrame([
            {"ID Variantă": m[0], "Rundă Potrivită": m[1], "Combinație": " ".join(map(str, m[2]))}
            for m in matches
        ])
        with st.expander("✅ Vezi potrivirile 4/4"):
            st.dataframe(matched_df, use_container_width=True)

    # --- Preview ---
    st.markdown("### 👁️‍🗨️ Primele 10 variante")
    st.dataframe(df.head(10), use_container_width=True, height=280)

    # --- Scroll complet ---
    with st.expander("📜 Vezi toate variantele generate"):
        st.dataframe(df, use_container_width=True, height=600)

    # --- Copy all ---
    all_text = "\n".join([f"{row.ID}, {row.Combinație}" for _, row in df.iterrows()])
    st.text_area("📋 Toate variantele (pentru copy)", all_text, height=250)

    # --- Copy button (JS) ---
    copy_button = f"""
        <button onclick="navigator.clipboard.writeText(`{all_text}`)"
                style="background-color:#4CAF50;color:white;padding:8px 16px;border:none;border-radius:4px;cursor:pointer;">
            📄 Copy all variants
        </button>
    """
    st.markdown(copy_button, unsafe_allow_html=True)

    # --- Export .txt ---
    txt_output = "\n".join([f"{i+1}, {' '.join(map(str, combo))}" for i, combo in enumerate(results)])
    st.download_button(
        label="💾 Descarcă variante (.txt)",
        data=txt_output,
        file_name="variante_4din4_12din66.txt",
        mime="text/plain"
    )

st.markdown("---")
st.caption("© 2025 Strategii 4/4 – Loteria 12/66 – Creat cu ❤️ în Streamlit.")