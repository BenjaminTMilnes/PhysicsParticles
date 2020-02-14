import os
import json
import re
import math
from decimal import *

context = getcontext()
context.prec = 30

class Measurement (object):
    def __init__(self):
        self.significand = Decimal(0)
        self.exponent = Decimal(0)
        self.unit = ""

    def roundSignificand(self, nsf = 3):
        return  str(roundToNSF( self.significand, nsf))


    def toHTML(self, nsf = 3):
        s = self.roundSignificand(nsf)
        e = str( self.exponent)
        u = self.unit

        if s[0] == "-":
            s = "&minus;" + s[1:]

        if e[0] == "-":
            e = "&minus;" + e[1:]

        if u in ["eV", "keV", "MeV", "GeV", "TeV"]:
            p = u
            u = "eV / <span style=\"font-style: italic;\">c</span><sup>2</sup>"

            if p == "keV":
                u = "k" + u
            elif p == "MeV":
                u = "M" + u
            elif p == "GeV":
                u = "G" + u
            elif p == "TeV":
                u = "T" + u

        if e == "0":
            return "{0} {1}".format(s, u)
        else:
            return "{0} &times; 10<sup>{1}</sup> {2}".format(s, e, u)

    def toLaTeX(self, nsf = 3):
        s = self.roundSignificand(nsf)
        e = str( self.exponent)
        u = self.unit

        if u in ["eV", "keV", "MeV", "GeV", "TeV"]:
            u = "\\mathrm{" + u + "} / c^{2}"
        elif u in ["kg", "u", "C"]:
            u = "\\mathrm{" + u + "}"

        if e == "0":
            return s + " \\, " + u
        else:
            return s + " \\times 10^{" + e + "} \\, " + u

    def toDictionary(self, nsf = 3):
        return {
            "Significand":  self.roundSignificand(nsf),
            "Base": "10",
            "Exponent": str( self.exponent),
              "Unit": self.unit,
            "Rounding": ( "{0}sf".format(nsf) if nsf > 0  else "none"),
            "HTML": self.toHTML( nsf),
            "LaTeX": self.toLaTeX( nsf)
  }

def orderOfMagnitude(n):
    return int(math.floor(float(n.log10())))

def roundToNSF(n, nsf = 3):
    if n == Decimal("0") or nsf == 0:
        return n

    o = orderOfMagnitude(n)

    m = n* Decimal("10") ** Decimal( -o + nsf - 1)
    m = round(m, 0)
    m = m* Decimal("10") ** Decimal( o- nsf + 1)

    return m



class Mass (object):
    def __init__(self):
        self.number = Decimal("0")
        self.unit =""

    @staticmethod
    def fromText(text):

        m = re.match(r"\s*[0]+\s*", text)

        if m:
            mass = Mass()

            mass.number = Decimal("0")
            mass.unit = "kg"

            return mass

        m = re.match(r"\s*([+-]?\d+(\.\d+)?)\s*(\\times|\*)\s*10\^\{([+-]?\d+)\}\s*(g|kg|u|eV|keV|MeV|GeV|TeV)\s*", text)

        if m:
            s = m.group(1)
            e = m.group(4)
            u = m.group(5)

            mass = Mass()

            mass.number = Decimal(s) * Decimal("10") ** Decimal(e)
            mass.unit = u

            return mass

        return None

    def tokg(self):
        if self.unit == "kg":
            return self
        elif self.unit in ["eV", "keV", "MeV", "GeV", "TeV"]:
            n = self.number * Decimal("1.78266192") * Decimal("10") ** Decimal("-36")

            if self.unit == "keV":
                n = n *( Decimal("10") **Decimal("3"))
            elif self.unit == "MeV":
                n = n *( Decimal("10") **Decimal("6"))
            elif self.unit == "GeV":
                n = n *( Decimal("10") **Decimal("9"))
            elif self.unit == "TeV":
                n = n *( Decimal("10") **Decimal("10"))

            mass = Mass()

            mass.number = n
            mass.unit = "kg"

            return mass

    def toev(self):
        if self.unit in  ["eV", "keV", "MeV", "GeV", "TeV"]:
            return self

        mkg = self.tokg().number

        if mkg == Decimal(0):
            mass = Mass()

            mass.number = mkg
            mass.unit = "eV"

            return mass

        mev = mkg / ( Decimal("1.78266192") * Decimal(10) ** Decimal(-36))
        o = orderOfMagnitude(mev)

        if o < 3:
            n = mev
            u = "eV"
        elif o >= 3 and o < 6:
            n = mev / Decimal(10**3)
            u = "keV"
        elif o >= 6 and o < 9:
            n = mev / Decimal(10**6)
            u = "MeV"
        elif o >= 9 and o < 12:
            n = mev / Decimal(10**9)
            u = "GeV"
        elif o >= 12:
            n = mev / Decimal(10**12)
            u = "TeV"

        mass = Mass()

        mass.number = n
        mass.unit = u

        return mass

    def tou(self):
        if self.unit == "u":
            return self

        mkg = self.tokg().number

        if mkg == Decimal(0):
            mass = Mass()

            mass.number = mkg
            mass.unit = "u"

            return mass

        mu = mkg / (  Decimal("1.66053906660") * Decimal(10) ** Decimal(-27))
     
        mass = Mass()

        mass.number = mu
        mass.unit = "u"

        return mass

    def toMeasurement(self):
        s = self.number

        if s == Decimal("0"):
            m = Measurement()

            m.significand = s
            m.exponent = Decimal("0")
            m.unit = self.unit

            return m
        
        else:
            o = orderOfMagnitude(s)
            e = Decimal("0")

            if o > 3 or o < -1:
                s = s / ( Decimal("10") ** Decimal(o))
                e = o

            m = Measurement()

            m.significand = s
            m.exponent = e
            m.unit = self.unit

            return m

    def toDictionary(self):
        return [ self.tokg().toMeasurement().toDictionary(),
        self.toev().toMeasurement().toDictionary(),
        self.tou().toMeasurement().toDictionary(),
        ]

