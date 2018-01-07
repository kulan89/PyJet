import sqlite3
import csv

baza = "PyJet.db"
con = sqlite3.connect(baza)
cur = con.cursor()
cur.execute("PRAGMA foreign_keys = ON")

def poisciIDdestinacije(destinacija):
    '''vrne ID destinacije, glede na izbrano ime'''
    cur.execute("""
        SELECT ID FROM Destinacije WHERE ime = ?
        """, (destinacija,))
    return cur.fetchone()

def OdhodnaLetalisca():
    '''vrne možna odhodna letališča'''
    cur.execute("""
    SELECT ime FROM Destinacije
    """)
    return cur.fetchall()

def PrihodnaLetalisca(odhodno):
    '''vrne možna prihodna letališča, glede na izbrano odhodno'''
    cur.execute("""
    SELECT ime FROM Destinacije WHERE ID  IN (
    SELECT Prihod FROM Let WHERE Odhod = ?) """,(poisciIDdestinacije(odhodno)))
    return cur.fetchall()

def vrniIDleta(prihod,odhod):
    '''vrne ID izbranega leta''' #odhod in prihod sta ID-ja destinacije
    cur.execute("""
    SELECT ID FROM Let
    WHERE Odhod = ? AND Prihod = ?""",(odhod,prihod))
    return cur.fetchone()

def vrniIDdrzave(drzava):
    '''vrne ID drzave'''
    cur.execute("""
    SELECT ID FROM Drzava
    WHERE Ime = ?""", (drzava,))
    return cur.fetchone()

def dodajPotnika(ime, priimek, emso, drzava):
    cur.execute("""
    INSERT INTO Potnik (Ime, Priimek, EMSO, IDdrzave)
    VALUES (?,?,?,?)
    """,(ime,priimek,emso,vrniIDdrzave(drzava)[0]))
    con.commit()    
    
def steviloSedezev(id_leta):
    '''vrne st. sedežev na letalu'''
    cur.execute("""
    SELECT Kapaciteta FROM TipLetala
    JOIN Let ON TipLetala.ID = Let.Letalo
    WHERE Let.ID = ?""", (id_leta,))
    return cur.fetchone()

def preveriZasedenost(id_urnika):
    '''preveri zasedenost leta z izbranim id-jem urnika'''
    cur.execute("""
    SELECT Zasedenost FROM Urnik WHERE ID = ?""", (id_urnika))
    return cur.fetchone()

def zasediSedez(id_urnika):
    cur.execute("""
    UPDATE Urnik
    SET Zasedenost = ? + 1
    WHERE ID = ?""",(preveriZasedenost(id_urnika)[0],id_urnika))
    con.commit()

def urnikInPotnik(id_potnika,id_urnika):
    '''v tabelo Razpored shrani potnika in njegov izbran let'''
    cur.execute("""
    INSERT INTO Razpored (IDpotnika, IDurnika)
    VALUES (?,?)""", (id_potnika, id_urnika))
    con.commit()
    
