import json
import yaml
import os
import os.path
from os import path
import datetime
import boto3

clear = lambda: os.system('cls')

def writeinfile(CRA_File,filepath):
    f = open(filepath, "w")
    f.write(json.dumps(CRA_File, indent=4))
    f.close()

def ProjectExists(CRA_File,projectName):
    try:
        for project in CRA_File["Projects"]:
            if project["Name"].lower() == projectName.lower():
                return project
    except:
        return False
    return False

def PrintProjects(CRA_File):
    clear()
    i = 0
    for project in CRA_File["Projects"]:
        i += 1
        print(str(i) + ". " + project["Name"])

def PrintActions(CRA_File, Projectnumber):
    clear()
    i = 0
    for action in CRA_File["Projects"][Projectnumber]["Actions"]:
        i += 1
        print(str(i) + ". " + action)

def GetCRA_File(filepath, last_wednesday):
    if path.exists(filepath):
        CRA_File_raw = open(filepath, 'r')
        CRA_File = json.load(CRA_File_raw)
        CRA_File_raw.close()
    else:
        create = input("Aucun fichier détécté, voulez-vous en créer un: ")
        if create.lower() == "yes" or "y" or "oui" or "o":
            CRA_File = NewCRA_File(last_wednesday,filepath)
    return CRA_File

def NewCRA_File(last_wednesday,filepath):
    CRA_File = {
        "date": last_wednesday,
        "Status": "En cours",
        "Projects": []
    }
    writeinfile(CRA_File,filepath)
    return CRA_File

def PrintChoices(CRA_File):
    print(
        "CRA:\n"\
        "‾‾‾‾\n"\
        + yaml.dump(CRA_File, allow_unicode=True, sort_keys=False)
        )
    message = "============================\n\n"\
    "1. Entrer un nouveau projet\n"\
    "2. Ajouter des action sur un projet\n"\
    "3. Supprimer une action d'un projet\n"\
    "4. Supprimer un projet\n"\
    "5. Envoyer le CRA\n"\
    "6. Quitter\n"\
    "\nQue voulez vous faire :"
    return message

# Actions

def NewProject(CRA_File,filepath):
    clear()
    projectName = input("Entrer le nom du projet : ")
    ProjectExist = ProjectExists(CRA_File,projectName)

    if ProjectExist != False:
        print("Le projet" + projectName + " existe déjà")
    else:
        CRA_File["Projects"].append({"Name": projectName, "Actions": []})
        writeinfile(CRA_File,filepath)
        print("Projet: "+ projectName + " ajouté")    

def AddAction(CRA_File,filepath):
    clear()
    PrintProjects(CRA_File)
    ProjectNumber = input("Entrer le numéro du projet (Press 'q' to quit): ")
    if type(ProjectNumber) is str and ProjectNumber.lower() == "q":
        return
    else:
        ProjectNumber = int(ProjectNumber) - 1
    
    if ProjectNumber >> len(CRA_File["Projects"]) or ProjectNumber << 0:
        print("Ce numéro n'existe pas")
    else: 
        clear()
        Action = input("Entrer la nouvelle action: ")
        clear()
        CRA_File["Projects"][ProjectNumber]["Actions"].append(str(Action))
        writeinfile(CRA_File,filepath)
        print("L'Action suivante a été ajouté au projet avec succès: " + Action )

        MoreAction = input("Voulez vous rentrer une autre action: ")
        if MoreAction.lower() == "yes" or MoreAction.lower() == "y":
            AddAction(CRA_File,filepath) 

def DeleteProject(CRA_File,filepath):
    clear()
    PrintProjects(CRA_File)
    ProjectToDelete = input("Entrer le numéro de Projet à supprimer (Press 'q' to quit): ")
    if type(ProjectToDelete) is str and ProjectToDelete.lower() == "q":
        return

    ProjectToDelete = int(ProjectToDelete) - 1
    if ProjectToDelete >= len(CRA_File["Projects"]) or 0 >> ProjectToDelete:
        print("Ce numéro n'existe pas")
    else:
        deleted = CRA_File["Projects"][ProjectToDelete]["Name"]
        del CRA_File["Projects"][ProjectToDelete]
        writeinfile(CRA_File,filepath)
        print("Projet: " + deleted + " supprimé")  

def DeleteAction(CRA_File,filepath):
    clear()
    PrintProjects(CRA_File)
    Project = input("Entrer le numéro de Projet (Press 'q' to quit): ")
    if type(Project) is str and Project.lower() == "q":
        return
    else:
        Project = int(Project)  - 1

    if Project >> len(CRA_File["Projects"]) or Project << 0:
        print("Ce numéro n'existe pas")
    else:
        PrintActions(CRA_File, Project)
        Action = input("Entrer le numéro d'action (Press 'q' to quit): ")
        if type(Action) is str and Action.lower() == "q":
            return
        Action = int(Action)
        if Action >> len(CRA_File["Projects"][Project]["Actions"]) or Action <= 0:
            print("Ce numéro n'existe pas")
        else:
            del CRA_File["Projects"][Project]["Actions"][Action]
            writeinfile(CRA_File,filepath)
            print("L'action suivante à été supprimée : " + CRA_File["Projects"][Project]["Actions"][Action])  

def SendCRA(filepath,filename,s3bucket,s3):
    clear()
    if path.exists(filepath):
        try:
            s3.upload_file(filepath, s3bucket, filename)
            print("CRA envoyé !")
        except Exception as errormessage:
            print("Imposssible d'uploader le CRA | message: " + str(errormessage))
    

####################################################################################################################################################################################################################################
#Obtention des dates
today = datetime.date.today()
offset = (today.weekday() - 2) % 7
last_wednesday_raw = today - datetime.timedelta(days=offset)
last_wednesday = last_wednesday_raw.strftime("%d/%m/%Y")

filepath = r".\CRA.json"
filename = "CRAs/" + os.path.basename(filepath)
s3bucket = "projetpython"
s3 = boto3.client('s3')

CRA_File = GetCRA_File(filepath, last_wednesday)
CRA_File_date = CRA_File["date"]

if CRA_File_date != last_wednesday:
    NewCra = input("On est mercredi, veux-tu faire un nouveau CRA (y,n) ? ")
    if NewCra.lower() == "y" or "yes":
        CRA_File = NewCRA_File(last_wednesday,filepath)

while True:
    clear()
    message = PrintChoices(CRA_File)

    UserInput = input(message)
    if UserInput == "1":
        NewProject(CRA_File,filepath)
    elif UserInput == "2":
        AddAction(CRA_File, filepath)
    elif UserInput == "3":
        DeleteAction(CRA_File,filepath)
    elif UserInput == "4":
        DeleteProject(CRA_File,filepath)
    elif UserInput == "5":
        SendCRA(filepath,filename,s3bucket,s3)      
    elif UserInput == "6":
        quit()
    else:
        print("Erreur, veuillez entrer un chiffre entre 1 et 6")
    
    input("\nPress Enter to continue...")