class Compiler (object):

    def getParticleFilePaths(self):
        filePaths = []

        for a in os.listdir("../data"):
            if a.endswith(".particle"):
                filePaths.append( os.path.join("../data", a))

        return filePaths

    def compileParticle(self, filePath):

        with open(filePath, "r") as fileObject:
            lines = fileObject.readlines()
            lines = [l.strip() for l in lines if l.strip() != ""]

            particle = {}

            particle["Reference"] = lines[0]
            particle["URLReference"] = particle["Reference"].lower()
            particle["URL"] = particle["URLReference"]
            particle["Name"] = lines[1]
            particle["MainSymbol"] = lines[2]
            particle["Symbol"] = lines[3]
            particle["Classes"] = [c.strip() for c in  lines[4].split(",")]
            particle["Antiparticle"] = {}
            particle["Antiparticle"]["Reference"] = ""

            lines = lines[5:]

            for line in lines:                   
                if line.startswith("other names:"):
                    particle["OtherNames"] = [n.strip() for n in line[12:].strip().split(",")]

                if line.startswith("mass:"):
                    particle["Mass"] = Mass.fromText( line[5:].strip()).toDictionary()

                if line.startswith("relative charge:"):
                    particle["RelativeCharge"] = line[16:].strip()

                    c = particle["RelativeCharge"]
                    f=0

                    if c == "+1":
                        f=1
                    if c == "+2/3":
                        f=2/3
                    if c == "+1/3":
                        f=1/3
                    if c == "0":
                        f=0
                    if c == "-1/3":
                        f=-1/3
                    if c == "-2/3":
                        f=-2/3
                    if c == "-1":
                        f=-1

                    charge = Decimal(f) * Decimal("1.602176634e-19")

                    if charge == Decimal(0):
                        o = 0
                        s = 0
                    else:
                        o =  int( math.floor(float( abs( charge).log10())))
                        s = charge * Decimal(10) ** Decimal(-o)

                    particle["Charge"] = {"Significand": str( s), "Exponent": o, "UnitClass":"C", "UnitsLaTeX":"C", "UnitsHTML": "C"}

                if line.startswith("spin:"):
                    particle["Spin"] = line[5:].strip()
            
                if line.startswith("magnetic moment:"):
                    particle["MagneticMoment"] = line[16:].strip()
        
                if line.startswith("antiparticle:"):
                    particle["Antiparticle"]["Reference"] = line[13:].strip()
    
                if line.startswith("mean lifetime:"):
                    particle["MeanLifetime"] = line[14:].strip()

                if line.startswith("year theorised:"):
                    particle["YearTheorised"] = line[15:].strip()

                if line.startswith("theorised by:"):
                    particle["TheorisedBy"] = line[13:].strip()

                if line.startswith("year discovered:"):
                    particle["YearDiscovered"] = line[16:].strip()

                if line.startswith("discovered by:"):
                    particle["DiscoveredBy"] = line[14:].strip()
                    
                if line.startswith("wikipedia:"):
                    particle["WikipediaURL"] = line[10:].strip()
                
            return particle

    def convertLaTeXToHTML(self, latex):

        html = latex
        html = re.sub(r"\\times", "&times;", html)
        html = re.sub(r"-(\d)", r"&minus;\g<1>", html)
        html = re.sub(r"\\mu", r"&mu;", html)
        html = re.sub(r"\^\{(.+)\}", r"<sup>\g<1></sup>", html)
        html = re.sub(r"_\{(.+)\}", r"<sub>\g<1></sub>", html)

        return html

    def compile(self):

        particleFilePaths = self.getParticleFilePaths()

        particles = [self.compileParticle(filePath) for filePath in particleFilePaths]

        for particle in particles:
            antiparticles = [p for p in particles if p["Reference"] == particle["Antiparticle"]["Reference"]]

            if len(antiparticles) > 0:
                particle["Antiparticle"]["Name"] = antiparticles[0]["Name"]
                particle["Antiparticle"]["URLReference"] = antiparticles[0]["URLReference"]
            else:
                particle["Antiparticle"]["Name"] =""
                particle["Antiparticle"]["URLReference"] = ""


        data = {}

        data["Particles"] = particles

        print(data)

        def decimal_default(o):
            if isinstance(o, Decimal):
                return str(o)
            raise TypeError()

        with open("../data/Compiled.json", "w") as  fileObject:
            json.dump(data, fileObject, indent = 4, default=decimal_default)

        with open("../web/particles.json", "w") as  fileObject:
            json.dump(data, fileObject, indent = 4, default=decimal_default)


if __name__ == "__main__":
    compiler = Compiler()

    compiler.compile()