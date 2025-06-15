from pydantic import BaseModel


class BalanceGeneral(BaseModel):
    efectivo_equivalentes: float
    cuentas_por_cobrar: float
    inventarios: float
    otros_activos_circulantes: float
    propiedades_plantas_equipos: float
    total_activo_circulante: float
    activos_intangibles: float
    otros_activos_no_circulantes: float
    total_activo_no_circulante: float
    total_activo: float
    cuentas_por_pagar: float
    pasivos_acumulados: float
    deuda_a_corto_plazo: float
    total_pasivo_circulante: float
    deuda_a_largo_plazo: float
    otros_pasivos_a_largo_plazo: float
    total_pasivo_a_largo_plazo: float
    total_pasivo: float
    capital_social_y_utilidades_retenidas: float
    total_pasivo_y_capital_contable: float

    # Razones de Liquidez
    @property
    def razon_corriente(self) -> float:
        """Razón Corriente = Activo Circulante / Pasivo Circulante"""
        if self.total_pasivo_circulante == 0:
            return 0.0
        return self.total_activo_circulante / self.total_pasivo_circulante

    @property
    def prueba_acida(self) -> float:
        """Prueba Ácida = (Activo Circulante - Inventarios) / Pasivo Circulante"""
        if self.total_pasivo_circulante == 0:
            return 0.0
        activos_liquidos = self.total_activo_circulante - self.inventarios
        return activos_liquidos / self.total_pasivo_circulante

    @property
    def capital_neto_trabajo(self) -> float:
        """Capital Neto de Trabajo = Activo Circulante - Pasivo Circulante"""
        return self.total_activo_circulante - self.total_pasivo_circulante

    # Razones de Endeudamiento
    @property
    def endeudamiento_total(self) -> float:
        """Endeudamiento Total = (Total Pasivo / Total Activo) * 100"""
        if self.total_activo == 0:
            return 0.0
        return (self.total_pasivo / self.total_activo) * 100

    @property
    def endeudamiento_patrimonial(self) -> float:
        """Endeudamiento Patrimonial = (Total Pasivo / Capital Contable) * 100"""
        if self.capital_social_y_utilidades_retenidas == 0:
            return 0.0
        return (self.total_pasivo / self.capital_social_y_utilidades_retenidas) * 100

    @property
    def apalancamiento_financiero(self) -> float:
        """Apalancamiento Financiero = Total Activo / Capital Contable"""
        if self.capital_social_y_utilidades_retenidas == 0:
            return 0.0
        return self.total_activo / self.capital_social_y_utilidades_retenidas
