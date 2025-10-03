from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
import os
import re

app = Flask(__name__)

# ------------------ BUSCADOR GOLLO ------------------ #
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
                    "precio_num": float(re.sub(r'[^\d.]', '', precio_tag.get_text())) if precio_tag else float('inf'),
                    "imagen": img_tag["src"] if img_tag else ""
                })
    except Exception as e:
        print("Error en Gollo:", e)

    return resultados

# ------------------ BUSCADOR MONGE ------------------ #
def buscar_monge(producto):
    url = f"https://www.tiendamonge.com/catalogsearch/result/?q={producto.replace(' ', '%20')}"
    headers = {"User-Agent": "Mozilla/5.0"}
    resultados = []

    try:
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        for item in soup.select("div.result-wrapper"):
            nombre_tag = item.select_one("h3.result-title")
            link_tag = item.select_one("a.result")
            precio_tag = item.select_one("span.after_special")
            img_tag = item.select_one("img[itemprop='image']")

            if nombre_tag and link_tag:
                precio_text = precio_tag.get_text(strip=True) if precio_tag else "No disponible"
                precio_num = float(re.sub(r'[^\d.]', '', precio_text)) if precio_tag else float('inf')
                resultados.append({
                    "tienda": "Importadora Monge",
                    "nombre_producto": nombre_tag.get_text(strip=True),
                    "url": link_tag["href"],
                    "precio": precio_text,
                    "precio_num": precio_num,
                    "imagen": img_tag["src"] if img_tag else ""
                })
    except Exception as e:
        print("Error en Monge:", e)

    return resultados

# ------------------ BUSCADOR CIUDAD MANGA ------------------ #
def buscar_ciudad_manga(producto):
    url = f"https://ciudadmangacr.com/es-cr/search?type=product&q={producto.replace(' ', '%20')}&options%5Bprefix%5D=last"
    headers = {"User-Agent": "Mozilla/5.0"}
    resultados = []

    try:
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        for item in soup.select("div.animated-grid"):
            nombre_tag = item.select_one("a.yv-product-title")
            precio_tag = item.select_one("span.yv-product-price")
            img_tag = item.select_one("img.product-first-img")

            if nombre_tag:
                precio_text = precio_tag.get_text(strip=True) if precio_tag else "No disponible"
                precio_num = float(re.sub(r'[^\d.]', '', precio_text)) if precio_tag else float('inf')
                resultados.append({
                    "tienda": "Ciudad Manga CR",
                    "nombre_producto": nombre_tag.get_text(strip=True),
                    "url": "https://ciudadmangacr.com" + nombre_tag["href"],
                    "precio": precio_text,
                    "precio_num": precio_num,
                    "imagen": "https:" + img_tag["src"] if img_tag else ""
                })
    except Exception as e:
        print("Error en Ciudad Manga:", e)

    return resultados

# ------------------ RUTA PRINCIPAL ------------------ #
@app.route("/", methods=["GET", "POST"])
def index():
    resultados = []
    if request.method == "POST":
        producto = request.form.get("producto")
        resultados += buscar_gollo(producto)
        resultados += buscar_monge(producto)
        resultados += buscar_ciudad_manga(producto)
        # Ordenar todos los resultados por precio_num
        resultados.sort(key=lambda x: x["precio_num"])
    return render_template("index.html", resultados=resultados)

# ------------------ EJECUTAR APP ------------------ #
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
