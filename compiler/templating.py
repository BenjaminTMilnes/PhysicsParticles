import os

class Templater (object):
    def __init__(self):
        pass

    def getTemplateContent(self, templateFilePath):
        with open(templateFilePath, "r") as  fileObject:
            templateContent = fileObject.read()

            return templateContent

    def getTemplateSections(self, templateContent):
        sections = []

        i = 0
        j = 0
        n = 0

        while i < len(templateContent) - 2:
            if n == 0 and templateContent[i:i+2] == "[[":
                sections.append({"Type": "Literal", "Content": templateContent[j:i]})
                i += 2
                j = i
                n = 1
            elif n == 1 and templateContent[i:i+2] == "]]" and templateContent[i+1:i+3] != "]]":
                sections.append({"Type": "Code", "Content": templateContent[j:i]})
                i += 2
                j = i
                n = 0
            else:
                i += 1

        i = len(templateContent)

        if j < i:
            if n == 0:
                sections.append({"Type": "Literal", "Content": templateContent[j:i]})
            if n == 1:
                sections.append({"Type": "Code", "Content": templateContent[j:i]})

        return sections

    def applyModelToTemplate(self, templateSections, model):
        output = ""
        Model = model

        for section in templateSections:
            if section["Type"] == "Literal":
                output += section["Content"]
            elif section["Type"] == "Code":
                output += exec(section["Content"], {"Model": Model})

        return output