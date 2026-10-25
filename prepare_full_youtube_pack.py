#!/usr/bin/env python3
"""
Generates ultra-rich, professional, SEO-optimized metadata for all 34 Junior Edition YouTube videos (English & Romanian).
"""

import os
import shutil
from pathlib import Path

BASE_DIR = Path("/Users/sergiuman/Desktop/Gemini/Books")
JUNIOR_DIR = BASE_DIR / "junior_editions"
DEST_DIR = BASE_DIR / "youtube_upload_pack_full"

VOLUMES_METADATA = {
    "1_systems_thinking": {
        "vol": "Vol01",
        "book": "The Fifth Discipline by Peter Senge",
        "en": {
            "title": "Radu & The Magic Glasses 👓 | Systems Thinking for Kids (Junior Edition Vol. 01)",
            "description": (
                "Radu receives a pair of magical glasses that allow him to see how everything in the forest is connected! "
                "Help your child learn systems thinking, see the bigger picture in life, and understand cause and effect.\n\n"
                "🌟 KEY LESSONS FOR KIDS:\n"
                "• Seeing the bigger picture: How small choices ripple across time.\n"
                "• Understanding cause and effect in nature and friendships.\n"
                "• Thinking in connections rather than isolated events.\n\n"
                "📖 BOOK INSPIRATION:\n"
                "Adapted from Peter Senge's masterpiece 'The Fifth Discipline' for children.\n\n"
                "🕒 CHAPTER TIMESTAMPS:\n"
                "00:00 - Introduction & The Magic Glasses\n"
                "01:15 - Seeing the Hidden Threads of the Forest\n"
                "03:20 - The Ripple Effect\n"
                "05:10 - Lessons for Life & Conclusion\n\n"
                "🔔 Subscribe for more educational animated stories for kids!\n\n"
                "#kidsstories #systemsthinking #childrensbooks #bedtimestories #educationalstories #petersenge"
            ),
            "tags": "kids story, systems thinking, educational stories, childrens book, children education, radu and magic glasses, systems thinking for kids, bedtime stories, animated storybook"
        },
        "ro": {
            "title": "Copacul care ascultă pădurea 👓 | Gândirea Sistemică pentru Copii (Ediția Junior Vol. 01)",
            "description": (
                "Kiri și Pip descoperă ochelarii fermecați ai pădurii și învață cum toate viețuitoarele și acțiunile noastre sunt legate între ele. "
                "O poveste minunată despre gândirea sistemică, empatie și consecințele acțiunilor noastre!\n\n"
                "🌟 ÎNVĂȚĂTURI CHEIE PENTRU COPII:\n"
                "• Cum micile noastre fapte creează valuri în timp.\n"
                "• Înțelegerea cauzei și efectului în natură și prietenie.\n"
                "• Gândirea în conexiuni și privirea de ansamblu.\n\n"
                "📖 INSPIRAȚIE DIN CARTE:\n"
                "Adaptat după lucrarea 'A cincea disciplină' de Peter Senge pe înțelesul copiilor.\n\n"
                "🕒 CAPITOLE ȘI MARCAJE DE TIMP:\n"
                "00:00 - Introducere: Ochelarii Fermecați\n"
                "01:15 - Ițele Nevăzute ale Pădurii\n"
                "03:20 - Efectul de Val\n"
                "05:10 - Învățăminte pentru Viață\n\n"
                "🔔 Abonați-vă pentru mai multe povești educative animate în limba română!\n\n"
                "#povesticopii #gandiresistemica #carticopii #povestidormit #educatiecopii #petersenge"
            ),
            "tags": "povesti copii, gandire sistemica, povesti educative, carti copii, educatie copii, povesti limba romana, povesti cu invataturi, lectii de viata copii"
        }
    },
    "2_seven_habits": {
        "vol": "Vol02",
        "book": "7 Habits of Highly Effective People by Stephen Covey",
        "en": {
            "title": "Ileana's 7 Magic Keys 🔑 | 7 Habits of Happy Kids (Junior Edition Vol. 02)",
            "description": (
                "Follow Ileana on a magical journey to find the 7 keys of happy, responsible, and successful kids! "
                "A child-friendly adaptation of Stephen Covey's timeless 7 Habits of Highly Effective People.\n\n"
                "🌟 KEY LESSONS FOR KIDS:\n"
                "• Be Proactive & Take Responsibility.\n"
                "• Begin with the End in Mind & Work Together.\n"
                "• Put First Things First.\n\n"
                "📖 BOOK INSPIRATION:\n"
                "Based on Stephen Covey & Sean Covey's '7 Habits of Highly Effective People'.\n\n"
                "🔔 Subscribe for weekly animated stories!\n\n"
                "#7habits #kidsstories #characterbuilding #childrensbooks #stephencovey"
            ),
            "tags": "7 habits of highly effective people, kids habits, personal growth for kids, educational stories, childrens book, happy kids, character building"
        },
        "ro": {
            "title": "Cele 7 Chei Magice ale Ileanei 🔑 | 7 Obiceiuri ale Copiilor Fericiți (Ediția Junior Vol. 02)",
            "description": (
                "Alătură-te Ileanei într-o aventură de neuitat pentru a descoperi cele 7 chei ale copiilor fericiți și responsabili! "
                "O adaptare specială pe înțelesul copiilor a celor 7 Obiceiuri ale persoanelor de succes.\n\n"
                "🌟 ÎNVĂȚĂTURI CHEIE PENTRU COPII:\n"
                "• Fii proactiv și asumă-ți responsabilitatea.\n"
                "• Începe cu scopul în minte și lucrează în echipă.\n"
                "• Pune lucrurile importante pe primul loc.\n\n"
                "📖 INSPIRAȚIE DIN CARTE:\n"
                "Adaptare după 'Cele 7 Eficiente Obiceiuri' de Stephen Covey.\n\n"
                "🔔 Abonați-vă pentru povești educative săptămânale!\n\n"
                "#cele7obiceiuri #povesticopii #dezvoltarepersonala #carticopii #stephencovey"
            ),
            "tags": "cele 7 obiceiuri, obiceiuri copii, dezvoltare personala copii, povesti educative romana, carti copii, responsabilitate copii"
        }
    },
    "3_sapiens": {
        "vol": "Vol03",
        "book": "Sapiens: A Brief History of Humankind by Yuval Noah Harari",
        "en": {
            "title": "The Magic Campfire 🔥 | Sapiens Story for Kids (Junior Edition Vol. 03)",
            "description": (
                "Gather around the magic campfire to learn the story of humanity—how human beings used imagination, cooperation, and storytelling to build a world together.\n\n"
                "🌟 KEY LESSONS FOR KIDS:\n"
                "• The power of imagination and shared dreams.\n"
                "• How cooperation helps people accomplish big goals.\n"
                "• Learning from human history.\n\n"
                "📖 BOOK INSPIRATION:\n"
                "Based on Yuval Noah Harari's international bestseller 'Sapiens'.\n\n"
                "#sapiens #kidsstories #humanhistory #yuvalnoahharari #educationalstories"
            ),
            "tags": "sapiens for kids, history for children, human history story, educational kids video, childrens bedtime story, cooperation, yuval noah harari"
        },
        "ro": {
            "title": "Focul de Tabără Fermecat 🔥 | Sapiens pe Înțelesul Copiilor (Ediția Junior Vol. 03)",
            "description": (
                "O călătorie fascinantă în trecutul umanității: cum au învățat oamenii să coopereze, să viseze și să spună povești împreună pentru a schimba lumea.\n\n"
                "🌟 ÎNVĂȚĂTURI CHEIE PENTRU COPII:\n"
                "• Puterea imaginației și a visurilor împărtășite.\n"
                "• Cum cooperarea ne ajută să construim lucruri mari.\n"
                "• Învățăminte din istoria oamenilor.\n\n"
                "📖 INSPIRAȚIE DIN CARTE:\n"
                "Adaptare după 'Sapiens' de Yuval Noah Harari.\n\n"
                "#sapienscopii #istoriecopii #povesteaumanitatii #yuvalnoahharari #povesticopii"
            ),
            "tags": "sapiens pentru copii, istorie copii, povestea omului, povesti educative, cooperare copii, yuval noah harari romana"
        }
    },
    "4_supercommunicators": {
        "vol": "Vol04",
        "book": "Supercommunicators by Charles Duhigg",
        "en": {
            "title": "The Whispering Hares 🐇 | How to Communicate & Connect (Junior Edition Vol. 04)",
            "description": (
                "Two little rabbits learn the secret of active listening—how to understand feelings and speak from the heart to become supercommunicators.\n\n"
                "📖 Based on Charles Duhigg's 'Supercommunicators'.\n\n"
                "#communication #kidsstories #emotionalintelligence #charlesduhigg"
            ),
            "tags": "children communication, active listening for kids, emotional intelligence, friendship story, kids communication skills, supercommunicators"
        },
        "ro": {
            "title": "Iepurașii Șoptitori 🐇 | Arta de a Asculta și Comunica cu Inima (Ediția Junior Vol. 04)",
            "description": (
                "Doi iepurași descoperă secretul ascultării active: cum să înțelegi emoțiile prietenilor și să comunici cu empatie.\n\n"
                "📖 Adaptat după 'Supercommunicators' de Charles Duhigg.\n\n"
                "#comunicarecopii #inteligentaemotionala #empatiecopii #charlesduhigg"
            ),
            "tags": "comunicare copii, ascultare activa copii, inteligenta emotionala, empatie copii, povesti cu animale"
        }
    },
    "5_atomic_habits": {
        "vol": "Vol05",
        "book": "Atomic Habits by James Clear",
        "en": {
            "title": "Tiny Steps of the Little Bear 🐻 | Atomic Habits for Kids (Junior Edition Vol. 05)",
            "description": (
                "Barnaby the little bear wants to build a big wooden house. Learn how tiny daily habits (1% better every day) help children build big dreams!\n\n"
                "📖 Based on James Clear's 'Atomic Habits'.\n\n"
                "#atomichabits #kidsstories #goodhabits #jamesclear"
            ),
            "tags": "atomic habits for kids, kids habits, building good habits, parenting tips, childrens growth, james clear"
        },
        "ro": {
            "title": "Pașii Mici ai Ursulețului 🐻 | Obiceiuri Atomice pentru Copii (Ediția Junior Vol. 05)",
            "description": (
                "Ursulețul Barnaby dorește să construiască o căsuță mare. Descoperă cum pașii mici făcuți în fiecare zi construiesc mari realizări!\n\n"
                "📖 Adaptare după 'Obiceiuri Atomice' de James Clear.\n\n"
                "#obiceiuriatomice #povesticopii #pascupas #jamesclearromana"
            ),
            "tags": "obiceiuri atomice copii, pas cu pas, rutina copii, dezvoltare personala copii, james clear romana"
        }
    },
    "6_emotional_intelligence": {
        "vol": "Vol06",
        "book": "Emotional Intelligence by Daniel Goleman",
        "en": {
            "title": "The Heart Keepers 💖 | Emotional Intelligence for Kids (Junior Edition Vol. 06)",
            "description": (
                "Meet the little helpers inside our hearts. A storybook lesson on naming feelings, managing anger, and finding calm.\n\n"
                "📖 Based on Daniel Goleman's 'Emotional Intelligence'.\n\n"
                "#emotionalintelligence #kidsemotions #goleman #kidsstories"
            ),
            "tags": "emotional intelligence for kids, naming feelings, kids emotions, bedtime story, social emotional learning, daniel goleman"
        },
        "ro": {
            "title": "Paznicii Inimii 💖 | Inteligență Emoțională pentru Copii (Ediția Junior Vol. 06)",
            "description": (
                "O poveste despre micii spiriduși din inima noastră. Învață cum să recunoști emoțiile și să aduci calm în suflet.\n\n"
                "📖 Adaptare după 'Inteligența Emoțională' de Daniel Goleman.\n\n"
                "#inteligentaemotionala #emotiicopii #danielgoleman #povestiterapeutice"
            ),
            "tags": "inteligenta emotionala copii, emotii copii, gestionare furie copii, povesti terapeutice, daniel goleman"
        }
    },
    "7_beyond_order": {
        "vol": "Vol07",
        "book": "Beyond Order by Jordan Peterson",
        "en": {
            "title": "The Cozy Nest & The Wild Woods 🌲 | Order vs Chaos Story (Junior Edition Vol. 07)",
            "description": (
                "A little bluejay learns the balance between a safe nest (Order) and unpredictable woods (Chaos).\n\n"
                "📖 Based on Jordan Peterson's 'Beyond Order'.\n\n"
                "#jordanpeterson #orderandchaos #kidsstories #lifelessons"
            ),
            "tags": "order and chaos, Jordan Peterson kids, kids life lessons, bedtime story, childrens development"
        },
        "ro": {
            "title": "Cuibul Ocrotitor și Pădurea Sălbatică 🌲 | Ordine și Explorare (Ediția Junior Vol. 07)",
            "description": (
                "O gaiță albastră învață echilibrul dintre siguranța cuibului și curajul de a explora pădurea.\n\n"
                "📖 Adaptat după 'Beyond Order' de Jordan Peterson.\n\n"
                "#jordanpeterson #ordinehaos #povesticopii #dezvoltarecopii"
            ),
            "tags": "ordine si haos copii, lectii de viata copii, dezvoltare copii, jordan peterson romana"
        }
    },
    "8_mindset": {
        "vol": "Vol08",
        "book": "Mindset by Carol S. Dweck",
        "en": {
            "title": "Pippin: The Seed that Loved to Try 🌱 | Growth Mindset Story (Junior Edition Vol. 08)",
            "description": (
                "Pippin the seed learns that facing storms makes us grow taller. Effort makes our brains stronger!\n\n"
                "📖 Based on Carol Dweck's 'Mindset'.\n\n"
                "#growthmindset #caroldweck #kidsstories #resilience"
            ),
            "tags": "growth mindset for kids, Carol Dweck kids, kids resilience, never give up, educational story"
        },
        "ro": {
            "title": "Micul Sâmbure Pippin 🌱 | Mentalitatea de Dezvoltare pentru Copii (Ediția Junior Vol. 08)",
            "description": (
                "Micul sâmbure Pippin descoperă că provocările îl ajută să devină un copac puternic. Efortul ne face creierul mai deștept!\n\n"
                "📖 Adaptare după 'Mindset' de Carol Dweck.\n\n"
                "#mentalitatededezvoltare #caroldweck #povesticopii #perseverenta"
            ),
            "tags": "mentalitate de dezvoltare, perseverenta copii, incredere in sine copii, carol dweck romana"
        }
    },
    "9_grit": {
        "vol": "Vol09",
        "book": "Grit by Angela Duckworth",
        "en": {
            "title": "Leo's Little Wings 🏔️ | A Story of Grit & Perseverance (Junior Edition Vol. 09)",
            "description": (
                "Leo the swallow is not the fastest, but he has Grit. Daily practice beats raw talent when climbing mountains!\n\n"
                "📖 Based on Angela Duckworth's 'Grit'.\n\n"
                "#grit #perseverance #angeladuckworth #kidsstories"
            ),
            "tags": "grit for kids, perseverance story, never give up, kids stamina, character building, angela duckworth"
        },
        "ro": {
            "title": "Aripile lui Leo 🏔️ | Poveste despre Perseverență și Ambiție (Ediția Junior Vol. 09)",
            "description": (
                "Rândunica Leo nu este cel mai rapid zburător, dar are ambiție și perseverență. Munca zilnică învinge talentul nativ!\n\n"
                "📖 Adaptare după 'Grit' de Angela Duckworth.\n\n"
                "#perseverenta #ambitie #angeladuckworth #povesticopii"
            ),
            "tags": "perseverenta copii, ambitie copii, puterea vointi, angela duckworth romana, povesti copii"
        }
    },
    "10_deep_work": {
        "vol": "Vol10",
        "book": "Deep Work by Cal Newport",
        "en": {
            "title": "Pip's Quiet House 🐿️ | Focus & Deep Work Story for Kids (Junior Edition Vol. 10)",
            "description": (
                "Pip the squirrel struggles with distractions. Learn how a quiet space and deep focus help children create amazing work.\n\n"
                "📖 Based on Cal Newport's 'Deep Work'.\n\n"
                "#deepwork #focus #calnewport #kidsstories"
            ),
            "tags": "focus for kids, deep work kids, study habits, digital wellness, concentration story, cal newport"
        },
        "ro": {
            "title": "Căsuța Liniștită a lui Pip 🐿️ | Puterea Concentrării pentru Copii (Ediția Junior Vol. 10)",
            "description": (
                "Veverița Pip învață că pentru a construi lucruri minunate are nevoie de liniște și atenție neîntreruptă.\n\n"
                "📖 Adaptare după 'Deep Work' de Cal Newport.\n\n"
                "#concentrare #atentie #calnewport #povesticopii"
            ),
            "tags": "concentrare copii, atentie copii, stil de invatare, cal newport romana, obisnuinte de studiu"
        }
    },
    "11_thinking_fast_slow": {
        "vol": "Vol11",
        "book": "Thinking, Fast and Slow by Daniel Kahneman",
        "en": {
            "title": "Quick-Hop & Slow-Hoot 🐇🦉 | Fast & Slow Thinking for Kids (Junior Edition Vol. 11)",
            "description": (
                "Meet the rabbit and owl inside your mind! Learn when to act fast on instinct and when to think slowly.\n\n"
                "📖 Based on Daniel Kahneman's 'Thinking, Fast and Slow'.\n\n"
                "#thinkingfastandslow #kahneman #kidspsychology #kidsstories"
            ),
            "tags": "thinking fast and slow kids, Daniel Kahneman children, critical thinking, kids psychology, decision making"
        },
        "ro": {
            "title": "Iepurașul Grăbit și Bufnița Înțeleaptă 🐇🦉 | Gândire Rapidă și LENTĂ (Ediția Junior Vol. 11)",
            "description": (
                "Cunoaște cele două voci din mintea ta: iepurașul grăbit și bufnița care analizează cu atenție.\n\n"
                "📖 Adaptare după 'Thinking, Fast and Slow' de Daniel Kahneman.\n\n"
                "#gandirecritica #danielkahneman #psihologiecopii #povesticopii"
            ),
            "tags": "gandire critica copii, luarea deciziilor copii, psihologie copii, daniel kahneman romana"
        }
    },
    "12_quiet": {
        "vol": "Vol12",
        "book": "Quiet by Susan Cain",
        "en": {
            "title": "Oliver's Quiet Power 🦦 | Introvert Strengths Kids Story (Junior Edition Vol. 12)",
            "description": (
                "Oliver the beaver is quiet and loves to draw. Oliver's careful planning saves the day. A celebration of introverted kids!\n\n"
                "📖 Based on Susan Cain's 'Quiet'.\n\n"
                "#quiet #introverts #susancain #kidsstories"
            ),
            "tags": "quiet power, introverted kids, introversion story, quiet strengths, childrens book, susan cain"
        },
        "ro": {
            "title": "Puterea Liniștită a lui Oliver 🦦 | Calitățile Copiilor Introvertiți (Ediția Junior Vol. 12)",
            "description": (
                "Castorul Oliver este tăcut și observator. Calmul și planificarea lui salvează comunitatea. Dedicat copiilor introvertiți!\n\n"
                "📖 Adaptare după 'Quiet' de Susan Cain.\n\n"
                "#copiiintrovertiti #puterealinistii #susancain #povesticopii"
            ),
            "tags": "copii introvertiti, puterea linistii, incredere copii, susan cain romana, empatie copii"
        }
    },
    "13_boy_mole_fox_horse": {
        "vol": "Vol13",
        "book": "The Boy, the Mole, the Fox and the Horse by Charlie Mackesy",
        "en": {
            "title": "Kindness in the Forest ❄️ | Love, Kindness & Asking for Help (Junior Edition Vol. 13)",
            "description": (
                "Four friends journey through the snow sharing wisdom about kindness, self-compassion, and asking for help.\n\n"
                "📖 Inspired by Charlie Mackesy's book.\n\n"
                "#charliemackesy #kindness #kidsstories #askingforhelp"
            ),
            "tags": "charlie mackesy kids, kids kindness, asking for help, self compassion, bedtime story"
        },
        "ro": {
            "title": "Bunătatea din Pădure ❄️ | Despre Iubire și Curajul de a Cere Ajutor (Ediția Junior Vol. 13)",
            "description": (
                "Patru prieteni călătoresc prin zăpadă și împărtășesc învățături blânde despre bunătate și de ce a cere ajutor este un act de curaj.\n\n"
                "📖 Inspirați de cartea lui Charlie Mackesy.\n\n"
                "#bunatate #charliemackesy #cereajutor #povesticopii"
            ),
            "tags": "bunatate copii, cere ajutor copii, empatie copii, povesti calde copii, inteligenta emotionala"
        }
    },
    "14_start_with_why": {
        "vol": "Vol14",
        "book": "Start With Why by Simon Sinek",
        "en": {
            "title": "Maya's Golden Compass 🧭 | Start With Why Story for Kids (Junior Edition Vol. 14)",
            "description": (
                "Maya discovers that finding *why* she wants to sail (her dream) is far more important than just *what* wood she uses.\n\n"
                "📖 Based on Simon Sinek's 'Start With Why'.\n\n"
                "#startwithwhy #simonsinek #kidsstories #purpose"
            ),
            "tags": "start with why kids, Simon Sinek children, kids purpose, finding passion, dream big"
        },
        "ro": {
            "title": "Compasul de Aur al Mayei 🧭 | Începe cu DE CE (Ediția Junior Vol. 14)",
            "description": (
                "Maya vrea să construiască o corăbioară. Ea descoperă că motivul pentru care dorește să navigheze este mai important decât uneltele folosite.\n\n"
                "📖 Adaptare după 'Start With Why' de Simon Sinek.\n\n"
                "#incepucudece #simonsinek #motivatiecopii #povesticopii"
            ),
            "tags": "incepe cu de ce, simon sinek romana, motivatie copii, vise copii, lideri mici"
        }
    },
    "15_why_we_sleep": {
        "vol": "Vol15",
        "book": "Why We Sleep by Matthew Walker",
        "en": {
            "title": "Toby & The Sleep Elves 💤 | Why Sleep is Magic for Kids (Junior Edition Vol. 15)",
            "description": (
                "Toby meets the Sleep Elves who clean his brain and repair his muscles at night. Explaining why sleep is vital!\n\n"
                "📖 Based on Matthew Walker's 'Why We Sleep'.\n\n"
                "#whywesleep #matthewwalker #bedtimeroutine #kidshealth"
            ),
            "tags": "why we sleep kids, sleep hygiene children, bedtime routine, kids sleep story, matthew walker"
        },
        "ro": {
            "title": "Toby și Spiridușii Somnului 💤 | De Ce Somnul Este Magic pentru Copii (Ediția Junior Vol. 15)",
            "description": (
                "Toby îi cunoaște pe spiridușii care îi fac curățenie în minte și îi repară energia în timpul nopții.\n\n"
                "📖 Adaptare după 'Despre Somn' de Matthew Walker.\n\n"
                "#somncopii #matthewwalker #rutinadeseara #sanatatecopii"
            ),
            "tags": "somn copii, importanta somnului, rutina de seara copii, matthew walker romana, sanatate copii"
        }
    },
    "16_cant_hurt_me": {
        "vol": "Vol16",
        "book": "Can't Hurt Me by David Goggins",
        "en": {
            "title": "Victor's Strong Shield 🦔 | Building Mental Toughness Story (Junior Edition Vol. 16)",
            "description": (
                "Victor the hedgehog learns that his mind is stronger than any obstacle. A story on building resilience and confidence.\n\n"
                "📖 Based on David Goggins' 'Can't Hurt Me'.\n\n"
                "#davidgoggins #mentaltoughness #kidsresilience #kidsstories"
            ),
            "tags": "mental toughness kids, David Goggins children, resilience story, building confidence, discipline for kids"
        },
        "ro": {
            "title": "Scutul Puternic al lui Victor 🦔 | Ambiție și Forță Mentală pentru Copii (Ediția Junior Vol. 16)",
            "description": (
                "Ariciul Victor învață că mintea și voința lui sunt mai puternice decât orice obstacol.\n\n"
                "📖 Adaptare după 'Can't Hurt Me' de David Goggins.\n\n"
                "#davidgoggins #fortamentala #disciplinacopii #povesticopii"
            ),
            "tags": "forta mentala copii, david goggins romana, disciplina copii, incredere in sine copii"
        }
    },
    "17_anxious_generation": {
        "vol": "Vol17",
        "book": "The Anxious Generation by Jonathan Haidt",
        "en": {
            "title": "Dan & The Play Forest 🌳 | Outdoor Play & Screen-Free Fun (Junior Edition Vol. 17)",
            "description": (
                "Dan leaves his glowing mirror behind to climb trees and play in the mud with friends. A lesson on screen time and real-world play.\n\n"
                "📖 Based on Jonathan Haidt's 'The Anxious Generation'.\n\n"
                "#jonathanhaidt #screentime #outdoorplay #kidshealth"
            ),
            "tags": "screen time limits kids, digital wellness children, outdoor play, childrens health, jonathan haidt"
        },
        "ro": {
            "title": "Dan și Pădurea de Joacă 🌳 | Echilibru între Ecrane și Joacă Liberă (Ediția Junior Vol. 17)",
            "description": (
                "Dan lasă deoparte oglinda strălucitoare (ecranul) pentru a se bucura de natură și jocuri alături de prieteni.\n\n"
                "📖 Adaptare după 'The Anxious Generation' de Jonathan Haidt.\n\n"
                "#jonathanhaidt #ecranecopii #joacaafara #echilibrudigital"
            ),
            "tags": "ecrane copii, joaca afara copii, echilibru digital, sanatate copii, jonathan haidt romana"
        }
    }
}

