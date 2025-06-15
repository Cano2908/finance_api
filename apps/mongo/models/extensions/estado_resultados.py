from pydantic import BaseModel


class EstadoResultados(BaseModel):
    ventas_netas: float
    costo_ventas: float
    utilidad_bruta: float
    gastos_operativos: float
    utilidad_operativa: float
    resultado_financieros: float
    utilidad_ante_impuestos: float
    impuesto_utilidad: float
    utilidad_neta: float

    # Razones de Rentabilidad
    @property
    def margen_bruto(self) -> float:
        """Margen Bruto = (Utilidad Bruta / Ventas Netas) * 100"""
        if self.ventas_netas == 0:
            return 0.0
        return (self.utilidad_bruta / self.ventas_netas) * 100

    @property
    def margen_operativo(self) -> float:
        """Margen Operativo = (Utilidad Operativa / Ventas Netas) * 100"""
        if self.ventas_netas == 0:
            return 0.0
        return (self.utilidad_operativa / self.ventas_netas) * 100

    @property
    def margen_neto(self) -> float:
        """Margen Neto = (Utilidad Neta / Ventas Netas) * 100"""
        if self.ventas_netas == 0:
            return 0.0
        return (self.utilidad_neta / self.ventas_netas) * 100
