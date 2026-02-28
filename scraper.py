import re
import time
import random
from dataclasses import dataclass
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, NoSuchElementException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

# ============================================================
# ---------------   COMMUN   ---------------
# ============================================================
# -----------------------------
# 1. Structure Produit
# -----------------------------
@dataclass
class Product:
    name: str
    price: str
    url: str
    description: str
    concern: str
    category: str

# -----------------------------
# 2. Base Scraper
# -----------------------------
class BaseScraper:
    USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    )

    def __init__(self, headless=False):
        self.headless = headless
        self.driver = None
        self._init_driver()

    def _init_driver(self):
        options = Options()
        options.add_argument(f"user-agent={self.USER_AGENT}")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        if self.headless:
            options.add_argument("--headless=new")

        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.implicitly_wait(10)

    def _wait(self, a=1.5, b=3.0):
        time.sleep(random.uniform(a, b))

    def close(self):
        if self.driver:
            self.driver.quit()

# ============================================================
# ---------------      MODULE SKINCARE         ---------------
# ============================================================

# -----------------------------
# 3. Fonctions "IA skincare"
# -----------------------------
def detect_category(name: str, description: str) -> str:
    text = (name + " " + description).lower()

    if any(k in text for k in ["cleanser", "wash", "gel", "mousse", "nettoyant"]):
        return "cleanser"
    if "toner" in text or "lotion tonique" in text:
        return "toner"
    if "serum" in text or "sérum" in text:
        return "serum"
    if any(k in text for k in ["cream", "crème", "moisturiser", "moisturizer", "soin hydratant"]):
        return "moisturizer"
    if any(k in text for k in ["spf", "sunscreen", "écran solaire", "protection solaire"]):
        return "spf"
    return "other"

def score_product_for_profile(product: Product, concern_key: str, skin_type_key: str, budget_max: float | None) -> int:
    text = (product.name + " " + product.description).lower()
    score = 0

    # Problème principal
    if concern_key == "1":  # Acné
        if "salicylic" in text or "acide salicylique" in text:
            score += 4
        if "non comédogène" in text or "non comedogenic" in text:
            score += 3
        if "purifiant" in text or "clarifying" in text:
            score += 2
    elif concern_key == "2":  # Peau sèche
        if "hyaluronic" in text or "acide hyaluronique" in text:
            score += 4
        if "glycérine" in text or "glycerin" in text:
            score += 3
        if "nourrissant" in text or "rich" in text:
            score += 2
    elif concern_key == "3":  # Anti-âge
        if "retinol" in text or "rétinol" in text:
            score += 4
        if "peptide" in text:
            score += 3
        if "firming" in text or "fermeté" in text:
            score += 2

    # Type de peau
    if skin_type_key == "1":  # sèche
        if "dry skin" in text or "peau sèche" in text:
            score += 3
    elif skin_type_key == "2":  # mixte
        if "combination" in text or "peau mixte" in text:
            score += 3
    elif skin_type_key == "3":  # grasse
        if "oily" in text or "peau grasse" in text:
            score += 3
        if "matifiant" in text or "matte" in text:
            score += 2
    elif skin_type_key == "4":  # sensible
        if "sensitive" in text or "peau sensible" in text:
            score += 3
        if "fragrance free" in text or "sans parfum" in text:
            score += 2

    # Budget
    if budget_max is not None:
        try:
            price_num = float(product.price.replace("€", "").replace(",", ".").strip())
            if price_num <= budget_max:
                score += 2
            else:
                score -= 2
        except ValueError:
            pass

    return score

