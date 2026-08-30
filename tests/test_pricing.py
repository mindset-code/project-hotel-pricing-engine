"""Pruebas del motor de precios.

Un motor de tarifas se juzga por lo que NUNCA hace: cobrar de menos en agosto,
vender mas habitaciones de las que tiene el hotel o proponer un precio fuera de
la banda que el revenue manager ha autorizado. Eso es lo que se fija aqui.

Los tests no dependen de fechas concretas: `START_DATE` se calcula desde
`datetime.now()`, asi que cualquier assert sobre un dia del calendario
caducaria manana.
"""

import numpy as np
import pytest

from dynamic_pricing_engine import (
    BASE_PRICES,
    DAYS_FORECAST,
    DAYS_HISTORY,
    DOW_FACTOR,
    EVENTS,
    ROOM_SHARE,
    SEASONALITY,
    TOTAL_ROOMS,
    build_forecast,
    build_historical,
)


@pytest.fixture(scope="module")
def historico():
    # Se re-siembra a proposito: la semilla del modulo solo actua al importarlo,
    # asi que sin esto una segunda llamada daria otros numeros.
    np.random.seed(42)
    return build_historical()


@pytest.fixture(scope="module")
def prevision(historico):
    return build_forecast(historico)


class TestConfiguracion:
    def test_los_doce_meses_tienen_indice_de_temporada(self):
        assert sorted(SEASONALITY) == list(range(1, 13))

    def test_los_siete_dias_tienen_factor(self):
        assert sorted(DOW_FACTOR) == list(range(7))

    def test_el_reparto_de_habitaciones_suma_el_cien_por_cien(self):
        assert sum(ROOM_SHARE.values()) == pytest.approx(1.0)

    def test_cada_tipo_de_habitacion_tiene_precio_y_cuota(self):
        assert set(BASE_PRICES) == set(ROOM_SHARE)

    def test_el_verano_cuesta_mas_que_el_invierno(self):
        assert SEASONALITY[7] > SEASONALITY[1]
        assert SEASONALITY[8] > SEASONALITY[2]

    def test_el_fin_de_semana_cuesta_mas_que_el_lunes(self):
        assert DOW_FACTOR[5] > DOW_FACTOR[0]   # sabado sobre lunes
        assert DOW_FACTOR[4] > DOW_FACTOR[1]   # viernes sobre martes

    def test_ningun_evento_abarata_la_noche(self):
        assert all(f > 1.0 for f in EVENTS.values())


class TestHistorico:
    def test_hay_una_fila_por_dia_y_tipo(self, historico):
        assert len(historico) == DAYS_HISTORY * len(BASE_PRICES)

    def test_no_se_venden_mas_habitaciones_de_las_que_hay(self, historico):
        assert historico["rooms_sold"].max() <= TOTAL_ROOMS
        assert historico["rooms_sold"].min() >= 0

    def test_la_ocupacion_se_queda_dentro_de_la_banda(self, historico):
        """El clip del codigo: entre el 25 % y el 98 %."""
        assert historico["occupancy"].min() >= 0.25
        assert historico["occupancy"].max() <= 0.98

    def test_ninguna_tarifa_es_cero_o_negativa(self, historico):
        assert (historico["adr"] > 0).all()
        assert (historico["revpar"] > 0).all()

    def test_el_revpar_es_la_tarifa_por_la_ocupacion(self, historico):
        """RevPAR = ADR x ocupacion, con la tolerancia que impone el redondeo.

        El motor calcula el RevPAR con la ocupacion completa pero publica la
        ocupacion redondeada a cuatro decimales, asi que quien rehaga la cuenta
        desde el CSV puede desviarse hasta medio diezmilesimo de ADR. La cota se
        deriva de ahi en vez de fijar un numero magico: 0,00005 x ADR por el
        redondeo de la ocupacion, mas el centimo del propio RevPAR.
        """
        muestra = historico.sample(200, random_state=0)
        esperado = muestra["adr"] * muestra["occupancy"]
        cota = muestra["adr"] * 0.00005 + 0.01
        assert ((muestra["revpar"] - esperado).abs() <= cota).all()

    def test_las_habitaciones_vendidas_salen_de_la_ocupacion(self, historico):
        muestra = historico.sample(200, random_state=1)
        esperado = (TOTAL_ROOMS * muestra["occupancy"]).astype(int)
        # occupancy viene redondeado a 4 decimales, de ahi la tolerancia de 1.
        assert (abs(muestra["rooms_sold"] - esperado) <= 1).all()

    def test_estan_los_tres_tipos_y_en_igual_numero(self, historico):
        cuenta = historico["room_type"].value_counts()
        assert set(cuenta.index) == set(BASE_PRICES)
        assert cuenta.nunique() == 1

    def test_no_faltan_datos(self, historico):
        assert not historico.isna().any().any()

    def test_la_suite_es_mas_cara_que_la_standard(self, historico):
        medias = historico.groupby("room_type")["adr"].mean()
        assert medias["Suite"] > medias["Deluxe"] > medias["Standard"]


