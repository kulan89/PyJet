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

##def OdhodnaLetalisca():
##    '''vrne možna odhodna letališča'''
##    cur.execute("""
##        SELECT ime FROM Destinacije
##        """)
##    return cur.fetchall()

def OdhodnaLetalisca():
    '''vrne možna odhodna letališča'''
    cur.execute("""
        SELECT ID,ime FROM Destinacije
        """)
    return cur.fetchall()

##def PrihodnaLetalisca(odhodno):
##    '''vrne možna prihodna letališča, glede na izbrano odhodno'''
##
##    mesta = ()
##    if odhodno.lower() == "ljubljana":
##        cur.execute("""
##             SELECT ime FROM Destinacije WHERE ime <> 'Ljubljana'
##             """)
##        mesta = cur.fetchall()
##    else:
##        mesta = [('Ljubljana',)]
##    return mesta


def PrihodnaLetalisca(odhodnoId):
    '''vrne možna prihodna letališča, glede na izbrano odhodno'''
    mesta = ()
    if odhodnoId == 1: # (1 == Ljubljana)
        # iberi vsa letališča razen Ljubljane
        cur.execute("""
             SELECT ID,ime FROM Destinacije WHERE ID <> 1
             """)
        mesta = cur.fetchall()
    else:
        cur.execute("""
             SELECT ID,ime FROM Destinacije WHERE ID == 1
             """)
        mesta = [cur.fetchone()]
    return mesta

def vrniIDleta(odhod, prihod):
    '''vrne ID izbranega leta''' #odhod in prihod sta ID-ja destinacije
    cur.execute("""
        SELECT ID FROM Let
        WHERE Odhod = ? AND Prihod = ?""",(odhod,prihod))
    return cur.fetchone()

def vrniIDleta2(id_urnika):
    '''vrne ID leta glede na urnik'''
    cur.execute("""
        SELECT IDleta FROM Urnik WHERE Urnik.ID = ?""", (id_urnika,))
    return cur.fetchone()

def vrniIDleta3(odhod, prihod):
    '''vrne ID izbranega leta za odhod in prihod z imeni destinacij'''

    odhodno = poisciIDdestinacije(odhod)
    prihodno = poisciIDdestinacije(prihod)
    return vrniIDleta(odhodno, prihodno)

def vrniIDdrzave(drzava):
    '''vrne ID drzave'''
    cur.execute("""
        SELECT ID FROM Drzava
        WHERE Ime = ?""", (drzava,))
    return cur.fetchone()

def dodajPotnika(ime, priimek, emso, drzava, email):
    cur.execute("""
        INSERT INTO Potnik (Ime, Priimek, EMSO, IDdrzave, Email)
        VALUES (?,?,?,?,?)
        """,(ime,priimek,emso,vrniIDdrzave(drzava)[0], email))
    con.commit()

def vrniIDpotnika(ime,priimek,emso,drzava,email):
    try:
        cur.execute("""
              SELECT ID FROM Potnik
              WHERE Ime = ? AND Priimek=? AND EMSO = ? AND IDdrzave = ? AND Email = ?""", (ime,priimek,emso,vrniIDdrzave(drzava)[0],email))
        return cur.fetchone()
    except:
        return None


def vrniPotnika(ID):
    cur.execute("""
        SELECT ime,priimek,emso,IDdrzave,email FROM Potnik
        WHERE ID = ?""", (ID,))
    return cur.fetchone()
    
    
    
def steviloSedezev(id_leta):
    '''vrne st. sedežev na letalu'''
    cur.execute("""
        SELECT Kapaciteta FROM TipLetala
        JOIN Let ON TipLetala.ID = Let.Letalo
        WHERE Let.ID = ?""", (id_leta,))
    return cur.fetchone()

def preveriZasedenostSedezev(id_urnika):
    '''preveri zasedenost leta z izbranim id-jem urnika'''
    cur.execute("""
        SELECT Zasedenost FROM Urnik WHERE ID = ?""", (id_urnika,))
    return cur.fetchone()

def zasediSedez(id_urnika):
    '''zasedemo samo, če imamo prosto mesto'''

    zasedenost = preveriZasedenostSedezev(id_urnika)[0]
    stSedezev = steviloSedezev(vrniIDleta2(id_urnika)[0])[0]
    if zasedenost + 1 > stSedezev:
        return None
    else:
        cur.execute("""
            UPDATE Urnik
            SET Zasedenost = ? + 1
            WHERE ID = ?""",(preveriZasedenostSedezev(id_urnika)[0],id_urnika))
        con.commit()

def vrniIDurnika(id_leta, datum):
    '''vrnemo ID urnika glede na izbran let in datum'''

    cur.execute("""
        SELECT ID FROM Urnik WHERE IDleta = ? AND Datum = ?""", (id_leta, datum))
    return cur.fetchone()

def urnikInPotnik(id_potnika,id_urnika):
    '''v tabelo Razpored shrani potnika in njegov izbran let'''
    cur.execute("""
        INSERT INTO Razpored (IDpotnika, IDurnika)
        VALUES (?,?)""", (id_potnika, id_urnika))
    con.commit()

def vrniDrzavo(id_drzave):
    cur.execute("""
        SELECT Ime FROM Drzava WHERE ID = ?""", (id_drzave,))
    return cur.fetchone()

def vrniDestinacijo(id_destinacije):
    cur.execute("""
        SELECT Ime FROM Destinacije WHERE ID = ?""", (id_destinacije,))
    return cur.fetchone()
    

def vrniDatume(id_leta):
    '''vrne datume letov med izbranima destinacijama'''
    cur.execute("""
        SELECT Datum FROM Urnik
        WHERE IDleta = ?""",(id_leta,))
    return cur.fetchall()

def vrniUro(id_leta):
    '''vrne uro leta med izbranima destinacijama'''
    cur.execute("""
        SELECT UraLeta FROM Let
        WHERE ID = ?""",(id_leta,))
    return cur.fetchone()    

def dodajNovLet(datum,id_leta):
    '''doda nov let za izbrano destinacijo in izbrani datum'''
    cur.execute("""
        INSERT INTO Urnik (IDleta, Datum, Zasedenost)
        VALUES (?,?,?)""", (id_leta, datum,1))
    con.commit()

    
