#import Zeug
import datetime
import os
import time

import csv
from docx2pdf import convert
import mailmerge
import pandas as pd
from PyPDF2 import PdfMerger
import pythoncom

from Datenbank import datenbank
import Web_interface


wdFormatPDF = 17
t = 1
start_time = ''
#zum speichern von variablen welche von überall abgerufen werden können


class speicher:

    def __init__(self):
        self.config_file =''
        self.urkunde_file = ''
        self.new_zeiten_file = ''
        self.new_teilnehmer_file=''
        self.urkunde_output_file=''
        self.zwischenspeicher_file=''
        self.Zeiten_file =''
        self.teilnehmer_file_excl=''
        self.temp_pfd_pfad = ''
        self.temp_docx_pfad =''
        self.export_pfad = ''
        self.urkunden_file =''
        self.ak =[]
        self.geschlechter = ["m","w"]
speicher_class = speicher()

def startup():
    if os.path.isfile(os.path.abspath(".")+"/files/teilnehmer.csv"):
        print("teilnehmer file vorhanden")
    else:
        csvdatei = open
        with open (os.path.abspath(".")+"\\files\\teilnehmer.csv","w",\
                   encoding="iso-8859-1") as csvdatei:
            writer = csv.writer(csvdatei,)
            writer.writerow(["Teilnehmer Nummer", "Vorname","Nachname",\
                             "Verein","Geschlecht", "Altersklasse", \
                             "Geburtstag", "Disziplin"])

def loade_config():
    speicher.temp_pdf_pfad = os.path.abspath(".") + '/files/temp/pdf/'
    speicher.temp_docx_pfad = os.path.abspath(".") + '/files/temp/docx/'
    speicher.export_pfad = os.path.abspath(".") + '\\files\\ergebnisse.pdf'
    speicher.urkunden_file =  os.path.abspath(".") +\
                              '/files/Urkunden_Zusammenfassung/'
    #config_file = os.path.abspath(".") + 'files/config.txt'
    Teilnehmer_file_excl = os.path.abspath(".") + '/files/Teilnehmer.xlsx'
    speicher.teilnehmer_file_excl = Teilnehmer_file_excl
    Zeiten_file = os.path.abspath(".") + '/files/zeiten.csv'
    speicher.Zeiten_file = Zeiten_file
    zwischenspeicher_file = os.path.abspath(".") + '/files/temp/pdf/'
    speicher.zwischenspeicher_file = zwischenspeicher_file
    urkunden_Output_file = os.path.abspath(".") + '/files/Urkunden_Gesamt.pdf'
    speicher.urkunde_output_file = urkunden_Output_file
    new_teilnehmer_file = os.path.abspath(".") + '/files/new_tn.xlsx'
    speicher.new_teilnehmer_file = new_teilnehmer_file
    new_zeiten_file = os.path.abspath(".") + '/files/zeiten.csv'
    speicher.new_zeiten_file=new_zeiten_file

def decode_time( zeit):  # gibt zeit im Format Stunden:Minuten:Sekunden zurück
    minuten, seconds = divmod(float(zeit), 60)
    minuten = int(minuten)
    zeit = str(minuten) + ':' + str(round(seconds))
    return zeit

class auswertung():
    def __init__(self,disziplin,db):
        self.disziplin = disziplin
        self.db = ""
        self.disziplin_nr = self.db.get_disziplin_nr(disziplin)

    def get_infos_tn (self, tn):
        datenbank.get_start_nr()
        print("Auswertung start")

    def start (self,disziplin):
        self.db = datenbank("wettkampf.db")
        disziplin_nr = datenbank.get_disziplin_nr(self.db,disziplin)
        zeiten = datenbank.get_zeiten(self.db,disziplin_nr)
        print(zeiten)
        self.cal_pos(self, disziplin_nr)

    def cal_pos(self,disziplin_nr):
        aks = self.db.get_aks(disziplin_nr)
        aks = aks[0][0].split(',')
        for geschlecht in ["m","w"]:
            for ak in aks:
                ergebnis = self.db.get_sortet_time(disziplin_nr,ak,geschlecht)
                print(ergebnis)
                pos= 1
                for zeiten in ergebnis:
                    if zeiten[0] != 0.0:
                        start_nr = zeiten[1]
                        datenbank.insert_pos_ergebnis(self.db,pos,start_nr)
                        pos = pos+1
                print(ergebnis)
                ergebnis = self.db.get_sortet_time_ges\
                            (disziplin_nr,geschlecht)
                pos = 1
                for teilnehmer in ergebnis:
                    if teilnehmer[0] != 0.0:
                        start_nr = teilnehmer[1]
                        datenbank.insert_pos_gesamt(self.db,start_nr,pos)
                        pos= pos+1

