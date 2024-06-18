import datetime
import os
from pathlib import Path
import time

import flask
from flask_dropzone import Dropzone
from flask_bootstrap import Bootstrap

import main
from Datenbank import datenbank

# pfade Definieren
basedir = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'files')
teilnehmer_file = basedir + '/files'
urkunden_file = basedir + "/files/Urkunden_Zusammenfassung"

# Flask config
app = flask.Flask(__name__, static_folder='static')
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
Bootstrap(app)
visibility_urkunden = "hidden"
visibility_teilnehmer = "hidden"

#dropzone config
app.config.update(
    UPLOADED_PATH=os.path.join(basedir, 'files'),
    # Flask-Dropzone config:
    DROPZONE_MAX_FILE_SIZE=2024,  # maximale file größe
    DROPZONE_TIMEOUT=5 * 60 * 1000,  # maximale uploade dauer (hier 5 min)
)
dropzone = Dropzone(app)


@app.route('/', methods=['GET', 'POST'])
def index():
    #Kontroller für die start Seite
    if flask.request.method == 'POST':
        if flask.request.form.get('einstellungen_button') == 'Einstellungen':
            return flask.render_template('einstellungen.html', \
                                         display_teilnehmer="none", \
                                         display_urkunde="none", \
                                         display_teilnehmer_list="none")
        elif flask.request.form.get('auswertung_start') == 'Auswertung start':
            disziplin = flask.request.form.get('disziplinselect')
            if disziplin == None:
                flask.flash("hi")
                disziplinen = main.get_disziplinen()
                return flask.render_template("home.html", \
                                             disziplinen=disziplinen, \
                                             flash_message="True")
            else:
                main.auswertung.start(main.auswertung, disziplin)
                disziplinen = main.get_disziplinen()
                return flask.render_template('home.html', \
                                             disziplinen=disziplinen)
        elif flask.request.form.get("zeiten_anzeigen") == "Zeiten anzeigen":
            disziplin_liste = main.get_disziplinen()
            return flask.render_template('zeiten_bearbeiten.html', \
                                         diplay_tabel="none", \
                                         disziplin_list=disziplin_liste)
        elif flask.request.form.get('home') == 'home':
            disziplinen = main.get_disziplinen()
            return flask.render_template('home.html', disziplinen=disziplinen)
        elif flask.request.form.get('zeitmessung_start') == \
                'zeitmessung start':
            disziplinen = main.get_disziplinen()
            return flask.render_template('zeit_stoppen.html', \
                                         display_zeit_stoppen_tn="none", \
                                         display_startup="True", \
                                         disziplinen=disziplinen)
        elif flask.request.form.get('export') == 'export':
            disziplin = flask.request.form.get('disziplinselect')
            if disziplin == None:
                flask.flash("hi")
                disziplinen = main.get_disziplinen()
                return flask.render_template("home.html", \
                                             disziplinen=disziplinen, \
                                             flash_message="True")
            else:
                main.export.export(main.export, disziplin)
                liste = main.get_export_files()
                return flask.render_template('upload.html', files=liste)
        elif flask.request.form.get("downloade_start") == 'downloade files':
            liste = main.get_export_files()
            return flask.render_template('upload.html', files=liste)
        elif flask.request.form.get('teilnehmer_anzeigen') == \
                'Teilnehmer anzeigen':
            db = datenbank("wettkampf.db")
            Teilnehmer_list = datenbank.get_Teilnehmer(db)
            Teilnerhmer_dic = []
            for teilnehmer in Teilnehmer_list:
                positionen = datenbank.get_pos(db, teilnehmer[0])
                pos = ""
                pos_gesamt = ""
                if positionen != None:
                    pos = positionen[0]
                    pos_gesamt = positionen[1]
                zeit = datenbank.get_time(db, teilnehmer[0])
                if zeit == None:
                    zeit = ""
                else:
                    zeit = main.decode_time(zeit[0])
                disziplin = datenbank.get_disziplin(db, teilnehmer[8])
                geburtsdatum = teilnehmer[4].split(' ')[0]
                Teilnerhmer_dic.append({
                    "tn": teilnehmer[0],
                    "vorname": teilnehmer[1],
                    "name": teilnehmer[2],
                    "ak": teilnehmer[3],
                    "geb": geburtsdatum,
                    "verein": teilnehmer[5],
                    "geschlecht": teilnehmer[6],
                    "pos": pos,
                    "pos_gesamt": pos_gesamt,
                    "zeit": zeit,
                    "disziplin": disziplin[0][0],
                    "email": teilnehmer[9],
                    "schule": teilnehmer[10],
                })
            return flask.render_template("teilnehmer_list.html", \
                                         teilnehmer_list=Teilnerhmer_dic)
        else:
            pass  #
    elif flask.request.method == 'GET':
        disziplinen = main.get_disziplinen()
        return flask.render_template('home.html', disziplinen=disziplinen)


