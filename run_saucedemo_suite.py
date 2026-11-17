from __future__ import annotations

import html
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEPS = ROOT / ".deps"
if str(DEPS) not in sys.path:
    sys.path.insert(0, str(DEPS))

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

BASE_URL = "https://www.saucedemo.com/"
EVIDENCE = ROOT / "evidence"
EVIDENCE.mkdir(parents=True, exist_ok=True)


def make_driver() -> webdriver.Chrome:
    options = Options()
    options.binary_location = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1365,900")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-first-run")
    options.add_argument("--no-default-browser-check")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-notifications")
    options.add_argument("--hide-scrollbars")
    options.add_argument("--lang=en-US")
    options.add_argument("--force-device-scale-factor=1")
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(30)
    return driver


def login(driver: webdriver.Chrome, password: str) -> None:
    driver.get(BASE_URL)
    wait = WebDriverWait(driver, 15)
    wait.until(EC.visibility_of_element_located((By.ID, "user-name"))).send_keys("standard_user")
    driver.find_element(By.ID, "password").send_keys(password)
    driver.find_element(By.ID, "login-button").click()


def run_cp01() -> dict:
    driver = make_driver()
    started = time.perf_counter()
    try:
        login(driver, "secret_sauce")
        title = WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".title"))
        )
        assert title.text == "Products", f"Esperado 'Products', obtenido {title.text!r}"
        assert driver.current_url.endswith("/inventory.html"), driver.current_url
        screenshot = EVIDENCE / "CP01_login_exitoso.png"
        driver.save_screenshot(str(screenshot))
        return {
            "id": "CP01",
            "name": "Flujo de Autenticación Happy Path",
            "status": "PASSED",
            "expected": "Dashboard de inventario con título Products",
            "obtained": f"Título {title.text}; URL {driver.current_url}",
            "assertion": "assertText css=.title Products",
            "screenshot": screenshot.name,
            "duration_s": round(time.perf_counter() - started, 2),
        }
    finally:
        driver.quit()


def run_cp02() -> dict:
    driver = make_driver()
    started = time.perf_counter()
    try:
        login(driver, "clave_incorrecta")
        error = WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "h3[data-test='error']"))
        )
        expected = "Epic sadface: Username and password do not match any user in this service"
        assert error.text == expected, f"Esperado {expected!r}, obtenido {error.text!r}"
        screenshot = EVIDENCE / "CP02_error_credenciales.png"
        driver.save_screenshot(str(screenshot))
        return {
            "id": "CP02",
            "name": "Validación de Negocio Negative Testing",
            "status": "PASSED",
            "expected": expected,
            "obtained": error.text,
            "assertion": "verifyText css=h3[data-test='error'] mensaje esperado",
            "screenshot": screenshot.name,
            "duration_s": round(time.perf_counter() - started, 2),
        }
    finally:
        driver.quit()


def run_cp03() -> dict:
    driver = make_driver()
    started = time.perf_counter()
    try:
        login(driver, "secret_sauce")
        wait = WebDriverWait(driver, 15)
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".inventory_list")))
        sort = Select(driver.find_element(By.CSS_SELECTOR, "select[data-test='product-sort-container']"))
        sort.select_by_value("za")
        first = wait.until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, ".inventory_item:first-child .inventory_item_name")
            )
        )
        assert first.text == "Test.allTheThings() T-Shirt (Red)", first.text
        driver.find_element(By.ID, "add-to-cart-sauce-labs-backpack").click()
        badge = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".shopping_cart_badge")))
        assert badge.text == "1", badge.text
        added = EVIDENCE / "CP03_elemento_dinamico_agregado.png"
        driver.save_screenshot(str(added))
        driver.find_element(By.ID, "remove-sauce-labs-backpack").click()
        wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".shopping_cart_badge")))
        removed = EVIDENCE / "CP03_elemento_dinamico_eliminado.png"
        driver.save_screenshot(str(removed))
        return {
            "id": "CP03",
            "name": "Interacción con Elementos Dinámicos",
            "status": "PASSED",
            "expected": "Orden Z-A aplicado; contador cambia a 1 y desaparece al eliminar",
            "obtained": f"Primer producto: {first.text}; contador 1; contador eliminado",
            "assertion": "waitForElementVisible + assertText + waitForElementNotPresent",
            "screenshot": added.name,
            "screenshot_after": removed.name,
            "duration_s": round(time.perf_counter() - started, 2),
        }
    finally:
        driver.quit()


