#import
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


def loade_config():
    #laden der einzelnen Pfade
    speicher.temp_pdf_pfad = os.path.abspath(".") + '/files/temp/pdf/'
    speicher.temp_docx_pfad = os.path.abspath(".") + '/files/temp/docx/'
    speicher.export_pfad = os.path.abspath(".") + '\\files\\ergebnisse.pdf'
    speicher.urkunden_file =  os.path.abspath(".") +\
                              '/files/Urkunden_Zusammenfassung/'
    Teilnehmer_file_excl = os.path.abspath(".") + '/files/Teilnehmer.xlsx'
    speicher.teilnehmer_file_excl = Teilnehmer_file_excl
def decode_time( zeit):
    # Zeit wird von Sekunden in Minuten, Sekunden Umgerechnet
    minuten, seconds = divmod(float(zeit), 60)
    minuten = int(minuten)
    zeit = str(minuten) + ':' + str(round(seconds))
    return zeit

class auswertung():
    def __init__(self,disziplin,db):
        self.disziplin = disziplin
        self.db = ""
        self.disziplin_nr = self.db.get_disziplin_nr(disziplin)

    def start (self,disziplin):
        self.db = datenbank("wettkampf.db")
        disziplin_nr = datenbank.get_disziplin_nr(self.db,disziplin)
        self.cal_pos(self, disziplin_nr)

    def cal_pos(self,disziplin_nr):
        #Die Positionen der Teilnehmer werden ermittelt
        # und in die Tabelle ergebnisse abgespeichert
        aks = self.db.get_aks(disziplin_nr)
        aks = aks[0][0].split(',')
        for geschlecht in ["m","w"]:
            for ak in aks:
                #Ermitteln der Position in der jeweiligen Altersklasse
                ergebnis = self.db.get_sortet_time\
                    (disziplin_nr,ak,geschlecht)
                pos= 1
                for zeiten in ergebnis:
                    if zeiten[0] != 0.0:
                        start_nr = zeiten[1]
                        datenbank.insert_pos_ergebnis(self.db,pos,start_nr)
                        pos = pos+1
            ergebnis = self.db.get_sortet_time_ges\
                            (disziplin_nr,geschlecht)
            pos = 1
            #Ermitteln der Gesamt Position (M,W getrennt)
            for teilnehmer in ergebnis:
                if teilnehmer[0] != 0.0:
                    start_nr = teilnehmer[1]
                    datenbank.insert_pos_gesamt(self.db,start_nr,pos)
                    pos= pos+1

def new_teilnehmer_file():
    #Laden neuer Teilnehmer aus einen xlsx File
    db = datenbank("wettkampf.db")
    dataframe1 = pd.read_excel('files/Teilnehmer.xlsx', index_col=False,sheet_name="2024")
    #Benneung der unbenannten Spalten
    dataframe1.rename(columns={"Startnummer" : "400m","Unnamed: 14": "1000m", "Unnamed: 15": "2500m"},inplace=True )
    for i, row in dataframe1.iterrows():
        #geht alle zeilen (Teilnehmer) des neuen File durch
        tn_nr = row.get('Nr.')
        if tn_nr is not None and tn_nr == tn_nr:
            start_nr_400 = row.get("400m")
            start_nr_1000 = row.get("1000m")
            start_nr_2500 = row.get("2500m")
            geb = row["Geburtsdatum"]
            ak = cal_ak(geb)
            geb = str(geb.day) +"." +str(geb.month) +"."+ str(geb.year)
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
            # falls eine Startnummer für die Disziplin enthalten ist,
            # wird der Tn mit der Startnummer hinzugefügt
            if start_nr_400 is not None and start_nr_400 == start_nr_400:
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
    #berechnet die Altersklasse anhand des Geburtsjahres
    if not isinstance(geburtsdatum,datetime.datetime):
        geburtsdatum = geburtsdatum.split(".")
        geburtsdatum = datetime.datetime(int(geburtsdatum[2]),\
                                         int(geburtsdatum[1]),\
                                         int(geburtsdatum[0]))
    datum = datetime.datetime.today().date()
    alter = datum.year - geburtsdatum.year
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

class stoppuhr:
    def new_time(self,start_time,disziplin,start_nr=0):
        #fügt eine neue Zeit hinzu und gibt diese zurück
        delta_time = time.monotonic() - start_time
        db = datenbank("wettkampf.db")
        disziplin_nr = datenbank.get_disziplin_nr(db,disziplin)
        if start_nr == 0:
            datenbank.insert_zeit(db,delta_time,disziplin_nr)
        else:
            datenbank.insert_time(db,start_nr,delta_time,disziplin_nr)
        return delta_time

def reset_temp():
    for files in os.listdir(os.path.abspath(".") + "/files/temp/"):
        os.remove(os.path.abspath(".") + "/files/temp/" + files)

