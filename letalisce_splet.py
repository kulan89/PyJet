import modeli as modeli
from bottle import *
from datetime import datetime
import hashlib


def pretvoriDatum(x):
    if x is None:
        return None
    if isinstance(x, str):
        return time.strftime("%d.%m.%Y", time.strptime(x, '%Y-%m-%d %H:%M:%S'))
    else:
        return datetime.strftime(x, "%d.%m.%Y")

##def dobiSeznamOdhodnihLetalisc():
##    odhodnaLetalisca = modeli.OdhodnaLetalisca()
##    mesta = []
##    for elt in odhodnaLetalisca:
##        mesta.append(elt[0])
##    return mesta

def dobiSeznamOdhodnihLetalisc():
    odhodnaLetalisca = modeli.OdhodnaLetalisca()
    return odhodnaLetalisca

##def dobiSeznamPrihodnihLetalisc(izhodisce):
##    prihodnaLetalisca = modeli.PrihodnaLetalisca(izhodisce)
##    mesta = []
##    for elt in prihodnaLetalisca:
##        mesta.append(elt[0])
##    return mesta


def dobiSeznamPrihodnihLetalisc(izhodisceId):
    prihodnaLetalisca = modeli.PrihodnaLetalisca(izhodisceId)
    return prihodnaLetalisca


@get('/')
def glavniMenu():
    odhodnaLetalisca = dobiSeznamOdhodnihLetalisc()
    odhodnaLetalisca.insert(0, (-1, "Izberi"))
    return template('glavni.html', odhodnaLetalisca=odhodnaLetalisca, prihodnaLetalisca=[(-1, "Prihodno letališče")])

@post('/')
def pokaziPrihodnaLetalisca():
    odhodnoLetalisceId = int(request.forms.get('odhodnoLetalisce'))

    odhodnaLetalisca = dobiSeznamOdhodnihLetalisc()
    prihodnaLetalisca = dobiSeznamPrihodnihLetalisc(odhodnoLetalisceId)
    return template('glavni.html', prihodnaLetaliscaOmogoceno=True, izbranoLetalisce=odhodnoLetalisceId,
                    odhodnaLetalisca=odhodnaLetalisca, prihodnaLetalisca=prihodnaLetalisca)

@get('/static/<filename:path>')
def static(filename):
    return static_file(filename, root='static')

@get('/datumLeta')
def datumLeta():
    napaka = None
    odhodnoLetalisce = int(request.query['odhodnoLetalisce'])
    prihodnoLetalisce = int(request.query['prihodnoLetalisce'])
    odhod = modeli.vrniDestinacijo(odhodnoLetalisce)[0]
    prihod = modeli.vrniDestinacijo(prihodnoLetalisce)[0]
    IDleta = modeli.vrniIDleta(odhodnoLetalisce, prihodnoLetalisce)
    #print(odhodnoLetalisce, prihodnoLetalisce, IDleta)
    return template('datumLeta.html',odhod = odhod, prihod = prihod, odhodnoLetalisce=odhodnoLetalisce,
                    prihodnoLetalisce=prihodnoLetalisce, IDleta = IDleta, napaka=napaka)


@get('/novPotnik')
def dodajNovegaPotnika():
    datumLeta = request.query['datum']
    odhodnoLetalisce=request.query['odhodnoLetalisce']
    prihodnoLetalisce = request.query['prihodnoLetalisce']
    IDleta = request.query['IDleta'][1:(-2)]

 
    datumi = modeli.vrniDatume(IDleta)
    datumi1 = [elt[0] for elt in datumi]

    #print(datumLeta, datumi1)

    if datumLeta not in datumi1:
        modeli.dodajNovLet(datumLeta,IDleta)
        IDurnika = modeli.vrniIDurnika(IDleta, datumLeta)[0]
        print(IDurnika)
        return template('novPotnik.html', ime = None, priimek = None, emso = None,
                        drzava = None,email = None, napaka = None,
                    datumLeta = datumLeta, odhodnoLetalisce = odhodnoLetalisce, prihodnoLetalisce = prihodnoLetalisce, IDleta = IDleta, IDurnika = IDurnika)
    else:
        IDurnika = modeli.vrniIDurnika(IDleta, datumLeta)[0]
        print(IDurnika)
        zasedenost = modeli.preveriZasedenostSedezev(IDurnika)[0]
        stSedezev = modeli.steviloSedezev(IDleta)[0]
        if zasedenost < stSedezev:
            modeli.zasediSedez(IDurnika)
            return template('novPotnik.html', ime = None, priimek = None, emso = None,
                        drzava = None,email = None, napaka = None,
                    datumLeta = datumLeta, odhodnoLetalisce = odhodnoLetalisce, prihodnoLetalisce = prihodnoLetalisce, IDleta = IDleta, IDurnika = IDurnika)
        else:
            return template('novPotnik.html', ime = None, priimek = None, emso = None,
                        drzava = None,email = None, napaka = 'Izbrani datum je zaseden - vrnite se na prejšnjo stran in izberite nov datum',
                    datumLeta = datumLeta, odhodnoLetalisce = odhodnoLetalisce, prihodnoLetalisce = prihodnoLetalisce, IDleta = IDleta)
            



