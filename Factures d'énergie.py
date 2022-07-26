#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 26 13:34:10 2022

@author: heloisevanrenterghem
"""

import pandas as pd
import numpy as np
import re

df = pd.read_csv("Invoice_20201220.csv", sep="|", encoding="latin-1")


# -------------------------------------------
# 1) Le nom d'une antenne a un format bien précis : il est toujours composé de 4 chiffres et de deux lettres. On te demande de retirer tout autre caractère de la colonne "SITE_NAME".
df['SITE_NAME'] = df['SITE_NAME'].str[11:17]

def clean_site_name(site_name):
    result = re.search("\d{4}[a-zA-Z]{2}", site_name)
    if result is None:
        return np.NaN
    else:
        return site_name
    return result

df["SITE_NAME"] = [clean_site_name(site_name) for site_name in df["SITE_NAME"]]

#print(df.isnull().sum())
#print(df[df['SITE_NAME'].isnull()])


# -------------------------------------------
# 2) On te demande de supprimer la colonne "INVOICE_NAME" qui n'apporte rien aux équipes.
df = df.drop(columns=["INVOICE_NAME"])


# -------------------------------------------
# 3) Il y a des antennes pour lesquelles on a des factures mensuelles tandis que pour d'autres, on les reçoit moins régulièrement (trimestre, semestre, année). Ajoute une colonne à ton tableau qui calcule le nombre de jours entre le début de la période de facturation et la fin de la période de facturation.
df["BEGIN"] = pd.to_datetime(df["BEGIN"],format='%d/%m/%Y',errors='coerce')
df["END"] = pd.to_datetime(df["END"],format='%d/%m/%Y',errors='coerce')
df["DAYS_IN_PERIOD"] = df["END"].sub(df["BEGIN"], axis=0).dt.days

# Je crée aussi une colonne bis avec la date de fin incluse dans le nb de jours
df["DAYS_IN_PERIOD_bis"] = pd.Series((df["END"].sub(df["BEGIN"], axis=0).dt.days)+1)


# -------------------------------------------
# 4) A partir de cette nouvelle colonne, crée une autre colonne qui nous donne la consommation journalière moyenne de la période.
df["KWH_PERIOD"] = df["KWH_PERIOD"].str.replace(" ", "")
df["KWH_PERIOD"] = pd.to_numeric(df["KWH_PERIOD"], errors='coerce')

df["AVG_DAILY_CONSUMPTION"] = df.apply(lambda x: "NaN" if x["DAYS_IN_PERIOD"] <= 0 else x["KWH_PERIOD"]/x["DAYS_IN_PERIOD"], axis=1)
df["AVG_DAILY_CONSUMPTION"] = pd.to_numeric(df["AVG_DAILY_CONSUMPTION"], errors='coerce')

df["AVG_DAILY_CONSUMPTION_bis"] = df.apply(lambda x: "NaN" if x["DAYS_IN_PERIOD_bis"] <= 0 else x["KWH_PERIOD"]/x["DAYS_IN_PERIOD_bis"], axis=1)


# -------------------------------------------
# 5) Merci d'ajouter également une colonne qui donne, pour chaque antenne, le nombre de factures dont on dispose au total. Pas grave si l'information se répète à chaque ligne pour une même antenne.
df['NB_OF_INVOICES'] = df.groupby(['SITE_NAME'])['SITE_NAME'].transform('count')


# -------------------------------------------
# 6) Et information bonus si tu y arrives : les équipes aimeraient beaucoup avoir une liste de toutes les antennes avec, pour chaque antenne, le coefficient de variation de la consommation. Cela permettra d'avoir une idée, pour chaque antenne, de la dispersion de sa consommation d'énergie.
coef_variation = df.groupby(["SITE_NAME"])["AVG_DAILY_CONSUMPTION"].std() / df.groupby(["SITE_NAME"])["AVG_DAILY_CONSUMPTION"].mean()
coef_variation = coef_variation.map('{:.3%}'.format)

# -------------------------------------------
# 7) Enfin, tu dois exporter ces deux fichiers obtenus pour pouvoir l'envoyer aux équipes de l'opérateur et leur demander si c'est bien cela qu'ils attendaient de toi.
df.to_csv(r'/Users/heloisevanrenterghem/Documents/THPprojets/factures_energie_clean.csv')
df.to_csv(r'/Users/heloisevanrenterghem/Documents/THPprojets/factures_energie_coefficient_variation.csv')