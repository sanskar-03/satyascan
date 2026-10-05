import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from rag.ingest import ingest_document, _collection

DOCUMENTS = [
    # T01: Apollo 11
    ("Apollo 11 Mission", 
     "The Apollo 11 mission was the spaceflight that first landed humans on the Moon. Commander Neil Armstrong and lunar module pilot Buzz Aldrin landed the Apollo Lunar Module Eagle on July 20, 1969. Armstrong became the first person to step onto the lunar surface.",
     "https://www.nasa.gov/mission/apollo-11/", "nasa.gov"),

    # T02: Human Heart
    ("Human Heart Anatomy",
     "A normal human heart consists of four distinct chambers: the upper left and right atria, and the lower left and right ventricles. These chambers work together to pump oxygenated blood throughout the body and return deoxygenated blood to the lungs.",
     "https://www.hopkinsmedicine.org/health/wellness-and-prevention/anatomy-of-the-heart", "hopkinsmedicine.org"),

    # T03: Properties of Water
    ("Properties of Water",
     "Water is a chemical compound consisting of two hydrogen atoms and one oxygen atom (H2O). At standard atmospheric pressure at sea level, pure water boils at exactly 100 degrees Celsius (212 degrees Fahrenheit) and freezes at 0 degrees Celsius (32 degrees Fahrenheit).",
     "https://www.britannica.com/science/water", "britannica.com"),

    # T04: Speed of Light
    ("Speed of Light Constant",
     "The speed of light in a perfect vacuum is exactly 299,792,458 meters per second. According to Albert Einstein's theory of special relativity, this is the maximum speed at which all conventional matter, energy, and information in the universe can travel.",
     "https://www.britannica.com/science/speed-of-light", "britannica.com"),

    # T05: Mount Everest
    ("Mount Everest Elevation",
     "Mount Everest is Earth's highest mountain above sea level, located in the Mahalangur Himal sub-range of the Himalayas. The China-Nepal border runs across its summit point. Its elevation of 8,848.86 meters was established by Nepali and Chinese authorities.",
     "https://www.britannica.com/place/Mount-Everest", "britannica.com"),

    # T06: Mars Planetary Profile
    ("Mars Planetary Profile",
     "Mars is the fourth planet from the Sun and the second-smallest planet in the Solar System. It is often referred to as the Red Planet because the iron oxide prevalent on its surface gives it a reddish appearance.",
     "https://www.nasa.gov/mars/", "nasa.gov"),

    # T07: Eiffel Tower History
    ("Eiffel Tower History",
     "The Eiffel Tower is a wrought-iron lattice tower on the Champ de Mars in Paris, France. Named after Gustave Eiffel, it was constructed from 1887 to 1889 as the centerpiece of the 1889 World's Fair.",
     "https://www.toureiffel.paris/en", "britannica.com"),

    # T08: Venus Planetary Rotation
    ("Venus Planetary Rotation",
     "A day on Venus (the time it takes for Venus to rotate once on its axis) is longer than a year on Venus (the time it takes for Venus to orbit the Sun). It takes Venus 243 Earth days to rotate once, but only 225 Earth days to complete one orbit around the Sun.",
     "https://www.nasa.gov/venus/", "nasa.gov"),

    # T09: Human Body Water Composition
    ("Human Body Water Composition",
     "The human body is composed of approximately 60 percent water. Water is vital for cellular homeostasis and life, with the brain and heart containing about 73 percent water and lungs about 83 percent.",
     "https://www.usgs.gov/special-topics/water-science-school/science/water-in-you-and-water-in-the-body", "usgs.gov"),

    # T10: William Shakespeare Hamlet
    ("William Shakespeare Hamlet",
     "William Shakespeare was an English playwright, poet, and actor regarded as the greatest writer in the English language. He wrote the famous tragedy Hamlet between 1599 and 1601 about the Prince of Denmark seeking revenge.",
     "https://www.britannica.com/topic/Hamlet-by-Shakespeare", "britannica.com"),

    # T11: Pacific Ocean Geography
    ("Pacific Ocean Geography",
     "The Pacific Ocean is the largest and deepest of Earth's oceanic divisions. It extends from the Arctic Ocean in the north to the Southern Ocean in the south and is bounded by Asia and Australia in the west and the Americas in the east.",
     "https://www.britannica.com/place/Pacific-Ocean", "britannica.com"),

    # T12: Japanese Yen Currency
    ("Japanese Yen Currency",
     "The Japanese yen is the official currency of Japan. It is the third most traded currency in the foreign exchange market after the United States dollar and the euro, and is widely used as a major reserve currency.",
     "https://www.britannica.com/money/yen-currency", "britannica.com"),

    # T13: Alexander Fleming Penicillin
    ("Alexander Fleming Penicillin",
     "Alexander Fleming was a Scottish physician and microbiologist, best known for discovering the world's first broadly effective antibiotic substance, which he named penicillin from Penicillium rubens in 1928, earning him the Nobel Prize in 1945.",
     "https://www.nobelprize.org/prizes/medicine/1945/fleming/biographical/", "nobelprize.org"),

    # T14: Moon and Ocean Tides
    ("Moon and Ocean Tides",
     "The Moon is Earth's only natural satellite. Its gravitational pull is the primary driver of Earth's ocean tides. The tides are long-period waves that move through oceans in response to gravitational forces exerted by the moon and sun.",
     "https://oceanservice.noaa.gov/facts/tidefrequency.html", "noaa.gov"),

    # T15: Tomato Botanical Classification
    ("Tomato Botanical Classification",
     "Botanically speaking, a tomato is a fruit—specifically, a berry—consisting of the ovary, together with its seeds, of a flowering plant. However, the tomato is considered a culinary vegetable because it has lower sugar content than culinary fruits.",
     "https://www.britannica.com/plant/tomato", "britannica.com"),

    # T16: Great Pyramid of Giza
    ("Great Pyramid of Giza",
     "The Great Pyramid of Giza is the largest Egyptian pyramid and the tomb of Fourth Dynasty pharaoh Khufu. Built in the early 26th century BC over 27 years, it is the oldest of the Seven Wonders of the Ancient World.",
     "https://www.britannica.com/topic/Pyramids-of-Giza", "britannica.com"),

    # T17: Leonardo da Vinci Mona Lisa
    ("Leonardo da Vinci Mona Lisa",
     "Leonardo da Vinci was an Italian polymath of the High Renaissance who was active as a painter, draughtsman, engineer, scientist, theorist, sculptor, and architect. He painted the Mona Lisa, which is considered an archetypal masterpiece of the Italian Renaissance and has been described as the best known work of art.",
     "https://www.britannica.com/topic/Mona-Lisa-painting", "britannica.com"),

    # T18: Earth Inner Core
    ("Earth Inner Core Temperature",
     "Earth's inner core is the innermost geologic layer of planet Earth, primarily a solid ball with a radius of about 1,220 km. The temperature at the inner core's surface is estimated to be approximately 5,430 degrees Celsius, which is about the temperature of the surface of the Sun.",
     "https://www.nationalgeographic.org/encyclopedia/core/", "nationalgeographic.com"),

    # T19: Speed of Sound
    ("Speed of Sound in Water vs Air",
     "Sound is a mechanical wave that is an oscillation of pressure transmitted through a solid, liquid, or gas. Sound travels faster in water (approx 1,500 m/s) than in air (approx 343 m/s) because water has higher density and lower compressibility.",
     "https://dosits.org/science/movement/speed-of-sound/", "noaa.gov"),

    # T20: Statue of Liberty
    ("Statue of Liberty France Gift",
     "The Statue of Liberty is a colossal neoclassical sculpture on Liberty Island in New York Harbor within New York City. The copper statue was a gift from the people of France to the people of the United States, designed by Bartholdi and built by Eiffel.",
     "https://www.nps.gov/stli/index.htm", "nps.gov"),

    # T21: Flat Earth Debunking
    ("Flat Earth Debunking",
     "The Earth is not flat and is not surrounded by an ice wall holding oceans in. Scientific geodesy, space photography, and astronomy conclusively prove Earth is an oblate spheroid.",
     "https://www.factcheck.org/2020/01/the-earth-is-not-flat/", "factcheck.org"),

    # T22: Venus Rotation Direction
    ("Venus Retrograde Rotation Fact-Check",
     "Venus does not rotate in the exact same direction as Earth. Venus has retrograde rotation, spinning from east to west, which is the opposite direction of Earth and most other planets in the Solar System.",
     "https://www.nasa.gov/venus-facts/", "nasa.gov"),

    # T23: Great Wall of China Moon Visibility Myth
    ("Great Wall of China Moon Visibility Myth",
     "The Great Wall of China is not visible from the surface of the Moon with the naked eye. Astronauts who walked on the Moon confirmed that no human-made structures can be seen from lunar distance without binoculars or cameras.",
     "https://www.nasa.gov/vision/space/workinginspace/great_wall.html", "nasa.gov"),

    # T24: Einstein Failed Math Myth
    ("Einstein Failed Math Myth",
     "Albert Einstein was not a terrible student who failed mathematics. Historical school records show Einstein excelled in mathematics and was mastering differential and integral calculus before age 15.",
     "https://www.britannica.com/biography/Albert-Einstein", "britannica.com"),

    # T25: Ten Percent Brain Myth
    ("Ten Percent of Brain Myth",
     "The belief that humans only use 10 percent of their brains is a complete scientific myth. Neuroimaging scans show that virtually all parts of the human brain are active and utilized during everyday tasks.",
     "https://www.scientificamerican.com/article/do-people-only-use-10-percent-of-their-brains/", "scientificamerican.com"),

    # T26: Carrots Night Vision Myth
    ("Carrots Night Vision Myth",
     "Eating massive amounts of carrots will not improve night vision beyond normal human limits or cause eyes to glow in the dark. This was a British WWII propaganda disinformation campaign to hide radar technology.",
     "https://www.smithsonianmag.com/arts-culture/a-wwii-propaganda-campaign-popularized-the-myth-that-carrots-help-you-see-in-the-dark-28812484/", "smithsonianmag.com"),

    # T27: Bulls and Red Color Myth
    ("Bulls and Red Color Myth",
     "Bulls are not enraged specifically by the color red. Cattle are red-green colorblind; bulls charge during bullfights because of the motion and waving movement of the matador's cape, not its color.",
     "https://www.britannica.com/story/do-bulls-really-hate-the-color-red", "britannica.com"),

    # T28: Capital of Australia Fact-Check
    ("Capital of Australia Canberra Fact-Check",
     "Sydney is not the capital city of Australia. The official capital of Australia is Canberra, which was founded as the nation's capital in 1913 as a compromise between Sydney and Melbourne.",
     "https://www.britannica.com/place/Canberra", "britannica.com"),

    # T29: Napoleon Short Stature Myth
    ("Napoleon Short Stature Myth",
     "Napoleon Bonaparte was not extremely short or a mere 5 feet 0 inches tall. Historical records show he stood about 5 feet 6 inches tall in modern British units, which was slightly above average for French men of his time.",
     "https://www.britannica.com/story/was-napoleon-really-short", "britannica.com"),

    # T30: George Washington Wooden Teeth Myth
    ("George Washington Wooden Teeth Myth",
     "George Washington never wore dentures that were carved out of solid wood. His dentures were crafted from hippopotamus ivory, cow and horse teeth, gold wire, and human teeth, but contained no wood.",
     "https://www.mountvernon.org/george-washington/health-and-appearance/teeth/", "mountvernon.org"),

    # T31: Goldfish Memory Span Myth
    ("Goldfish Memory Span Myth",
     "Goldfish do not have an extremely short memory span of three seconds. Controlled behavioral experiments prove that goldfish can remember cues, navigate mazes, and retain learned behaviors for months.",
     "https://www.livescience.com/goldfish-memory.html", "livescience.com"),

    # T32: Atlantic Ocean Largest Ocean Myth
    ("Atlantic Ocean Size Fact-Check",
     "The Atlantic Ocean is not by far the largest ocean on Earth. The Pacific Ocean is the largest ocean on Earth, containing more than double the volume and surface area of the Atlantic.",
     "https://www.britannica.com/place/Atlantic-Ocean", "britannica.com"),

    # T33: Julius Caesar Emperor Myth
    ("Julius Caesar Emperor Myth",
     "Julius Caesar was never crowned as the first Emperor of the Roman Empire. Caesar was dictator of the Roman Republic; his adopted heir Augustus became the first official Roman Emperor in 27 BC.",
     "https://www.britannica.com/biography/Augustus-Roman-emperor", "britannica.com"),

    # T34: Blind Bats Myth
    ("Blind Bats Myth",
     "Bats are not completely blind and do not lack functional eyes. All bat species have eyes and can see; many bats use sharp vision in combination with echolocation to navigate and hunt.",
     "https://www.britannica.com/story/are-bats-really-blind", "britannica.com"),

    # T35: Diamonds from Coal Myth
    ("Diamonds from Coal Myth",
     "Diamonds are not formed strictly from highly compressed chunks of coal. Most diamonds on Earth formed in the mantle billions of years before land plants existed to create coal.",
     "https://geology.com/articles/diamonds-from-coal/", "geology.com"),

    # T36: Lightning Strikes Same Place Myth
    ("Lightning Strikes Same Place Myth",
     "The belief that lightning never strikes the same place twice is completely false. Lightning strikes tall structures repeatedly; the Empire State Building is struck an average of 25 times every year.",
     "https://www.weather.gov/safety/lightning-myths", "weather.gov"),

    # T37: Sahara Largest Desert Myth
    ("Sahara Largest Desert Myth",
     "The Sahara is not the largest desert in the entire world. The Antarctic polar desert is the largest desert on Earth, followed by the Arctic desert; the Sahara is the third-largest desert globally.",
     "https://www.usgs.gov/faqs/what-largest-desert-world", "usgs.gov"),

    # T38: Atmospheric Oxygen Abundance Myth
    ("Atmospheric Oxygen Abundance Myth",
     "Oxygen is not the single most abundant element in Earth's atmosphere. Nitrogen is by far the most abundant element, comprising about 78 percent of Earth's atmosphere, while oxygen makes up about 21 percent.",
     "https://www.noaa.gov/jetstream/atmosphere", "noaa.gov"),

    # T39: Dogs Black and White Vision Myth
    ("Dogs Black and White Vision Myth",
     "Dogs do not see only in black and white. Canine eyes have two types of cone photoreceptors, enabling them to perceive color, specifically shades of blue, yellow, and gray.",
     "https://www.akc.org/expert-advice/health/are-dogs-color-blind/", "akc.org"),

    # T40: Penny Empire State Building Myth
    ("Penny Empire State Building Myth",
     "Dropping a copper penny from the Empire State Building cannot penetrate concrete or kill a pedestrian. Aerodynamic drag limits the penny's terminal velocity to about 30 to 50 mph, making it non-lethal.",
     "https://www.scientificamerican.com/article/could-a-penny-dropped-off/", "scientificamerican.com"),

    # T41: Chameleon Camouflage Myth
    ("Chameleon Camouflage Myth",
     "Chameleons do not change their skin color primarily to blend in with surroundings for camouflage. Color changing in chameleons is primarily an emotional and social signal, as well as a thermoregulation response.",
     "https://www.britannica.com/story/why-do-chameleons-change-colors", "britannica.com"),

    # T42: Viking Horned Helmets Myth
    ("Viking Horned Helmets Myth",
     "Viking warriors historically never wore metal helmets with horns attached to the sides into battle. Horned helmets were an artistic invention created for 19th-century theater costumes.",
     "https://www.history.com/news/did-vikings-really-wear-horned-helmets", "history.com"),

    # T43: Knuckle Cracking Arthritis Myth
    ("Knuckle Cracking Arthritis Myth",
     "Cracking your knuckles every day does not cause severe arthritis. Medical studies have found no causal connection between habitual knuckle cracking and osteoarthritis in hands.",
     "https://www.health.harvard.edu/pain/does-knuckle-cracking-cause-arthritis", "health.harvard.edu"),

    # T44: Hair Nails Grow After Death Myth
    ("Hair Nails Grow After Death Myth",
     "Human hair and fingernails do not continue to grow after a person dies. Biological cellular growth stops upon death; the apparent lengthening is an optical illusion caused by the skin dehydrating and shrinking.",
     "https://www.bbc.com/future/article/20130526-do-your-nails-grow-after-death", "bbc.com"),

    # T45: Sugar Hyperactivity Myth
    ("Sugar Hyperactivity Myth",
     "Consuming sugar does not cause children to become hyperactive. Multiple double-blind scientific trials show that sugar intake does not affect children's behavior or attention spans.",
     "https://www.scientificamerican.com/article/busting-the-sugar-rush-myth/", "scientificamerican.com"),

    # T46: Tongue Taste Map Myth
    ("Tongue Taste Map Myth",
     "Different specific parts of the human tongue are not strictly responsible for detecting different tastes. All regions of the tongue with taste buds can sense sweet, salty, sour, bitter, and umami tastes.",
     "https://www.smithsonianmag.com/science-nature/neat-and-tidy-map-tastes-tongue-you-learned-school-all-wrong-180963407/", "smithsonianmag.com"),

    # T47: Ostriches Bury Head Myth
    ("Ostriches Bury Head Myth",
     "Ostriches do not bury their heads in the sand when scared or threatened by a predator. They run away from danger at speeds exceeding 40 mph or lie flat on the ground to blend in with vegetation.",
     "https://www.britannica.com/story/do-ostriches-really-bury-their-heads-in-the-sand", "britannica.com"),

    # T48: Toads Cause Warts Myth
    ("Toads Cause Warts Myth",
     "Touching a toad or a frog does not cause warts to grow on your hands. Human warts are skin infections caused exclusively by the human papillomavirus (HPV), not by amphibians.",
     "https://www.britannica.com/story/do-toads-really-cause-warts", "britannica.com"),

    # T49: Swallowing Spiders in Sleep Myth
    ("Swallowing Spiders in Sleep Myth",
     "Humans do not unknowingly swallow eight live spiders a year while sleeping. Spiders have no reason to crawl into a human mouth and deliberately avoid large sleeping organisms.",
     "https://www.scientificamerican.com/article/fact-or-fiction-people-swallow-8-spiders-a-year-while-sleeping/", "scientificamerican.com")
]

def populate():
def populate():
    print(f"Populating ChromaDB trusted_sources with {len(DOCUMENTS)} reference records...")
    count = 0
    for title, content, url, source in DOCUMENTS:
        ingest_document(title, content, url, source)
        count += 1
    print(f"Successfully ingested {count} documents into ChromaDB! Total count: {_collection.count()}")

if __name__ == "__main__":
    populate()
