from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# ======================= GOLLO =======================
def buscar_gollo(producto):
    url = f"https://www.gollo.com/search/{producto.replace(' ', '%20')}"
    headers = {"User-Agent": "Mozilla/5.0"}
    resultados = []

    try:
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        for item in soup.select("div.product-item-info"):
            nombre_tag = item.select_one("h3.product-item-name a")
            precio_tag = item.select_one("span.price-wrapper span.price")
            img_tag = item.select_one("img.product-image-photo")

            if nombre_tag:
                resultados.append({
                    "tienda": "Gollo CR",
                    "nombre_producto": nombre_tag.get_text(strip=True),
                    "url": nombre_tag["href"],
                    "precio": precio_tag.get_text(strip=True) if precio_tag else "No disponible",
                    "imagen": img_tag["src"] if img_tag else ""
                })
    except Exception as e:
        print("Error en Gollo:", e)

    return resultados

# ======================= MONGE =======================
def buscar_monge(producto):
    url = f"https://www.tiendamonge.com/catalogsearch/result/?q={producto.replace(' ', '%20')}"
    headers = {"User-Agent": "Mozilla/5.0"}
    resultados = []

    try:
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        for item in soup.select("a.result"):
            nombre_tag = item.select_one("h3.result-title")
            link_tag = item
            precio_tag = item.select_one("span.after_special")
            img_tag = item.select_one("img[itemprop='image']")

            if nombre_tag and link_tag:
                resultados.append({
                    "tienda": "Importadora Monge",
                    "nombre_producto": nombre_tag.get_text(strip=True),
                    "url": "https://www.tiendamonge.com" + link_tag["href"] if link_tag["href"].startswith("/") else link_tag["href"],
                    "precio": precio_tag.get_text(strip=True) if precio_tag else "No disponible",
                    "imagen": img_tag["src"] if img_tag else ""
                })
    except Exception as e:
        print("Error en Monge:", e)

    return resultados

# ======================= CIUDAD MANGA =======================
def buscar_ciudadmanga(producto):
    url = f"https://ciudadmangacr.com/es-cr/search?type=product&q={producto.replace(' ', '%20')}&options%5Bprefix%5D=last"
    headers = {"User-Agent": "Mozilla/5.0"}
    resultados = []

    try:
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        for item in soup.select("div.animated-grid"):
            nombre_tag = item.select_one("a.yv-product-title")
            link_tag = nombre_tag
            precio_tag = item.select_one("span.yv-product-price")
            img_tag = item.select_one("img.product-first-img")

            if nombre_tag and link_tag:
                img_url = img_tag["src"] if img_tag else ""
                if img_url.startswith("//"):
                    img_url = "https:" + img_url

                resultados.append({
                    "tienda": "Ciudad Manga CR",
                    "nombre_producto": nombre_tag.get_text(strip=True),
                    "url": "https://ciudadmangacr.com" + link_tag["href"] if link_tag["href"].startswith("/") else link_tag["href"],
                    "precio": precio_tag.get_text(strip=True) if precio_tag else "No disponible",
                    "imagen": img_url
                })
    except Exception as e:
        print("Error en Ciudad Manga:", e)

    return resultados

# ======================= RUTA PRINCIPAL =======================
@app.route("/", methods=["GET", "POST"])
def index():
    resultados = []
    if request.method == "POST":
        producto = request.form.get("producto")
        resultados += buscar_gollo(producto)
        resultados += buscar_monge(producto)
        resultados += buscar_ciudadmanga(producto)

        # Ordenar por precio numérico de menor a mayor, ignorando símbolos
        def parse_precio(p):
            try:
                return float(p.replace("₡", "").replace(",", "").replace(".", "").strip())
            except:
                return float("inf")
        resultados.sort(key=lambda x: parse_precio(x["precio"]))

    return render_template("index.html", resultados=resultados)

if __name__ == "__main__":
    app.run(debug=True)