def build_routine(products, concern_key, skin_type_key, budget_max):
    scored = []
    for p in products:
        s = score_product_for_profile(p, concern_key, skin_type_key, budget_max)
        scored.append((s, p))

    # On trie tous les produits, même ceux avec score négatif
    scored.sort(key=lambda x: x[0], reverse=True)

    routine = {
        "cleanser": None,
        "serum": None,
        "moisturizer": None,
        "spf": None
    }

    for _, p in scored:
        if p.category == "cleanser" and routine["cleanser"] is None:
            routine["cleanser"] = p
        elif p.category == "serum" and routine["serum"] is None:
            routine["serum"] = p
        elif p.category == "moisturizer" and routine["moisturizer"] is None:
            routine["moisturizer"] = p
        elif p.category == "spf" and routine["spf"] is None:
            routine["spf"] = p

        if all(routine.values()):
            break

    # Récupérer le nom du problème de peau pour le champ 'concern'
    concern_label = LookfantasticScraper.CONCERNS.get(concern_key, ("Inconnu", "", ""))[0]

    # Ajout de produits par défaut si nécessaire
    for step in routine:
        if routine[step] is None:
            routine[step] = Product(
                name="Produit recommandé par défaut",
                price="9,99 €",
                description="Produit générique ajouté automatiquement pour compléter la routine.",
                url="https://www.lookfantastic.fr",
                category=step,
                concern=concern_label
            )

    return routine

# -----------------------------
# 4. Scraper Lookfantastic FR
# -----------------------------
class LookfantasticScraper(BaseScraper):

    # Problèmes principaux
    CONCERNS = {
        "1": (
            "Acné",
            r"acné|boutons|imperfections|purifiant|salicylique",
            "https://www.lookfantastic.fr/c/health-beauty/face/acne-blemishes/"
        ),
        "2": (
            "Peau sèche",
            r"peau sèche|hydratation|nourrissant|tiraillement|hyaluronique",
            "https://www.lookfantastic.fr/c/health-beauty/face/dry-skin/"
        ),
        "3": (
            "Anti-âge",
            r"rides|fermeté|anti-âge|jeunesse|rétinol",
            "https://www.lookfantastic.fr/c/health-beauty/face/anti-ageing/"
        )
    }

    # Catégories par étape de routine
    CATEGORY_URLS = {
        "cleanser": "https://www.lookfantastic.fr/c/health-beauty/face/acne-blemishes/",
        "serum": "https://www.lookfantastic.fr/c/health-beauty/face/skincare-products/specific-care/serums/",
        "moisturizer": "https://www.lookfantastic.fr/c/health-beauty/face/skincare-products/moisturisers/",
        "spf": "https://www.lookfantastic.fr/c/health-beauty/face/suncare/"
    }

    def _accept_cookies(self):
        try:
            btn = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
            )
            btn.click()
        except:
            pass

    def _scrape_category(self, url, concern_key):
        concern_name, pattern, _ = self.CONCERNS[concern_key]

        self.driver.get(url)
        self._accept_cookies()
        self._wait()

        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.product-data"))
        )

        product_elements = self.driver.find_elements(By.CSS_SELECTOR, "div.product-data")

        links = []
        for el in product_elements:
            try:
                a = el.find_element(By.CSS_SELECTOR, "a.product-item-title")
                href = a.get_attribute("href")
                if href:
                    links.append(href)
            except:
                continue

        links = list(set(links))
        return concern_name, pattern, links

    def _scrape_product_page(self, link, concern_name, pattern, forced_category=None):
        self.driver.get(link)
        self._wait()

        try:
            name = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "h1#product-title"))
            ).text
        except TimeoutException:
            raise NoSuchElementException("Titre introuvable")

        try:
            price_el = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "span.text-gray-900"))
            )
            price = price_el.text.strip()
        except TimeoutException:
            raise NoSuchElementException("Prix introuvable")

        try:
            desc_el = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div#product-description-0"))
            )
            description = desc_el.text
        except TimeoutException:
            description = ""

        # if not re.search(pattern, description, re.IGNORECASE):
        #    return None

        # On ne filtre PAS les masques et sérums (trop de variations)
        if forced_category not in ["mask", "hair_serum"]:
            if not re.search(pattern, description, re.IGNORECASE):
                return None

        category = forced_category if forced_category else detect_category(name, description)

        return Product(
            name=name,
            price=price,
            url=link,
            description=description[:600] + ("..." if len(description) > 600 else ""),
            concern=concern_name,
            category=category
        )

    def generate_products(self, links, concern_name, pattern, step):
        for link in links[:12]:
            try:
                p = self._scrape_product_page(link, concern_name, pattern, forced_category=step)
                if p:
                    yield p
            except Exception as e:
                print(f"Erreur produit ({step}) : {e}")
                continue

    def collect_products_for_routine(self, concern_key):
        all_products = []

        for step, url in self.CATEGORY_URLS.items():
            try:
                print(f"\n--- Étape {step} : {url} ---")
                concern_name, pattern, links = self._scrape_category(url, concern_key)

                if not links:
                    continue

                for p in self.generate_products(links, concern_name, pattern, step):
                    all_products.append(p)

            except WebDriverException as e:
                print(f"Erreur de navigation ({step}) : {e}")
                continue

        return all_products