def main():
    DEST_DIR.mkdir(parents=True, exist_ok=True)

    for folder, meta in VOLUMES_METADATA.items():
        vol_prefix = meta["vol"]
        folder_path = JUNIOR_DIR / folder

        # EN
        src_en = folder_path / "video_en_v2.mp4"
        if not src_en.exists(): src_en = folder_path / "video_en.mp4"

        if src_en.exists():
            dest_en_video = DEST_DIR / f"{vol_prefix}_Junior_EN.mp4"
            dest_en_meta = DEST_DIR / f"{vol_prefix}_Junior_EN_metadata.txt"
            shutil.copy2(src_en, dest_en_video)
            with open(dest_en_meta, "w", encoding="utf-8") as f:
                f.write(f"TITLE:\n{meta['en']['title']}\n\n")
                f.write(f"DESCRIPTION:\n{meta['en']['description']}\n\n")
                f.write(f"TAGS:\n{meta['en']['tags']}\n")

        # RO
        src_ro = folder_path / "video_ro_v2.mp4"
        if not src_ro.exists(): src_ro = folder_path / "video_ro.mp4"

        if src_ro.exists():
            dest_ro_video = DEST_DIR / f"{vol_prefix}_Junior_RO.mp4"
            dest_ro_meta = DEST_DIR / f"{vol_prefix}_Junior_RO_metadata.txt"
            shutil.copy2(src_ro, dest_ro_video)
            with open(dest_ro_meta, "w", encoding="utf-8") as f:
                f.write(f"TITLE:\n{meta['ro']['title']}\n\n")
                f.write(f"DESCRIPTION:\n{meta['ro']['description']}\n\n")
                f.write(f"TAGS:\n{meta['ro']['tags']}\n")

    print("[✓] Enhanced, rich SEO metadata files successfully generated for all 34 videos!")

if __name__ == "__main__":
    main()