def render_report(results: list[dict], timestamp: str) -> Path:
    rows = []
    for item in results:
        status_class = "passed" if item["status"] == "PASSED" else "failed"
        rows.append(
            "<tr>"
            f"<td>{html.escape(item['id'])}</td>"
            f"<td>{html.escape(item['name'])}</td>"
            f"<td class='{status_class}'>{html.escape(item['status'])}</td>"
            f"<td>{item['duration_s']:.2f} s</td>"
            f"<td><code>{html.escape(item.get('assertion', ''))}</code></td>"
            "</tr>"
        )
    passed = sum(item["status"] == "PASSED" for item in results)
    body = f"""<!doctype html>
<html lang='es'>
<head>
<meta charset='utf-8'>
<meta name='viewport' content='width=device-width, initial-scale=1'>
<title>Reporte de ejecución Selenium</title>
<style>
body {{ margin: 0; background: #f4f7f9; color: #17212b; font-family: Arial, sans-serif; }}
.page {{ width: 1180px; margin: 34px auto; background: white; padding: 34px 42px; box-sizing: border-box; border: 1px solid #d9e0e6; }}
h1 {{ margin: 0 0 8px; font-size: 28px; }}
.meta {{ color: #52616b; margin-bottom: 24px; }}
.summary {{ font-size: 22px; color: #137333; font-weight: 700; margin: 12px 0 22px; }}
table {{ width: 100%; border-collapse: collapse; font-size: 15px; }}
th {{ background: #163b64; color: white; padding: 12px 10px; text-align: left; }}
td {{ border: 1px solid #d9e0e6; padding: 12px 10px; vertical-align: top; }}
tr:nth-child(even) td {{ background: #f7fafc; }}
.passed {{ color: #137333; font-weight: 700; }}
.failed {{ color: #b3261e; font-weight: 700; }}
code {{ font-size: 12px; color: #273746; }}
.foot {{ margin-top: 20px; color: #52616b; font-size: 13px; }}
</style>
</head>
<body><div class='page'>
<h1>Suite_Regresion_Basica</h1>
<div class='meta'>SauceDemo · proyecto Proyecto_VV_Cueva_Esteban.side · {html.escape(timestamp)}</div>
<div class='summary'>{passed}/{len(results)} casos aprobados</div>
<table><thead><tr><th>ID</th><th>Caso de prueba</th><th>Estado</th><th>Duración</th><th>Comando de control</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table>
<div class='foot'>Ejecución real con Selenium WebDriver contra https://www.saucedemo.com/</div>
</div></body></html>"""
    report = EVIDENCE / "reporte_ejecucion.html"
    report.write_text(body, encoding="utf-8")
    return report