# -----------------------------
# 5. Interface utilisateur
# -----------------------------
def ask_user_profile():
    print("Complète ta phrase en choisissant les options :\n")

    print("1) J'ai une peau :")
    print("   1. Sèche")
    print("   2. Mixte")
    print("   3. Grasse")
    print("   4. Sensible")
    skin_type = input("   → Choix (1-4) : ").strip()

    print("\n2) Mon principal problème est :")
    print("   1. Acné / imperfections")
    print("   2. Déshydratation / tiraillements")
    print("   3. Rides / perte de fermeté")
    concern = input("   → Choix (1-3) : ").strip()

    print("\n3) Mon budget maximum par produit est :")
    print("   1. 15 €")
    print("   2. 25 €")
    print("   3. 40 €")
    print("   4. Pas de limite")
    budget_choice = input("   → Choix (1-4) : ").strip()

    budget_map = {
        "1": 15.0,
        "2": 25.0,
        "3": 40.0,
        "4": None
    }
    budget_max = budget_map.get(budget_choice, None)

    print("\nTa phrase :")
    skin_label = {
        "1": "sèche",
        "2": "mixte",
        "3": "grasse",
        "4": "sensible"
    }.get(skin_type, "non précisée")

    concern_label = {
        "1": "acné / imperfections",
        "2": "déshydratation / tiraillements",
        "3": "rides / perte de fermeté"
    }.get(concern, "non précisé")

    if budget_max is None:
        budget_text = "je n'ai pas de limite de budget."
    else:
        budget_text = f"j'ai un budget d'environ {budget_max:.0f} € par produit."

    print(f"→ J'ai une peau {skin_label}, j'ai surtout des problèmes de {concern_label}, et {budget_text}\n")

    return skin_type, concern, budget_max

# -----------------------------
# 6. Programme principal
# -----------------------------
def main():
    scraper = LookfantasticScraper(headless=False)

    try:
        print("=== Assistant Beauté Lookfantastic — Création de routine skincare ===\n")

        skin_type, concern_key, budget_max = ask_user_profile()

        if concern_key not in scraper.CONCERNS:
            print("Problème de peau non reconnu. Fin du programme.")
            return

        products = scraper.collect_products_for_routine(concern_key)

        if not products:
            print("\nAucun produit trouvé pour ce profil.")
            return

        routine = build_routine(products, concern_key, skin_type, budget_max)

        print("\n=== Routine skincare personnalisée ===")

        steps_labels = {
            "cleanser": "Nettoyant",
            "serum": "Sérum",
            "moisturizer": "Crème hydratante",
            "spf": "Protection solaire (SPF)"
        }

        for step, label in steps_labels.items():
            p = routine.get(step)
            if p:
                print(f"\n➡ {label} :")
                print(f"   {p.name}")
                print(f"   Prix : {p.price}")
                print(f"   Lien : {p.url}")
            else:
                print(f"\n➡ {label} : (aucun produit trouvé pour cette étape)")

    finally:
        input("\nAppuie sur Entrée pour fermer le programme...")
        scraper.close()


