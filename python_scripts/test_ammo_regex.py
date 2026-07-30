import re

def test():
    # RG42 pattern
    rg42_pattern = r'(?:(?:ручна\s*)?гранат[аи]?\s*[-–—]*)?(?:rg|рг|pg|пг|рg|pг)[\s\-_]*42'
    
    # AT4 pattern
    at4_pattern = r'(?:(?:рпг|гранатомет)[\s\-_]*)?(?:ат|at)[\s\-]*4(?:[\s\-]*(?:cs|кс|сs|сз)[-_\s]*(?:rs|рс))?'

    sep = r'[\s\-–—:=./;\\x5c]*'
    unit = r'(?:[\s\-]*[\-\\/\\s]*шт\.?|щт\.?|штук[и]?|гранат[аи]?|грн)?'
    num_prefix = r'(?<![a-zA-Zа-яА-ЯіІїЇєЄґҐ_])'

    # ammoFirst: ammo + sep + num + unit
    ammo_first_rg42 = re.compile(rf'(?:{rg42_pattern}){sep}{num_prefix}(\d+)\s*{unit}', re.IGNORECASE)
    
    # numFirst: num + unit + sep + ammo
    num_first_at4 = re.compile(rf'{num_prefix}(\d+)\s*{unit}{sep}(?:{at4_pattern})', re.IGNORECASE)

    t1 = "PG-42- 2 шт"
    m1 = ammo_first_rg42.search(t1)
    print("t1 match:", m1.group(0), "qty:", m1.group(1) if m1 else "NONE")

    t2 = "граната РG-42-1 шт"
    m2 = ammo_first_rg42.search(t2)
    print("t2 match:", m2.group(0), "qty:", m2.group(1) if m2 else "NONE")

    t3 = "1шт-РПГ AT4CS-RS"
    m3 = num_first_at4.search(t3)
    print("t3 match:", m3.group(0), "qty:", m3.group(1) if m3 else "NONE")

if __name__ == '__main__':
    test()