class TestPrevision:
    def test_hay_una_fila_por_dia_previsto_y_tipo(self, prevision):
        assert len(prevision) == DAYS_FORECAST * len(BASE_PRICES)

    def test_ninguna_tarifa_se_sale_de_la_banda_autorizada(self, prevision):
        """El clip es [base x 0,7 ; base x 2,2]: es la banda que se firma."""
        for tipo, base in BASE_PRICES.items():
            tarifas = prevision[prevision["room_type"] == tipo]["suggested_adr"]
            assert tarifas.min() >= round(base * 0.7, 2) - 0.01
            assert tarifas.max() <= round(base * 2.2, 2) + 0.01

    def test_la_ocupacion_prevista_se_queda_dentro_de_su_banda(self, prevision):
        assert prevision["expected_occupancy"].min() >= 0.20
        assert prevision["expected_occupancy"].max() <= 0.97

    def test_el_revpar_previsto_es_tarifa_por_ocupacion(self, prevision):
        """Mismo redondeo a cuatro decimales que en el historico, misma cota."""
        esperado = prevision["suggested_adr"] * prevision["expected_occupancy"]
        cota = prevision["suggested_adr"] * 0.00005 + 0.01
        assert ((prevision["expected_revpar"] - esperado).abs() <= cota).all()

    def test_los_dias_de_antelacion_van_de_uno_a_sesenta(self, prevision):
        assert sorted(prevision["lead_days"].unique()) == list(range(1, DAYS_FORECAST + 1))

    def test_reservar_con_mucha_antelacion_no_lleva_recargo(self, prevision):
        """El recargo de ultima hora solo aplica dentro de los 30 dias."""
        lejos = prevision[prevision["lead_days"] >= 30]
        assert (lejos["lead_factor"] == 1.0).all()

    def test_cuanto_mas_cerca_esta_la_fecha_mayor_es_el_recargo(self, prevision):
        cerca = prevision[prevision["lead_days"] < 30]
        por_dia = cerca.groupby("lead_days")["lead_factor"].first()
        assert list(por_dia) == sorted(por_dia, reverse=True)

    def test_la_marca_de_evento_coincide_con_el_factor(self, prevision):
        assert (prevision["has_event"] == (prevision["event_factor"] > 1.0)).all()

    def test_no_faltan_datos(self, prevision):
        assert not prevision.isna().any().any()

    def test_el_precio_de_partida_es_el_del_catalogo(self, prevision):
        for tipo, base in BASE_PRICES.items():
            filas = prevision[prevision["room_type"] == tipo]
            assert (filas["base_price"] == base).all()


class TestReproducibilidad:
    def test_re_sembrando_se_obtiene_el_mismo_historico(self):
        """La semilla del modulo solo actua al importarlo.

        Sin volver a sembrar, dos llamadas seguidas dan numeros distintos: quien
        necesite reproducir un dataset tiene que hacerlo explicitamente, y este
        test lo deja por escrito.
        """
        np.random.seed(42)
        uno = build_historical()
        np.random.seed(42)
        dos = build_historical()
        assert uno.equals(dos)

    def test_sin_re_sembrar_los_numeros_cambian(self):
        np.random.seed(42)
        uno = build_historical()
        dos = build_historical()   # sin sembrar de nuevo
        assert not uno["adr"].equals(dos["adr"])