# ============================================================
# ---------------   MODULE CHEVEUX (COMPLET)   ---------------
# ============================================================

# 1. Détection catégorie cheveux
def detect_hair_category(name: str, description: str) -> str:
    text = (name + " " + description).lower()

    if any(k in text for k in ["shampoo", "shampoing", "cleanser", "scalp wash"]):
        return "shampoo"
    if any(k in text for k in ["conditioner", "après-shampoing", "conditionneur"]):
        return "conditioner"
    if any(k in text for k in ["mask", "masque", "deep treatment", "repair mask"]):
        return "mask"
    if any(k in text for k in ["oil", "huile", "serum", "sérum capillaire", "hair oil"]):
        return "hair_serum"
    if any(k in text for k in ["leave-in", "sans rinçage"]):
        return "leave_in"
    return "other_hair"


# 2. Scoring cheveux (version élargie)
def score_hair_product(product: Product, concern_key: str, hair_type_key: str, budget_max: float | None) -> int:
    text = (product.name + " " + product.description).lower()
    score = 0

    # -------------------------
    # PROBLÈMES PRINCIPAUX
    # -------------------------

    # Cheveux secs → hydratation, nutrition, réparation
    if concern_key == "1":
        if any(k in text for k in [
            "hydrating", "hydration", "moisture", "moisturizing",
            "nourrissant", "nourishing", "nutrition",
            "repair", "réparateur", "damage", "damaged",
            "dry hair", "cheveux secs",
            "butter", "beurre", "shea", "karité",
            "rich", "intense", "deep conditioning"
        ]):
            score += 4
        if any(k in text for k in ["oil", "huile", "argan", "coconut", "coco"]):
            score += 3

    # Cheveux gras → purification, séborégulation
    elif concern_key == "2":
        if any(k in text for k in [
            "purifying", "purifiant", "clarifying", "clarifiant",
            "seboregulating", "séborégulateur",
            "oily hair", "cheveux gras",
            "fresh", "fraîcheur", "detox", "détox",
            "scalp balance", "équilibrant"
        ]):
            score += 4
        if any(k in text for k in ["mint", "menthe", "tea tree"]):
            score += 3

    # Chute / densité → fortifiant, croissance
    elif concern_key == "3":
        if any(k in text for k in [
            "hair loss", "chute", "anti-chute",
            "densifying", "densité", "density",
            "growth", "croissance", "stimulating", "stimulant",
            "fortifying", "strengthening", "strength",
            "biotin", "caffeine", "caféine", "keratin", "kératine"
        ]):
            score += 4
        if any(k in text for k in ["volume", "volumizing", "volumateur"]):
            score += 3

    # -------------------------
    # TYPES DE CHEVEUX
    # -------------------------

    # Fins → volume, légèreté
    if hair_type_key == "1":
        if any(k in text for k in [
            "volume", "volumizing", "volumateur",
            "lightweight", "léger", "fine hair"
        ]):
            score += 3

    # Épais → discipline, anti-frizz
    elif hair_type_key == "2":
        if any(k in text for k in [
            "smoothing", "lissant", "discipline",
            "anti-frizz", "anti-frisottis",
            "thick hair", "cheveux épais"
        ]):
            score += 3

    # Bouclés → définition, hydratation
    elif hair_type_key == "3":
        if any(k in text for k in [
            "curl", "boucles", "curly",
            "definition", "définition",
            "hydrating", "moisture",
            "anti-frizz", "anti-frisottis"
        ]):
            score += 3

    # Crépus → nutrition intense, beurres, huiles
    elif hair_type_key == "4":
        if any(k in text for k in [
            "rich", "ultra nourishing", "ultra-nourrissant",
            "beurre", "butter", "karité", "shea",
            "deep conditioning", "intense repair",
            "coily", "kinky", "afro"
        ]):
            score += 3

    # -------------------------
    # BUDGET
    # -------------------------
    if budget_max is not None:
        try:
            price_num = float(product.price.replace("€", "").replace(",", ".").strip())
            if price_num <= budget_max:
                score += 2
            else:
                score -= 2
        except ValueError:
            pass

    return score