@post('/dodaj')
def dodaj():
    ime = request.forms.ime
    priimek = request.forms.priimek
    emso = request.forms.emso
    drzava = request.forms.drzava
    email = request.forms.email
    idPotnika = modeli.vrniIDpotnika(ime,priimek,emso,drzava,email)
    if idPotnika is None:
        try :
            modeli.dodajPotnika(ime, priimek, emso, drzava, email)
            idPotnika = modeli.vrniIDpotnika(ime,priimek,emso,drzava,email)
        except Exception as e:
            return template('novPotnik.html', ime = ime, priimek = priimek, emso = emso,
                        drzava = drzava, email = email, napaka = e)

    IDpotnika = str(idPotnika[0])
    IDurnika = request.forms.IDurnika
    datumLeta = request.forms.datumLeta
    odhodnoLetalisce = request.forms.odhodnoLetalisce
    prihodnoLetalisce = request.forms.prihodnoLetalisce
    IDleta = request.forms.IDleta
    IDurnika = request.forms.IDurnika
    print(datumLeta, odhodnoLetalisce, prihodnoLetalisce, IDleta)
    pot=IDpotnika+'&'+datumLeta+'&'+odhodnoLetalisce+'&'+prihodnoLetalisce+'&'+IDleta+'&'+IDurnika
    redirect('/opravljenaRezervacija/' + str(pot))
    

@get('/opravljenaRezervacija/<pot>')
def rezervacija(pot):
    napaka = request.query.napaka
    if not napaka:
        napaka = None

    hashPoti = hashlib.md5(pot.encode())
    referencnaSt = hashPoti.hexdigest()[:10]
    #print(referencnaSt)
    
    IDpotnika, datumLeta, odhodnoLetalisce, prihodnoLetalisce, IDleta, IDurnika = pot.split('&')
    leto, mesec, dan = datumLeta.split('-')
    novDatum = dan+'-'+mesec+'-'+leto
    ime, priimek, emso, IDdrzave, email = modeli.vrniPotnika(IDpotnika)

    odhodnoLetalisceIme=modeli.vrniDestinacijo(odhodnoLetalisce)[0]
    prihodnoLetalisceIme=modeli.vrniDestinacijo(prihodnoLetalisce)[0]
    
    modeli.urnikInPotnik(IDpotnika,IDurnika)
    
    return template('opravljenaRezervacija.html', ime = ime, priimek = priimek, emso = emso, drzava = modeli.vrniDrzavo(IDdrzave)[0], email = email,
                    datumLeta = novDatum, odhodnoLetalisce=odhodnoLetalisceIme, prihodnoLetalisce=prihodnoLetalisceIme, referencnaSt = referencnaSt, napaka = napaka)
       
    
        
        
       
##@get('/oseba/<emso>')
##def oOsebi(emso):
##    napaka = request.query.napaka
##    if not napaka:
##        napaka = None
##    emso, ime, priimek, ulica, hisna_st, postna_st, posta = modeli.poisciEMSO(emso)
##    racuni = modeli.racunEMSO(emso)
##    return template('oseba.html', emso = emso, ime = ime, priimek = priimek,
##                    ulica = ulica, hisna_st = hisna_st, postna_st = postna_st,
##                    posta = posta, racuni = racuni, pretvori = pretvoriDatum,
##                    napaka = napaka)
##
##@get('/isci')
##def isci():
##    priimek = request.query.iskalniNiz
##    rezultat = modeli.poisciPriimek(priimek)
##    return template('isci.html', rezultat = rezultat)
##
##@post('/dodaj')
##def dodaj():
##    emso = request.forms.emso
##    ime = request.forms.ime
##    priimek = request.forms.priimek
##    ulica = request.forms.ulica
##    hisna_st = request.forms.hisna_st
##    postna_st = request.forms.postna_st
##    kraj = request.forms.kraj
##    try:
##        if not modeli.dodajOsebo(ime, priimek, emso, ulica, hisna_st, postna_st):
##            modeli.dodajKraj(postna_st, kraj)
##            modeli.dodajOsebo(ime, priimek, emso, ulica, hisna_st, postna_st)
##    except Exception as e:
##        return template('glavni.html', ime = ime, priimek = priimek, emso = emso,
##                        ulica = ulica, hisna_st = hisna_st, postna_st = postna_st,
##                        kraj = kraj, napaka = e)
##    redirect('/oseba/' + emso)
##
##@post('/polog/<racun>')
##def polog(racun):
##    emso, = modeli.emsoRacun(racun)
##    try:
##        znesek = int(request.forms.znesek)
##    except Exception as e:
##        redirect('/oseba/' + emso + '?napaka=Neveljaven znesek!')
##    if znesek <= 0:
##        redirect('/oseba/' + emso + '?napaka=Znesek mora biti pozitiven!')
##    else:
##        modeli.dodajTransakcijo(racun, znesek)
##        redirect('/oseba/' + emso)
##
##@post('/dvig/<racun>')
##def dvig(racun):
##    emso, = modeli.emsoRacun(racun)
##    try:
##        znesek = int(request.forms.znesek)
##    except Exception as e:
##        redirect('/oseba/' + emso + '?napaka=Neveljaven znesek!')
##    if znesek <= 0:
##        redirect('/oseba/' + emso + '?napaka=Znesek mora biti pozitiven!')
##    else:
##        modeli.dodajTransakcijo(racun, -znesek)
##        redirect('/oseba/' + emso)

# poženemo strežnik na portu 8080, glej http://localhost:8080/
run(host='localhost', port=8080, reloader=False)