@app.route("/home", methods=['POST', 'GET'])
def home():
    # Funktion für Home Button
    disziplinen = main.get_disziplinen()
    return flask.render_template('home.html', disziplinen=disziplinen)

@app.route("/zeiten_anzeigen", methods=['POST', 'GET'])
def zeiten_anzeigen():
    #anzeigen der Zeiten
    db = datenbank("wettkampf.db")
    if flask.request.form.get("enter") == "enter":
        disziplin = flask.request.form.get("disziplin")
        disziplin_nr = datenbank.get_disziplin_nr(db, disziplin)
        zeiten = datenbank.get_zeiten(db, int(disziplin_nr))
        data = []
        for zeile in zeiten:
            if zeile[1] == None:
                tn = ""
            else:
                tn = zeile[1]
            data.append({"zeit": zeile[0], "tn": tn, "pos": zeile[3]})
    disziplinen_list = main.get_disziplinen()
    return flask.render_template('zeiten_bearbeiten.html', \
                                 disziplinen_list=disziplinen_list, \
                                 data=data, \
                                 display_tabel="true")

@app.route('/add_tn', methods=['POST'])
def add_tn():
    # Kontroller um Tn zu Zeiten hinzuzufügen
    data = flask.request.get_json()
    db = datenbank("wettkampf.db")
    for zeile in data:
        if zeile["tn"] != None:
            datenbank.ad_tn_to_zeiten(db, zeile["tn"], zeile["zeit"])
    return flask.jsonify(success=True)

@app.route('/update_teilnehmer', methods=['POST'])
def update_teilnehmer():
    # kontrolliert ob Teilnehmerdaten verändert wurden und
    # updatet diese in der Datenbank
    global data
    updated_data = flask.request.get_json()
    data = updated_data
    db = datenbank("wettkampf.db")
    Teilnehmer_list = datenbank.get_Teilnehmer(db)
    i = 0
    for row in data:
        teilnehmer = Teilnehmer_list[i]
        if row.get("name") != teilnehmer[2] \
                or row.get("vorname") != teilnehmer[1] \
                or row.get("verein") != teilnehmer[5] \
                or row.get("schule") != teilnehmer[10] \
                or row.get("geb") != teilnehmer[4].split(' ')[0] \
                or row.get("email") != teilnehmer[9] \
                or row.get("geschlecht") != teilnehmer[6]:
            datenbank.update_tn(db, row.get("tn"), row)
        i = i + 1
    return flask.jsonify(success=True)


@app.route('/uploade_urkunde', methods=['POST', 'GET'])
def uploade_urkunde():
    # Kontroller um Urkunden hochzuladen
    if flask.request.method == 'POST':
        f = flask.request.files.get('file')
        if f:
            file_path = urkunden_file + '/' + f.filename
            f.save(file_path)
        return flask.render_template("einstellungen.html")
    return flask.render_template("einstellungen.html")

@app.route('/zeit_messung', methods=['POST', 'GET'])
def zeit_messung():
    if flask.request.method == 'POST':
        if flask.request.form.get('back_button') == 'back':
            temp_class.temp_teilnehmer_nummer = \
                temp_class.temp_teilnehmer_nummer[ \
                0:len(temp_class.temp_teilnehmer_nummer) - 1]
            return flask.render_template('zeit_stoppen.html', \
                                         prediction_text=str( \
                                             temp_class.temp_teilnehmer_nummer \
                                             ), \
                                         display_startup="none", \
                                         display_zeit_stoppem_tn="True")
        elif flask.request.form.get('enter_button') == 'enter':
            teilnehmer_zeit = main.stoppuhr.new_time(main.stoppuhr, \
                                                     temp_class.start_time, \
                                                     temp_class.disziplin, \
                                                     temp_class. \
                                                     temp_teilnehmer_nummer)
            teilenhmer_nummer = temp_class.temp_teilnehmer_nummer
            teilnehmer = datenbank.get_tn_infos(datenbank("wettkampf.db"),teilenhmer_nummer)
            teilnehmer_zeit = main.decode_time(teilnehmer_zeit)
            teilnehmer_name = teilnehmer[1] + ' '  \
                              + teilnehmer[2]
            teilnehmer = dict(nummer=teilenhmer_nummer, \
                              name=teilnehmer_name, \
                              zeit=teilnehmer_zeit)
            temp_class.last_teilnehmer_list.append(teilnehmer)
            temp_class.temp_teilnehmer_nummer = ''
            return flask.render_template('zeit_stoppen.html', \
                                         prediction_text=' ', \
                                         display_startup="none", \
                                         display_zeit_stoppen_tn="True", \
                                         display_zeit_stoppen_ohne_tn="none", \
                                         teilnehmer_list= \
                                             temp_class.last_teilnehmer_list)
        elif flask.request.form.get('stopp_button') == 'stoppen':
            teilnehmer_zeit = main.stoppuhr.new_time(main.stoppuhr, \
                                                     temp_class.start_time, \
                                                     temp_class.disziplin)
            temp_class.zeiten_list.insert(0, teilnehmer_zeit)
            return flask.render_template('zeit_stoppen.html', \
                                         prediction_text=' ', \
                                         display_startup="none", \
                                         display_zeit_stoppen_ohne_tn="True", \
                                         display_zeit_stoppen_tn="none", \
                                         zeiten_list=temp_class.zeiten_list)
        elif flask.request.form.get('start_button') == 'start':
            disziplin = flask.request.form.get('disziplinselect')
            mit_tn = flask.request.form.get("mit_startnr")
            temp_class.disziplin = disziplin
            temp_class.start_time = time.monotonic()
            if mit_tn == "true":
                return flask.render_template('zeit_stoppen.html', \
                                             display_zeit_stoppen_tn="True", \
                                             display_startup="none", \
                                             display_zeit_stoppen_ohne_tn= \
                                                 "none")
            else:
                return flask.render_template('zeit_stoppen.html', \
                                             display_zeit_stoppen_tn="none", \
                                             display_startup="none", \
                                             display_zeit_stoppen_ohne_tn= \
                                                 "True")
        elif flask.request.form.get('Zahlen_button'):
            temp_class.temp_teilnehmer_nummer = \
                temp_class.temp_teilnehmer_nummer + \
                str(flask.request.form.get('Zahlen_button'))
            return flask.render_template('zeit_stoppen.html', \
                                         prediction_text= \
                                             str(temp_class. \
                                                 temp_teilnehmer_nummer), \
                                         display_zeit_stoppen_tn="True", \
                                         display_startup='none', \
                                         teilnehmer_list= \
                                             temp_class.last_teilnehmer_list)
        elif flask.request.form.get("home_button") == "home":
            disziplinen_list = main.get_disziplinen()
            return flask.render_template("home.html")


