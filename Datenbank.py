import sqlite3

class datenbank:

    def __init__(self,db):
        self.db = sqlite3.connect(db)
        self.cursor = self.db.cursor()

    def close_db(self):
        self.cursor.close()
        self.db.commit()
        self.db.close()

    def get_disziplin_nr(self,disziplin):
        print(disziplin)
        sql_befehl =f"Select Disziplin_NR from Disziplin \
        Where Disziplin = %s;"%(disziplin)
        self.cursor.execute(sql_befehl)
        disziplin_nr = self.cursor.fetchall()
        print(disziplin_nr)
        return disziplin_nr

    def ad_teilnehmer(self,teilnehmer):
        disziplin_nr = self.get_disziplin_nr(teilnehmer["disziplin"])
        sql_befehl = "INSERT INTO Teilnehmer (Start_Nr,Vorname,Nachname,\
        Ak,Geburtsdatum,Verein,geschlecht,disziplin_nr,email,schule)\
        Values (?,?,?,?,?,?,?,?,?,?)"
        print(teilnehmer)
        self.cursor.execute(sql_befehl,(teilnehmer["start_nr"],\
                                        teilnehmer["vorname"],\
                                        teilnehmer["name"],\
                                        teilnehmer["Ak"],\
                                        teilnehmer["geburtsdatum"],\
                                        teilnehmer["verein"],\
                                        teilnehmer["geschlecht"],\
                                        disziplin_nr,\
                                        teilnehmer["email"],\
                                        teilnehmer["schule"]))#auto increment wert zurückgeben
        self.db.commit()
        #bekomme höchste tn für disziplin, +1

    def test_tabelle_vorhanden(self,name,datenbank) :
        try:
            db = sqlite3.connect(datenbank)
            cursor = db.cursor()
            sql_command ='''Exist SELECT * FROM sqlite_master\
                            WHERE name="''' +name+ '''";'''
            print(sql_command)
            cursor.execute(sql_command)
            temp = cursor.fetchone()
            print(temp)
            return True
        except:
            return False

    def get_disziplin_nr(self,Name_disziplin): #gibt die der disziplin zugeordneten NR zurück
        sql_command = "SELECT Disziplin_Nr From Disziplin \
                        Where Disziplin = '%s';" %(Name_disziplin)
        print(sql_command)
        self.cursor.execute(sql_command)
        return self.cursor.fetchone()[0]

    def insert_new_disziplin(self,Disziplin,Urkunde,): #erstellt neuen db Eintrag disziplin, Disziplin ist der namen und Urkunde der Urkundenfile
        sql_command = "INSERT INTO Disziplin (Urkunde,Disziplin) VALUES(?,?);"
        self.cursor.execute(sql_command, (Urkunde, Disziplin))
        self.db.commit()

    def get_start_nr(self,tn,disp_nr): #gibt die Startnummer des TN für die Disziplin zurück
        sql_command =" SELECT Start_Nr FROM schwimmt \
                        WHERE Tn = '%s' & Disziplin_Nr = '%s';" %(tn,disp_nr)
        self.cursor.execute(sql_command)
        return self.cursor.fetchall()

    def erstelle_tabelle(self,tabel_name,spalten):
        sql_command ="Create Table " + tabel_name + "(" + spalten +");"
        self.cursor.execute(sql_command)
        self.db.commit()

    def insert_into_zeiten(self,zeit,diziplin_nr):
        sql_command = "INSERT INTO zeiten (zeit,disziplin_nr) VALUES(?,?);"
        self.cursor.execute(sql_command,(zeit,diziplin_nr))
        self.db.commit()

    def ad_tn_to_zeiten(self,start_nr,zeit):
        sql_command ="Update Zeiten Set Start_Nr = '%s'\
                        Where Zeiten = %s;"%(int(start_nr),zeit)
        print(sql_command)
        self.cursor.execute(sql_command)
        self.db.commit()

    def get_zeiten(self,disziplin_nr):
        print(disziplin_nr)
        sql_command = "SELECT * FROM zeiten \
                        WHERE disziplin_nr ='%s';" %(disziplin_nr)
        print(sql_command)
        self.cursor.execute(sql_command)
        return self.cursor.fetchall()

    def get_sortet_time(self,disziplin_nr,ak,geschlecht):
        sql_command = "Select z.Zeiten,t.Start_Nr \
                        From Teilnehmer As t,Zeiten As z \
                        Where t.Start_Nr = z.Start_Nr \
                         AND z.disziplin_nr = '%s' \
                         AND t.Ak = '%s' \
                         And t.geschlecht = '%s'  \
                         ORDER BY z.Zeiten;"%(disziplin_nr,ak,geschlecht)
        print(sql_command)
        self.cursor.execute(sql_command)
        return self.cursor.fetchall()

    def get_sortet_time_ges(self,disziplin,geschlecht ):
        sql_command ="Select z.Zeiten,t.Start_Nr \
                        From Teilnehmer AS t, Zeiten As z \
                            Where t.Start_Nr =z.Start_Nr \
                                AND z.disziplin_nr = '%s' \
                                AND t.geschlecht = '%s' \
                                ORDER BY z.Zeiten;" %(disziplin,geschlecht)
        self.cursor.execute(sql_command)
        return self.cursor.fetchall()

    def get_tn_infos(self,start_nr):
        sql_command = "Select * From Teilnehmer \
                        Where Start_Nr = '%s';" %(start_nr)
        self.cursor.execute(sql_command)
        return self.cursor.fetchall()

    def insert_zeiten(self,zeit,start_nr,pos):
        sql_command = "Update Teilnehmer Set Zeit = '%s', pos_ges = '%s'\
                        WHERE Start_Nr = '%s' ;"%(zeit,pos,start_nr)
        self.cursor.execute(sql_command)
        self.db.commit()

    def get_aks(self,disziplin_nr):
        sql_command ="Select aks From Disziplin \
                       WHERE Disziplin_Nr = '%s';"%(disziplin_nr)
        self.cursor.execute(sql_command)
        return self.cursor.fetchall()

    def add_pos(self,pos,start_nr):
        sql_command ="Update Teilnehmer Set pos = '%s' \
                        WHERE Start_Nr = '%s'; " %(pos,start_nr)
        self.cursor.execute(sql_command)
        self.db.commit()

    def get_Teilnehmer(self):
        sql_command =" SELECT * From Teilnehmer; "
        self.cursor.execute(sql_command)
        teilnehmer_list = self.cursor.fetchall()
        return teilnehmer_list

    def get_disziplin(self,disziplin_nr):
        sql_command ="Select Disziplin from Disziplin\
                        Where Disziplin_Nr = '%s';" %(disziplin_nr)
        self.cursor.execute(sql_command)
        return self.cursor.fetchall()

    def insert_pos_ergebnis(self,pos,start_nr):
        sql_command ="  Insert Into ergebnisse (Pos,Start_Nr)\
                        SELECT '%s', '%s' WHERE NOT EXISTS\
                        (SELECT * From ergebnisse \
                            WHERE Start_Nr = '%s') ;"%(pos,start_nr,start_nr)
        print(sql_command)
        self.cursor.execute(sql_command)
        self.db.commit()

    def get_pos(self,start_nr):
        sql_command = "SELECT Pos, Pos_Gesamt From ergebnisse \
                        Where Start_Nr = '%s';"%(start_nr)
        self.cursor.execute(sql_command)
        return self.cursor.fetchone()

    def get_time(self,start_nr):
        sql_command = "SELECT Zeiten From Zeiten \
                        Where Start_Nr = '%s';"%(start_nr)
        self.cursor.execute(sql_command)
        return self.cursor.fetchone()

    def update_tn(self,start_nr,row):
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
        print(zeit)
        print(disziplin_nr)
        sql_command ="Insert INto Zeiten (Zeiten,disziplin_nr) Values(?,?);"
        self.cursor.execute(sql_command,(zeit,disziplin_nr))
        self.db.commit()

    def insert_time(self,start_nr,zeit,disziplin_nr):
        sql_command ="Insert Into Zeiten (Start_Nr,Zeiten,disziplin_nr)\
                        Values(?,?,?);"
        self.cursor.execute(sql_command,(start_nr,zeit,disziplin_nr))
        self.db.commit()

    def insert_pos_gesamt(self,start_nr,pos_ges):
        sql_command = "Update ergebnisse Set Pos_Gesamt = '%s'\
                        Where Start_Nr = '%s';" %(pos_ges,start_nr)
        self.cursor.execute(sql_command)
        self.db.commit()

    def get_ergebnisse_disziplin(self,disziplin_nr):
        sql_command = ("Select e.Start_Nr,t.Vorname,t.Nachname,\
                        z.Zeiten,Ak,e.Pos\
                        From Teilnehmer AS t, Zeiten AS z, ergebnisse AS e \
                        Where e.Start_Nr = z.Start_Nr \
                        AND z.Start_Nr= t.Start_Nr \
                        AND t.disziplin_nr = '%s';")%(disziplin_nr)
        self.cursor.execute(sql_command)
        return self.cursor.fetchall()

    def get_ergebnisse(self,disziplin_nr,geschlecht):
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
