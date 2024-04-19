from flask import Flask, send_file, render_template
import requests
from bs4 import BeautifulSoup
import csv
import os

app = Flask(__name__)


REPLACEMENTS = {
    '<em class="aperto"> scade il giorno ': "",
    "</em>": " ; ",
    "<p>": "",
    "<br/>": "",
    "<strong>": "",
    "</strong>": " ; ",
    "</a>": ";",
    '<a href="': "https://bandi.mur.gov.it",
    '">': "; ",
    "</strong><br/>": " ;",
    "Numero posti:": "",
    "</p>": "",
    "Titolo:": "",
    "Settore": "",
    "\n": "",
    "\n\r": "",
}

app.config["RESULT_STATIC_PATH"] = "/wwwroot"


def replace_all(text, replacements):
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


@app.route("/download/<idArea>")
def resultArea(idArea):
    url = f"https://bandi.mur.gov.it/bandi.php/public/cercaFellowship?jf_comp_status_id=3&bb_type_code=%25&idarea={idArea}&azione=cerca&orderby=scadenza_desc"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    div = soup.find("div", id="hiddenresult")
    paragraphs = div.find_all("p")

    rows = [[replace_all(str(p), REPLACEMENTS)] for p in paragraphs]

    with open("Editais.csv", "w", newline="") as f:
        writer = csv.writer(f, escapechar=" ", quoting=csv.QUOTE_NONE)
        writer.writerow(
            ["Prazo ;  Universidade ; Link ; Titulo ; Area ; Numero de Vagas"]
        )
        writer.writerows(rows)

    return send_file("Editais.csv", as_attachment=True)


@app.route("/", methods=["GET", "POST"])
def home():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