# 3. Construction routine cheveux
def build_hair_routine(products, concern_key, hair_type_key, budget_max):
    scored = []
    for p in products:
        s = score_hair_product(p, concern_key, hair_type_key, budget_max)
        scored.append((s, p))

    # On trie tous les produits, même ceux avec score négatif
    scored.sort(key=lambda x: x[0], reverse=True)

    routine = {
        "shampoo": None,
        "conditioner": None,
        "mask": None,
        "hair_serum": None
    }

    for _, p in scored:
        if p.category == "shampoo" and routine["shampoo"] is None:
            routine["shampoo"] = p
        elif p.category == "conditioner" and routine["conditioner"] is None:
            routine["conditioner"] = p
        elif p.category == "mask" and routine["mask"] is None:
            routine["mask"] = p
        elif p.category == "hair_serum" and routine["hair_serum"] is None:
            routine["hair_serum"] = p

        if all(routine.values()):
            break

    # Récupérer le nom du problème capillaire pour le champ 'concern'
    concern_label = LookfantasticScraper.HAIR_CONCERNS.get(concern_key, ("Inconnu", "", ""))[0]

    # Ajout de produits par défaut si nécessaire
    for step in routine:
        if routine[step] is None:
            routine[step] = Product(
                name="Produit recommandé par défaut",
                price="9,99 €",
                description="Produit générique ajouté automatiquement pour compléter la routine.",
                url="https://www.lookfantastic.fr",
                category=step,
                concern=concern_label
            )

    return routine

# 4. Ajout des URLs cheveux dans LookfantasticScraper
LookfantasticScraper.HAIR_CONCERNS = {
    "1": ("Cheveux secs", r"sec|dry|hydrating|moisture|nourrissant|repair", "https://www.lookfantastic.fr/c/health-beauty/hair/dry-hair/"),
    "2": ("Cheveux gras", r"gras|oily|purifying|clarifying|seboregulating", "https://www.lookfantastic.fr/c/health-beauty/hair/oily-hair/"),
    "3": ("Chute / densité", r"chute|hair loss|densité|biotin|caffeine|keratin", "https://www.lookfantastic.fr/c/health-beauty/hair/hair-loss/")
}

LookfantasticScraper.HAIR_CATEGORY_URLS = {
    "shampoo": "https://www.lookfantastic.fr/c/health-beauty/hair/shampoo/",
    "conditioner": "https://www.lookfantastic.fr/c/health-beauty/hair/conditioner/",
    "mask": "https://www.lookfantastic.fr/c/health-beauty/hair/hair-treatments/masks/",
    "hair_serum": "https://www.lookfantastic.fr/c/health-beauty/hair/hair-treatments/serums-oils/"
}


# 5. Scraper cheveux
def collect_hair_products(self, concern_key):
    all_products = []

    for step, url in self.HAIR_CATEGORY_URLS.items():
        try:
            print(f"\n--- Étape cheveux {step} : {url} ---")
            concern_name, pattern, links = self._scrape_category(url, concern_key)

            if not links:
                continue

            for link in links[:12]:
                try:
                    p = self._scrape_product_page(
                        link,
                        concern_name,
                        pattern,
                        forced_category=step
                    )
                    if p:
                        all_products.append(p)
                except Exception as e:
                    print(f"Erreur produit ({step}) : {e}")
                    continue

        except WebDriverException as e:
            print(f"Erreur de navigation ({step}) : {e}")
            continue

    return all_products

# On attache la méthode à la classe
LookfantasticScraper.collect_hair_products = collect_hair_products