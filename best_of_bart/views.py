from django.shortcuts import render
import json
from django.http import HttpResponse
import os


GALLERY_ITEMS = [
    {
        'id': 1,
        'title': 'Pepernoten proeverij',
        'description': 'In deze les doen de leerlingen een proeverij met verschillende soorten pepernoten en kruidnoten. Ze onderzoeken de producten met hun zintuigen en verwerken hun bevindingen in eenvoudige observaties en vergelijkingen.',
        'image': {'url': 'main/images/IMG_2777.JPG'},
        'tiktok_url': 'https://www.tiktok.com/@bestofbart/video/7578943053881298208',
        'genre': 'rekenen',
        'files': [{'url': '/media/main/files/pepernoten-proeverij.zip'}],
    },
    {
        'id': 2,
        'title': "'t Sexy fokschaap",
        'description': "Een creatieve spellingles waarin leerlingen een visuele en grappige uitwerking maken van de regel van 't fokschaap. Door tekenen en ontwerpen wordt de werkwoordspelling beter onthouden.",
        'image': {'url': 'main/images/IMG_2778.JPG'},
        'tiktok_url': 'https://www.tiktok.com/@bestofbart/video/7574094689893223713',
        'genre': 'spelling',
        'files': [{'url': '/media/main/files/t-sexy-fokschaap.zip'}],
    },
    {
        'id': 3,
        'title': "Maak je eigen prentenboek",
        'description': 'De leerlingen ontwerpen hun eigen prentenboek. Ze bedenken een verhaal, maken zelf de illustraties en zetten alles digitaal in een prentenboekvorm.',
        'image': {'url': 'main/images/IMG_2779.JPG'},
        'tiktok_url': 'https://www.tiktok.com/@bestofbart/video/7559623858534337824',
        'genre': 'crea',
        'files': [{'url': '/media/main/files/prentenboek.zip'}],
    },
    {
        'id': 4,
        'title': 'Neon lights schilderen',
        'description': 'In deze crea-les maken leerlingen een schilderij met een neon-licht-effect. Met contrast en kleurgebruik ontstaat een opvallend, lichtgevend resultaat.',
        'image': {'url': 'main/images/IMG_2780.JPG'},
        'tiktok_url': 'https://www.tiktok.com/@bestofbart/video/7552943116949523744',
        'genre': 'crea',
        'files': [{'url': '/media/main/files/neon-lights.zip'}],
    },
    {
        'id': 5,
        'title': 'Moederdagcadeau',
        'description': "Leerlingen ontwerpen een persoonlijke wikkel voor een chocoladereep en maken een bijpassende 'golden ticket'. Het eindresultaat is een creatief en persoonlijk Moederdagcadeau.",
        'image': {'url': 'main/images/IMG_2781.JPG'},
        'tiktok_url': 'https://www.tiktok.com/@bestofbart/video/7501702548282150166',
        'genre': 'crea',
        'files': [{'url': '/media/main/files/moederdagcadeau.zip'}],
    },
    {
        'id': 6,
        'title': "Emoji's vouwen",
        'description': 'In deze les vouwen leerlingen papier tot herkenbare emoji-figuren. Er wordt gewerkt aan nauwkeurig vouwen, vorm en expressie.',
        'image': {'url': 'main/images/IMG_2782.JPG'},
        'tiktok_url': 'https://www.tiktok.com/@bestofbart/video/7466871827034508567',
        'genre': 'crea',
        'files': [{'url': '/media/main/files/emojis-vouwen.zip'}],
    },
    {
        'id': 7,
        'title': "Rocky Road",
        'description': 'De klas maakt samen een Sinterklaas-variant van Rocky Road. Leerlingen volgen een recept en verwerken verschillende ingrediënten tot een feestelijk eindproduct.',
        'image': {'url': 'main/images/IMG_2783.JPG'},
        'tiktok_url': 'https://www.tiktok.com/@bestofbart/video/7443536203560881430',
        'genre': 'crea',
        'files': [{'url': '/media/main/files/rocky-road.zip'}],
    },
    {
        'id': 8,
        'title': "Schuifpuzzel maken",
        'description': 'Leerlingen ontwerpen en maken hun eigen schuifpuzzel. Ze werken aan beeld, indeling en logisch nadenken om een speelbare puzzel te creëren.',
        'image': {'url': 'main/images/IMG_2784.JPG'},
        'tiktok_url': 'https://www.tiktok.com/@bestofbart/video/7464288494601440534',
        'genre': 'crea',
        'files': [{'url': '/media/main/files/schuifpuzzel.zip'}],
    },
    {
        'id': 9,
        'title': "Mascotte maken",
        'description': 'In deze lessenserie ontwerpen leerlingen een eigen mascotte. Ze tekenen het ontwerp, kleien het figuur en schilderen het uiteindelijk af.',
        'image': {'url': 'main/images/IMG_2785.JPG'},
        'tiktok_url': 'https://www.tiktok.com/@bestofbart/video/7426633807169719585',
        'genre': 'crea',
        'files': [{'url': '/media/main/files/mascotte.zip'}],
    },
    {
        'id': 10,
        'title': "Schatkaarten maken",
        'description': "Leerlingen maken een schatkaart op 'verouderd' papier. Ze geven hun kaart vorm met symbolen, routes en fantasierijke details.",
        'image': {'url': 'main/images/IMG_2786.JPG'},
        'tiktok_url': 'https://www.tiktok.com/@bestofbart/video/7277228115951209760',
        'genre': 'crea',
        'files': [{'url': '/media/main/files/schatkaart.zip'}],
    },
    {
        'id': 11,
        'title': "Adventkalender maken",
        'description': "In deze les maken leerlingen een adventskalender in de vorm van een decemberdorpje. Elk huisje staat voor een dag en bevat een kleine verrassing of opdracht.",
        'image': {'url': 'main/images/IMG_2787.JPG'},
        'tiktok_url': 'https://www.tiktok.com/@bestofbart/video/7172094048319196421',
        'genre': 'crea',
        'files': [{'url': '/media/main/files/adventkalender.zip'}],
    },
    {
        'id': 12,
        'title': "Expeditie eiland maken",
        'description': "Leerlingen ontwerpen en bouwen een eigen eiland geïnspireerd op Expeditie Robinson. Ze werken met reliëf, materialen en fantasie om hun eiland vorm te geven.",
        'image': {'url': 'main/images/IMG_2788.JPG'},
        'tiktok_url': 'https://www.tiktok.com/@bestofbart/video/7379850710663351585',
        'genre': 'crea',
        'files': [{'url': '/media/main/files/expeditie-eiland.zip'}],
    },
    {
        'id': 13,
        'title': "Skyline schilderen",
        'description': "Leerlingen schilderen een skyline tegen een zonsondergang. De focus ligt op kleurverloop, silhouetten en dieptewerking.",
        'image': {'url': 'main/images/IMG_2789.JPG'},
        'tiktok_url': 'https://www.tiktok.com/@bestofbart/video/7418997114086231328',
        'genre': 'crea',
        'files': [{'url': '/media/main/files/sunset-skyline.zip'}],
    },
    {
        'id': 14,
        'title': "'t Kofschip X",
        'description': "Een spellingles waarin leerlingen de regel van 't kofschip X visueel en praktisch verwerken. Door het maken van een concreet product wordt de regel beter onthouden.",
        'image': {'url': 'main/images/IMG_2790.JPG'},
        'tiktok_url': 'https://www.tiktok.com/@bestofbart/video/7296574980156820769',
        'genre': 'spelling',
        'files': [{'url': '/media/main/files/t-kofschip-x.zip'}],
    },
    {
        'id': 15,
        'title': "Krastekeningen maken",
        'description': "In deze les maken leerlingen een kleurrijke krastekening met het jaartal 2026. Eerst kleuren ze een vel stevig papier helemaal vol met blokjes wasco. Daarna verven ze het blad zwart. Door een beetje afwasmiddel door de zwarte verf te mengen hecht de verf beter aan de wasco en is het later ook makkelijker om in de verflaag te krassen. Als het werk goed is opgedroogd, krassen de leerlingen met een satéprikker vuurwerk en andere tekeningen in de verflaag, waardoor de kleuren er weer tevoorschijn komen. Met de bijbehorende presentatie kun je deze les eenvoudig stap voor stap uitvoeren.",
        'image': {'url': 'main/images/IMG_2791.JPG'},
        'tiktok_url': 'https://www.tiktok.com/@bestofbart/video/7593764950741486880',
        'genre': 'crea',
        'files': [{'url': '/media/main/files/krastekening.zip'}],
    },
    {
        'id': 16,
        'title': "Musical uitkiezen",
        'description': "De leukste tijd van het groep 8-jaar is weer begonnen: de musical! In deze les laat ik de kinderen zelf hun musical kiezen. We bekijken samen trailers van verschillende nieuwe musicals en bespreken klassikaal wat ze aanspreekt in het verhaal, de rollen en de liedjes. Zo denken de leerlingen actief mee en kiezen we samen een musical waar de hele groep enthousiast van wordt. Met de bijbehorende presentatie kun je dit proces eenvoudig ook met jouw klas doorlopen.",
        'image': {'url': 'main/images/IMG_2792.JPG'},
        'tiktok_url': 'https://www.tiktok.com/@bestofbart/video/7611196918248656161',
        'genre': 'musical',
        'files': [{'url': '/media/main/files/musical-uitkiezen.zip'}],
    },

]

def home_view(request):
    items = [dict(item, files=json.dumps(item['files'])) for item in GALLERY_ITEMS]
    return render(request, 'home.html', {'gallery_items': items[:4], 'total_items': len(items)})


def items_view(request):
    items = [dict(item, files=json.dumps(item['files'])) for item in GALLERY_ITEMS]
    return render(request, 'items.html', {'gallery_items': items})


def contact_view(request):
    return render(request, "contact.html")