def get_disziplinen():
    #Gibt eine List mit allen Disziplinen zurück
    disziplinen_list = []
    for f in os.listdir(os.path.abspath(".") + \
                        '/files/Urkunden_Zusammenfassung'):
        disziplinen_list.append(f.split('.')[0])
    return disziplinen_list

class export:
    #Exportiert die Ergebnisse als xlsx
    #und erstellt die einzelnen Urkunden
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
        time.sleep(2)
        self.docx_to_pdf(disziplin)
        self.delete_temp_files(self)
        try:
            pythoncom.UnInitialize()
        except:
            print("buffer")
        self.export_xlsx(self,disziplin)

    def write_to_docx(self,list_teilnehmer,disziplin):
        #überträgt daten in die Textfieldes des docx Dokumentes
        if len(list_teilnehmer) > 0:
            #erstellt dynamisch bis zu 10 Dictionarys,
            #die jeweils die Daten zu einem Teilnehmer erhalten
            #diese werden dann zusammen in eine Word Datei geschrieben.
            datum = self.get_datum(self)
            tn_dic_list =[]
            for teilnehmer in list_teilnehmer:
                tn_dic = {
                    'teilnehmer_Vorname': teilnehmer[1],
                    'teilnehmer_Nachname': teilnehmer[2],
                    'teilnehmer_ak': teilnehmer[4],
                    'teilnehmer_Zeit': decode_time(teilnehmer[3]),
                    'datum': datum,
                    'teilnehmer_platz': str(teilnehmer[5])}
                tn_dic_list.append(tn_dic)
                urkunden_file = os.path.abspath(".") + \
                              '/files/Urkunden_Zusammenfassung/' +disziplin+".docx"
                with mailmerge.MailMerge(urkunden_file) \
                        as Urkunden_dokument:
                    Urkunden_dokument.merge_templates(tn_dic_list, separator='page_break')
                    Urkunden_dokument.write(os.path.abspath(".") +\
                                            '/files/temp/docx/'\
                                            +disziplin + '.docx')
                    Urkunden_dokument.close()
        else:
            print('error keine daten erhalten')
        try:
            Urkunden_dokument.close()
        except:
            print('fehler bem Schließen der Urkunde')

    def docx_to_pdf(self,disziplin):
        # convertiert docx datei zu pdf
        output_File =os.path.abspath(".") + '/files/export/Urkunden'+ \
                      disziplin +".pdf"
        input_File = os.path.abspath(".") + \
                     '/files/temp/docx/' + disziplin + ".docx"
        convert(input_File,output_File)

    def get_datum(self):
        #gibt das aktuelle datum zurück
        datum = datetime.date.today()
        tag = datum.day
        monat = datum.month
        jahr = datum.year
        datum = str(tag) + '.' + str(monat) + '.' + str(jahr)
        return datum

    def delete_temp_files(self):
        #löscht die Files in files/temp
        counter = 0
        for file in os.listdir(os.path.abspath(".") + '/files/temp/pdf/'):
            os.remove(os.path.abspath(".") + '/files/temp/pdf/' + file)
            counter = counter + 1
        for file in os.listdir(os.path.abspath(".")+'/files/temp/docx/'):
            os.remove(os.path.abspath(".")+ '/files/temp/docx/' + file)
            counter = counter +1

    def export_xlsx(self,disziplin):
        # überträgt die Ergebnisse aus der db in xlsx Datei
        db = datenbank("wettkampf.db")
        disziplin_nr = db.get_disziplin_nr(disziplin)
        geschlechter = ["w", "m"]
        for geschlecht in geschlechter:
                ergebnisse,description = db.get_ergebnisse(disziplin_nr,\
                                                           geschlecht)
                columns = [desc[0] for desc in description ]
                tabelle = disziplin +"_" + geschlecht
                if len(ergebnisse) > 0:
                    df = pd.DataFrame(list(ergebnisse), columns=columns)
                    writer = pd.ExcelWriter( os.path.join(\
                                os.path.abspath(".") + \
                                '/files/export/export' + tabelle + '.xlsx'))
                    df.to_excel(writer, sheet_name=tabelle,index = False)
                    writer.save()

def reset_export():
    #löscht alle Files aus export ordner
    for files in os.listdir(os.path.abspath(".") + "/files/export/"):
        os.remove(os.path.abspath(".") + "/files/export/" + files)

def get_export_files():
    #Gibt alle Files in /files/export/ zurück
    files = []
    for file in os.listdir(os.path.abspath(".") + '/files/export/'):
        files.append(file)
    return files

def get_urkunden_files():
    #gibt alle Files Zurück die Unter /Files/Urkunden_Zusammenfassung/
    # gespeichert sind
    files = []
    for file in os.listdir(os.path.abspath(".") + \
                           '/files/Urkunden_Zusammenfassung/'):
        files.append(file)
    return files

def main():
    if __name__ == '__main__':
        loade_config()
        Web_interface.start_Web_interface()
if __name__ == '__main__':
    main()
