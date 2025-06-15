from typing import Optional


from apps.mongo.core.base_mongo_model import BaseMongoModel, mongo_model
from apps.mongo.models.extensions.balance_general import BalanceGeneral
from apps.mongo.models.extensions.estado_resultados import EstadoResultados
from apps.tools.date import Date
from apps.tools.objectid import ObjectId


def parse_amount(amount_str) -> float:
    """Limpia strings con símbolos de moneda y comas para convertir a float."""
    amount_str = str(amount_str)
    return float(amount_str.replace("$", "").replace(",", "").strip())


@mongo_model(collection_name="periodo_contable", schema_version=1)
class PeriodoContable(BaseMongoModel):
    id_empresa: ObjectId
    anio: int
    fecha_inicio: Date
    fecha_fin: Date
    estado_resultado: Optional[EstadoResultados] = None
    balance_general: Optional[BalanceGeneral] = None

    # Razones de Actividad (requieren datos de ambos estados)
    @property
    def rotacion_inventarios(self) -> float:
        """Rotación de Inventarios = Costo de Ventas / Inventario Promedio"""
        if not self.estado_resultado or not self.balance_general:
            return 0.0
        if self.balance_general.inventarios == 0:
            return 0.0
        return self.estado_resultado.costo_ventas / self.balance_general.inventarios

    @property
    def dias_inventario(self) -> float:
        """Días de Inventario = 365 / Rotación de Inventarios"""
        rotacion = self.rotacion_inventarios
        if rotacion == 0:
            return 0.0
        return 365 / rotacion

    @property
    def rotacion_cuentas_cobrar(self) -> float:
        """Rotación de Cuentas por Cobrar = Ventas Netas / Cuentas por Cobrar"""
        if not self.estado_resultado or not self.balance_general:
            return 0.0
        if self.balance_general.cuentas_por_cobrar == 0:
            return 0.0
        return (
            self.estado_resultado.ventas_netas / self.balance_general.cuentas_por_cobrar
        )

    @property
    def periodo_promedio_cobro(self) -> float:
        """Período Promedio de Cobro = 365 / Rotación de Cuentas por Cobrar"""
        rotacion = self.rotacion_cuentas_cobrar
        if rotacion == 0:
            return 0.0
        return 365 / rotacion

    @property
    def rotacion_cuentas_pagar(self) -> float:
        """Rotación de Cuentas por Pagar = Costo de Ventas / Cuentas por Pagar"""
        if not self.estado_resultado or not self.balance_general:
            return 0.0
        if self.balance_general.cuentas_por_pagar == 0:
            return 0.0
        return (
            self.estado_resultado.costo_ventas / self.balance_general.cuentas_por_pagar
        )

    @property
    def periodo_promedio_pago(self) -> float:
        """Período Promedio de Pago = 365 / Rotación de Cuentas por Pagar"""
        rotacion = self.rotacion_cuentas_pagar
        if rotacion == 0:
            return 0.0
        return 365 / rotacion

    @property
    def ciclo_efectivo(self) -> float:
        """Ciclo de Efectivo = Días de Inventario + Período Promedio de Cobro - Período Promedio de Pago"""
        return (
            self.dias_inventario
            + self.periodo_promedio_cobro
            - self.periodo_promedio_pago
        )

    # Razón de Cobertura de Intereses
    @property
    def cobertura_intereses(self) -> float:
        """Cobertura de Intereses = Utilidad Operativa / Gastos Financieros"""
        if not self.estado_resultado:
            return 0.0
        # Asumiendo que resultado_financieros negativo son gastos financieros
        gastos_financieros = abs(min(self.estado_resultado.resultado_financieros, 0))
        if gastos_financieros == 0:
            return float("inf")  # Sin gastos financieros
        return self.estado_resultado.utilidad_operativa / gastos_financieros

    # Razones de Rentabilidad Adicionales
    @property
    def roa(self) -> float:
        """ROA = (Utilidad Neta / Total Activo) * 100"""
        if not self.estado_resultado or not self.balance_general:
            return 0.0
        if self.balance_general.total_activo == 0:
            return 0.0
        return (
            self.estado_resultado.utilidad_neta / self.balance_general.total_activo
        ) * 100

    @property
    def roe(self) -> float:
        """ROE = (Utilidad Neta / Capital Contable) * 100"""
        if not self.estado_resultado or not self.balance_general:
            return 0.0
        if self.balance_general.capital_social_y_utilidades_retenidas == 0:
            return 0.0
        return (
            self.estado_resultado.utilidad_neta
            / self.balance_general.capital_social_y_utilidades_retenidas
        ) * 100

    # Método para obtener resumen de todas las razones
    def get_razones_financieras(self) -> dict:
        """Retorna un diccionario con todas las razones financieras calculadas"""
        razones = {}

        # Razones de Liquidez
        if self.balance_general:
            razones["liquidez"] = {
                "razon_corriente": self.balance_general.razon_corriente,
                "prueba_acida": self.balance_general.prueba_acida,
                "capital_neto_trabajo": self.balance_general.capital_neto_trabajo,
            }

            # Razones de Endeudamiento
            razones["endeudamiento"] = {
                "endeudamiento_total": self.balance_general.endeudamiento_total,
                "endeudamiento_patrimonial": self.balance_general.endeudamiento_patrimonial,
                "apalancamiento_financiero": self.balance_general.apalancamiento_financiero,
            }

        # Razones de Rentabilidad
        if self.estado_resultado:
            razones["rentabilidad"] = {
                "margen_bruto": self.estado_resultado.margen_bruto,
                "margen_operativo": self.estado_resultado.margen_operativo,
                "margen_neto": self.estado_resultado.margen_neto,
            }

        # Razones combinadas
        if self.estado_resultado and self.balance_general:
            razones["actividad"] = {
                "rotacion_inventarios": self.rotacion_inventarios,
                "dias_inventario": self.dias_inventario,
                "rotacion_cuentas_cobrar": self.rotacion_cuentas_cobrar,
                "periodo_promedio_cobro": self.periodo_promedio_cobro,
                "rotacion_cuentas_pagar": self.rotacion_cuentas_pagar,
                "periodo_promedio_pago": self.periodo_promedio_pago,
                "ciclo_efectivo": self.ciclo_efectivo,
            }

            razones["rentabilidad_adicional"] = {"roa": self.roa, "roe": self.roe}

            razones["cobertura"] = {"cobertura_intereses": self.cobertura_intereses}

        return razones
