import modeli as modeli
from bottle import *
from datetime import datetime
from collections import defaultdict
import hashlib

glavniMenuAktivniGumb=""
glavniMenuTemplate = '''<li><a {gumbRezervacija} href="/izbiraDestinacije" >Rezervacija leta</a></li>
        <li><a {gumbReferencna} href="/referencna">Informacije o rezerviranem letu</a></li>
        <li><a {gumbDestinacije} href="/destinacije">Destinacije</a></li>
        <li><a {gumbUdobje} href="/udobje">Za vaše udobje</a></li>
        <li><a {gumbPodjetje} href="/podjetje">O podjetju</a></li>'''

def nastaviAktivniGumbMenuja(gumb):
    global glavniMenuAktivniGumb
    glavniMenuAktivniGumb = gumb


def glavniMeni(**kwargs):
    glavniMenu = glavniMenuTemplate
    if kwargs is not None and "aktivniGumb" in kwargs:
        if kwargs["aktivniGumb"] == "gumbDestinacije":
            glavniMenu = glavniMenu.format_map(defaultdict(str, gumbDestinacije='class="active"'))
        elif kwargs["aktivniGumb"] == "gumbRezervacija":
            glavniMenu = glavniMenu.format_map(defaultdict(str, gumbRezervacija='class="active"'))
        elif kwargs["aktivniGumb"] == "gumbUdobje":
            glavniMenu = glavniMenu.format_map(defaultdict(str, gumbUdobje='class="active"'))
        elif kwargs["aktivniGumb"] == "gumbReferencna":
            glavniMenu = glavniMenu.format_map(defaultdict(str, gumbReferencna='class="active"'))
        elif kwargs["aktivniGumb"] == "gumbPodjetje":
            glavniMenu = glavniMenu.format_map(defaultdict(str, gumbPodjetje='class="active"'))
    return glavniMenu

def oblikujTemplate(*args, **kwargs):
    kwargs["glavni_menu"] = glavniMeni(aktivniGumb=glavniMenuAktivniGumb)
    return template(*args, **kwargs)

def pretvoriDatum(x):
    if x is None:
        return None
    if isinstance(x, str):
        return time.strftime("%d.%m.%Y", time.strptime(x, '%Y-%m-%d %H:%M:%S'))
    else:
        return datetime.strftime(x, "%d.%m.%Y")

def dobiSeznamOdhodnihLetalisc():
    odhodnaLetalisca = modeli.OdhodnaLetalisca()
    return odhodnaLetalisca

def dobiSeznamPrihodnihLetalisc(izhodisceId):
    prihodnaLetalisca = modeli.PrihodnaLetalisca(izhodisceId)
    return prihodnaLetalisca


@get('/static/<filename:path>')
def static(filename):
    return static_file(filename, root='static')


@get('/')
def pozdravnaStran():
    nastaviAktivniGumbMenuja("")
    return oblikujTemplate('pozdravnaStran.html')

@get('/destinacije')
def destinacije():
    nastaviAktivniGumbMenuja("gumbDestinacije")
    return oblikujTemplate('destinacije.html')

@get('/izbiraDestinacije')
def izbiraDestinacije():
    odhodnaLetalisca = dobiSeznamOdhodnihLetalisc()
    odhodnaLetalisca.insert(0, (-1, "Izberi"))

    nastaviAktivniGumbMenuja("gumbRezervacija")
    return oblikujTemplate('izbiraDestinacije.html',
                           odhodnaLetalisca=odhodnaLetalisca,
                           prihodnaLetalisca=[(-1, "Prihodno letališče")])

@post('/izbiraDestinacije')
def pokaziPrihodnaLetalisca():
    odhodnoLetalisceId = int(request.forms.get('odhodnoLetalisce'))

    odhodnaLetalisca = dobiSeznamOdhodnihLetalisc()
    prihodnaLetalisca = dobiSeznamPrihodnihLetalisc(odhodnoLetalisceId)

    return oblikujTemplate('izbiraDestinacije.html',
                           gumbRezervacijaAktiven=True,
                           prihodnaLetaliscaOmogoceno=True,
                           izbranoLetalisce=odhodnoLetalisceId,
                           odhodnaLetalisca=odhodnaLetalisca,
                           prihodnaLetalisca=prihodnaLetalisca)

