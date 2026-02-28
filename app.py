import streamlit as st
from scraper import LookfantasticScraper, build_routine, build_hair_routine

# -----------------------------
# 1. PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="Assistant Beauté IA",
    page_icon="✨",
    layout="wide"
)

# -----------------------------
# 2. HEADER + WARNINGS
# -----------------------------
st.title("✨ Assistant Beauté IA — Routine Personnalisée")

st.warning("""
⚠️ **Nous ne sommes pas dermatologues.**
Cet assistant ne remplace pas un avis médical professionnel.
Il est destiné aux débutants qui veulent une routine simple et adaptée.
""")

st.info("""
🧪 **Comment fonctionne cet assistant ?**

- Les recommandations sont basées sur des mots‑clés dans les descriptions produits.
- Les scores ne sont **pas** basés sur des études scientifiques.
- Le système n’analyse **pas** les ingrédients de manière médicale.
- L’objectif est de proposer une routine simple, cohérente et accessible.
""")

# -----------------------------
# 3. FORMULAIRE UTILISATEUR SKINCARE
# -----------------------------
st.header("🧍‍♀️ Ton profil skincare")

col1, col2, col3 = st.columns(3)

with col1:
    skin_type = st.selectbox("Ton type de peau", ["Sèche", "Mixte", "Grasse", "Sensible"])

with col2:
    concern = st.selectbox("Ton principal problème", ["Acné", "Déshydratation", "Anti‑âge"])

with col3:
    budget = st.slider("Budget maximum par produit (€)", 10, 80, 25)

start = st.button("✨ Générer ma routine")

st.divider()

# -----------------------------
# 4. LANCEMENT DU SCRAPING SKINCARE
# -----------------------------
if start:
    st.header("🔍 Recherche des meilleurs produits pour toi…")

    skin_map = {"Sèche": "1", "Mixte": "2", "Grasse": "3", "Sensible": "4"}
    concern_map = {"Acné": "1", "Déshydratation": "2", "Anti‑âge": "3"}

    skin_key = skin_map[skin_type]
    concern_key = concern_map[concern]

    progress = st.progress(0)

    with st.spinner("Connexion à Lookfantastic…"):
        scraper = LookfantasticScraper(headless=True)

    with st.spinner("🔍 Recherche des produits…"):
        if "products_skin" not in st.session_state or st.session_state.get("last_skin_key") != concern_key:
            st.session_state.products_skin = scraper.collect_products_for_routine(concern_key)
            st.session_state.last_skin_key = concern_key
        products = st.session_state.products_skin
        progress.progress(50)

    with st.spinner("🧪 Analyse des produits…"):
        routine = build_routine(products, concern_key, skin_key, budget)
        progress.progress(100)

    scraper.close()

    st.success("✨ Routine générée avec succès !")
    st.divider()

    st.header("🌿 Ta routine skincare personnalisée")

    steps_labels = {
        "cleanser": "Nettoyant",
        "serum": "Sérum",
        "moisturizer": "Crème hydratante",
        "spf": "Protection solaire (SPF)"
    }

    cols = st.columns(4)

    for i, (step, label) in enumerate(steps_labels.items()):
        p = routine.get(step)
        with cols[i]:
            st.subheader(label)
            if p:
                st.write(f"**{p.name}**")
                st.write(f"💶 Prix : {p.price}")
                st.write(p.description[:200] + "...")
                st.link_button("Voir le produit", p.url)
            else:
                st.error("Aucun produit trouvé")

# -----------------------------
# 5. FORMULAIRE UTILISATEUR CHEVEUX
# -----------------------------
st.divider()
st.header("💇‍♀️ Ton profil capillaire")

colh1, colh2, colh3 = st.columns(3)

with colh1:
    hair_type = st.selectbox("Type de cheveux", ["Fins", "Épais", "Bouclés", "Crépus"])

with colh2:
    hair_concern = st.selectbox("Problème principal", ["Cheveux secs", "Cheveux gras", "Chute / perte de densité"])

with colh3:
    hair_budget = st.slider("Budget maximum par produit (cheveux) (€)", 10, 80, 25)

start_hair = st.button("💇‍♀️ Générer ma routine cheveux")

# -----------------------------
# 6. LANCEMENT DU SCRAPING CHEVEUX
# -----------------------------
if start_hair:
    st.header("🔍 Recherche des meilleurs produits capillaires…")

    hair_type_map = {"Fins": "1", "Épais": "2", "Bouclés": "3", "Crépus": "4"}
    hair_concern_map = {
        "Cheveux secs": "1",
        "Cheveux gras": "2",
        "Chute / perte de densité": "3"
    }

    hair_type_key = hair_type_map[hair_type]
    hair_concern_key = hair_concern_map[hair_concern]

    progress_hair = st.progress(0)

    with st.spinner("Connexion à Lookfantastic…"):
        scraper = LookfantasticScraper(headless=True)

    with st.spinner("🔍 Recherche des produits cheveux…"):
        if "products_hair" not in st.session_state or st.session_state.get("last_hair_key") != hair_concern_key:
            st.session_state.products_hair = scraper.collect_hair_products(hair_concern_key)
            st.session_state.last_hair_key = hair_concern_key
        products_hair = st.session_state.products_hair
        progress_hair.progress(50)

    with st.spinner("🧪 Analyse des produits…"):
        routine_hair = build_hair_routine(products_hair, hair_concern_key, hair_type_key, hair_budget)
        progress_hair.progress(100)

    scraper.close()

    st.success("✨ Routine capillaire générée avec succès !")
    st.divider()

    st.header("💇‍♀️ Ta routine capillaire personnalisée")

    hair_steps_labels = {
        "shampoo": "Shampoing",
        "conditioner": "Après‑shampoing",
        "mask": "Masque",
        "hair_serum": "Sérum / Huile"
    }

    cols_hair = st.columns(4)

    for i, (step, label) in enumerate(hair_steps_labels.items()):
        p = routine_hair.get(step)
        with cols_hair[i]:
            st.subheader(label)
            if p:
                st.write(f"**{p.name}**")
                st.write(f"💶 Prix : {p.price}")
                st.write(p.description[:200] + "...")
                st.link_button("Voir le produit", p.url)
            else:
                st.error("Aucun produit trouvé")