@app.route('/download/<path:filename>', methods=['GET'])
def download(filename):
    # Kontroller um Ergebnisse runterzuladen
    return flask.send_from_directory(os.path.abspath(".") \
                                     + '/files/export/', \
                                     filename, \
                                     as_attachment=True)


@app.route('/downloade_urkunden/<path:filename>', methods=['GET'])  #sendet urkunde an client
def downloade(filename):
    # Kontroller um Urkunden Vorlagen runterzuladen
    return flask.send_from_directory(os.path.abspath(".") \
                            +'/files/Urkunden_Zusammenfassung/', \
                            filename, as_attachment=True)


@app.route('/einstellungen', methods=['POST', 'GET'])
def einstellungen():
    # Kontroller für die Einstellungen
    if flask.request.method == 'POST':
        if flask.request.form.get('urkunden_bt'):
            urkunden = main.get_urkunden_files()
            return flask.render_template('einstellungen.html', \
                                         display_urkunde="True", \
                                         display_teilnehmer="none", \
                                         urkunden=urkunden)
        elif flask.request.form.get('home') == 'home':
            disziplinen_list = main.get_disziplinen()
            return flask.render_template('home.html', \
                                         disziplinen=disziplinen_list)

        elif flask.request.form.get('uploade_urkunde_bt'):
            neue_urkunde = flask.request.files['urkunde']
            disziplin = flask.request.form["disziplin_urkunde"]
            neue_urkunde.save(os.path.join(os.path.abspath(".") + \
                                           "/files/Urkunden_Zusammenfassung/" \
                                           + disziplin + \
                                           ".docx"))
            urkunden = main.get_urkunden_files()
            return flask.render_template('einstellungen.html', \
                                         display_urkunde="True", \
                                         display_teilnehmer="none", \
                                         urkunden=urkunden)
        elif flask.request.form.get('teilnehmer_bt'):
            return flask.render_template('einstellungen.html', \
                                         display_urkunde="none", \
                                         display_teilnehmer="True", \
                                         display_teilnehmer_list="none")
        elif flask.request.form.get("show_teilnehmer_bt"):  #
            teilnehmer_list = main.get_teilnehmer_list()
            return flask.render_template('einstellungen.html', \
                                         display_urkunde="none", \
                                         display_teilnehmer="True", \
                                         diplay_teilnehmer_list="True", \
                                         Teilnehmer_array=teilnehmer_list)
        elif flask.request.form.get("uploade_teilnehmer_bt"):
            neuer_teilnehmer_file = flask.request.files['teilnehmer_file']
            neuer_teilnehmer_file.save(os.path.join(os.path.abspath(".") \
                                                    + "/files/Teilnehmer.xlsx"))

            main.new_teilnehmer_file()
            return flask.render_template('einstellungen.html', \
                                         display_urkunde="none", \
                                         display_teilnehmer="True", \
                                         display_teilnehmer_list="none")

class speicher:
    def __init__(self):
        self.temp_teilnehmer_nummer = ''
        self.last_teilnehmer_list = []
        self.start_time = ''
        self.disziplin = ''
        self.teilnehmer_list = []
        self.zeiten_list = []


uhr = flask.Flask(__name__, static_folder='static')

def start_Web_interface():
    app.run()


temp_class = speicher()
