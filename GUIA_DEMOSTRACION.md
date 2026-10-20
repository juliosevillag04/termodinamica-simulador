# ChocoLab — Guía breve de exposición para el integrante 5

**Tiempo sugerido:** 4–5 minutos, dentro de la exposición de 20–25 min del Grupo 5.

## Diapositiva de introducción (30–40 s)

- Nombre y propósito: **ChocoLab**, laboratorio virtual de gases reales.
- Fórmula central: **(P+a/v̄²)(v̄−b)=RᵤT**.
- Explica que los compañeros ya presentaron la teoría y ahora la van a comprobar numéricamente.

## Pantalla 1 · Caso experimental de Çengel (60–75 s)

1. Presiona **Cargar caso Çengel 3-13** en la barra lateral.
2. Señala el nitrógeno (N₂), T = 175 K, volumen específico = 0.00375 m³/kg.
3. Observa la presión ideal ≈ **13 851 kPa** y Van der Waals ≈ **9 471 kPa**, frente a medición de **10 000 kPa**.
4. Explica que la presión ideal se aparta mucho más del dato experimental en ese estado.
5. Despliega «Ver cómo se sustituyen los datos en las ecuaciones» para mostrar de dónde proceden los resultados.

## Pantalla 2 · Isotermas P–v (75–90 s)

1. Abre la pestaña **02 · Curvas P–v e isotermas**.
2. Muestra las curvas que representan diferentes temperaturas y el punto crítico del modelo.
3. Cambia al escenario **Punto crítico**; nota que la curva a Tc se aplana en el entorno crítico.
4. Advierte que en temperaturas inferiores a Tc pueden aparecer ramas inestables y que el simulador es un **modelo aproximado**, no un cálculo del equilibrio líquido-vapor.

## Pantalla 3 · Factor de compresibilidad Z (50–60 s)

1. Abre la pestaña **03 · Factor de compresibilidad Z**.
2. Indica que Z = Pv̄/(RᵤT): cuando Z ≈ 1 la relación se parece a la del gas ideal.
3. Presiona **Gas diluido** y observa que Z se aproxima a 1 en este escenario.
4. Señala la curva Z vs. volumen y explica que cambiar las condiciones modifica las desviaciones.

## Conclusión (15–25 s)

«Con ChocoLab podemos comprobar, con datos y gráficas, por qué una ecuación de estado real puede describir mejor ciertas condiciones que la ecuación del gas ideal. También aprendemos que cada modelo tiene límites y debe usarse de acuerdo con el estado del fluido».

## Lista de comprobación previa

- [ ] Ejecutar `INICIAR_CHOCOLAB.bat` y verificar `http://localhost:8501`.
- [ ] Confirmar que el logo ChocoLab aparece arriba a la izquierda.
- [ ] Comprobar que el caso de Çengel devuelve valores próximos a los del libro.
- [ ] Verificar las tres pestañas y que las gráficas se pueden ampliar.
- [ ] No cerrar la consola mientras el navegador esté abierto.
- [ ] Ensayar con cronómetro y tener preparada una captura de pantalla por si surge un problema técnico.
