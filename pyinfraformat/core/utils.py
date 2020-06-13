"""General information concerning Finnish Infraformat."""
import logging

import numpy as np

__all__ = ["identifiers", "print_info"]

logger = logging.getLogger("pyinfraformat")


def is_number(number_str):
    """Test if number_str is number including infraformat logic."""
    try:
        complex(number_str)
    except ValueError:
        if number_str == "-":
            return True
        return False
    return True


def custom_int(number):
    """Test if number is integer."""
    try:
        return int(number)
    except ValueError:
        try:
            floating_number = float(number.replace(",", "."))
            integer_number = int(floating_number)
            if integer_number == floating_number:
                return integer_number
            else:
                msg = "Non-integer value detected, a floating point number is returned"
                logger.debug(msg)
                return floating_number
        except ValueError:
            msg = "Not a Number (NaN) value detected, a NaN is returned"
            logger.debug(msg)
            return np.nan


def custom_float(number):
    """Test if number is floating point number."""
    try:
        return float(number.replace(",", "."))
    except ValueError:
        msg = "Not a Number (NaN) value detected, a NaN is returned"
        logger.debug(msg)
        return np.nan


def identifiers():
    """Return header identifiers.

    Identifier key: (names, dtype, mandatory)

    Returns
    -------
    tuple
        file_header_identifiers,
        header_identifiers,
        inline_identifiers,
        survey_identifiers,
    """
    file_header_identifiers = {
        "FO": (
            ["Format version", "Software", "Software version"],
            [str, str, str],
            [False, False, False],
        ),
        "KJ": (["Coordinate system", "Height reference"], [str, str], [True, False]),
    }

    # point specific
    header_identifiers = {
        "OM": (["Owner"], [str], [False]),
        "ML": (["Soil or rock classification"], [str], [False]),
        "OR": (["Research organization"], [str], [False]),
        "TY": (["Work number", "Work name"], [str, str], [True, False]),
        "PK": (
            ["Record number", "Driller", "Inspector", "Handler"],
            [custom_int, str, str, str],
            [False, False, False, False, False],
        ),
        "TT": (
            ["Survey abbreviation", "Class", "Survey ID", "Used standard", "Sampler"],
            [str, custom_int, str, str, str],
            [True, False, True, False, False, False],
        ),
        "LA": (
            ["Device number", "Device description text"],
            [custom_int, str],
            [False, False, False],
        ),
        "XY": (
            ["X", "Y", "Z-start", "Date", "Point ID"],
            [custom_float, custom_float, custom_float, str, str],
            [True, True, True, True, False],
        ),
        "LN": (
            ["Line name or number", "Pole", "Distance"],
            [str, custom_float, custom_float],
            [True, False, False],
        ),
        "-1": (["Ending"], [str], [True]),
        "GR": (["Software name", "Date", "Programmer"], [str, str, str], [False, False, False]),
        "GL": (["Survey info"], [str], [False]),
        "AT": (["Rock sample attribute", "Possible value"], [str, str], [True, True]),
        "AL": (
            ["Initial boring depth", "Initial boring method", "Initial boring soil type"],
            [custom_float, str, str],
            [True, False, False],
        ),
        "ZP": (
            ["ZP1", "ZP2", "ZP3", "ZP4", "ZP5"],
            [custom_float, custom_float, custom_float, custom_float, custom_float],
            [False, False, False, False, False],
        ),
        "TP": (
            ["TP1", "TP2", "TP3", "TP4", "TP5"],
            [str, custom_float, str, str, str],
            [False, False, False, False, False],
        ),
        "LP": (
            ["LP1", "LP2", "LP3", "LP4", "LP5"],
            [str, str, str, str, str],
            [False, False, False, False, False],
        ),
    }
    # line specific
    # inline comment / info
    inline_identifiers = {
        "HM": (["obs"], [str], [False]),
        "TX": (["free text"], [str], [False]),
        "HT": (["hidden text"], [str], [False]),
        "EM": (["Unofficial soil type"], [str], [False]),
        "VH": (["Water level observation"], [], [False]),
        "KK": (
            ["Azimuth (degrees)", "Inclination (degrees)", "Diameter (mm)"],
            [custom_float, custom_float, custom_int],
            [True, True, False],
        ),
    }

    # datatypes
    # most contain tuple (column_names, column_dtype)
    # 1 dictionary for 'HP'
    survey_identifiers = {
        "PA/WST": (
            ["Depth (m)", "Load (kN)", "Rotation of half turns (-)", "Soil type"],
            [custom_float, custom_float, custom_int, str],
            [True, False, False, False],
        ),
        "PA": (
            ["Depth (m)", "Load (kN)", "Rotation of half turns (-)", "Soil type"],
            [custom_float, custom_float, custom_int, str],
            [True, False, False, False],
        ),
        "WST": (
            ["Depth (m)", "Load (kN)", "Rotation of half turns (-)", "Soil type"],
            [custom_float, custom_float, custom_int, str],
            [True, False, False, False],
        ),
        "PI": (["Depth (m)", "Soil type"], [custom_float, str], [True, False]),
        "LY": (
            ["Depth (m)", "Load (kN)", "Blows", "Soil type"],
            [custom_float, custom_float, custom_int, str],
            [True, False, False, False],
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
            [True, False, False, False, False],
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
            [True, False, False, False, False],
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
            [True, False, False, False, False],
        ),
        "HE/DP": (
            ["Depth (m)", "Blows", "Soil type"],
            [custom_float, custom_int, str],
            [True, False, False],
        ),
        "HE": (
            ["Depth (m)", "Blows", "Soil type"],
            [custom_float, custom_int, str],
            [True, False, False],
        ),
        # 'DP' : (),
        "HK/DP": (
            ["Depth (m)", "Blows", "Torque (Nm)", "Soil type"],
            [custom_float, custom_int, custom_float, str],
            [True, False, False, False],
        ),
        "HK": (
            ["Depth (m)", "Blows", "Torque (Nm)", "Soil type"],
            [custom_float, custom_int, custom_float, str],
            [True, False, False, False],
        ),
        # 'DP' : (),
        "PT": (["Depth (m)", "Soil type"], [custom_float, str], [True, False]),
        "TR": (["Depth (m)", "Soil type"], [custom_float, str], [True, False]),
        "PR": (
            ["Depth (m)", "Total resistance (MN/m^2)", "Sleeve friction (kN/m^2)", "Soil type"],
            [custom_float, custom_float, custom_float, str],
            [True, False, False, False],
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
            [True, False, False, False, False],
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
            [True, False, False, False, False],
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
            [True, False, False, False, False],
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
            [True, False, False, False, False, False],
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
            [True, False, False, False, False, False],
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
            [True, False, False, False, False, False],
        ),
        "HP": {
            "H": (
                ["Depth (m)", "Blows", "Torque (Nm)", "Survey type", "Soil type"],
                [custom_float, custom_int, custom_float, str, str],
                [True, False, False, True, False],
            ),
            "P": (
                ["Depth (m)", "Pressure (MN/m^2)", "Torque (Nm)", "Survey type", "Soil type"],
                [custom_float, custom_float, custom_float, str, str],
                [True, False, False, True, False],
            ),
        },
        "PO": (
            ["Depth (m)", "Time (s)", "Soil type"],
            [custom_float, custom_int, str],
            [True, False, False],
        ),
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
            [True, True, True, False, False, False, False, True, False],
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
            [True, True, False, False, False, False],
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
            [True, True, False, False, False, False],
        ),
        "VK": (["Water level", "Date", "Type"], [custom_float, str, str], [True, True, False]),
        "VPK": (["Water level", "Date"], [custom_float, str], [True, True, False]),
        "HV": (
            ["Depth (m)", "Pressure (kN/m^2)", "Date", "Measurer"],
            [custom_float, custom_float, str, str],
            [False, False, False, False],
        ),
        "HU": (
            ["Height", "Date", "Pipe top level", "Pipe bottom level", "Filter lenght", "Measurer"],
            [custom_float, str, custom_float, custom_float, custom_float, str],
            [False, False, False, False, False, False],
        ),
        "PS/PMT": (
            ["Depth (m)", "Pressometer modulus (MN/m^2)", "Burst pressure (MN/m^2)"],
            [custom_float, custom_float, custom_float],
            [False, False, False],
        ),
        "PS": (
            ["Depth (m)", "Pressometer modulus (MN/m^2)", "Burst pressure (MN/m^2)"],
            [custom_float, custom_float, custom_float],
            [False, False, False],
        ),
        "PMT": (
            ["Depth (m)", "Pressometer modulus (MN/m^2)", "Burst pressure (MN/m^2)"],
            [custom_float, custom_float, custom_float],
            [False, False, False],
        ),
        "PM": (["Height", "Date", "Measurer"], [custom_float, str, str], [False, False, False]),
        "KO": (
            ["Depth (m)", "Soil type", "rock", "rock", "Maximum width", "Minimum width"],
            [custom_float, str, custom_float, custom_int, custom_float, custom_float],
            [False, False, False, False, False, False],
        ),
        "KE": (
            ["Initial depth (m)", "Final depth (m)"],
            [custom_float, custom_float],
            [True, False],
        ),
        "KR": (
            ["Initial depth (m)", "Final depth (m)"],
            [custom_float, custom_float],
            [True, True],
        ),
        "NO": (
            ["Depth  info 1 (m)", "Sample ID", "Depth info 2 (m)", "Soil type"],
            [custom_float, str, custom_float, str],
            [True, True, True, False],
        ),
        "NE": (
            ["Depth info 1 (m)", "Sample ID", "Depth info 2 (m)", "Soil type"],
            [custom_float, str, custom_float, str],
            [True, True, True, False],
        ),
        "LB": (["Laboratory", "Result", "Unit"], [str, str, str], [True, True, False]),
        "RK": (["Sieve size", "Passing percentage"], [custom_float, custom_float], [True, True]),
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
        ML: Maa- tai kalliolajiluokitus (SFS-EN ISO 14688-2)
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
    print(info_fi())
