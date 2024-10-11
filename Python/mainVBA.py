import win32com.client as win32
import pandas as pd
    
def greekstab(Greeks_Argument,file):
    # Créer une instance d'Excel
    excel_instance_1 = win32.Dispatch('Excel.Application')
    excel_instance_1.Visible = True 
    # Ouvrir le fichier Excel avec la macro VBA
    wb = excel_instance_1.Workbooks.Open(file)
    #Greeks_Argument = ('Call', 'Européen', 100, 100, 0.22, 3, 0.01, 365)
    print(Greeks_Argument)
    excel_instance_1.Application.Run('CalculateGreeks',*Greeks_Argument)#CalculateGreeks')

    mavariable = wb.Sheets("Pricer").Range("Delta:Rho").Value
    mavariable = [x[0] for x in mavariable]
    return mavariable

def VBAtabAnalysis(file):
    df = pd.read_excel(file, sheet_name='Analysis')

    start_row = df[df.isin(['Steps']).any(axis=1)].index[0]
    #start_col = df[df.isin(['Steps']).any()].index[1]
    # Extraire les données à partir de la ligne trouvée jusqu'à la fin du DataFrame
    extracted_data = df.iloc[start_row:].reset_index(drop=True)
    extracted_data.columns = extracted_data.iloc[0]
    extracted_data = extracted_data.iloc[1:].dropna(axis=1)
    return extracted_data

#print("aaa",greekstab())
#print(VBAtabAnalysis())