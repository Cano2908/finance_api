from io import BytesIO
from typing import List

import dask.dataframe as dd
import pandas as pd

from apps.api.models.map_conceptos import agrupaciones, conceptos_map
from apps.mongo.core.base_mongo_model import BaseMongoModel, mongo_model
from apps.tools.objectid import ObjectId


@mongo_model(collection_name="balance_general", schema_version=1)
class BalanceGeneral(BaseMongoModel):
    id_periodo: ObjectId
    activo: float
    activo_corto_plazo: float
    caja: float
    caja_efectivo: float
    bancos: float
    inversiones: float
    inversiones_temporales: float
    clientes: float
    clientes_nacionales: float
    cuentas_documentos_por_cobrar_corto_plazo: float
    cuentas_documentos_por_cobrar_corto_plazo_nacional: float
    deudores_diversos: float
    funcionarios_empleados: float
    otros_deudores_diversos: float
    estimacion_cuentas_incobrables: float
    pagos_anticipados: float
    seguros_finanzas_pagados_anticipado_nacional: float
    rentas_pagados_anticipado_nacional: float
    inventario: float
    materia_prima_materiales: float
    produccion_en_proceso: float
    anticipo_proveedores: float
    anticipo_proveedores_nacional: float
    otros_activos_corto_plazo: float
    activo_corto_plazo: float
    terreno: float
    edificios: float
    maquinas_equipos: float
    autos_camiones: float
    mobiliario_equipo_oficina: float
    equipo_computo: float
    equipo_comunicacion: float
    otros_activos_fijos: float
    gastos_diferidos: float
    activos_intangibles: float
    gastos_organizacion: float
    gastos_instalacion: float
    cuentas_documentos_por_cobrar_largo_plazo: float
    cuentas_documentos_por_cobrar_largo_plazo_nacional: float
    pasivo: float
    pasivo_corto_plazo: float
    proveedores: float
    cuentas_por_pagar_corto_plazo: float
    documento_por_pagar_bancario: float
    cobros_anticipados_corto_plazo: float
    rentas_cobradas_anticipado_corto_plazo_nacional: float
    impuestos_traslados: float
    iva_traslado: float
    otros_pasivos_corto_plazo: float
    pasivo_largo_plazo: float
    acreedores_diversos_largo_plazo: float
    cuentas_por_pagar_largo_plazo: float
    documentos_bancarios_financieros_por_pagar_largo_plazo_nacional: float
    capital_contable: float
    capital_social: float
    capital_fijo: float
    capital_variable: float
    patrimonio: float
    aportacion_patrimonial: float
    reserva_legal: float
    resultado_ejercicios_anteriores: float
    utilidad_ejercicios_anteriores: float
    perdidas_ejercicios_anteriores: float
    resultado_integral_ejercicios_anteriores: float
    resultado_ejercicio: float
    utilidad_ejecicio: float
    perida_ejercicio: float


class AnalisisHorizontalBalanceGeneral:
    def calcular_analisis_horizontal(
        self, years: List[int], balances: List[BalanceGeneral]
    ):
        """
        Calculate the horizontal analysis of the balance sheet.
        :param years: List of years to analyze.q
        :param balances: List of balance sheets for each year.
        :return: Dictionary with the analysis results.
        """

        if len(balances) < 2:
            raise ValueError("At least two balance sheets are required for analysis.")

        campos = [
            campo
            for campo in BalanceGeneral.model_fields.keys()
            if campo not in ["id", "id_periodo"]
        ]

        conceptos_legibles = [conceptos_map.get(campo, campo) for campo in campos]

        data = {"Concepto": conceptos_legibles}

        # Datos Originales
        for i in range(len(balances)):
            año_actual = years[i]
            balance_actual = balances[i]

            for campo in campos:
                val_actual = getattr(balance_actual, campo)
                key = f"{año_actual}"
                if key not in data:
                    data[key] = []
                data[key].append(val_actual)

        # Datos de Diferencia y Porcentaje
        for i in range(len(balances)):
            if i == 0:
                continue

            año_actual = years[i]
            balance_actual = balances[i]
            balance_anterior = balances[i - 1]

            key_delta = f"Δ{año_actual}"
            key_pct = f"%{año_actual}"

            data[key_delta] = []
            data[key_pct] = []

            for campo in campos:
                val_actual = getattr(balance_actual, campo)
                val_anterior = getattr(balance_anterior, campo)

                delta = val_actual - val_anterior
                pct = (
                    round((delta / val_anterior) * 100, 2)
                    if val_anterior != 0
                    else None
                )

                data[key_delta].append(delta)
                data[key_pct].append(pct)  # type: ignore

        df = pd.DataFrame(data)
        ddf = dd.from_pandas(df, npartitions=1)

        output = BytesIO()
        ddf.compute().to_excel(output, index=False, engine="openpyxl")
        output.seek(0)
        return output


class AnalisisVerticalBalanceGeneral:
    def calcular_analisis_vertical(
        self, years: List[int], balances: List[BalanceGeneral]
    ):
        """
        Calcula el análisis vertical del balance general para múltiples periodos.
        :param years: Lista de años.
        :param balances: Lista de objetos BalanceGeneral por año.
        :return: BytesIO con archivo Excel del análisis.
        """

        if len(balances) != len(years):
            raise ValueError(
                "La cantidad de balances debe coincidir con la cantidad de años."
            )

        datos = {"Categoría": [], "Cuenta": []}

        # Inicializa estructura
        for año in years:
            datos[f"Valor {año}"] = []
            datos[f"% del Total {año}"] = []

        for grupo, campos in agrupaciones.items():
            for campo in campos:
                # Añadir grupo
                datos["Categoría"].append(grupo)
                # Usar nombre legible
                datos["Cuenta"].append(conceptos_map.get(campo, campo))

                for i, balance in enumerate(balances):
                    año = years[i]
                    valor = getattr(balance, campo, 0)

                    # Total del grupo para este año
                    total_grupo = sum(getattr(balance, c, 0) for c in campos)
                    porcentaje = (valor / total_grupo * 100) if total_grupo != 0 else 0

                    datos[f"Valor {año}"].append(valor)
                    datos[f"% del Total {año}"].append(round(porcentaje, 2))

        df = pd.DataFrame(datos)
        ddf = dd.from_pandas(df, npartitions=1)

        output = BytesIO()
        ddf.compute().to_excel(output, index=False, engine="openpyxl")
        output.seek(0)
        return output