def new_teilnehmer_file():#file mit neuen Teilnehmern wird hinzugefügt
    db = datenbank("wettkampf.db")
    print('start new Teilnehmer')
    dataframe1 = pd.read_excel('files/Teilnehmer.xlsx', index_col=False,sheet_name="2024") #liest die Daten in ein pandas dataframe ein
    teilnehmer_vorhanden = False
    dataframe1.rename(columns={"Startnummer" : "400m","Unnamed: 14": "1000m", "Unnamed: 15": "2500m"},inplace=True )
    for i, row in dataframe1.iterrows():#geht alle zeilen des neuen file durch,
        # wenn teilnehmer noch nicht in der csv Datei sind werden sie dort hinzugefügt
        tn_number = row.get('Teilnehmer Nummer')
        tn_nr = row.get('Nr.')
        #print(tn_nr)
        print(row)
        if tn_nr is not None and tn_nr == tn_nr:
            start_nr_400 = row.get("400m")
            start_nr_1000 = row.get("1000m")
            start_nr_2500 = row.get("2500m")
            geb = row["Geburtsdatum"]
            ak = cal_ak(geb)
            geb = str(geb.day) +"." +str(geb.month) +"."+ str(geb.year)
            #print(start_nr_400)
            teilnehmer = {
                "vorname": row["Vorname"],
                "name": row["Name"],
                "geburtsdatum": geb,
                "disziplin": "",
                "verein": row["Verein"],
                "schule": row["Schule"],
                "geschlecht": row["Geschlecht"],
                "start_nr": "",
                "Ak": ak,
                "email": row["Email"],
            }
            if start_nr_400 is not None and start_nr_400 == start_nr_400:
                print("400m")
                print(start_nr_400)
                #print(datenbank.get_tn_infos(db,start_nr_400))
                if not datenbank.get_tn_infos(db,start_nr_400):
                    teilnehmer["disziplin"] = "400m"
                    teilnehmer["start_nr"] = start_nr_400
                    datenbank.ad_teilnehmer(db,teilnehmer)
            if start_nr_1000 is not None and start_nr_1000 == start_nr_1000:
                if not datenbank.get_tn_infos(db,start_nr_1000)  :
                    teilnehmer["disziplin"] = "1000m"
                    teilnehmer["start_nr"] = start_nr_1000
                    datenbank.ad_teilnehmer(db,teilnehmer)
            if start_nr_2500 is not None and start_nr_2500 == start_nr_2500 and start_nr_2500 != 'Stand 30.5.2024':
                if not datenbank.get_tn_infos(db, start_nr_2500):
                    teilnehmer["disziplin"] = "2500m"
                    teilnehmer["start_nr"] = start_nr_2500
                    datenbank.ad_teilnehmer(db, teilnehmer)

def cal_ak(geburtsdatum):
    #berechnet die altersklasse
    print(geburtsdatum)
    if not isinstance(geburtsdatum,datetime.datetime):
        geburtsdatum = geburtsdatum.split(".")
        geburtsdatum = datetime.datetime(int(geburtsdatum[2]),\
                                         int(geburtsdatum[1]),\
                                         int(geburtsdatum[0]))
    datum = datetime.datetime.today().date()
    alter = datum.year - geburtsdatum.year
    if datum.month < geburtsdatum.month:
        alter = alter - 1
    elif datum.month == geburtsdatum.month:
        #day = geburtsdatum.split('.')[0]
        if datum.day < geburtsdatum.day:
            alter = alter - 1
    if alter < 13:
        ak = "AK0"
    elif alter < 20:
        ak = "AK1"
    elif alter < 35:
        ak = "AK2"
    elif alter < 50:
        ak = "AK3"
    else :
        ak = "AK4"
    return ak

def cal_disziplinen(row):
    #print(row)
    disziplinen = ""
    kurz = row.get("400m")
    mittel = row.get("1000m")
    lang = row.get("2500m")
    print(lang)
    if kurz == 1.0:
        disziplinen = "400m"
        print(kurz)
    if mittel == 1.0:
        disziplinen = disziplinen + "_1000m"
        print(mittel)
    if lang == 1.0:
        disziplinen= disziplinen +"_2500m"
        print(lang)
    return disziplinen
#alles runt um Zeitstoppen

