def info_fi():
    """
    Print class info in Finnish, infraformaatti 2.3
    
    Main site: http://www.citygeomodel.fi/
    Link to file: http://www.citygeomodel.fi/Infra_formaatti_v2.3_211215.pdf
    """

    helper_str = """    tiedot kerätty infraformaatti 2.3
        Pääsivu: http://www.citygeomodel.fi/
        Linkki tiedostoon: http://www.citygeomodel.fi/Infra_formaatti_v2.3_211215.pdf
        
    LYHENTEET:
        i    kokonaisluku
        t    tekstikenttä, pituutta ei ole rajoitettu.
                 ei sisällä välilyöntejä.
        c    tekstikenttä, pituus on rajoitettu.
                 ei sisällä välilyöntejä
                 c4 = neljä merkkiä pitkä tekstikenttä
        f    desimaaliluku, jossa desimaalien määrää ei ole rajoitettu.
        '-'  tietoa ei käsitellä luvussa eikä kirjoituksessa.
                 kun jonkun kentän arvoa ei anneta, tilalla esitetään '-' merkki.
        v    vakio attribuutti (K/E, H/P)
            ei alkuperäinen tunnus infraformaatissa
            
        isolla kirjaimella merkitty havaintoarvon oltava olemassa ilman '-' –merkkiä
        
    TUNNUKSET (LYHYT)
    
        TIEDOSTOKOHTAISET
            FO, 3 (t, t ,t)
            KJ, 2 (T, t)
        PISTEKOHTAISET
            OM, 1 (t)
            ML, 1 (t)
            OR, 1 (t)
            TY, 2 (T, t)
            PK, 4 (i, t, t, t)
            TT, 5 (T, i, T, t, t)
            LA, 2 (i, t)
            XY, 5 (F, F, F, T, t)
            LN, 3 (T, f, f)
            -1, 1 (T)
            GR, 3 (t, t, t)
            GL, 1 (t)
            AT, 2 (T, T) # kallionäytekairauksissa
            AL, 3 (F, t, t)
            ZP, 5 (f, f, f, f, f)
            TP, 5 (t, f, t, t, t)
            LP, 5 (t, t, v, t, t)
        RIVIKOHTAISET
            HM, 1 (t) # välilyönnit sallittu
            TX, 1 (t) # välilyönnit sallittu
            HT, 1 (t)
            EM, 1 (t)
            VH, 0 ()
            KK, 3 (F, F, i)
        
        TUTKIMUSTAPATUNNUKSET
            PA/WST,  4 (F, f, i, t)
            PI,      2 (F, t)
            LY,      4 (F, f, i, t)
            SI/FVT,  5 (F, f, f, f, f)
            HE/DP,   3 (F, i, t)
            HK/DP,   4 (F, i, f, t)
            PT,      2 (F, t)
            TR,      2 (F, t)
            PR,      4 (F, f, f, t)
            CP/CPT,  5 (F, f, f, f, t)
            CU/CPTU, 6 (F, f, f, f, f, t)
            HP,      5
                H,   5 (F, i, f, V, t)
                P,   5 (F, f, f, V, t)
            PO,      3 (F, i, t)
            MW,      9 (F, F, F, f, f, f, f, V, t)
            
            VP       6 (F, T, f, f, f, t)
            VO       6 (F, T, f, f, f, t)
            VK       3 (F, T, v)
            VPK      2 (F, T)
            HV       4 (f, f, t, t)
            PS/PMT   3 (f, f, f)
            PM       3 (f, t, t)
            KO       6 (f, t, f, i, f, f)
            KE       2 (F, f)
            KR       2 (F, F)
            NO       4 (F, T, F, t)
            NE       4 (F, T, F, t)
            LB       3 (T, T, t)
            RK       2 (F, F)
            
    TIEDOSTOTUNNUKSET
    
        TIEDOSTOKOHTAISET
        FO: Formaattitiedot
            t   Formaatin versio nro
            t   Kirjoittava sovellus
            t   Sov. versio nro
        KJ: Mittausjärjestelmä
            T   Koordinaatisto
            t   Korkeusjärj.
            
        PISTEKOHTAISET
        OM: Tiedon omistaja
            t   Nimi
        ML: Maa- tai kalliolajiluokitus
            t   Nimi
        OR: Tutkimusorganisaatio
            t   Nimi
        TY: Työnumero
            T   Työnumero
            t   Nimi
        PK: Pöytäkirja
            i   Pöytäkirjan nro
            t   Kairaaja
            t   Tarkastaja
            t   Käsittelijä
        TT: Tutkimustapa
            T   Tutkimustapalyhenne
            i   Luokka
            T   Tunnus1
            t   Noudatettu standardi
            t   Näytteenotin
        LA: Laitetiedot
            i   Laitenumero
            t   Laitteen selitysteksti
        XY: Koordinaattitiedot
            F   x
            F   y
            F   kair. aloitustaso
            T   Päiväys
            t   Tunnus2
        LN: Linjatiedot
            T   Linjan nimi tai nro
            f   Paalu
            f   Etäisyys
        -1: Päättymistapa
            T   Päättymistapa
        GR: Pohjatutk. ohj. yleistiedot
            t   Ohjelman nimi
            t   Päiväys
            t   Ohjelmoija
        GL: Pohjatutk.ohj.tekstirivit
            t   Pohjatutk. ohj. tekstirivit
        AT: Syvyyden attribuuttitieto (kallionäytekairauksissa)
            T   Kallionäyteattribuutin nimi
            T   Mahdollinen arvo
        AL: Alkukairaustiedot
            F   Alkukair. syvyys (m)
            t   Alkukair. tapa
            t   Alkukair. maalaji
        ZP: Vesiputken tasotiedot
            f   Putken yläpään taso (m) PP
            f   Maanpinnan taso (m) MP
            f   Suojaputken yläpää taso (m) SP
            f   Kaivon kannen taso (m) KN
            f   Suod. alap. taso (m)
        TP: Vesiputken rakenne
            t   Yläosan rakenne (putki, suojap, kaivo)
            f   Suodattimen pit. (m)
            t   Suodatinmalli
            t   Putkenhalkaisija (sisä/ulko mm)
            t   Putkiaines (taul 11)
        LP: Vesiputken lisätiedot
            t   Mittauskohta (PP, MP, SP, KN)
            t   Lisätieto
            v   Lukittu Kyllä / Ei (vakiot = K/E)
            t   Lukon omistaja
            t   Asentaja
            
        RIVIKOHTAISET
        HM: Huomautustekstit
            t   Huomautusteksti (välilyönnit sallitaan)
        TX: Vapaat tekstit
            t   Vapaa teksti (välilyönnit sallitaan)
        HT: Piiloteksti
            t   Ei tulostettava teksti
        EM: Epävirallinen maalaji
            t   Epävirallinen maalaji
        VH: Vedenpinnan havainto
            -
        KK: Kallionäytekairaustiedot (Vino kairaus)
            F   Suuntakulma (aste)
            F   Pystykulma (aste)
            i   Halkaisija (mm)
            
        TUTKIMUSTAPATUNNUKSET
        PA/WST: Painokairaus
            F    Syvyys (m)
            f    Kuorma (kN)
            i    Puolikierrokset (-)
            t    Maalaji
        PI: Pistokairaus
            F    Syvyys (m)
            t    Maalaji
        LY: Lyöntikairaus
            F    Syvyys (m)
            f    Kuorma (kN)
            i    Lyönnit (-)
            t    Maalaji
        SI/FVT: Siipikairaus
            F    Syvyys (m)
            f    Leikkauslujuus (kN/m^2)
            f    Häiritty leikkauslujuus (kN/m^2)
            f    Sensitiivisyys (-)
            f    Jäännöslujuus (MPa)
        HE/DP: Heijarikairaus
            F    Syvyys (m)
            i    Lyönnit (-)
            t    Maalaji
        HK/DP: Heijarikairaus vääntömomentilla
            F    Syvyys (m)
            i    Lyönnit (-)
            f    Vääntömomentti (Nm)
            t    Maalaji
        PT: Putkikairaus
            F    Syvyys (m)
            t    Maalaji
        TR: Tärykairaus
            F    Syvyys (m)
            t    Maalaji
        PR: Puristinkairaus
            F    Syvyys (m)
            f    Kokonaisvastus (MN/m^2)
            f    Vaippavastus (kN/m^2)
            t    Maalaji
        CP/CPT: Puristinkairaus (CPT)
            F    Syvyys (m)
            f    Kokonaisvastus (MN/m^2)
            f    Vaippavastus (kN/m^2)
            f    Kärkivastus (MN/m^2)
            t    Maalaji
        CU/CPTU: Huokospainekairaus (CPTU)
            F    Syvyys (m)
            f    Kokonaisvastus (MN/m^2)
            f    Vaippavastus (kN/m^2)
            f    Kärkivastus (MN/m^2)
            f    Huokospaine (kN/m^2)
            t    Maalaji
        HP: Puristin-heijari -kairaus
            HP Heijarivaihe
            F    Syvyys (m)
            i    Lyönnit (-)
            f    Vääntömomentti (Nm)
            v    Vakio=H
            t    Maalaji
            HP Puristinvaihe
            F    Syvyys (m)
            f    Puristinpaine (MN/m^2)
            f    Vääntömomentti (Nm)
            v    Vakio=P
            t    Maalaji
        PO: Porakonekairaus
            F    Syvyys (m)
            i    Aika (s)
            t    Maalaji
        MW: MWD-kairaus
            F    Syvyys (m)
            F    Etenemisnopeus (cm/min)
            F    Puristusvoima (kN)
            f    Huuhtelupaine (bar)
            f    Vesimenekki (l/min)
            f    Vääntömomentti(Nm)
            f    Pyöritysnopeus (rmp)
            v    Isku (Vakio=0/1)
            t    Maalaji
        VP: Pohjaveden mittausputki
            F    Pinnan korkeusasema
            T    Päiväys
            f    Putken yläpään korkeusasema
            f    Putken alapaan korkeusasema
            f    Siiviläosan pituus (m)
            t    Mittaaja
        VO: Orsiveden mittausputki
            F    Pinnan korkeusasema
            T    Päiväys
            f    Putken yläpään korkeusasema
            f    Putken alapaan korkeusasema
            f    Siiviläosan pituus (m)
            t    Mittaaja
        VK: Vedenpinnan mittaus kaivosta
            F    Pinnan korkeusasema
            T    Päiväys
            v    Tyyppi O=orsivesi/P=pohjavesi(vakio=O/P)
        VPK: Kalliopohjavesiputki
            F    Pinnan korkeusasema
            T    Päiväys
        HV: Huokosvedenpaineen mittaus
            f    Syvyys (m)
            f    Paine (kN/m^2)
            t    Päiväys
            t    Mittaaja
        PS/PMT: Pressometrikoe
            f    Syvyys (m)
            f    Pressometrimoduli (MN/m^2)
            f    Murtopaine (MN/m^2)
        PM: Painumamittaus
            f    Korkeusluku
            t    Päiväys
            t    Mittaaja
        KO: Koekuoppa
            f    Syvyys (m)
            t    Maalaji
            f    Kivisyys
            i    Lohkareisuus
            f    Maksimileveys
            f    Minimileveys
        KE: Kallionäytekairaus laajennettu
            F    Alkusyvyys (m)
            f    Loppusyvyys (m)
        KR: Kallionäytekairaus videoitu
            F    Alkusyvyys (m)
            F    Loppusyvyys (m)
        NO: Näytteenotto häiritty
            F    Syvyystieto1 (m)
            T    Käyttäjän antama näytteen tunnus
            F    Näytteen syvyystieto2 (m)
            t    Maalaji
        NE: Näytteenotto häiriintymätön
            F    Syvyystieto1 (m)
            T    Käyttäjän antama näytteen tunnus
            F    Näytteen syvyystieto2 (m)
            t    Maalaji
        LB: Laboratoriotutkimukset / Kallionäytetutkimus
            T    Laboratoriolyhenne / Kallionäyteattribuutin nimi
            T    Tutkimustulos
            t    Yksikkö (esim. kg)
        RK: Rakeisuuskäyrä
            F    Seulamillimetri
            F    Läpäisyprosentti
    """

    return helper_str
