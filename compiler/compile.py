import os
import json
import re
import math
from decimal import *

context = getcontext()
context.prec = 12


zero = Decimal("0")
e1 = Decimal("10")
e3 = Decimal("10") ** Decimal("3")
e6 = Decimal("10") ** Decimal("6")
e9 = Decimal("10") ** Decimal("9")
e12 = Decimal("10") ** Decimal("12")
evcc = Decimal("1.78266192e-36")
ec = Decimal("1.602176634e-19")


def orderOfMagnitude(n):
    return int(math.floor(float(abs(n).log10())))


def powerOf10(e):
    return e1 ** Decimal(e)


def roundToNSF(n, nsf=3):
    if n == zero or nsf == 0:
        return n

    o = orderOfMagnitude(n)
    p = -o + nsf - 1

    m = n * powerOf10(p)
    m = round(m, 0)
    m = m * powerOf10(-p)

    return m


class Measurement (object):
    def __init__(self, significand, exponent, unit):
        self.significand = significand
        self.exponent = exponent
        self.unit = unit

    def roundSignificand(self, nsf=3):
        return str(roundToNSF(self.significand, nsf))

    def toHTML(self, nsf=3):
        s = self.roundSignificand(nsf)
        e = str(self.exponent)
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
        elif u == "\\mu_{B}":
            u = "&mu;<sub>B</sub>"

        if s == "0":
            return "{0}".format(s)
        elif e == "0":
            return "{0} {1}".format(s, u)
        else:
            return "{0} &times; 10<sup>{1}</sup> {2}".format(s, e, u)

    def toLaTeX(self, nsf=3):
        s = self.roundSignificand(nsf)
        e = str(self.exponent)
        u = self.unit

        if u in ["eV", "keV", "MeV", "GeV", "TeV"]:
            u = "\\mathrm{" + u + "} / c^{2}"
        elif u in ["kg", "u", "C"]:
            u = "\\mathrm{" + u + "}"

        if e == "0":
            return s + " \\, " + u
        else:
            return s + " \\times 10^{" + e + "} \\, " + u

    @property
    def unitClass(self):
        if self.unit in ["eV", "keV", "MeV", "GeV", "TeV"]:
            return "eV"

        return self.unit

    def toDictionary(self, nsf=3):
        return {
            "Significand":  self.roundSignificand(nsf),
            "Base": "10",
            "Exponent": str(self.exponent),
            "Unit": self.unit,
            "UnitClass": self.unitClass,
            "Rounding": ("{0}sf".format(nsf) if nsf > 0 else "none"),
            "HTML": self.toHTML(nsf),
            "LaTeX": self.toLaTeX(nsf)
        }


class Mass (object):
    def __init__(self, number, unit):
        self.number = number
        self.unit = unit

    @staticmethod
    def fromText(text):
        m = re.match(r"\s*[0]+\s*", text)

        if m:
            return Mass(zero, "kg")

        m = re.match(r"\s*([+-]?\d+(\.\d+)?)\s*(\\times|\*)\s*10\^\{([+-]?\d+)\}\s*(g|kg|u|eV|keV|MeV|GeV|TeV)\s*", text)

        if m:
            s = m.group(1)
            e = m.group(4)
            u = m.group(5)

            return Mass(Decimal(s) * e1 ** Decimal(e), u)

        return None

    def tokg(self):
        if self.unit == "kg":
            return self
        elif self.unit in ["eV", "keV", "MeV", "GeV", "TeV"]:
            n = self.number * evcc

            if self.unit == "keV":
                n = n * e3
            elif self.unit == "MeV":
                n = n * e6
            elif self.unit == "GeV":
                n = n * e9
            elif self.unit == "TeV":
                n = n * e12

            return Mass(n, "kg")

    def toev(self):
        if self.unit in ["eV", "keV", "MeV", "GeV", "TeV"]:
            return self

        mkg = self.tokg().number

        if mkg == zero:
            return Mass(mkg, "eV")

        mev = mkg / evcc
        o = orderOfMagnitude(mev)

        if o < 3:
            n = mev
            u = "eV"
        elif o >= 3 and o < 6:
            n = mev / e3
            u = "keV"
        elif o >= 6 and o < 9:
            n = mev / e6
            u = "MeV"
        elif o >= 9 and o < 12:
            n = mev / e9
            u = "GeV"
        elif o >= 12:
            n = mev / e12
            u = "TeV"

        return Mass(n, u)

    def tou(self):
        if self.unit == "u":
            return self

        mkg = self.tokg().number

        if mkg == zero:
            return Mass(mkg, "u")

        mu = mkg / (Decimal("1.66053906660") * Decimal("10") ** Decimal("-27"))

        return Mass(mu, "u")

    def toMeasurement(self):
        s = self.number

        if s == zero:
            return Measurement(s, zero, self.unit)
        else:
            o = orderOfMagnitude(s)
            e = zero

            if o > 3 or o < -1:
                s = s / powerOf10(o)
                e = o

            return Measurement(s, e, self.unit)

    def toDictionary(self):
        return [self.tokg().toMeasurement().toDictionary(0),
                self.tokg().toMeasurement().toDictionary(3),
                self.toev().toMeasurement().toDictionary(0),
                self.toev().toMeasurement().toDictionary(3),
                self.tou().toMeasurement().toDictionary(0),
                self.tou().toMeasurement().toDictionary(3),
                ]


