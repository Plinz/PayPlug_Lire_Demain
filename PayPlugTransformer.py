import PySimpleGUI as sg
import csv, os

def removeChars(text, chars):
    return ''.join(c for c in text if c not in chars)
    
def popupError(errorText):
    error = sg.Window(windowName, [[sg.Text(errorText)], [sg.Column([[sg.Button("Continuer"), sg.Button("Arrêter")]], element_justification='c', expand_x=True)]], modal = True)
    eventError, valuesError = error.read()
    error.close()
    return eventError


def parseInputFile(csvInput, csvBDDFacture, csvBDDPayPlug, csvOutput):
    panierIdFactureSet = {}
    refCodeClientSet = {}
    refPanierIdSet = {}
    errors = set()
    with open(csvBDDFacture) as csvfileinput:
        reader = list(csv.reader(csvfileinput, delimiter=';'))
        i=1
        while (i < len(reader)  and len(reader[i]) > 3 and reader[i][0]):
            if (reader[i][3].strip().startswith('F')):
                if (reader[i][2] and reader[i][2].strip() in panierIdFactureSet):
                    error = '[' + csvBDDFacture + '] Duplicata de facture pour le panier ID [' + reader[i][2] + '] ligne ' + str(i+1)
                    errors.add(error)
                elif (reader[i][2]):
                    panierIdFactureSet[reader[i][2]] = reader[i][3]
            i += 1  
    with open(csvBDDPayPlug) as csvfileinput:
        reader = list(csv.reader(csvfileinput, delimiter=';'))
        i=1
        while (i < len(reader) and len(reader[i]) > 10 and reader[i][0] and 'Paiement' in reader[i][3]):
            if (reader[i][0].strip() in refCodeClientSet):
                error = '[' + csvBDDPayPlug + '] Duplicata de référence [' + reader[i][0] + '] ligne ' + str(i+1)
                errors.add(error)
            else :
                codeClient = removeChars(reader[i][10], '"}{').split(',')[4].split(':')[1].strip()
                refCodeClientSet[reader[i][0]] = codeClient
                panierId = removeChars(reader[i][10], '"}{').split(',')[1].split(':')[1].strip()
                refPanierIdSet[reader[i][0]] = panierId                
            i += 1

    with open(csvOutput, 'w', newline='') as csvfileoutput:
        writer = csv.writer(csvfileoutput, delimiter=';')
        with open(csvInput) as csvfileinput:
            reader = list(csv.reader(csvfileinput, delimiter=','))
            i = 1
            while (i < len(reader) and len(reader[i]) > 10 and reader[i][0]):
                if len(reader[i]) > 11 :
                    date = reader[i][1].split(' ')[0]
                    date = date[8:] + date[5:7] + date[2:4]
                    ref = removeChars(reader[i][0], ' "')
                    val = removeChars(reader[i][5], ' -+"')
                    type = removeChars(reader[i][3], ' "')
                    if ('Paiement' in type):
                        listLib = removeChars(reader[i][10], '"}{').split(',')
                        if (len(listLib) < 4) :
                            error = '[' + csvInput + '] Ligne [' + str(i+1) + '] Colonne [11] Valeur [' + reader[i][10] + '] Impossible de lire le panierID et nom du client '
                            errors.add(error)
                        else :
                            panierID = listLib[1].split(':')[1].strip()
                            nomClient = listLib[3].split(':')[1].strip()
                            lib = 'Nom_client : ' + nomClient + ' panierID : ' + panierID
                            compteTiers = listLib[4].split(':')[1].strip()
                            numFacture = ''
                            if (panierID in panierIdFactureSet):
                                numFacture = panierIdFactureSet[panierID]
                            writer.writerow(['PAY', date, '51710000', '', '', ref, lib, val, ''])
                            writer.writerow(['PAY', date, '41110000', compteTiers, numFacture, ref, lib, '', val])
                    elif ('Remboursement' in type or 'Opposition' in type):
                        listRef = reader[i][4].strip().split('#')
                        if (len(listRef) < 1) :
                            error = '[' + csvInput + '] Ligne [' + str(i+1) + '] Colonne [5] Valeur [' + reader[i][4] + '] Impossible de lire la référence du paiement '
                            errors.add(error)
                        else :
                            ref = listRef[1]
                            if (ref in refCodeClientSet):
                                compteTiers = refCodeClientSet[ref]
                                refPanierID = refPanierIdSet[ref]
                                if (refPanierID in panierIdFactureSet):
                                    numFacture = panierIdFactureSet[refPanierID]
                                    listLib = removeChars(reader[i][10], '"}{').split(',')
                                    panierID = listLib[1].split(':')[1].strip()
                                    nomClient = listLib[3].split(':')[1].strip()
                                    lib = 'Nom_client : ' + nomClient + ' panierID : ' + panierID
                                    writer.writerow(['PAY', date, '51710000', '', '', reader[i][0], lib, '', val])
                                    writer.writerow(['PAY', date, '41110000', compteTiers, numFacture, reader[i][0], lib, val, ''])
                                else:
                                    error = '[' + csvInput + '] Ligne [' + str(i+1) + '] Impossible de trouver la facture correspondant au panierID [' + refPanierID + '] du paiement avec la ref [' + ref + ']'
                                    errors.add(error)
                            else:
                                error = '[' + csvInput + '] Ligne [' + str(i+1) + '] Impossible de trouver le paiement avec la ref [' + ref + ']'
                                errors.add(error)
                    elif ('Facture' in type):
                        lib = removeChars(reader[i][4], '"')
                        writer.writerow(['PAY', date, '51710000', '', '', ref, lib, '', val])
                        writer.writerow(['PAY', date, '4110000', 'ZZATTENTE', '', ref, lib, val, ''])
                    else:
                        eventError = popupError("Le Type (" + type + ") de la ligne " + str(i+1) + " n'a pas été reconnu.")
                        if eventError != "Continuer" :
                            return False
                else :
                    eventError = popupError("La ligne " + str(i+1) + " n'a pas pu être transformée, car le nombre de colonnes est insuffisant")
                    if eventError != "Continuer" :
                        return False
                i += 1
    csvOutputErr = csvOutput + '.err'
    with open(csvOutputErr, 'w', newline='') as csvfileerroutput:
        for item in errors:
            csvfileerroutput.write("%s\n" % item)
    return True
    
