import pythoncom
import win32com.client as win32
import pandas as pd
import numpy as np

# Récupération des grecques calculés en VBA
def greekstab(Greeks_Argument,file):
    # Créer une instance d'Excel
    pythoncom.CoInitialize()
    excel_instance = win32.Dispatch('Excel.Application')
    excel_instance.Visible = False 
    wb = excel_instance.Workbooks.Open(file)

    # Calcule des grecques via le code VBA
    excel_instance.Application.Run('CalculateGreeks',*Greeks_Argument)

    ResultatGreeksVBA = wb.Sheets("Pricer").Range("Delta:Rho").Value
    ResultatGreeksVBA = [x[0] for x in ResultatGreeksVBA]

    # Ferme le fichier excel ouvert en arrière plan
    wb.Close(SaveChanges=False)
    pythoncom.CoUninitialize()

    print('Ok: Récupération des grecques calculés en VBA')
    return ResultatGreeksVBA

# Calcul des prix en VBA // marche pas
def VBAprice(file):
    # Créer une instance d'Excel
    pythoncom.CoInitialize()
    excel_instance = win32.Dispatch('Excel.Application')
    excel_instance.Visible = True 
    wb = excel_instance.Workbooks.Open(file)

    wb.Sheets("Pricer").Range("StockPrice").Value = 10
    wb.Sheets("Pricer").Range("NbSteps").Value = 11
    # Lance le main du code VBA
    excel_instance.Application.Run('Main')

    ResultatGreeksVBA = wb.Sheets("Pricer").Range("Delta:Rho").Value
    ResultatGreeksVBA = [x[0] for x in ResultatGreeksVBA]

    # Ferme le fichier excel ouvert en arrière plan
    wb.Close(SaveChanges=False)
    pythoncom.CoUninitialize()

    print('Ok: Récupération des grecques calculés en VBA')
    return ResultatGreeksVBA

#print(VBAprice(r'C:\Users\lince\Downloads\Trinomial_VBA_FINAL_VERSION.xlsm'))

# Récupération du tableau d'analyse calculé en VBA et du prix calculé par BS
def VBAdata(file):
    df = pd.read_excel(file, sheet_name='Analysis')
    start_row = df[df.isin(['Steps']).any(axis=1)].index[0]
    ExtractedTab = df.iloc[start_row:].reset_index(drop=True)
    ExtractedTab.columns = ExtractedTab.iloc[0]
    ExtractedTab = ExtractedTab.iloc[1:].dropna(axis=1)

    print("Ok: Récupération du tableau d'analyse calculé en VBA")

    df = pd.read_excel(file, sheet_name='Pricer')
    array = df.to_numpy()
    result = np.argwhere(array == 'Black-Scholes')
    BSVBA = df.iloc[result[0][0],result[0][1]+1]
    BSVBATime = df.iloc[result[0][0],result[0][1]+2]

    print("Ok: Récupération du prix BS calculé en VBA")
    return ExtractedTab, BSVBA, BSVBATime
