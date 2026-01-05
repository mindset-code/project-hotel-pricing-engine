# 🏨 Proyecto 7: Motor de Precios Dinámicos para Hoteles (Revenue Management)

## Resumen del Proyecto
Este proyecto es un **Motor de Precios Dinámicos** desarrollado en Python, diseñado para simular la toma de decisiones de **Revenue Management** en la industria hotelera. Demuestra mi comprensión de los factores que influyen en la fijación de precios (demanda, estacionalidad, eventos) y mi capacidad para construir modelos algorítmicos que optimizan los ingresos.

Este proyecto es ideal para roles de **Revenue Manager**, **Business Intelligence** o **Consultor de Operaciones** en el sector de *hospitality* o viajes.

## Habilidades Demostradas
*   **Revenue Management:** Aplicación de conceptos clave como ADR (Average Daily Rate), RevPAR y optimización de ocupación.
*   **Modelado de Negocio:** Creación de un modelo basado en reglas para ajustar precios en función de la demanda y eventos.
*   **Análisis de Datos:** Uso de Python (Pandas, NumPy) para simular datos históricos y generar proyecciones.
*   **Toma de Decisiones Algorítmica:** Implementación de lógica condicional para maximizar el ingreso potencial.

## Estructura del Repositorio
*   `dynamic_pricing_engine.py`: Script principal de Python que simula los datos históricos y genera el pronóstico de precios.
*   `historical_hotel_data.csv`: Datos históricos simulados (Ocupación, ADR, RevPAR).
*   `pricing_forecast.csv`: El resultado del motor de precios: precios sugeridos para los próximos 30 días.
*   `pricing_forecast_sample.md`: Muestra de las primeras 10 filas del pronóstico.
*   `README.md`: Este archivo.

## Lógica del Motor de Precios
El motor ajusta el precio base de la habitación considerando tres factores principales:
1.  **Estacionalidad Semanal:** Aumento de precio en fines de semana (Viernes a Domingo).
2.  **Presión de Ocupación:** Aumento de precio si la ocupación promedio reciente es alta, y reducción si es baja.
3.  **Eventos Locales:** Ajuste al alza para simular picos de demanda por conferencias o eventos.

## Cómo Ejecutar
1.  Clonar el repositorio.
2.  Instalar las dependencias: `pip install pandas numpy`
3.  Ejecutar el script: `python dynamic_pricing_engine.py`
4.  Revisar el archivo `pricing_forecast.csv` para ver los precios sugeridos.
