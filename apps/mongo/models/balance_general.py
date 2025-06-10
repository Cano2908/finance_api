from io import BytesIO
from typing import Annotated, List

import dask.dataframe as dd
import pandas as pd
from pydantic import BaseModel, Field

from apps.api.models.map_conceptos import agrupaciones, conceptos_map




# class AnalisisHorizontalBalanceGeneral:
#     def calcular_analisis_horizontal(
#         self, years: List[int], balances: List[BalanceGeneral]
#     ):
#         """
#         Calculate the horizontal analysis of the balance sheet.
#         :param years: List of years to analyze.q
#         :param balances: List of balance sheets for each year.
#         :return: Dictionary with the analysis results.
#         """

#         if len(balances) < 2:
#             raise ValueError("At least two balance sheets are required for analysis.")

#         campos = [
#             campo
#             for campo in BalanceGeneral.model_fields.keys()
#             if campo not in ["id", "id_periodo"]
#         ]

#         conceptos_legibles = [conceptos_map.get(campo, campo) for campo in campos]

#         data = {"Concepto": conceptos_legibles}

#         # Datos Originales
#         for i in range(len(balances)):
#             año_actual = years[i]
#             balance_actual = balances[i]

#             for campo in campos:
#                 val_actual = getattr(balance_actual, campo)
#                 key = f"{año_actual}"
#                 if key not in data:
#                     data[key] = []
#                 data[key].append(val_actual)

#         # Datos de Diferencia y Porcentaje
#         for i in range(len(balances)):
#             if i == 0:
#                 continue

#             año_actual = years[i]
#             balance_actual = balances[i]
#             balance_anterior = balances[i - 1]

#             key_delta = f"Δ{año_actual}"
#             key_pct = f"%{año_actual}"

#             data[key_delta] = []
#             data[key_pct] = []

#             for campo in campos:
#                 val_actual = getattr(balance_actual, campo)
#                 val_anterior = getattr(balance_anterior, campo)

#                 delta = val_actual - val_anterior
#                 pct = (
#                     round((delta / val_anterior) * 100, 2)
#                     if val_anterior != 0
#                     else None
#                 )

#                 data[key_delta].append(delta)
#                 data[key_pct].append(pct)  # type: ignore

#         df = pd.DataFrame(data)
#         ddf = dd.from_pandas(df, npartitions=1)

#         output = BytesIO()
#         ddf.compute().to_excel(output, index=False, engine="openpyxl")
#         output.seek(0)
#         return output


# class AnalisisVerticalBalanceGeneral:
#     def calcular_analisis_vertical(
#         self, years: List[int], balances: List[BalanceGeneral]
#     ):
#         """
#         Calcula el análisis vertical del balance general para múltiples periodos.
#         :param years: Lista de años.
#         :param balances: Lista de objetos BalanceGeneral por año.
#         :return: BytesIO con archivo Excel del análisis.
#         """

#         if len(balances) != len(years):
#             raise ValueError(
#                 "La cantidad de balances debe coincidir con la cantidad de años."
#             )

#         datos = {"Categoría": [], "Cuenta": []}

#         # Inicializa estructura
#         for año in years:
#             datos[f"Valor {año}"] = []
#             datos[f"% del Total {año}"] = []

#         for grupo, campos in agrupaciones.items():
#             for campo in campos:
#                 # Añadir grupo
#                 datos["Categoría"].append(grupo)
#                 # Usar nombre legible
#                 datos["Cuenta"].append(conceptos_map.get(campo, campo))

#                 for i, balance in enumerate(balances):
#                     año = years[i]
#                     valor = getattr(balance, campo, 0)

#                     # Total del grupo para este año
#                     total_grupo = sum(getattr(balance, c, 0) for c in campos)
#                     porcentaje = (valor / total_grupo * 100) if total_grupo != 0 else 0

#                     datos[f"Valor {año}"].append(valor)
#                     datos[f"% del Total {año}"].append(round(porcentaje, 2))

#         df = pd.DataFrame(datos)
#         ddf = dd.from_pandas(df, npartitions=1)

#         output = BytesIO()
#         ddf.compute().to_excel(output, index=False, engine="openpyxl")
#         output.seek(0)
#         return output
