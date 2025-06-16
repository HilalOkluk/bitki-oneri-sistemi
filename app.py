from flask import Flask, render_template, request
import pandas as pd
import requests
from unidecode import unidecode
##from graphviz import Digraph
import os

app = Flask(__name__)

# CSV dosyasını oku
df = pd.read_csv(r"evde_bakilabilir_bitkiler_dataset_guncel.csv")


# --- Karar Ağacı Çizimi ---
def karar_agaci_uyumlu_ciz(bitki_adi, girdi, en_iyi_satir):
    dot = Digraph()
    dot.attr(rankdir='TB')  # Yukarıdan aşağı

    kriterler = [
        ("Bütçe", "butce"),
        ("Cephe", "cephe"),
        ("Sulama Sıklığı", "sulama"),
        ("Çiçek Açıyor mu", "cicek"),
        ("Kokulu mu", "koku"),
        ("Boyut", "boyut")
    ]

    dot.node("start", "Başla", shape="ellipse")
    previous_node = "start"

    for i, (kriter_label, kriter_key) in enumerate(kriterler):
        secenekler = list(df[kriter_label].unique())
        correct_option = en_iyi_satir[kriter_label]
        user_option = girdi[kriter_key]

        option_nodes = {}
        for secenek in secenekler:
            node_id = f"{i}_{secenek}"
            if secenek == correct_option and user_option == correct_option:
                renk = "lightgreen"
            else:
                renk = "lightcoral"
            label = f"{kriter_label}: {secenek}"
            dot.node(node_id, label, style="filled", fillcolor=renk)
            option_nodes[secenek] = node_id

        for secenek, node_id in option_nodes.items():
            if secenek == correct_option:
                if user_option == correct_option:
                    edge_style = "bold"
                    edge_color = "green"
                else:
                    edge_style = "dashed"
                    edge_color = "red"
            else:
                edge_style = "dotted"
                edge_color = "gray"
            dot.edge(previous_node, node_id, style=edge_style, color=edge_color)

        previous_node = option_nodes[correct_option]

    dot.node("result", f"Önerilen Bitki:\n{bitki_adi}", shape="box", style="filled", fillcolor="gold")
    dot.edge(previous_node, "result", style="bold", color="blue")

    ##dot.render("bitki_karar_agaci_uyumlu", format="png", cleanup=True)
     ##dot.view()


# --- Tahmin Fonksiyonu ---
def tahmin_et(girdi):
    en_iyi_bitki = None
    en_yuksek_puan = -1
    en_iyi_satir = None

    for _, satir in df.iterrows():
        puan = 0
        if satir["Bütçe"] == girdi["butce"]: puan += 6
        if satir["Cephe"] == girdi["cephe"]: puan += 5
        if satir["Sulama Sıklığı"] == girdi["sulama"]: puan += 4
        if satir["Çiçek Açıyor mu"] == girdi["cicek"]: puan += 3
        if satir["Kokulu mu"] == girdi["koku"]: puan += 2
        if satir["Boyut"] == girdi["boyut"]: puan += 1



        if puan > en_yuksek_puan:
            en_yuksek_puan = puan
            en_iyi_bitki = satir["Bitki Adı"]
            en_iyi_satir = satir

    if en_iyi_satir is not None:
        karar_agaci_uyumlu_ciz(en_iyi_bitki, girdi, en_iyi_satir)

    return en_iyi_bitki if en_iyi_bitki else "Uygun bitki bulunamadı"


# --- Resim Yolu Fonksiyonu ---
def bitki_resim_yolu(bitki_adi):
    if not bitki_adi or bitki_adi == "Uygun bitki bulunamadı":
        return None

        # Dosya adı oluştur (turkce karakterleri sadeleştir, küçük harf, tireli)
    dosya_adi = unidecode(bitki_adi).lower().replace(" ", "-")
    desteklenen_uzantilar = [".webp", ".jpg", ".png"]

    for uzanti in desteklenen_uzantilar:
        dosya_yolu = f"static/images/{dosya_adi}{uzanti}"
        if os.path.exists(dosya_yolu):
            return dosya_yolu

    return None  # Hiçbiri yoksa


# --- Blog Link Bulucu ---
def blog_link_bul(bitki_adi):
    slug = unidecode(bitki_adi).lower().replace(" ", "-")
    linkler = [
        f"https://www.fidanburada.com/blog/{slug}-bakimi/",
        f"https://www.fidanburada.com/blog/{slug}-bakimi-nasil-olmalidir/",
        f"https://www.ciceksel.com.tr/{slug}-bakimi/",
        f"https://www.ciceksel.com.tr/{slug}",
        f"https://www.ciceksel.com.tr/{slug}-nedir/"
    ]
    for link in linkler:
        try:
            response = requests.get(link, timeout=5)
            if response.status_code == 200 and "404" not in response.text.lower():
                return link
        except:
            continue
    return None


# --- Ana Sayfa ---
@app.route("/", methods=["GET", "POST"])
def index():
    bitki_adi = None
    blog_link = None
    resim_yolu = None

    if request.method == "POST":
        girdi = {
            "butce": request.form["butce"],
            "cephe": request.form["cephe"],
            "sulama": request.form["sulama"],
            "cicek": request.form["cicek"],
            "koku": request.form["koku"],
            "boyut": request.form["boyut"]
        }
        bitki_adi = tahmin_et(girdi)
        blog_link = blog_link_bul(bitki_adi)
        resim_yolu = bitki_resim_yolu(bitki_adi)

        print(f"Tahmin edilen bitki: {bitki_adi}")
        print(f"Bulunan blog linki: {blog_link}")
        print(f"Görsel dosyası: {resim_yolu}")

    return render_template("index2.html", sonuc=bitki_adi, blog_link=blog_link, resim_yolu=resim_yolu)


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

