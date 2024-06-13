from flask import Flask, send_file, render_template
import requests
from bs4 import BeautifulSoup
import csv
import os
import re

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

def merge_areas(s):
    pattern = re.compile(r"[;][\s]+[A-Z]{3}\/[0-9]{2}")
    result = pattern.search(s)
    
    if result == None:
        last = s.rfind(';')
        s = s[:last] + '; ;' + s[last+1: ]
        return s
    
    index = result.span()
    
    result = pattern.search(s, index[1])
    
    while result != None :
        index = result.span()
        s = s[:index[0]] + ' ' + s[index[0]+1:]
        result = pattern.search(s, index[1])
        if result != None:
            index = result.span()
    
    return s

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

    with open("Editais.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, escapechar=" ", quoting=csv.QUOTE_NONE)
        writer.writerow(
            ["Prazo ;  Universidade ; Link ; Titulo ; Area ; Numero de Vagas"]
        )
        for index, row in enumerate(rows):
            print(row)
            rows[index][0] = merge_areas(row[0])
            rows[index][0] = rows[index][0].replace("\"", "'")
        writer.writerows(rows)

    return send_file("Editais.csv", as_attachment=True)


@app.route("/", methods=["GET", "POST"])
def home():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