class Charge (object):
    def __init__(self, number, unit):
        self.number = number
        self.unit = unit

    @staticmethod
    def fromText(text):
        m = re.match(r"\s*[0]+\s*", text)

        if m:
            return Charge(zero, "C")

        m = re.match(r"^\s*([+-]?\s*\d+)\s*/\s*(\d+)\s*", text)

        if m:
            n = Decimal(m.group(1))
            d = Decimal(m.group(2))

            return Charge((n/d) * ec, "C")

        m = re.match(r"\s*[+-]?\d+\s*", text)

        if m:
            f = Decimal(text)

            return Charge(f * ec, "C")

        m = re.match(r"\s*([+-]?\d+(\.\d+)?)\s*(\\times|\*)\s*10\^\{([+-]?\d+)\}\s*(C)\s*", text)

        if m:
            s = m.group(1)
            e = m.group(4)
            u = m.group(5)

            return Charge(Decimal(s) * e1 ** Decimal(e), u)

        return None

    def toMeasurement(self):
        s = self.number

        if s == zero:
            return Measurement(s, zero, self.unit)
        else:
            o = orderOfMagnitude(s)
            e = zero

            if o > 3 or o < -1:
                s = s / powerOf10(o)
                e = o

            return Measurement(s, e, self.unit)

    def toDictionary(self):
        return [self.toMeasurement().toDictionary(0),
                self.toMeasurement().toDictionary(3),
                ]


class Time (object):
    def __init__(self, number, unit):
        self.number = number
        self.unit = unit

    @staticmethod
    def fromText(text):
        m = re.match(r"\s*[0]+\s*", text)

        if m:
            return Time(zero, "C")

        m = re.match(r"\s*([+-]?\d+(\.\d+)?)\s*(\\times|\*)\s*10\^\{([+-]?\d+)\}\s*(s)\s*", text)

        if m:
            s = m.group(1)
            e = m.group(4)
            u = m.group(5)

            return Time(Decimal(s) * e1 ** Decimal(e), u)

        return None

    def toMeasurement(self):
        s = self.number

        if s == zero:
            return Measurement(s, zero, self.unit)
        else:
            o = orderOfMagnitude(s)
            e = zero

            if o > 3 or o < -1:
                s = s / powerOf10(o)
                e = o

            return Measurement(s, e, self.unit)

    def toDictionary(self):
        return [self.toMeasurement().toDictionary(0),
                self.toMeasurement().toDictionary(3),
                ]


class MagneticMoment (object):
    def __init__(self, number, unit):
        self.number = number
        self.unit = unit

    @staticmethod
    def fromText(text):
        m = re.match(r"\s*[0]+\s*", text)

        if m:
            return MagneticMoment(zero, "\mu_{B}")

        m = re.match(r"\s*([+-]?\d+(\.\d+)?)\s*((\\times|\*)\s*10\^\{([+-]?\d+)\})?\s*(\\mu_\{B\})\s*", text)

        if m:
            s = m.group(1)
            u = m.group(6)

            return MagneticMoment(Decimal(s), u)

        return None

    def toMeasurement(self):
        s = self.number

        if s == zero:
            return Measurement(s, zero, self.unit)
        else:
            o = orderOfMagnitude(s)
            e = zero

            if o > 3 or o < -1:
                s = s / powerOf10(o)
                e = o

            return Measurement(s, e, self.unit)

    def toDictionary(self):
        return [self.toMeasurement().toDictionary(0),
                self.toMeasurement().toDictionary(3),
                ]