class stoppuhr:
    def __init__(self,disziplin):
        self.diszilpin = disziplin
        self.start_time = time.monotonic()

    def new_time(self,start_time,disziplin,start_nr=0): #fügt eine neue Zeit hinzu
        delta_time = time.monotonic() - start_time
        db = datenbank("wettkampf.db")
        disziplin_nr = datenbank.get_disziplin_nr(db,disziplin)
        #zeit wird in Stunden Minuten Sekunden umgerechnet
        if start_nr == 0:
            datenbank.insert_zeit(db,delta_time,disziplin_nr)
        else:
            datenbank.insert_time(db,start_nr,delta_time,disziplin_nr)
        return delta_time

    def start_stoppuhr(self):
        start_time = time.monotonic()

def reset(): # löscht alles dateien
    try:
        os.remove(os.path.abspath(".") + '/files/zeiten.csv')
    except:
        print('kein zeitenfile vorhanden')
    try:
        os.remove(os.path.abspath(".") + '/files/Teilnehmer.xlsx')
    except:
        print('kein Teilnehmerfile vorhanden')
    try:
        os.remove(os.path.abspath(".")+"/ergebnis.db")
    except:
        print('keine Ergebnis Datenbank vorhanden')
    reset_export()
    reset_temp()
    if os.path.exists(os.path.abspath('.')+'/Teilnehmer.xlsx'):
        os.remove(os.path.abspath('.')+'Teilnehmer.xlsx')
    if os.path.exists(os.path.abspath('.')+'/zeiten.csv'):
        os.remove(os.path.abspath('.')+'/zeiten.csv')

def reset_Urkuden():
    print('start reset urkunden')
    x = 0
    for files in os.listdir(os.path.abspath(".") + \
                            "/files/Urkunden_Zusammenfassung/"):
        os.remove(os.path.abspath(".") + "/files/Urkunden_Zusammenfassung/" +\
                  files)
        x = x + 1
    print('Es wurden ' + str(x) + 'files gelöscht')

def reset_temp():
    print('start reset temp')
    x = 0
    for files in os.listdir(os.path.abspath(".") + "/files/temp/"):
        os.remove(os.path.abspath(".") + "/files/temp/" + files)
        x = x + 1
    print('Es wurden ' + str(x) + 'files gelöscht')

def get_disziplinen(): #return list mit allen disziplinen
    disziplinen_list = []
    for f in os.listdir(os.path.abspath(".") + \
                        '/files/Urkunden_Zusammenfassung'):
        disziplinen_list.append(f.split('.')[0])
    return disziplinen_list

def loade_ak():#list alle vorhandenen Altersklassen aus und returnt diese als list

    dataframe1 = pd.read_csv(os.path.join(os.path.abspath(".") + \
                                          '/files/teilnehmer.csv'),\
                             index_col=False, encoding="iso-8859-1")
    df_altersklassen = dataframe1['Altersklasse']
    altersklassen = []
    for ak in df_altersklassen:
        vorhanden = False
        for temp in altersklassen:
            if temp == ak:
                vorhanden = True
        if vorhanden == False:
            altersklassen.append(ak)
    return altersklassen