def runScript(values):
    csvInput = values['input']
    csvBDDFacture = values['bddFacture']
    csvBDDPayPlug = values['bddPayPlug']
    csvOutput = values['output']
    isCompleted = parseInputFile(csvInput, csvBDDFacture, csvBDDPayPlug, csvOutput)
    endText = "Fin de l'exécution" if isCompleted else "L'exécution a été interrompu"
    window = sg.Window(windowName, [[sg.Text(endText)], [sg.Button('Ouvrir le dossier'), sg.Button('Ouvrir le fichier'), sg.Button('Fermer')]], modal = True)
    event, values = window.read()
    window.close()
    if event == 'Ouvrir le dossier':
        path = os.path.dirname(os.path.abspath(csvOutput))
        os.startfile(path)
    elif event == 'Ouvrir le fichier' :
        path = os.path.realpath(csvOutput)
        os.startfile(path)

windowName = 'PayPlug Transformer - AUZOU EDITIONS'
layout = [[sg.Text(text='AUZOU EDITIONS', font='_ 20 bold', justification='c', expand_x=True)],
          [sg.Text('Fichier CSV PayPlug')],
          [sg.Input(key='input'), sg.FileBrowse("Parcourir", target='input', file_types=(("Fichiers CSV", "*.csv"),))],
          [sg.Text('Fichier CSV BDD Factures')],
          [sg.Input(key='bddFacture'), sg.FileBrowse("Parcourir", target='bddFacture', file_types=(("Fichiers CSV", "*.csv"),))],
          [sg.Text('Fichier CSV BDD PayPlug')],
          [sg.Input(key='bddPayPlug'), sg.FileBrowse("Parcourir", target='bddPayPlug', file_types=(("Fichiers CSV", "*.csv"),))],
          [sg.Text('Fichier à générer')],
          [sg.Input(key='output') , sg.SaveAs("Enregistrer sous", target='output', file_types=(("Fichiers Texte", "*.txt"),))],
          [sg.Column([[sg.OK(), sg.Cancel("Annuler")]], element_justification='c', expand_x=True)]]

window = sg.Window(windowName, layout, margins=(0, 0))
event, values = window.read()
if event == 'OK' :
    runScript(values)
