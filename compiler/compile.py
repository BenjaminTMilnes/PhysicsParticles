import os
import json
import re
import math
from decimal import *

class Measurement (object):
    def __init__(self):
        self.significand = Decimal(0)
        self.exponent = Decimal(0)
        self.unit = ""

    def toHTML(self):
        s = str( self.significand)
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

        return "{0} &times; 10<sup>{1}</sup> {2}".format(s, e, u)

    def toLaTeX(self):
        s = str( self.significand)
        e = str( self.exponent)
        u = self.unit

        if u in ["eV", "keV", "MeV", "GeV", "TeV"]:
            u = "\\mathrm{" + u + "} / c^{2}"
        elif u in ["kg", "u", "C"]:
            u = "\\mathrm{" + u + "}"

        return "{0} \\times 10^{{1}} \\, {2}".format(s, e, u)

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

            lines = lines[5:]

            for line in lines:                   
                if line.startswith("other names:"):
                    particle["OtherNames"] = line[12:].strip()

                if line.startswith("mass:"):
                    particle["Mass"] = []

                    mass = line[5:].strip()

                    match = re.match(r"\s*([+-]?\d+(\.\d+)?)\s*\\times\s*10\^\{([+-]?\d+)\}\s*kg\s*", mass)

                    if match:
                        significand = match.group(1)
                        exponent = match.group(3)
                        units = "kg"
                        latex = match.group(0).strip()
                        html = "{0} &times; 10<sup>{1}</sup> kg".format(significand, exponent)

                        particle["Mass"].append({"Significand": significand, "Exponent": exponent, "UnitClass":"kg", "UnitsLaTeX":"\\mathrm{kg}", "UnitsHTML":"kg"})

                        mkg = Decimal(significand) * Decimal(10) ** Decimal(exponent)
                        evc2 =   Decimal("1.78266192") * Decimal(10) ** Decimal("-36")
                        mevc2 = mkg / evc2

                        o =  int( math.floor(float( mevc2.log10())))

                        unitsLaTeX = "\\frac{eV}{c^{2}}"
                        unitsHTML = "eV / <span style=\"font-style: italic;\">c</span><sup>2</sup>"

                        if o >= 3 and o < 6:
                            unitsLaTeX = "\\frac{keV}{c^{2}}"
                            unitsHTML = "k" + unitsHTML
                            mevc2 = mevc2 / Decimal(10**3)
                            
                        if o >= 6 and o < 9:
                            unitsLaTeX = "\\frac{MeV}{c^{2}}"
                            unitsHTML = "M" + unitsHTML
                            mevc2 = mevc2 / Decimal(10**6)
                            
                        if o >= 9 and o < 12:
                            unitsLaTeX = "\\frac{GeV}{c^{2}}"
                            unitsHTML = "G" + unitsHTML
                            mevc2 = mevc2 / Decimal(10**9)
                            
                        if o >= 12:
                            unitsLaTeX = "\\frac{TeV}{c^{2}}"
                            unitsHTML = "T" + unitsHTML
                            mevc2 = mevc2 / Decimal(10**12)

                        
                        particle["Mass"].append({"Significand": str(mevc2), "Exponent": "0", "UnitClass":"eV", "UnitsLaTeX": unitsLaTeX, "UnitsHTML": unitsHTML})



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
                    particle["Antiparticle"] = {}
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

        with open("../data/Compiled.json", "w") as  fileObject:
            json.dump(data, fileObject, indent = 4)

        with open("../web/particles.json", "w") as  fileObject:
            json.dump(data, fileObject, indent = 4)


if __name__ == "__main__":
    compiler = Compiler()

    compiler.compile()