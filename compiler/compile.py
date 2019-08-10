import os
import json

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
            particle["Name"] = lines[1]
            particle["Symbol"] = lines[2]
            particle["Classes"] = [c.strip() for c in  lines[3].split(",")]

            lines = lines[4:]

            for line in lines:                
                if line.startswith("mass:"):
                    particle["Mass"] = line[5:].strip()

                if line.startswith("relative charge:"):
                    particle["RelativeCharge"] = line[16:].strip()
                    
                if line.startswith("spin:"):
                    particle["Spin"] = line[5:].strip()
            
                if line.startswith("magnetic moment:"):
                    particle["MagneticMoment"] = line[16:].strip()
        
                if line.startswith("antiparticle:"):
                    particle["Antiparticle"] = line[13:].strip()
    
                if line.startswith("mean lifetime:"):
                    particle["MeanLifetime"] = line[14:].strip()

                if line.startswith("year discovered:"):
                    particle["YearDiscovered"] = line[16:].strip()

                if line.startswith("discovered by:"):
                    particle["DiscoveredBy"] = line[14:].strip()
                    
                if line.startswith("wikipedia:"):
                    particle["WikipediaURL"] = line[10:].strip()

            return particle

    def removeParticlePages(self):

        if not os.path.isdir("../web/particles"):
            os.mkdir("../web/particles")

        for a in os.listdir("../web/particles"):
            os.remove(os.path.join("../web/particles", a))

    def makeParticlePage(self, template, particle):

        page = template

        page = page.replace("[Name]", particle["Name"])
        page = page.replace("[RelativeCharge]", particle["RelativeCharge"])

        with open(os.path.join("../web/particles", particle["URLReference"] + ".html"), "w") as fileObject:
            fileObject.write(page)

    def compile(self):

        particleFilePaths = self.getParticleFilePaths()

        particles = [self.compileParticle(filePath) for filePath in particleFilePaths]

        data = {}

        data["Particles"] = particles

        print(data)

        with open("../data/Compiled.json", "w") as  fileObject:
            json.dump(data, fileObject, indent = 4)

        self.removeParticlePages()

        with open("../web-templates/particle.html", "r") as fileObject:
            particlePageTemplate = fileObject.read()

        for particle in particles:
            self.makeParticlePage(particlePageTemplate, particle)

if __name__ == "__main__":
    compiler = Compiler()

    compiler.compile()