@get('/datumLeta')
def datumLeta():
    napaka = None
    odhodnoLetalisce = int(request.query['odhodnoLetalisce'])
    prihodnoLetalisce = int(request.query['prihodnoLetalisce'])
    odhod  = modeli.vrniDestinacijo(odhodnoLetalisce)[0]
    prihod = modeli.vrniDestinacijo(prihodnoLetalisce)[0]
    IDleta = modeli.vrniIDleta(odhodnoLetalisce, prihodnoLetalisce)

    return oblikujTemplate('datumLeta.html',
                           odhod=odhod, prihod=prihod,
                           odhodnoLetalisce=odhodnoLetalisce, prihodnoLetalisce=prihodnoLetalisce,
                           IDleta=IDleta, napaka=napaka)

@get('/novPotnik')
def dodajNovegaPotnika():
    datumLeta = request.query['datum']
    odhodnoLetalisce=request.query['odhodnoLetalisce']
    prihodnoLetalisce = request.query['prihodnoLetalisce']
    IDleta = request.query['IDleta'][1:(-2)]

    datumi = modeli.vrniDatume(IDleta)
    datumi1 = [elt[0] for elt in datumi]

    drzave = modeli.vseDrzave()
    drzave.insert(0, (-1, "Izberi Državo"))
    if datumLeta not in datumi1:
        modeli.dodajNovLet(datumLeta,IDleta)
        IDurnika = modeli.vrniIDurnika(IDleta, datumLeta)[0]
        return oblikujTemplate('novPotnik.html',
                               ime=None, priimek=None, emso=None,
                               drzave=drzave,
                               email=None,
                               datumLeta=datumLeta,
                               odhodnoLetalisce=odhodnoLetalisce, prihodnoLetalisce=prihodnoLetalisce,
                               IDleta=IDleta, IDurnika=IDurnika,
                               napaka=None)
    else:
        IDurnika = modeli.vrniIDurnika(IDleta, datumLeta)[0]
        zasedenost = modeli.preveriZasedenostSedezev(IDurnika)[0]
        stSedezev = modeli.steviloSedezev(IDleta)[0]

        if zasedenost < stSedezev:
            modeli.zasediSedez(IDurnika)
            return oblikujTemplate('novPotnik.html',
                                   ime=None, priimek=None, emso=None,
                                   drzave=drzave,email=None, napaka=None,
                                   datumLeta=datumLeta,
                                   odhodnoLetalisce=odhodnoLetalisce, prihodnoLetalisce=prihodnoLetalisce,
                                   IDleta=IDleta, IDurnika=IDurnika)
        else:
            return oblikujTemplate('novPotnik.html',
                                   napaka='Izbrani datum je zaseden - vrnite se na prejšnjo stran in izberite nov datum',
                                   ime=None, priimek=None, emso=None,
                                   drzave=drzave, email=None,
                                   datumLeta=datumLeta,
                                   odhodnoLetalisce=odhodnoLetalisce, prihodnoLetalisce=prihodnoLetalisce,
                                   IDleta=None, IDurnika=None)
            

@post('/dodaj')
def dodaj():
    ime       = request.forms.ime
    priimek   = request.forms.priimek
    emso      = request.forms.emso
    idDrzave  = int(request.forms.drzava_id)
    email     = request.forms.email
    idPotnika = modeli.vrniIDpotnika(ime, priimek, emso, idDrzave, email)

    datumLeta = request.forms.datumLeta
    odhodnoLetalisce = request.forms.odhodnoLetalisce
    prihodnoLetalisce = request.forms.prihodnoLetalisce
    IDleta   = request.forms.IDleta
    IDurnika = request.forms.IDurnika


    if idPotnika is None:
        try:
            modeli.dodajPotnika(ime, priimek, emso, idDrzave, email)
            idPotnika = modeli.vrniIDpotnika(ime, priimek, emso, idDrzave, email)
        except:
            e = 'Prosimo vnesite vse podatke'
            drzave = modeli.vseDrzave()
            if idDrzave < 0:
                drzave.insert(0, (-1, "Izberi Državo"))
            return oblikujTemplate('novPotnik.html',
                                   napaka=e,
                                   ime=ime, priimek=priimek, emso=emso,
                                   drzave=drzave, izbranaDrzava=idDrzave,
                                   email=email,
                                   datumLeta=datumLeta,
                                   odhodnoLetalisce=odhodnoLetalisce, prihodnoLetalisce=prihodnoLetalisce,
                                   IDleta=IDleta, IDurnika=IDurnika)


    IDpotnika = str(idPotnika[0])
    pot = IDpotnika + '&' + datumLeta + '&' + odhodnoLetalisce + '&' + prihodnoLetalisce + '&' + IDleta + '&' + IDurnika
    hashPoti = hashlib.md5(pot.encode())
    referencnaSt = hashPoti.hexdigest()[:10]
    referencne = modeli.vseReferencne()
    sezReferencnih = [elt[0] for elt in referencne]


    if referencnaSt in sezReferencnih:
        napaka = 'Let je na izbrani destinaciji za vnešenega potnika že rezerviran'
        drzave = modeli.vseDrzave()
        if idDrzave < 0:
            drzave.insert(0, (-1, "Izberi Državo"))
        return oblikujTemplate('novPotnik.html',
                                   napaka=napaka,
                                   ime=ime, priimek=priimek, emso=emso,
                                   drzave=drzave,izbranaDrzava=idDrzave,
                                   email=email,
                                   datumLeta=datumLeta,
                                   odhodnoLetalisce=odhodnoLetalisce, prihodnoLetalisce=prihodnoLetalisce,
                                   IDleta=IDleta, IDurnika=IDurnika)
    else:
        redirect('/opravljenaRezervacija/' + str(pot))

    

