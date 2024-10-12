import pythoncom
import win32com.client as win32
import pandas as pd

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

# Récupération du tableau d'analyse calculé en VBA
def VBAtabAnalysis(file):
    df = pd.read_excel(file, sheet_name='Analysis')

    start_row = df[df.isin(['Steps']).any(axis=1)].index[0]
    ExtractedTab = df.iloc[start_row:].reset_index(drop=True)
    ExtractedTab.columns = ExtractedTab.iloc[0]
    ExtractedTab = ExtractedTab.iloc[1:].dropna(axis=1)

    print("Ok: Récupération du tableau d'analyse calculé en VBA")
    return ExtractedTab
