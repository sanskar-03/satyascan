import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from rag.ingest import ingest_document, _collection

DOCUMENTS_2ND = [
    # E01: Photosynthesis
    ("Photosynthesis Process and Solar Energy Conversion",
     "Photosynthesis is the fundamental biological process by which green plants, algae, and certain bacteria convert sunlight, water, and atmospheric carbon dioxide into chemical energy stored in glucose molecules. During this process, chlorophyll pigments located within plant chloroplasts absorb solar light energy and release oxygen gas as a byproduct into the atmosphere.",
     "https://www.britannica.com/science/photosynthesis", "britannica.com"),

    # E02: DNA Structure
    ("DNA Double Helix Structure and Genetics",
     "Deoxyribonucleic acid, commonly known as DNA, is the hereditary molecule that carries genetic instructions for the development, functioning, growth, and reproduction of all known living organisms. In 1953, James Watson and Francis Crick discovered that DNA forms a double helix structure composed of two antiparallel strands of four nucleotide bases.",
     "https://www.nature.com/scitable/topicpage/discovery-of-dna-structure-and-function-392/", "nature.com"),

    # E03: Plate Tectonics
    ("Plate Tectonics and Earth Lithosphere Dynamics",
     "The theory of plate tectonics describes the large-scale motions of Earth's lithosphere, which is divided into several major and minor rigid tectonic plates. These continental and oceanic plates float atop the semi-fluid asthenosphere beneath them, and their constant interactions along fault boundaries generate seismic earthquakes, oceanic trenches, and volcanic activity across the globe.",
     "https://www.usgs.gov/programs/earthquake-hazards/science/plate-tectonics", "usgs.gov"),

    # E04: Moon Orbit
    ("Moon Orbit Distance and Tidal Locking",
     "The Moon orbits planet Earth at an average orbital distance of approximately 384,400 kilometers in an elliptical path. Because the Moon is gravitationally tidally locked to Earth in synchronous rotation, it rotates on its axis in the exact same time it takes to orbit Earth, always presenting the same face to us.",
     "https://www.nasa.gov/moon-facts/", "nasa.gov"),

    # E05: Great Barrier Reef
    ("Great Barrier Reef Marine Ecosystem",
     "The Great Barrier Reef is the world's largest coral reef ecosystem, located in the Coral Sea off the northeastern coast of Queensland, Australia. Stretching over 2,300 kilometers across an area of approximately 344,400 square kilometers, it is composed of over 2,900 individual reefs and can even be seen from space.",
     "https://www.britannica.com/place/Great-Barrier-Reef", "britannica.com"),

    # E06: Periodic Table
    ("Periodic Table Dmitri Mendeleev Formulation",
     "Russian chemist Dmitri Mendeleev formulated the periodic law and published the first widely recognized periodic table of chemical elements in 1869. Mendeleev arranged the known elements in order of increasing atomic mass and discovered recurring chemical properties, remarkably predicting the properties of several undiscovered elements that were later discovered by scientists.",
     "https://www.britannica.com/biography/Dmitri-Mendeleev", "britannica.com"),

    # E07: Antibiotic Resistance
    ("Antibiotic Resistance Public Health Overview",
     "Antibiotic resistance occurs when pathogenic bacteria evolve mechanisms that enable them to survive exposure to antibiotics designed to destroy them. The overuse and inappropriate prescription of antibiotic medications in clinical medicine and agriculture has accelerated this biological resistance process, posing a severe public health challenge to healthcare systems around the world.",
     "https://www.cdc.gov/drugresistance/about.html", "cdc.gov"),

    # E08: Human Skeleton
    ("Human Skeleton Bones Count and Development",
     "An adult human skeletal system consists of 206 distinct bones that provide mechanical support, protect fragile internal organs, and enable bodily locomotion. Human infants are actually born with approximately 270 bones at birth, but many of these smaller cartilaginous bones gradually fuse together during growth throughout childhood and adolescence into adulthood.",
     "https://www.britannica.com/science/human-skeleton", "britannica.com"),

    # E09: Lightning and Thunder
    ("Speed Difference Between Lightning and Thunder",
     "During a thunderstorm, an observer will always see a flash of lightning before hearing the sound of thunder. This physical phenomenon occurs because light waves travel through Earth's atmosphere at roughly 300,000 kilometers per second, whereas sound waves propagate through air at a much slower speed of approximately 343 meters per second.",
     "https://www.weather.gov/safety/lightning-science", "weather.gov"),

    # E10: Saturn's Rings
    ("Saturn Planetary Rings Composition",
     "The planet Saturn possesses the most extensive and visible ring system of any planet in our Solar System. These magnificent rings are composed of billions of individual ring particles consisting predominantly of water ice with a trace component of rocky debris, ranging in diameter from micrometers up to several meters in size.",
     "https://www.nasa.gov/saturn-rings/", "nasa.gov"),

    # E11: Isaac Newton
    ("Isaac Newton Principia Mathematica Gravitation",
     "English mathematician and physicist Sir Isaac Newton published his monumental treatise Philosophiæ Naturalis Principia Mathematica in 1687, which formulated the fundamental laws of motion and universal gravitation. Newton's work established classical mechanics and demonstrated that the motions of objects on Earth and celestial bodies are governed by identical physical laws.",
     "https://www.britannica.com/biography/Isaac-Newton", "britannica.com"),

    # E12: Amazon Rainforest
    ("Amazon Rainforest Ecosystem and Biodiversity",
     "The Amazon rainforest is the largest tropical rainforest in the world, covering over five and a half million square kilometers across nine South American nations. The vast Amazon basin accounts for roughly one-fifth of the total river discharge into Earth's oceans and harbors an unrivaled biodiversity of plant and animal species.",
     "https://www.worldwildlife.org/places/amazon", "worldwildlife.org"),

    # E13: Marie Curie
    ("Marie Curie Nobel Prizes Radioactivity",
     "Marie Curie was a pioneering Polish-born naturalized French physicist and chemist who conducted groundbreaking research on radioactivity, a term she personally coined. She discovered two new elements, polonium and radium, and remains the only person to ever win Nobel Prizes in two different scientific fields: Physics in 1903 and Chemistry in 1911.",
     "https://www.nobelprize.org/prizes/physics/1903/marie-curie/biographical/", "nobelprize.org"),

    # E14: Jupiter Planet
    ("Jupiter Gas Giant Planetary Properties",
     "Jupiter is the largest planet in our Solar System and the fifth planet out from the Sun. It is a massive gas giant with a mass more than two and a half times that of all the other planets in the Solar System combined, famous for its Great Red Spot storm.",
     "https://www.nasa.gov/jupiter/", "nasa.gov"),

    # E15: Red Blood Cells
    ("Red Blood Cells Erythrocytes Oxygen Transport",
     "Human red blood cells, or erythrocytes, are the most abundant type of blood cell in the human circulatory system. Their primary biological function is to deliver oxygen to bodily tissues via blood flow, utilizing specialized iron-containing protein molecules known as hemoglobin that bind tightly to oxygen within the capillaries of the lungs.",
     "https://www.hopkinsmedicine.org/health/wellness-and-prevention/what-are-red-blood-cells", "hopkinsmedicine.org"),

    # E16: Panama Canal
    ("Panama Canal Maritime History and Transit",
     "The Panama Canal is an artificial 82-kilometer commercial waterway in Panama that cuts across the Isthmus of Panama to connect the Atlantic Ocean with the Pacific Ocean. Officially opened for maritime transit in August 1914, the canal revolutionized global maritime commerce by allowing ships to avoid the treacherous Cape Horn route.",
     "https://www.britannica.com/topic/Panama-Canal", "britannica.com"),

    # E17: Boiling Point Liquid Nitrogen
    ("Liquid Nitrogen Cryogenic Boiling Point",
     "Liquid nitrogen is nitrogen gas that has been cooled into a cryogenic liquid state at an extremely low temperature. At standard atmospheric pressure at sea level, liquid nitrogen boils at minus 195.79 degrees Celsius, or minus 320 degrees Fahrenheit, making it an invaluable industrial substance used for cryopreservation and scientific cooling applications.",
     "https://www.britannica.com/science/liquid-nitrogen", "britannica.com"),

    # E18: Charles Darwin
    ("Charles Darwin Origin of Species Evolution",
     "English naturalist Charles Darwin published his revolutionary scientific masterwork On the Origin of Species in November 1859. The book introduced the foundational scientific theory that biological populations evolve over generations through a process of natural selection, which became the unifying bedrock of modern evolutionary biology and understanding of the diversity of life.",
     "https://www.britannica.com/biography/Charles-Darwin", "britannica.com"),

    # E19: Dead Sea
    ("Dead Sea Lowest Land Elevation Geographic Profile",
     "The Dead Sea is a landlocked hypersaline salt lake bordered by Jordan to the east and Israel and the West Bank to the west. Its surface and shores lie approximately 430 meters below sea level, officially making it the lowest land elevation point on the entire surface of the planet Earth.",
     "https://www.britannica.com/place/Dead-Sea", "britannica.com"),

    # E20: Mitochondria
    ("Mitochondria Powerhouse of the Cell ATP Production",
     "Mitochondria are membrane-bound cellular organelles found in the cytoplasm of virtually all eukaryotic organisms, commonly referred to as the powerhouses of the cell. They generate the vast majority of the cell's supply of adenosine triphosphate, a complex chemical compound that serves as the primary currency of cellular energy for metabolic functions.",
     "https://www.nature.com/scitable/topicpage/mitochondria-14053590/", "nature.com"),

    # E21: Humans and Dinosaurs Myth
    ("Humans and Dinosaurs Coexistence Myth Fact-Check",
     "Ancient humans did not live alongside or hunt non-avian dinosaurs. Scientific paleontological fossil records conclusively prove that non-avian dinosaurs went completely extinct approximately 66 million years before the earliest modern humans first evolved on Earth.",
     "https://www.usgs.gov/faqs/did-humans-and-dinosaurs-live-together", "usgs.gov"),

    # E22: Blue Blood in Veins Myth
    ("Blue Vein Blood Myth Fact-Check",
     "Human blood is never blue in color inside the human body. Deoxygenated venous blood is dark red, not blue; veins appear bluish through the skin purely due to optical physics and how different wavelengths of light penetrate and scatter through human skin.",
     "https://www.scientificamerican.com/article/why-does-deoxygenated-blood-appear-blue/", "scientificamerican.com"),

    # E23: Chewing Gum 7 Years Myth
    ("Swallowed Chewing Gum Digestive Myth Fact-Check",
     "Swallowed chewing gum does not remain in the human digestive system or stomach for seven years. While gum base cannot be digested by stomach acids, it passes smoothly through the digestive tract and is excreted within several days, just like insoluble dietary fiber.",
     "https://www.hopkinsmedicine.org/health/wellness-and-prevention/swallowing-gum-facts", "hopkinsmedicine.org"),

    # E24: Shaving Thicker Hair Myth
    ("Shaving Hair Thickness Growth Myth Fact-Check",
     "Shaving hair does not cause it to grow back thicker, coarser, or darker. Shaving merely cuts the hair shaft at the skin's surface with a blunt end, which makes it feel temporarily coarse as it emerges, but has zero effect on the hair follicle underneath.",
     "https://www.mayoclinic.org/healthy-lifestyle/adult-health/expert-answers/hair-removal/faq-20058427", "mayoclinic.org"),

    # E25: Bermuda Triangle Myth
    ("Bermuda Triangle Disappearance Rates Myth Fact-Check",
     "The Bermuda Triangle does not experience a statistically higher rate of ship or aircraft disappearances than any other heavily traveled ocean region. Extensive statistical analyses by the US Coast Guard and maritime insurers show disappearance rates are entirely normal.",
     "https://oceanservice.noaa.gov/facts/bermudatriangle.html", "noaa.gov"),

    # E26: Coffee Stunts Growth Myth
    ("Caffeine Stunting Child Growth Myth Fact-Check",
     "Drinking coffee or caffeine does not stunt child growth or cause bones to stop growing. Rigorous pediatric health studies demonstrate that moderate caffeine intake has no measurable causal link to bone density loss or impaired longitudinal height development.",
     "https://www.health.harvard.edu/staying-healthy/can-coffee-stunt-growth", "health.harvard.edu"),

    # E27: Reading in Dim Light Myth
    ("Reading in Dim Light Eye Damage Myth Fact-Check",
     "Reading in dim light does not cause permanent or irreversible damage to eyesight or the human eye. While reading in low light can cause temporary eyestrain, squinting, or fatigue, ophthalmologists confirm it does not damage optical anatomy or degrade visual acuity.",
     "https://www.aao.org/eye-health/ask-ophthalmologist-q/reading-in-the-dark", "aao.org"),

    # E28: Edison Invented Light Bulb Myth
    ("Thomas Edison Light Bulb Invention Myth Fact-Check",
     "Thomas Edison did not invent the very first electric incandescent light bulb from scratch. Dozens of earlier inventors, including Humphry Davy, Warren de la Rue, and Joseph Swan, had already patented and built working electric incandescent lamps decades before Edison improved the design.",
     "https://www.britannica.com/biography/Thomas-Edison", "britannica.com"),

    # E29: Sitting Close to TV Myth
    ("Sitting Close to TV Vision Damage Myth Fact-Check",
     "Sitting close to a television set does not cause permanent eye damage or ruin your vision. Modern televisions emit no harmful ionizing radiation; while sitting close can cause mild temporary eye fatigue, medical studies confirm it does not permanently degrade visual health.",
     "https://www.scientificamerican.com/article/earth-talk-tv-eyesight/", "scientificamerican.com"),

    # E30: Body Heat Through Head Myth
    ("Body Heat Loss Through Head Myth Fact-Check",
     "The human body loses only 7 to 10 percent of body heat through the head. Heat loss is strictly proportional to exposed body surface area, meaning the head accounts for only about 7 to 10 percent of total heat loss.",
     "https://www.bmj.com/content/337/bmj.a2769", "bmj.com"),

    # E31: Rust Causes Tetanus Myth
    ("Rust Causes Tetanus Infection Myth Fact-Check",
     "Rust on metal does not directly cause tetanus infections. Tetanus is caused by the bacterium Clostridium tetani, which thrives in anaerobic environments like soil, dust, and animal feces; a puncture wound from a rusty nail causes infection only if the bacterial spores are present.",
     "https://www.cdc.gov/tetanus/about/causes.html", "cdc.gov"),

    # E32: Mentos Diet Coke Toxic Gas Myth
    ("Mentos and Diet Coke Toxic Gas Myth Fact-Check",
     "Dropping Mentos into diet soda does not create a chemical reaction or produce toxic poisonous gas. The eruption is a purely physical phenomenon called nucleation, where microscopic pits on the candy surface allow dissolved carbon dioxide gas to rapidly form bubbles and erupt harmlessly.",
     "https://www.scientificamerican.com/article/bring-science-home-coke-mentos/", "scientificamerican.com"),

    # E33: Raw Rice Explodes Birds Myth
    ("Raw Rice Exploding Birds Myth Fact-Check",
     "Feeding raw rice to birds does not cause their stomachs to expand or explode. Many species of wild birds consume raw agricultural grains and rice safely in nature without any digestive harm, as avian stomachs easily grind and digest dry grains.",
     "https://www.audubon.org/news/did-you-know-eating-rice-makes-birds-explode", "audubon.org"),

    # E34: Einstein Relativity Nobel Myth
    ("Albert Einstein Nobel Prize Citation Fact-Check",
     "Albert Einstein was not awarded the 1921 Nobel Prize in Physics for his Theory of General Relativity. Einstein was awarded the 1921 Nobel Prize specifically for his discovery of the law of the photoelectric effect, as general relativity was still considered controversial by the Nobel Committee.",
     "https://www.nobelprize.org/prizes/physics/1921/summary/", "nobelprize.org"),

    # E35: Bananas Grow on Trees Myth
    ("Banana Plant Tree Myth Fact-Check",
     "Bananas do not grow on woody trees with wooden trunks. The banana plant is technically a giant perennial arborescent herb, and what resembles a wooden tree trunk is actually a pseudostem composed of tightly wrapped overlapping leaf sheaths with no woody tissue.",
     "https://www.britannica.com/plant/banana-plant", "britannica.com"),

    # E36: Glass is Slow Liquid Myth
    ("Glass is Liquid Cathedral Myth Fact-Check",
     "Window glass is not a slow-flowing liquid that flows downward over centuries. Glass is an amorphous solid that does not flow at room temperature; the uneven thickness observed in medieval church windows was simply the result of early glassmakers' inability to make completely uniform flat panes.",
     "https://www.scientificamerican.com/article/fact-fiction-glass-liquid/", "scientificamerican.com"),

    # E37: Baby Birds Human Scent Myth
    ("Touching Baby Bird Human Scent Myth Fact-Check",
     "Touching a baby bird will not cause the parent bird to abandon it due to human scent. The vast majority of bird species have a very limited and poorly developed sense of smell and cannot detect human scent, continuing to care for chicks returned to their nests.",
     "https://www.scientificamerican.com/article/fact-or-fiction-birds-abandon-young-at-human-touch/", "scientificamerican.com"),

    # E38: Alcohol Brain Cells Myth
    ("Alcohol Kills Brain Cells Myth Fact-Check",
     "Drinking alcohol does not physically kill brain cells on contact. Medical research demonstrates that even heavy alcohol consumption damages dendrite connections and communication between neurons, but does not actually cause widespread death of brain neurons.",
     "https://www.scientificamerican.com/article/does-alcohol-kill-brain-c/", "scientificamerican.com"),

    # E39: Mount Everest Closest to Space Myth
    ("Mount Everest Closest to Space Myth Fact-Check",
     "The summit of Mount Everest is not the closest place on Earth's surface to outer space. Because Earth is an oblate spheroid with a pronounced equatorial bulge, the summit of Mount Chimborazo in Ecuador is the farthest terrestrial point from Earth's center and closest to space.",
     "https://oceanservice.noaa.gov/facts/highestpoint.html", "noaa.gov"),

    # E40: Microwaves Radioactive Food Myth
    ("Microwave Oven Radioactive Food Myth Fact-Check",
     "Microwave ovens do not use nuclear radiation or make food radioactive. Microwaves produce non-ionizing electromagnetic radiation that causes polar water molecules within food to vibrate and generate thermal heat, without altering atomic nuclei or leaving behind any radiation.",
     "https://www.fda.gov/radiation-emitting-products/resources-you-radiation-emitting-products/microwave-ovens", "fda.gov")
]

def populate_2nd():
    print(f"Populating ChromaDB with {len(DOCUMENTS_2ND)} 2nd evaluation reference records...")
    count = 0
    for title, content, url, source in DOCUMENTS_2ND:
        ingest_document(title, content, url, source)
        count += 1
    print(f"Successfully ingested {count} documents! ChromaDB total count: {_collection.count()}")

if __name__ == "__main__":
    populate_2nd()
