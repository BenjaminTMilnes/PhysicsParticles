import os

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

            return lines[0]

    def compile(self):

        particleFilePaths = self.getParticleFilePaths()

        for p in particleFilePaths:
            print(self.compileParticle(p))

if __name__ == "__main__":
    compiler = Compiler()

    compiler.compile()

