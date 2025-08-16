"""
Gathers band conditions and solar data to reply to an SMS with the latest update
"""
import datetime
import pytz
import requests
import xmltodict

USER_AGENT = 'HamPuff/14.074/220213'
HP_URL = 'http://www.hamqsl.com/solarxml.php'
HP_HDRS = {'User-Agent' : USER_AGENT}
HP_REQ = requests.get(HP_URL, params=HP_HDRS)
HP_RES = HP_REQ.text
MY_DICT = xmltodict.parse(HP_RES)
SOLARFLUX = MY_DICT['solar']['solardata']['solarflux']
A_INDEX = MY_DICT['solar']['solardata']['aindex']
K_INDEX = MY_DICT['solar']['solardata']['kindex']
SUNSPOTS = MY_DICT['solar']['solardata']['sunspots']
XRAY = MY_DICT['solar']['solardata']['xray']
HELIUMLINE = MY_DICT['solar']['solardata']['heliumline']
PROTONFLUX = MY_DICT['solar']['solardata']['protonflux']
ELECTRONFLUX = MY_DICT['solar']['solardata']['electonflux']
AURORA = MY_DICT['solar']['solardata']['aurora']
NORMALIZATION = MY_DICT['solar']['solardata']['normalization']
LATDEGREE = MY_DICT['solar']['solardata']['latdegree']
SOLARWIND = MY_DICT['solar']['solardata']['solarwind']
MAGNETICFIELD = MY_DICT['solar']['solardata']['magneticfield']
GEOMAGFIELD = MY_DICT['solar']['solardata']['geomagfield']
SIGNALNOISE = MY_DICT['solar']['solardata']['signalnoise']
FOF2 = MY_DICT['solar']['solardata']['fof2']
MUFFFACTOR = MY_DICT['solar']['solardata']['muffactor']
MUF = MY_DICT['solar']['solardata']['muf']
4080M_DAY = MY_DICT['solar']['solardata']['band name="80m-40m" time="day">Fair</band>


def hampuff_data(hampuff_args):
    # (1) Set the timezone
    PAC               = pytz.timezone('US/Pacific')
    EAS               = pytz.timezone('US/Eastern')

    hampuff_list = list(hampuff_args.lower())
    if len(hampuff_list) != 8:
        return("Hampuff Length Error")
    hp_timezone = hampuff_list[7]
    if hp_timezone=='e' or hp_timezone=='p':
        if hp_timezone=='e':
            hp_local_tz = EAS
        if hp_timezone=='p':
            hp_local_tz = PAC
        #return (hp_local_tz)
    else:
        return ("Hampuff Timezone Unknown Error - only Pacfic (hampuffp) and Eastern (hampuffe) are supported")
    # (2) Get the reported time
    HAMQSL_UPDATE     = MY_DICT['solar']['solardata']['updated']
    # (3) Figure out what format #2 is in
    HAMQSL_FMT        = '%d %b %Y %H%M %Z'
    # (4) Parse the time from #2 using the format in #3
    HAMQSL_CUR_TIME   = datetime.datetime.strptime(HAMQSL_UPDATE, HAMQSL_FMT).replace(tzinfo=datetime.timezone.utc)
    # (5) Convert the timezone
    HAMQSL_CONV_TIME  = HAMQSL_CUR_TIME.astimezone(hp_local_tz)
    # (6)Set the output format
    HAMQSL_OUT_FORMAT = '%a %d %b %H:%M'
    # (7) format the time
    HAMQSL_OUT_TIME      = datetime.datetime.strftime(HAMQSL_CONV_TIME, HAMQSL_OUT_FORMAT)

    hampuff_data = "[Hampuff]\t%-s: %s\n\t%-11s= %s\n\t%-11s= %s\n\t%-11s= %s\n\t%-11s= %s\n\t%-11s= %s\n\t%-11s= %s\n\t%-11s= %s" % \
        ("Updated", HAMQSL_OUT_TIME, "Solar Flux", SOLARFLUX, "A Index", A_INDEX, \
            "K Index", K_INDEX, "Sunspot #", SUNSPOTS, "MUF", MUF, "XRay", XRAY, "Solar Winds", SOLARWIND)
    return hampuff_data