import streamlit as st
import pandas as pd
import random
from collections import Counter
from itertools import combinations
import io

st.set_page_config(page_title="Strategii 4/4", page_icon="🎯")

st.title("🎯 Strategii 4/4 – Generator inteligent de combinații")
st.write("Analizează fișierul cu runde istorice și generează 1000 de combinații posibile pentru a obține o variantă 4/4.")

# ===== 1. Încărcare fișier =====
uploaded_file = st.file_uploader("Încarcă fișierul cu runde (format .txt sau .csv)", type=["txt", "csv"])

if uploaded_file:
    # Citire runde
    try:
        rounds = []
        for line in uploaded_file:
            line = line.decode("utf-8").strip()
            if line:
                rounds.append(list(map(int, line.replace(" ", "").split(","))))
        st.success(f"S-au încărcat {len(rounds)} runde cu {len(rounds[0])} numere fiecare.")
    except Exception as e:
        st.error(f"Eroare la citire: {e}")
        st.stop()

    # ===== 2. Analiză frecvență =====
    all_nums = [n for r in rounds for n in r]
    freq = Counter(all_nums)
    freq_df = pd.DataFrame(freq.items(), columns=["Număr", "Frecvență"]).sort_values("Frecvență", ascending=False)
    st.subheader("📊 Frecvența numerelor")
    st.dataframe(freq_df, use_container_width=True)

    # ===== 3. Generare variante =====
    top = st.slider("Câte numere de top (cele mai frecvente) să folosim?", 10, 40, 20)
    mid = st.slider("Câte numere medii să includem?", 10, 40, 20)
    low = st.slider("Câte numere rare (din coadă) să includem?", 5, 30, 15)

    if st.button("🔮 Generează 1000 variante"):
        sorted_nums = [n for n, _ in freq.most_common()]
        variants = []
        while len(variants) < 1000:
            nums = []
            nums += random.sample(sorted_nums[:top], 2)
            nums.append(random.choice(sorted_nums[top:top+mid]))
            nums.append(random.choice(sorted_nums[-low:]))
            variant = tuple(sorted(set(nums)))
            if len(variant) == 4:
                variants.append(variant)

        # ===== 4. Verificare 4/4 =====
        hits = 0
        for v in variants:
            for r in rounds:
                if set(v).issubset(r):
                    hits += 1
                    break

        st.success(f"🎉 Din 1000 de variante generate, {hits} obțin 4/4!")

        # ===== 5. Export =====
        df_var = pd.DataFrame(variants, columns=["N1", "N2", "N3", "N4"])
        csv_buf = io.StringIO()
        df_var.to_csv(csv_buf, index=False)
        st.download_button(
            "💾 Descarcă variantele în CSV",
            data=csv_buf.getvalue(),
            file_name="variante_4din4.csv",
            mime="text/csv"
        )

        st.subheader("📋 Exemple de variante generate")
        st.dataframe(df_var.head(20), use_container_width=True)
else:
    st.info("Încarcă mai întâi fișierul tău cu runde (ex: 1300runde.txt).")

st.markdown("---")
st.caption("© 2025 Strategii 4/4 – Creat cu ❤️ în Streamlit.")