@get('/opravljenaRezervacija/<pot>')
def rezervacija(pot):
    napaka = request.query.napaka
    if not napaka:
        napaka = None

    hashPoti = hashlib.md5(pot.encode())
    referencnaSt = hashPoti.hexdigest()[:10]
    
    IDpotnika, datumLeta, odhodnoLetalisce, prihodnoLetalisce, IDleta, IDurnika = pot.split('&')
    leto, mesec, dan = datumLeta.split('-')
    novDatum = dan+'-'+mesec+'-'+leto
    ime, priimek, emso, IDdrzave, email = modeli.vrniPotnika(IDpotnika)
    uraLeta = modeli.vrniUro(IDleta)[0]
    

    odhodnoLetalisceIme=modeli.vrniDestinacijo(odhodnoLetalisce)[0]
    prihodnoLetalisceIme=modeli.vrniDestinacijo(prihodnoLetalisce)[0]
    
    modeli.urnikInPotnik(IDpotnika, IDurnika, referencnaSt)
    
    return oblikujTemplate('opravljenaRezervacija.html',
                           ime=ime, priimek=priimek,
                           emso=emso, drzava=modeli.vrniDrzavo(IDdrzave)[0],
                           email=email,
                           datumLeta=novDatum,
                           odhodnoLetalisce=odhodnoLetalisceIme, prihodnoLetalisce=prihodnoLetalisceIme,
                           referencnaSt=referencnaSt, uraLeta = uraLeta, napaka=napaka)


@get('/udobje')
def destinacije():
    nastaviAktivniGumbMenuja("gumbUdobje")
    return oblikujTemplate('udobje.html')

@get('/referencna')
def destinacije():
    nastaviAktivniGumbMenuja("gumbReferencna")
    return oblikujTemplate('referencna.html',refSt = None, napaka = None)

@get('/informacijeOLetu')
def informacije():
    refSt = request.query['refSt']
    referencne = modeli.vseReferencne()
    sezReferencnih = [elt[0] for elt in referencne]
    if refSt not in sezReferencnih:
        napaka= 'Vnešena referenčna številka je napačna'
        return oblikujTemplate('referencna.html',refSt = None, napaka=napaka)
    
        
    IDpotnika, IDurnika = modeli.IDpotnikainIDurnika(refSt)[0]
    ime,priimek,emso,IDdrzave,email = modeli.vrniPotnika(IDpotnika)
    IDleta, datumLeta = modeli.IDletaDatum(IDurnika)[0]
    leto, mesec, dan = datumLeta.split('-')
    novDatum = dan+'-'+mesec+'-'+leto
    IDodhod,IDprihod,letalo,uraLeta = modeli.informacijeOLetu(IDleta)[0]
    odhodnoLetalisce = modeli.vrniDestinacijo(IDodhod)[0]
    prihodnoLetalisce = modeli.vrniDestinacijo(IDprihod)[0]
    
    return oblikujTemplate('informacijeOLetu.html', refSt=refSt, ime=ime, priimek=priimek, emso=emso,
                           datumLeta = novDatum,uraLeta=uraLeta, odhodnoLetalisce=odhodnoLetalisce, prihodnoLetalisce=prihodnoLetalisce)
    

@get('/podjetje')
def destinacije():
    nastaviAktivniGumbMenuja("gumbPodjetje")
    return oblikujTemplate('podjetje.html')


# poženemo strežnik na portu 8080, glej http://localhost:8080/
run(host='localhost', port=8080, reloader=False)