class export:
    #in der export classe sind alle methoden die für den export der Daten in pdf und xlsx benötigt werden
    def __int__(self):
        self.temp_pfd_pfad =  os.path.abspath(".") + '/files/temp/pdf/'
        self.temp_docx_pfad = os.path.abspath(".") + '/files/temp/docx/'
        self.export_pfad= os.path.abspath(".") + '\\files\\ergebnisse.pdf'

    def export(self,disziplin):
        pythoncom.CoInitialize()
        db = datenbank("wettkampf.db")
        disziplin_nr = datenbank.get_disziplin_nr(db,disziplin)
        ergebnisse = datenbank.get_ergebnisse_disziplin(db,disziplin_nr)
        self.write_to_docx(self,ergebnisse,disziplin)
        print(ergebnisse)
        print('schlafe 5 s')
        time.sleep(5)
        for f in os.listdir(os.path.abspath(".") + '/files/temp/docx/'):
            self.docx_to_pdf(self,os.path.abspath(".") +\
                             '/files/temp/docx/' + f)
            time.sleep(1)
        self.merge_pdf(self)
        time.sleep(2)
        self.delete_temp_files(self)
        try:
            pythoncom.UnInitialize()
        except:
            print("buffer")
        self.export_xlsx(self,disziplin)

    def write_to_docx(self,list_teilnehmer,disziplin):#überträgt daten in textfieldes des docx dokumentes
        x = 1
        y = 1
        print(disziplin)
        if len(list_teilnehmer) > 0:
            x = 0
            # erstellt dynamisch bis zu 10 dictionary die jeweils die daten zu einen Teilnehmer erhalten diese werden dann zusammen in eine word datei geschrieben
            # dies ist effizienter als jeden teilnehmer einzelt in eine word datei zu schreiben
            # eventuell erweiterung in 10ner schritte zur steigerung der effiziens
            datum = self.get_datum(self)
            for teilnehmer in list_teilnehmer:
                x = x + 1
                globals()[f"cust_{x}"] = {
                    'teilnehmer_Vorname': teilnehmer[1],
                    'teilnehmer_Nachname': teilnehmer[2],
                    'teilnehmer_ak': teilnehmer[4],
                    'teilnehmer_Zeit': decode_time(teilnehmer[3]),
                    'datum': datum,
                    'teilnehmer_platz': str(teilnehmer[0])}
                if x == 10:
                    urkunden_file = os.path.abspath(".") + \
                                  '/files/Urkunden_Zusammenfassung/' +disziplin+".docx"
                    with mailmerge.MailMerge(urkunden_file) \
                            as Urkunden_dokument:
                        Urkunden_dokument.merge_templates(
                            [cust_1, cust_2, cust_3, cust_4, cust_5, cust_6,\
                                        cust_7, cust_8, cust_9, cust_10], \
                                        separator='page_break')
                        x = 0
                        while os.path.isfile(os.path.abspath(".") + \
                                             '/files/temp/docx/dokument' +\
                                             str(y) + '.docx'):
                            y = y + 1
                        Urkunden_dokument.write(os.path.abspath(".") +\
                                                '/files/temp/docx/dokument'\
                                                + str(y) + '.docx')
                        Urkunden_dokument.close()
            urkunden_file =os.path.abspath(".") + \
                           '/files/Urkunden_Zusammenfassung/' +\
                           disziplin + '.docx'
            with mailmerge.MailMerge(urkunden_file) as Urkunden_dokument:
                if x == 10:
                    Urkunden_dokument.merge_templates(
                        [cust_1, cust_2, cust_3, cust_4, cust_5,\
                                    cust_6, cust_7, cust_8, cust_9, cust_10],\
                                    separator='page_break')
                elif x == 9:
                    Urkunden_dokument.merge_templates(
                        [cust_1, cust_2, cust_3, cust_4, cust_5,\
                                    cust_6, cust_7, cust_8, cust_9],\
                                    separator='page_break')
                elif x == 8:
                    Urkunden_dokument.merge_templates(
                        [cust_1, cust_2, cust_3, cust_4, cust_5,\
                                    cust_6, cust_7, cust_8],\
                                    separator='page_break')
                elif x == 7:
                    Urkunden_dokument.merge_templates(
                        [cust_1, cust_2, cust_3, cust_4, cust_5,\
                                    cust_6, cust_7],\
                                    separator='page_break')
                elif x == 6:
                    Urkunden_dokument.merge_templates(
                        [cust_1, cust_2, cust_3, cust_4, cust_5, cust_6],\
                                    separator='page_break')
                elif x == 5:
                    Urkunden_dokument.merge_templates(
                        [cust_1, cust_2, cust_3, cust_4, cust_5],\
                                    separator='page_break')
                elif x == 4:
                    Urkunden_dokument.merge_templates(
                        [cust_1, cust_2, cust_3, cust_4],\
                                    separator='page_break')
                elif x == 3:
                    Urkunden_dokument.merge_templates(
                        [cust_1, cust_2, cust_3], separator='page_break')
                elif x == 2:
                    Urkunden_dokument.merge_templates(
                        [cust_1, cust_2], separator='page_break')
                elif x == 1:
                    Urkunden_dokument.merge_templates(
                        [cust_1], separator='page_break')
                while os.path.isfile(os.path.abspath(".") +\
                                     '/files/temp/docx/dokument' + \
                                     str(y) + '.docx'):
                    y = y + 1
                Urkunden_dokument.write(os.path.abspath(".") + \
                                        '/files/temp/docx/dokument' + \
                                        str(y) + '.docx')
                print('daten in docx übertragen')
                Urkunden_dokument.close()
        else:
            print('error keine daten erhalten')
        try:
            Urkunden_dokument.close()
        except:
            print('nö')

    def docx_to_pdf(self,inputFile): # convertiert docx datei zu pdf
        print('start docx_to_pdf')
        x = 1
        check = True
        while check: #um keine vorhandenen datei zu überschreiben
            outputFile =os.path.abspath(".") + '/files/temp/pdf/'+ \
                        str(x) + '.pdf'
            if os.path.isfile(outputFile):
                check = True
                x = x + 1
            else:
                check = False
        convert(inputFile,outputFile)

    def merge_pdf(self):#fügt alle dateien in /files/temp/pdf/ zu einer pdf zusammen
        print('merge pdf')
        check = True
        x = 1
        merger = PdfMerger()
        vorhanden = False
        for f in os.listdir(os.path.abspath(".") + '/files/temp/pdf/'):
            merger.append(os.path.abspath(".") + '/files/temp/pdf/' + f)
            vorhanden = True
        if vorhanden: # falls keine dateien exestieren wird auch keine merge datei erstellt
            merger.write(os.path.abspath(".") + '/files/export/ergebnise.pdf')
        merger.close()

    def get_datum(self): #gibt das aktuelle datum zurück
        print('start get_datum')
        datum = datetime.date.today()
        tag = datum.day
        monat = datum.month
        jahr = datum.year
        datum = str(tag) + '.' + str(monat) + '.' + str(jahr)
        return datum

    def delete_temp_files(self): #löscht die files in files/temp
        print("start delete_temp_files")
        counter = 0
        for file in os.listdir(os.path.abspath(".") + '/files/temp/pdf/'):
            os.remove(os.path.abspath(".") + '/files/temp/pdf/' + file)
            counter = counter + 1
        for file in os.listdir(os.path.abspath(".")+'/files/temp/docx/'):
            os.remove(os.path.abspath(".")+ '/files/temp/docx/' + file)
            counter = counter +1
        print("es wurden " + str(counter) + ' Dateien gelöscht')

    def export_xlsx(self,disziplin): # überträgt daten aus sqllite db in xlsx datei
        db = datenbank("wettkampf.db")
        disziplin_nr = db.get_disziplin_nr(disziplin)
        alterstklassen = db.get_aks(disziplin_nr)
        geschlechter = ["w", "m"]
        for geschlecht in geschlechter:
                ergebnisse,description = db.get_ergebnisse(disziplin_nr,\
                                                           geschlecht)
                columns = [desc[0] for desc in description ]
                print(columns)
                tabelle = disziplin +"_" + geschlecht
                if len(ergebnisse) > 0:
                    df = pd.DataFrame(list(ergebnisse), columns=columns)
                    writer = pd.ExcelWriter( os.path.join(\
                                os.path.abspath(".") + \
                                '/files/export/export' + tabelle + '.xlsx'))
                    df.to_excel(writer, sheet_name=tabelle,index = False)
                    writer.save()

