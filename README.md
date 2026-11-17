# Proyecto Selenium IDE para SauceDemo

El archivo `Proyecto_VV_Cueva_Esteban.side` contiene los tres casos obligatorios y la suite `Suite_Regresion_Basica`.

**Integrantes:** Esteban Cueva, Stheeven Quishpe, Daniel Encalada y Jorge Ramos.  
**Asignatura:** Verificación y Validación de Software.  
**Fecha de ejecución:** 17 de noviembre de 2026.

## Casos

- CP01: autenticación válida con `assertText` sobre el título `Products`.
- CP02: autenticación inválida con `verifyText` sobre el mensaje de error.
- CP03: ordenamiento Z-A, alta temporal en carrito, espera del contador y eliminación.

## Ejecución de evidencia

`run_saucedemo_suite.py` reproduce los mismos pasos con Selenium WebDriver y guarda capturas y logs en `evidence/`. El archivo `.side` se abre directamente con Selenium IDE. La ejecución documentada obtuvo 3 de 3 casos aprobados en Google Chrome 158.0.8127.37.

Credenciales del sandbox: `standard_user` / `secret_sauce`.

## Uso del proyecto

1. Abra `Proyecto_VV_Cueva_Esteban.side` en Selenium IDE.
2. Seleccione la suite `Suite_Regresion_Basica`.
3. Ejecute la suite completa y verifique que CP01, CP02 y CP03 finalicen en estado aprobado.

Para repetir la evidencia con WebDriver, instale `requirements.txt` y ejecute `python run_saucedemo_suite.py`. El script usa Google Chrome en modo headless y conserva los resultados en `evidence/`.

## Resultado documentado

| Caso | Estado | Duración |
|---|---|---:|
| CP01 | PASSED | 14.63 s |
| CP02 | PASSED | 7.90 s |
| CP03 | PASSED | 14.55 s |
