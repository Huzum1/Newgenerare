import streamlit as st
import pandas as pd
import random
from collections import Counter
import io

st.set_page_config(page_title="Strategii 4/4", page_icon="🎯", layout="wide")

st.title("🎯 Strategii 4/4 – Generator inteligent de combinații")
st.write("Analizează runde istorice și generează 1000 de combinații posibile pentru o șansă de 4/4.")

# ===== 1. Încărcare fișier =====
uploaded_file = st.file_uploader("📤 Încarcă fișierul cu runde (TXT sau CSV)", type=["txt", "csv"])

if uploaded_file:
    try:
        rounds = []
        for line in uploaded_file:
            line = line.decode("utf-8").strip()
            if line:
                rounds.append(list(map(int, line.replace(" ", "").split(","))))
        st.success(f"✅ S-au încărcat {len(rounds)} runde cu {len(rounds[0])} numere fiecare.")
    except Exception as e:
        st.error(f"Eroare la citire: {e}")
        st.stop()

    # ===== 2. Analiză frecvență =====
    all_nums = [n for r in rounds for n in r]
    freq = Counter(all_nums)
    freq_df = pd.DataFrame(freq.items(), columns=["Număr", "Frecvență"]).sort_values("Frecvență", ascending=False)
    with st.expander("📊 Vezi frecvența numerelor"):
        st.dataframe(freq_df, use_container_width=True)

    # ===== 3. Setări =====
    st.subheader("⚙️ Setări generator")
    top = st.slider("Câte numere frecvente (Top) să folosim?", 10, 40, 20)
    mid = st.slider("Câte numere medii (Mid) să includem?", 10, 40, 20)
    low = st.slider("Câte numere rare (Low) să includem?", 5, 30, 15)

    # ===== 4. Generare =====
    if st.button("🔮 Generează 1000 de variante"):
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

        # ===== 5. Verificare 4/4 =====
        hits = 0
        for v in variants:
            for r in rounds:
                if set(v).issubset(r):
                    hits += 1
                    break

        st.success(f"🎉 Din 1000 de variante generate, {hits} obțin 4/4!")

        # ===== 6. Creare tabel cu ID-uri =====
        df_var = pd.DataFrame({
            "ID": range(1, len(variants) + 1),
            "Combinație": [" ".join(map(str, v)) for v in variants]
        })

        # ===== 7. Afișare preview =====
        st.subheader("👁️‍🗨️ Preview – primele 10 variante")
        st.dataframe(df_var.head(10), use_container_width=True, height=300)

        # ===== 8. Scroll complet =====
        with st.expander("📜 Vezi toate cele 1000 de variante"):
            st.dataframe(df_var, use_container_width=True, height=600)

        # ===== 9. Buton Copy All =====
        all_text = "\n".join([f"({row.ID}, {row.Combinație})" for _, row in df_var.iterrows()])

        st.text_area("📋 Toate variantele (poți copia manual sau folosește butonul de mai jos):",
                     all_text, height=200)

        st.button("📄 Copy all variants", help="Selectează tot textul de mai sus și apasă Ctrl+C / Cmd+C pentru a copia.")

        # ===== 10. Export CSV =====
        csv_buf = io.StringIO()
        df_var.to_csv(csv_buf, index=False)
        st.download_button(
            "💾 Descarcă variantele (CSV)",
            data=csv_buf.getvalue(),
            file_name="variante_4din4.csv",
            mime="text/csv"
        )

else:
    st.info("📂 Încarcă fișierul tău cu runde (ex: 1300runde.txt) pentru a începe.")

st.markdown("---")
st.caption("© 2025 Strategii 4/4 – Creat cu ❤️ în Streamlit.")