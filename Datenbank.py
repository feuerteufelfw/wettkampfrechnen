import sqlite3
import time


class datenbank:

    def __init__(self,db):
        self.db = sqlite3.connect(db)
        self.cursor = self.db.cursor()

    def close_db(self):
        self.cursor.close()
        self.db.commit()
        self.db.close()

    def ad_teilnehmer(self,teilnehmer):
        # fügt einen neuen Teilnehmer in die DB hinzu
        disziplin_nr = self.get_disziplin_nr(teilnehmer["disziplin"])
        sql_befehl = "INSERT INTO Teilnehmer (Start_Nr,Vorname,Nachname,\
        Ak,Geburtsdatum,Verein,geschlecht,disziplin_nr,email,schule)\
        Values (?,?,?,?,?,?,?,?,?,?)"
        self.cursor.execute(sql_befehl,(teilnehmer["start_nr"],\
                                        teilnehmer["vorname"],\
                                        teilnehmer["name"],\
                                        teilnehmer["Ak"],\
                                        teilnehmer["geburtsdatum"],\
                                        teilnehmer["verein"],\
                                        teilnehmer["geschlecht"],\
                                        disziplin_nr,\
                                        teilnehmer["email"],\
                                        teilnehmer["schule"]))
        self.db.commit()

    def get_disziplin_nr(self,Name_disziplin):
        # gibt die der Disziplin zugeordneten Nummer zurück
        sql_command = "SELECT Disziplin_Nr From Disziplin \
                        Where Disziplin = '%s';" %(Name_disziplin)
        self.cursor.execute(sql_command)
        return self.cursor.fetchone()[0]

    def insert_new_disziplin(self,Disziplin,Urkunde,):
        # erstellt neuen db Eintrag Disziplin
        sql_command = "INSERT INTO Disziplin (Urkunde,Disziplin) VALUES(?,?);"
        self.cursor.execute(sql_command, (Urkunde, Disziplin))
        self.db.commit()

    def insert_into_zeiten(self,zeit,diziplin_nr):
        # fügt eine neue Zeit hinzu
        sql_command = "INSERT INTO zeiten (zeit,disziplin_nr) VALUES(?,?);"
        self.cursor.execute(sql_command,(zeit,diziplin_nr))
        self.db.commit()

    def ad_tn_to_zeiten(self,start_nr,zeit):
        # Fügt einer Zeit eine Startnummer hinzu
        sql_command ="Update Zeiten Set Start_Nr = '%s'\
                        Where Zeiten = '%s';"%(int(start_nr),zeit)
        self.cursor.execute(sql_command)
        self.db.commit()
        time.sleep((0.2))

    def get_zeiten(self,disziplin_nr):
        # Gibt die gemessenen Zeiten zu einer Disziplin zurück
        sql_command = "SELECT * FROM zeiten \
                        WHERE disziplin_nr ='%s';" %(disziplin_nr)
        self.cursor.execute(sql_command)
        return self.cursor.fetchall()

    def get_sortet_time(self,disziplin_nr,ak,geschlecht):
        # gibt zeiten und Startnummern einer Disziplin
        # sortiert zurück, in Bezug auf Altersklasse und Geschlecht
        sql_command = "Select z.Zeiten,t.Start_Nr \
                        From Teilnehmer As t,Zeiten As z \
                        Where t.Start_Nr = z.Start_Nr \
                         AND z.disziplin_nr = '%s' \
                         AND t.Ak = '%s' \
                         And t.geschlecht = '%s'  \
                         ORDER BY z.Zeiten;"%(disziplin_nr,ak,geschlecht)

        self.cursor.execute(sql_command)
        return self.cursor.fetchall()

    def get_sortet_time_ges(self,disziplin,geschlecht ):
        # gibt zeiten und Startnummern einer Disziplin
        # sortiert zurück, unter Beachtung des Geschlechtes
        sql_command ="Select z.Zeiten,t.Start_Nr \
                        From Teilnehmer AS t, Zeiten As z \
                            Where t.Start_Nr =z.Start_Nr \
                                AND z.disziplin_nr = '%s' \
                                AND t.geschlecht = '%s' \
                                ORDER BY z.Zeiten;" %(disziplin,geschlecht)
        self.cursor.execute(sql_command)
        return self.cursor.fetchall()

    def get_tn_infos(self,start_nr):
        # gibt hinterlegte Infos zu einer Startnummer zurück
        sql_command = "Select * From Teilnehmer \
                        Where Start_Nr = '%s';" %(start_nr)
        self.cursor.execute(sql_command)
        return self.cursor.fetchone()

    def get_aks(self,disziplin_nr):
        # gibt Altersklassen, welche die Disziplin schwimmen zurück
        sql_command ="Select aks From Disziplin \
                       WHERE Disziplin_Nr = '%s';"%(disziplin_nr)
        self.cursor.execute(sql_command)
        return self.cursor.fetchall()

    def get_Teilnehmer(self):
        # gibt alle gespeicherten Teilnehmer zurück
        sql_command =" SELECT * From Teilnehmer; "
        self.cursor.execute(sql_command)
        teilnehmer_list = self.cursor.fetchall()
        return teilnehmer_list

    def get_disziplin(self,disziplin_nr):
        # gibt Namen der Disziplin zurück
        sql_command ="Select Disziplin from Disziplin\
                        Where Disziplin_Nr = '%s';" %(disziplin_nr)
        self.cursor.execute(sql_command)
        return self.cursor.fetchall()

    def insert_pos_ergebnis(self,pos,start_nr):
        # fügt eine Startnummer und deren Position
        # in die Tabelle ergebnisse hinzu
        sql_command ="  Insert Into ergebnisse (Pos,Start_Nr)\
                        SELECT '%s', '%s' WHERE NOT EXISTS\
                        (SELECT * From ergebnisse \
                            WHERE Start_Nr = '%s') ;"%(pos,start_nr,start_nr)
        self.cursor.execute(sql_command)
        self.db.commit()

    def get_pos(self,start_nr):
        # Gibt die Position und die Gesamtposition einer Startnummer zurück
        sql_command = "SELECT Pos, Pos_Gesamt From ergebnisse \
                        Where Start_Nr = '%s';"%(start_nr)
        self.cursor.execute(sql_command)
        return self.cursor.fetchone()

    def get_time(self,start_nr):
        # Gibt Zeit einer Startnummer zurück
        sql_command = "SELECT Zeiten From Zeiten \
                        Where Start_Nr = '%s';"%(start_nr)
        self.cursor.execute(sql_command)
        return self.cursor.fetchone()

    def update_tn(self,start_nr,row):
        # Updatet die zu einer Startnummer hinterlegten Teilnehmerdaten
        vorname =row.get("vorname")
        name = row.get("name")
        verein = row.get("verein")
        schule = row.get("schule")
        geb = row.get("geb")
        geschlecht = row.get("geschlecht")
        email = row.get("email")
        sql_command ="Update Teilnehmer \
                        Set Vorname ='%s', \
                            Nachname = '%s',\
                            Verein = '%s',\
                            Schule = '%s',\
                            Geburtsdatum = '%s',\
                            Email ='%s',\
                            geschlecht = '%s' \
                            WHERE Start_Nr = '%s'"\
                            %(vorname,name,verein,schule,geb,\
                              email,geschlecht,start_nr)
        self.cursor.execute(sql_command)
        self.db.commit()

    def insert_zeit(self,zeit,disziplin_nr):
        # speichert eine Zeit
        # und die Diszplinnummer auf welche sich die Zeit bezieht
        sql_command ="Insert INto Zeiten (Zeiten,disziplin_nr) Values(?,?);"
        self.cursor.execute(sql_command,(zeit,disziplin_nr))
        self.db.commit()

    def insert_time(self,start_nr,zeit,disziplin_nr):
        # speichert eine Zeit, die entsprechende Disziplin Nummer
        # und die zugeordnete Startnummer
        sql_command ="Insert Into Zeiten (Start_Nr,Zeiten,disziplin_nr)\
                        Values(?,?,?);"
        self.cursor.execute(sql_command,(start_nr,zeit,disziplin_nr))
        self.db.commit()

    def insert_pos_gesamt(self,start_nr,pos_ges):
        # fügt Gesamtpostion hinzu
        sql_command = "Update ergebnisse Set Pos_Gesamt = '%s'\
                        Where Start_Nr = '%s';" %(pos_ges,start_nr)
        self.cursor.execute(sql_command)
        self.db.commit()

    def get_ergebnisse_disziplin(self,disziplin_nr):
        # gibt alle Ergebnisse einer Disziplin zurück
        sql_command = ("Select e.Start_Nr,t.Vorname,t.Nachname,\
                        z.Zeiten,Ak,e.Pos\
                        From Teilnehmer AS t, Zeiten AS z, ergebnisse AS e \
                        Where e.Start_Nr = z.Start_Nr \
                        AND z.Start_Nr= t.Start_Nr \
                        AND t.disziplin_nr = '%s';")%(disziplin_nr)
        self.cursor.execute(sql_command)
        return self.cursor.fetchall()

    def get_ergebnisse(self,disziplin_nr,geschlecht):
        # gibt die Ergebnisse eines Geschlechtes in einer Disziplin zurück
        sql_command = ("Select e.Pos_Gesamt,z.Zeiten,t.Vorname,t.Nachname,\
                        t.geschlecht,Ak,e.Pos,t.Verein \
                        From Teilnehmer AS t, Zeiten AS z, ergebnisse AS e \
                        Where e.Start_Nr = z.Start_Nr \
                        AND z.Start_Nr= t.Start_Nr \
                        AND t.disziplin_nr = '%s' \
                        AND t.geschlecht = '%s' \
                        ORDER BY e.Pos_Gesamt;") % (disziplin_nr,geschlecht)
        self.cursor.execute(sql_command)
        return self.cursor.fetchall(), self.cursor.description
