"""General information concerning Finnish Infraformat."""
import logging
import numpy as np

__all__ = ["identifiers", "print_info"]

logger = logging.getLogger("pyinfraformat")


def custom_int(number):
    """Test if number is integer."""
    try:
        return int(number)
    except ValueError:
        if number == "-":
            return np.nan
        if int(float(number)) == float(number):
            return int(float(number))
        else:
            msg = "Non-integer value detected, a floating point number is returned"
            logger.warning(msg)
            return float(number)


def custom_float(number):
    """Test if number is floating point number."""
    if number.strip() == "-":
        return np.nan
    else:
        try:
            return float(number)
        except ValueError:
            return np.nan


def identifiers():
    """Return header identifiers.

    Returns
    -------
    tuple
        file_header_identifiers,
        header_identifiers,
        inline_identifiers,
        survey_identifiers,
    """
    file_header_identifiers = {
        "FO": (["Format version", "Software", "Software version"], [str, str, str]),
        "KJ": (["Coordinate system", "Height reference"], [str, str]),
    }

    # point specific
    header_identifiers = {
        "OM": (["Owner"], [str]),
        "ML": (["Soil or rock classification"], [str]),
        "OR": (["Research organization"], [str]),
        "TY": (["Work number", "Work name"], [str, str]),
        "PK": (["Record number", "Driller", "Inspector", "Handler"], [custom_int, str, str, str]),
        "TT": (
            ["Survey abbreviation", "Class", "ID1", "Used standard", "Sampler"],
            [str, custom_int, str, str, str],
        ),
        "LA": (["Device number", "Device description text"], [custom_int, str]),
        "XY": (
            ["X", "Y", "Z-start", "Date", "ID2"],
            [custom_float, custom_float, custom_float, str, str],
        ),
        "LN": (["Line name or number", "Pole", "Distance"], [str, custom_float, custom_float]),
        "-1": (["Ending"], [str]),
        "GR": (["Software name", "Date", "Programmer"], [str, str, str]),
        "GL": (["Survey info"], [str]),
        "AT": (["Rock sample attribute", "Possible value"], [str, str]),
        "AL": (
            ["Initial boring depth", "Initial boring method", "Initial boring soil type"],
            [custom_float, str, str],
        ),
        "ZP": (
            ["ZP1", "ZP2", "ZP3", "ZP4", "ZP5"],
            [custom_float, custom_float, custom_float, custom_float, custom_float],
        ),
        "TP": (["TP1", "TP2", "TP3", "TP4", "TP5"], [str, custom_float, str, str, str]),
        "LP": (["LP1", "LP2", "LP3", "LP4", "LP5"], [str, str, str, str, str]),
    }
    # line specific
    # inline comment / info
    inline_identifiers = {
        "HM": (["obs"], [str]),
        "TX": (["free text"], [str]),
        "HT": (["hidden text"], [str]),
        "EM": (["Unofficial soil type"], [str]),
        "VH": (["Water level observation"], []),
        "KK": (
            ["Azimuth (degrees)", "Inclination (degrees)", "Diameter (mm)"],
            [custom_float, custom_float, custom_int],
        ),
    }

    # datatypes
    # most contain tuple (column_names, column_dtype)
    # 1 dictionary for 'HP'
    survey_identifiers = {
        "PA/WST": (
            ["Depth (m)", "Load (kN)", "Rotation of half turns (-)", "Soil type"],
            [custom_float, custom_float, custom_int, str],
        ),
        "PA": (
            ["Depth (m)", "Load (kN)", "Rotation of half turns (-)", "Soil type"],
            [custom_float, custom_float, custom_int, str],
        ),
        "WST": (
            ["Depth (m)", "Load (kN)", "Rotation of half turns (-)", "Soil type"],
            [custom_float, custom_float, custom_int, str],
        ),
        "PI": (["Depth (m)", "Soil type"], [custom_float, str]),
        "LY": (
            ["Depth (m)", "Load (kN)", "Blows", "Soil type"],
            [custom_float, custom_float, custom_int, str],
        ),
        "SI/FVT": (
            [
                "Depth (m)",
                "Shear strenght (kN/m^2)",
                "Residual Shear strenght (kN/m^2)",
                "Sensitivity (-)",
                "Residual strenght (MPa)",
            ],
            [custom_float, custom_float, custom_float, custom_float, custom_float],
        ),
        "SI": (
            [
                "Depth (m)",
                "Shear strenght (kN/m^2)",
                "Residual Shear strenght (kN/m^2)",
                "Sensitivity (-)",
                "Residual strenght (MPa)",
            ],
            [custom_float, custom_float, custom_float, custom_float, custom_float],
        ),
        "FVT": (
            [
                "Depth (m)",
                "Shear strenght (kN/m^2)",
                "Residual Shear strenght (kN/m^2)",
                "Sensitivity (-)",
                "Residual strenght (MPa)",
            ],
            [custom_float, custom_float, custom_float, custom_float, custom_float],
        ),
        "HE/DP": (["Depth (m)", "Blows", "Soil type"], [custom_float, custom_int, str]),
        "HE": (["Depth (m)", "Blows", "Soil type"], [custom_float, custom_int, str]),
        # 'DP' : (),
        "HK/DP": (
            ["Depth (m)", "Blows", "Torque (Nm)", "Soil type"],
            [custom_float, custom_int, custom_float, str],
        ),
        "HK": (
            ["Depth (m)", "Blows", "Torque (Nm)", "Soil type"],
            [custom_float, custom_int, custom_float, str],
        ),
        # 'DP' : (),
        "PT": (["Depth (m)", "Soil type"], [custom_float, str]),
        "TR": (["Depth (m)", "Soil type"], [custom_float, str]),
        "PR": (
            ["Depth (m)", "Total resistance (MN/m^2)", "Sleeve friction (kN/m^2)", "Soil type"],
            [custom_float, custom_float, custom_float, str],
        ),
        "CP/CPT": (
            [
                "Depth (m)",
                "Total resistance (MN/m^2)",
                "Sleeve friction (kN/m^2)",
                "Cone resistance (MN/m^2)",
                "Soil type",
            ],
            [custom_float, custom_float, custom_float, custom_float, str],
        ),
        "CP": (
            [
                "Depth (m)",
                "Total resistance (MN/m^2)",
                "Sleeve friction (kN/m^2)",
                "Cone resistance (MN/m^2)",
                "Soil type",
            ],
            [custom_float, custom_float, custom_float, custom_float, str],
        ),
        "CPT": (
            [
                "Depth (m)",
                "Total resistance (MN/m^2)",
                "Sleeve friction (kN/m^2)",
                "Cone resistance (MN/m^2)",
                "Soil type",
            ],
            [custom_float, custom_float, custom_float, custom_float, str],
        ),
        "CU/CPTU": (
            [
                "Depth (m)",
                "Total resistance (MN/m^2)",
                "Sleeve friction (kN/m^2)",
                "Cone resistance (MN/m^2)",
                "Pore pressure (kN/m^2)",
                "Soil type",
            ],
            [custom_float, custom_float, custom_float, custom_float, custom_float, str],
        ),
        "CU": (
            [
                "Depth (m)",
                "Total resistance (MN/m^2)",
                "Sleeve friction (kN/m^2)",
                "Cone resistance (MN/m^2)",
                "Pore pressure (kN/m^2)",
                "Soil type",
            ],
            [custom_float, custom_float, custom_float, custom_float, custom_float, str],
        ),
        "CPTU": (
            [
                "Depth (m)",
                "Total resistance (MN/m^2)",
                "Sleeve friction (kN/m^2)",
                "Cone resistance (MN/m^2)",
                "Pore pressure (kN/m^2)",
                "Soil type",
            ],
            [custom_float, custom_float, custom_float, custom_float, custom_float, str],
        ),
        "HP": {
            "H": (
                ["Depth (m)", "Blows", "Torque (Nm)", "Survey type", "Soil type"],
                [custom_float, custom_int, custom_float, str, str],
            ),
            "P": (
                ["Depth (m)", "Pressure (MN/m^2)", "Torque (Nm)", "Survey type", "Soil type"],
                [custom_float, custom_float, custom_float, str, str],
            ),
        },
        "PO": (["Depth (m)", "Time (s)", "Soil type"], [custom_float, custom_int, str]),
        "MW": (
            [
                "Depth (m)",
                "Speed (cm/min)",
                "Compressive force (kN)",
                "MW4",
                "MW5",
                "Torque (Nm)",
                "Rotational speed (rpm)",
                "Blow",
                "Soil type",
            ],
            [
                custom_float,
                custom_float,
                custom_float,
                custom_float,
                custom_float,
                custom_float,
                custom_float,
                str,
                str,
            ],
        ),
        "VP": (
            [
                "Water level",
                "Date",
                "Top level of pipe",
                "Bottom level of pipe",
                "Lenght of the sieve(m)",
                "Inspector",
            ],
            [custom_float, str, custom_float, custom_float, custom_float, str],
        ),
        "VO": (
            [
                "Water level",
                "Date",
                "Top level of pipe",
                "Bottom level of pipe",
                "Lenght of the sieve(m)",
                "Inspector",
            ],
            [custom_float, str, custom_float, custom_float, custom_float, str],
        ),
        "VK": (["Water level", "Date", "Type"], [custom_float, str, str]),
        "VPK": (["Water level", "Date"], [custom_float, str]),
        "HV": (
            ["Depth (m)", "Pressure (kN/m^2)", "Date", "Measurer"],
            [custom_float, custom_float, str, str],
        ),
        "PS/PMT": (
            ["Depth (m)", "Pressometer modulus (MN/m^2)", "Burst pressure (MN/m^2)"],
            [custom_float, custom_float, custom_float],
        ),
        "PS": (
            ["Depth (m)", "Pressometer modulus (MN/m^2)", "Burst pressure (MN/m^2)"],
            [custom_float, custom_float, custom_float],
        ),
        "PMT": (
            ["Depth (m)", "Pressometer modulus (MN/m^2)", "Burst pressure (MN/m^2)"],
            [custom_float, custom_float, custom_float],
        ),
        "PM": (["Height", "Date", "Measurer"], [custom_float, str, str]),
        "KO": (
            ["Depth (m)", "Soil type", "rock", "rock", "Maximum width", "Minimum width"],
            [custom_float, str, custom_float, custom_int, custom_float, custom_float],
        ),
        "KE": (["Initial depth (m)", "Final depth (m)"], [custom_float, custom_float]),
        "KR": (["Initial depth (m)", "Final depth (m)"], [custom_float, custom_float]),
        "NO": (
            ["Depth  info 1 (m)", "Sample ID", "Depth info 2 (m)", "Soil type"],
            [custom_float, str, custom_float, str],
        ),
        "NE": (
            ["Depth info 1 (m)", "Sample ID", "Depth info 2 (m)", "Soil type"],
            [custom_float, str, custom_float, str],
        ),
        "LB": (["Laboratory", "Result", "Unit"], [str, str, str]),
        "RK": (["Sieve size", "Passing percentage"], [custom_float, custom_float]),
    }
    # common_survey_mistakes = {'KK' : ['KE', 'KR'],
    #                          'DP' : ['HE', 'HK']}

    result_tuple = (
        file_header_identifiers,
        header_identifiers,
        inline_identifiers,
        survey_identifiers,
        # common_survey_mistakes
    )
    return result_tuple


def info_fi():
    """Print class info in Finnish, infraformaatti 2.3.

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


def print_info(language="fi"):
    """Print out information about the finnish infraformat.

    Currently defined only in Finnish.

    Parameters
    ----------
    language : str, {"fi"}
        short format for language.
    """
    if language.lower() != "fi":
        logger.critical("Only 'fi' info is implemented")
        raise NotImplementedError("Only 'fi' info is implemented")
    print(_info_fi())
