import os
import json
import re

class MeasuredValue (object):
    def __init__(self, significand = 0, exponent = 0, units = ""):
        self.significand = significand
        self.exponent = exponent
        self.units = units

    @staticmethod
    def fromText(text):
        match = re.match("([+-]?[\d\.]+)\s*\\times\s*10\^\{([+-]?\d+)\}\s*(kg|s)")

        if match:
            value = MeasuredValue()

            value.significand = float(match.group(1))
            value.exponent = float(match.group(2))
            value.units = match.group(3)

            return value

        return None

    def toHTML(self):
        pass

class Compiler (object):
    def __init__(self):
        pass

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
            particle["Symbol"] = lines[2]
            particle["Classes"] = [c.strip() for c in  lines[3].split(",")]

            lines = lines[4:]

            for line in lines:                   
                if line.startswith("other names:"):
                    particle["OtherNames"] = line[12:].strip()

                if line.startswith("mass:"):
                    particle["Mass"] = line[5:].strip()

                if line.startswith("relative charge:"):
                    particle["RelativeCharge"] = line[16:].strip()
                    
                if line.startswith("spin:"):
                    particle["Spin"] = line[5:].strip()
            
                if line.startswith("magnetic moment:"):
                    particle["MagneticMoment"] = line[16:].strip()
        
                if line.startswith("antiparticle:"):
                    particle["AntiparticleReference"] = line[13:].strip()
    
                if line.startswith("mean lifetime:"):
                    particle["MeanLifetime"] = line[14:].strip()

                if line.startswith("year discovered:"):
                    particle["YearDiscovered"] = line[16:].strip()

                if line.startswith("discovered by:"):
                    particle["DiscoveredBy"] = line[14:].strip()
                    
                if line.startswith("wikipedia:"):
                    particle["WikipediaURL"] = line[10:].strip()
                    
                if line.startswith("colour:"):
                    particle["BackgroundColour"] = line[7:].strip().split(",")[0].strip()
                    particle["BorderColour"] = line[7:].strip().split(",")[1].strip()

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
            antiparticles = [p for p in particles if p["Reference"] == particle["AntiparticleReference"]]

            if len(antiparticles) > 0:
                particle["Antiparticle"] = {}
                particle["Antiparticle"]["Name"] = antiparticles[0]["Name"]
                particle["Antiparticle"]["URL"] = antiparticles[0]["URL"]
            else:
                particle["Antiparticle"] = {}
                particle["Antiparticle"]["Name"] =""
                particle["Antiparticle"]["URL"] = ""


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