def reset_export(): #löscht alle Files aus export ordner
    print('start reset export')
    x = 0
    for files in os.listdir(os.path.abspath(".") + "/files/export/"):
        os.remove(os.path.abspath(".") + "/files/export/" + files)
        x = x + 1
    print('Es wurden ' + str(x) + 'files gelöscht')

def get_export_files(): #returnt alle files in /files/export/
    files = []
    for file in os.listdir(os.path.abspath(".") + '/files/export/'):
        files.append(file)
    return files

def get_urkunden_files(): #gibt alle files Zurück die Unter /Files/Urkunden_Zusammenfassung/ gespeichert sind
    files = []
    for file in os.listdir(os.path.abspath(".") + \
                           '/files/Urkunden_Zusammenfassung/'):
        files.append(file)
    return files

def get_teilnehmer_list():
    teilnehmer_list = []
    dataframe1 = pd.read_csv('files/teilnehmer.csv', index_col=False,\
                             encoding="iso-8859-1")  # liest die Daten in ein pandas dataframe ein
    for i,row in dataframe1.iterrows():
        tn_number = row.get('Teilnehmer Nummer')
        tn_vorname = row.get('Vorname')
        tn_nachname = row.get('Nachname')
        tn_Verein = row.get('Verein')
        tn_ak = row.get("Altersklasse")
        tn_geschlecht = row.get('Geschlecht')
        tn_disziplin = row.get('Disziplin').split('_')
        tn_geburtstag = row.get('Geburtstag')
        tn_disziplinen = ""
        for disziplin in tn_disziplin :
            tn_disziplinen = tn_disziplinen + " " +  disziplin
        teilnehmer = [tn_number, tn_vorname, tn_nachname, tn_Verein,\
                      tn_ak, tn_disziplinen, tn_geschlecht, tn_geburtstag]
        teilnehmer_list.append(teilnehmer)
    return teilnehmer_list

def main():
    if __name__ == '__main__':
        db = datenbank("wettkampf.db")
        #loade_ak()
        startup()
        loade_config()
        #new_teilnehmer_file()
        Web_interface.start_Web_interface()
if __name__ == '__main__':
    main()
