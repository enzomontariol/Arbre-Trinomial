import pythoncom
import win32com.client as win32
import pandas as pd
import numpy as np
from datetime import datetime, date

import streamlit as st

# Calcul des prix en VBA // marche pas
def VBAprice(file):
    
    # Créer une instance d'Excel
    pythoncom.CoInitialize()
    excel_instance = win32.Dispatch('Excel.Application')
    excel_instance.Visible = True 
    wb = excel_instance.Workbooks.Open(file)

    wb.Sheets("Pricer").Range("StockPrice").Value = st.session_state["StockPrice"]
    wb.Sheets("Pricer").Range("Vol").Value = st.session_state["Volatilite"]
    wb.Sheets("Pricer").Range("InterestRate").Value = st.session_state["TauxInteret"]
    wb.Sheets("Pricer").Range("Dividend").Value = st.session_state["Dividende"]
    wb.Sheets("Pricer").Range("ExDateDiv").Value = datetime.combine(st.session_state["ExDateDividende"], datetime.min.time())
    wb.Sheets("Pricer").Range("PricingDate").Value = datetime.combine(st.session_state["PricingDate"], datetime.min.time())
    wb.Sheets("Pricer").Range("NbSteps").Value = st.session_state["NbStep"]
    wb.Sheets("Pricer").Range("Alpha").Value = st.session_state["AlphaParameter"]
    wb.Sheets("Pricer").Range("BaseYear").Value = st.session_state["YearBase"]
    wb.Sheets("Pricer").Range("Maturity").Value = datetime.combine(st.session_state["Maturite"], datetime.min.time())
    wb.Sheets("Pricer").Range("OptionType").Value = st.session_state["Optiontype"]
    wb.Sheets("Pricer").Range("ExerciseType").Value = st.session_state["Exercicetype"]
    wb.Sheets("Pricer").Range("Strike").Value = st.session_state["Strike"]
    wb.Sheets("Pricer").Range("Pruning").Value = st.session_state["Pruning"]

    # Lance le main du code VBA
    excel_instance.Application.Run('Main.Main')

    # Prix de l'option calculé par le code VBA et temps de calcul
    TrinomialPrice = wb.Sheets("Pricer").Range("OurPrice").Value
    TrinomialTime = wb.Sheets("Pricer").Range("OurTime").Value

    # Prix de l'option calculé par le code VBA avec la formule de BS et temps de calcul
    BSPriceVBA = wb.Sheets("Pricer").Range("BSPrice").Value
    BSTimeVBA = wb.Sheets("Pricer").Range("BSTime").Value

    print("Ok: Récupération des prix calculé en VBA")

    # Greeks de l'option calculé par le code VBA
    ResultatGreeksVBA = wb.Sheets("Pricer").Range("Delta:Rho").Value
    ResultatGreeksVBA = [x[0] for x in ResultatGreeksVBA]

    # Ferme le fichier excel ouvert en arrière plan
    # wb.Close(SaveChanges=False)
    pythoncom.CoUninitialize()

    print('Ok: Récupération des grecques calculés en VBA')
    return ResultatGreeksVBA, TrinomialPrice, TrinomialTime, BSPriceVBA, BSTimeVBA

# Calcul des prix en VBA // marche pas
def VBAEmpiriqueGreeks(file):
    
    # Créer une instance d'Excel
    pythoncom.CoInitialize()
    excel_instance = win32.Dispatch('Excel.Application')
    excel_instance.Visible = True 
    wb = excel_instance.Workbooks.Open(file)

    wb.Sheets("Pricer").Range("StockPrice").Value = st.session_state["StockPrice"]
    wb.Sheets("Pricer").Range("Vol").Value = st.session_state["Volatilite"]
    wb.Sheets("Pricer").Range("InterestRate").Value = st.session_state["TauxInteret"]
    wb.Sheets("Pricer").Range("Dividend").Value = st.session_state["Dividende"]
    wb.Sheets("Pricer").Range("ExDateDiv").Value = datetime.combine(st.session_state["ExDateDividende"], datetime.min.time())
    wb.Sheets("Pricer").Range("PricingDate").Value = datetime.combine(st.session_state["PricingDate"], datetime.min.time())
    wb.Sheets("Pricer").Range("NbSteps").Value = st.session_state["NbStep"]
    wb.Sheets("Pricer").Range("Alpha").Value = st.session_state["AlphaParameter"]
    wb.Sheets("Pricer").Range("BaseYear").Value = st.session_state["YearBase"]
    wb.Sheets("Pricer").Range("Maturity").Value = datetime.combine(st.session_state["Maturite"], datetime.min.time())
    wb.Sheets("Pricer").Range("OptionType").Value = st.session_state["Optiontype"]
    wb.Sheets("Pricer").Range("ExerciseType").Value = st.session_state["Exercicetype"]
    wb.Sheets("Pricer").Range("Strike").Value = st.session_state["Strike"]
    wb.Sheets("Pricer").Range("Pruning").Value = st.session_state["Pruning"]

    # Lance le main du code VBA
    excel_instance.Application.Run('Greeks.GreeksEmpirique')

    # Greeks Empirique de l'option calculé par le code VBA
    ResultatGreeksEmpiriqueVBA = wb.Sheets("Pricer").Range("DeltaEmpirique:RhoEmpirique").Value
    ResultatGreeksEmpiriqueVBA = [x[0] for x in ResultatGreeksEmpiriqueVBA]

    # Ferme le fichier excel ouvert en arrière plan
    # wb.Close(SaveChanges=False)
    pythoncom.CoUninitialize()

    print('Ok: Récupération des grecques empiriques calculés en VBA')
    return ResultatGreeksEmpiriqueVBA


# Récupération du tableau d'analyse calculé en VBA et du prix calculé par BS
def VBAdata(file):
    df = pd.read_excel(file, sheet_name='Analysis')

    start_row = df[df.isin(['Black Scholes']).any(axis=1)].index[0]

    BSTab = df.iloc[start_row:start_row+2].reset_index(drop=True)
    print('=========', BSTab)
    BSTab.columns = BSTab.iloc[0]
    BSTab = BSTab.iloc[1:].dropna(axis=1,how='all').dropna(axis=0,how='all')
    print("Ok: Récupération du tableau d'analyse sur les pas calculé en VBA")

    start_row = df[df.isin(['Steps']).any(axis=1)].index[0]
    end_row = df[df.isin(['Strike']).any(axis=1)].index[0]
    ExtractedTab = df.iloc[start_row:end_row].reset_index(drop=True)
    ExtractedTab.columns = ExtractedTab.iloc[0]
    ExtractedTab = ExtractedTab.iloc[1:].dropna(axis=1,how='all').dropna(axis=0,how='all')
    print("Ok: Récupération du tableau d'analyse sur les pas calculé en VBA")

    StrikeTab = df.iloc[end_row:].reset_index(drop=True)
    StrikeTab.columns = StrikeTab.iloc[0]
    StrikeTab = StrikeTab.iloc[1:].dropna(axis=1,how='all').dropna(axis=0,how='all')
    print("Ok: Récupération du tableau d'analyse sur les strike calculé en VBA")

    return BSTab, ExtractedTab, StrikeTab


cheminVBA = r'C:\Users\lince\Downloads\Trinomial_VBA_FINAL_VERSION.xlsm'

print(VBAdata(cheminVBA))