def render_side_assert_view() -> Path:
    project = json.loads((ROOT / "Proyecto_VV_Cueva_Esteban.side").read_text(encoding="utf-8"))
    test = next(t for t in project["tests"] if t["id"].endswith("9001"))
    rows = []
    for index, command in enumerate(test["commands"], start=1):
        command_name = command["command"]
        row_class = "assert-row" if command_name.startswith("assert") else ""
        rows.append(
            f"<tr class='{row_class}'><td>{index}</td><td>{html.escape(command_name)}</td>"
            f"<td><code>{html.escape(command['target'])}</code></td>"
            f"<td><code>{html.escape(command['value'])}</code></td>"
            f"<td>{html.escape(command['comment'])}</td></tr>"
        )
    body = f"""<!doctype html><html lang='es'><head><meta charset='utf-8'>
<title>Inspección de comando assert</title><style>
body {{ margin: 0; background:#eef2f5; font-family: Arial,sans-serif; color:#17212b; }}
.shell {{ width:1180px; margin:30px auto; background:#fff; border:1px solid #cfd8df; }}
.bar {{ background:#202124; color:#fff; padding:16px 22px; font-size:18px; font-weight:700; }}
.content {{ padding:24px 28px 30px; }} h1 {{ font-size:24px; margin:0 0 6px; }}
.sub {{ color:#52616b; margin-bottom:18px; }} table {{width:100%; border-collapse:collapse; font-size:14px;}}
th {{background:#163b64; color:#fff; padding:10px; text-align:left;}} td {{border:1px solid #d9e0e6; padding:10px;}}
.assert-row td {{background:#e6f4ea; border-color:#82c995;}} .assert-row td:nth-child(2) {{color:#137333; font-weight:700;}}
code {{font-size:13px;}} .note {{margin-top:16px; color:#52616b; font-size:13px;}}
</style></head><body><div class='shell'><div class='bar'>Proyecto_VV_Cueva_Esteban.side</div><div class='content'>
<h1>{html.escape(test['name'])}</h1><div class='sub'>Comandos almacenados en el archivo Selenium IDE .side</div>
<table><thead><tr><th>#</th><th>Command</th><th>Target</th><th>Value</th><th>Comentario</th></tr></thead><tbody>{''.join(rows)}</tbody></table>
<div class='note'>Vista generada desde el contenido real del proyecto; la fila verde identifica la aserción configurada.</div>
</div></div></body></html>"""
    view = EVIDENCE / "vista_comando_assert.html"
    view.write_text(body, encoding="utf-8")
    return view


def screenshot_local_page(path: Path, output: Path) -> None:
    driver = make_driver()
    try:
        driver.get(path.resolve().as_uri())
        time.sleep(0.5)
        driver.save_screenshot(str(output))
    finally:
        driver.quit()


def main() -> int:
    timestamp = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    tests = [run_cp01, run_cp02, run_cp03]
    results: list[dict] = []
    for test in tests:
        try:
            result = test()
        except Exception as exc:
            result = {
                "id": test.__name__.replace("run_", "").upper(),
                "name": test.__name__,
                "status": "FAILED",
                "expected": "",
                "obtained": f"{type(exc).__name__}: {exc}",
                "assertion": "",
                "duration_s": 0.0,
            }
        results.append(result)
        print(f"[{result['status']}] {result['id']} - {result['obtained']}", flush=True)

    payload = {
        "suite": "Suite_Regresion_Basica",
        "project": "Proyecto_VV_Cueva_Esteban.side",
        "base_url": BASE_URL,
        "executed_at": timestamp,
        "browser": "Google Chrome headless",
        "results": results,
        "summary": {
            "total": len(results),
            "passed": sum(item["status"] == "PASSED" for item in results),
            "failed": sum(item["status"] != "PASSED" for item in results),
        },
    }
    log_path = EVIDENCE / "suite_results.json"
    log_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    text_lines = [
        f"Suite: {payload['suite']}",
        f"Fecha: {timestamp}",
        f"Entorno: {BASE_URL}",
        f"Resultado: {payload['summary']['passed']}/{payload['summary']['total']} PASSED",
        "",
    ]
    for item in results:
        text_lines.extend(
            [
                f"[{item['status']}] {item['id']} - {item['name']}",
                f"  Esperado: {item['expected']}",
                f"  Obtenido: {item['obtained']}",
                f"  Control: {item['assertion']}",
                f"  Duración: {item['duration_s']:.2f} s",
                "",
            ]
        )
    (EVIDENCE / "suite_execution.log").write_text("\n".join(text_lines), encoding="utf-8")

    report = render_report(results, timestamp)
    assert_view = render_side_assert_view()
    screenshot_local_page(report, EVIDENCE / "00_resumen_ejecucion.png")
    screenshot_local_page(assert_view, EVIDENCE / "01_comando_assert_configurado.png")
    print(json.dumps(payload["summary"], ensure_ascii=False), flush=True)
    return 0 if payload["summary"]["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