class Compiler (object):

    def getParticleFilePaths(self):
        filePaths = []

        for a in os.listdir("../data"):
            if a.endswith(".particle"):
                filePaths.append(os.path.join("../data", a))

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
            particle["Classes"] = [c.strip() for c in lines[4].split(",")]
            particle["Antiparticle"] = {}
            particle["Antiparticle"]["Reference"] = ""

            lines = lines[5:]

            for line in lines:
                if line.startswith("other names:"):
                    particle["OtherNames"] = [n.strip() for n in line[12:].strip().split(",")]

                if line.startswith("status:"):
                    particle["Status"] = line[7:].strip()

                if line.startswith("composition:"):
                    particle["Composition"] = line[12:].strip()

                if line.startswith("mass:"):
                    mass = Mass.fromText(line[5:].strip())

                    if mass != None:
                        if mass == zero:
                            particle["Mass"] = "0"
                        else:
                            particle["Mass"] = mass.toDictionary()
                    else:
                        particle["Mass"] = line[5:].strip()

                if line.startswith("relative charge:"):
                    particle["RelativeCharge"] = line[16:].strip()
                    charge =  Charge.fromText(line[16:].strip())

                    if charge.number == zero:
                        particle["Charge"] = "0"
                    else:
                        particle["Charge"] = charge.toDictionary()

                if line.startswith("spin:"):
                    particle["Spin"] = line[5:].strip()
                    
                if line.startswith("isospin:"):
                    particle["Isospin"] = line[8:].strip()

                if line.startswith("magnetic moment:"):
                    particle["MagneticMoment"] = MagneticMoment.fromText(line[16:].strip()).toDictionary()

                if line.startswith("antiparticle:"):
                    particle["Antiparticle"]["Reference"] = line[13:].strip()

                if line.startswith("generation:"):
                    particle["Generation"] = line[11:].strip()

                if line.startswith("monte carlo particle number:"):
                    particle["MonteCarloParticleNumber"] = line[28:].strip()

                if line.startswith("mean lifetime:"):
                    t = line[14:].strip()

                    if t == "stable":
                        particle["MeanLifetime"] = t
                    else:
                        particle["MeanLifetime"] = Time.fromText(t).toDictionary()

                if line.startswith("upness:"):
                    particle["Upness"] = line[7:].strip()

                if line.startswith("downness:"):
                    particle["Downness"] = line[9:].strip()

                if line.startswith("charm:"):
                    particle["Charm"] = line[6:].strip()

                if line.startswith("strangeness:"):
                    particle["Strangeness"] = line[12:].strip()

                if line.startswith("topness:"):
                    particle["Topness"] = line[8:].strip()

                if line.startswith("bottomness:"):
                    particle["Bottomness"] = line[11:].strip()

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

                if line.startswith("hyperphysics:"):
                    particle["HyperphysicsURL"] = line[13:].strip()

            return particle

    def compile(self):

        particleFilePaths = self.getParticleFilePaths()

        particles = [self.compileParticle(filePath) for filePath in particleFilePaths]

        for particle in particles:
            antiparticles = [p for p in particles if p["Reference"] == particle["Antiparticle"]["Reference"]]

            if len(antiparticles) > 0:
                particle["Antiparticle"]["Name"] = antiparticles[0]["Name"]
                particle["Antiparticle"]["URLReference"] = antiparticles[0]["URLReference"]
            else:
                particle["Antiparticle"]["Name"] = ""
                particle["Antiparticle"]["URLReference"] = ""

        data = {}

        data["Particles"] = particles

        print(data)

        def decimal_default(o):
            if isinstance(o, Decimal):
                return str(o)
            raise TypeError()

        with open("../data/Compiled.json", "w") as fileObject:
            json.dump(data, fileObject, indent=4, default=decimal_default)

        with open("../web/particles.json", "w") as fileObject:
            json.dump(data, fileObject, indent=4, default=decimal_default)


if __name__ == "__main__":
    compiler = Compiler()

    compiler.compile()
