from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
EVIDENCE = ROOT / "evidence"
WIDTH, HEIGHT = 1365, 900


def font(size: int, bold: bool = False, mono: bool = False) -> ImageFont.FreeTypeFont:
    if mono:
        path = r"C:\Windows\Fonts\consola.ttf"
    elif bold:
        path = r"C:\Windows\Fonts\arialbd.ttf"
    else:
        path = r"C:\Windows\Fonts\arial.ttf"
    return ImageFont.truetype(path, size=size)


def wrapped(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, width: int,
            fnt: ImageFont.FreeTypeFont, fill: str, line_gap: int = 4) -> int:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if draw.textlength(candidate, font=fnt) <= width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    x, y = xy
    bbox = draw.textbbox((0, 0), "Ag", font=fnt)
    line_height = bbox[3] - bbox[1] + line_gap
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += line_height
    return y


def make_summary() -> None:
    data = json.loads((EVIDENCE / "suite_results.json").read_text(encoding="utf-8"))
    image = Image.new("RGB", (WIDTH, HEIGHT), "#F2F5F7")
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((55, 42, WIDTH - 55, HEIGHT - 42), radius=8, fill="white", outline="#D5DDE3", width=2)
    draw.text((95, 76), "Suite_Regresion_Basica", font=font(32, bold=True), fill="#17212B")
    draw.text((95, 123), "Ejecución real con Selenium WebDriver · SauceDemo", font=font(18), fill="#52616B")
    draw.text((95, 153), f"Proyecto: {data['project']} · {data['executed_at']}", font=font(16), fill="#52616B")
    draw.rounded_rectangle((95, 198, 440, 267), radius=8, fill="#E6F4EA", outline="#82C995", width=2)
    draw.text((120, 217), f"{data['summary']['passed']}/{data['summary']['total']} CASOS APROBADOS", font=font(23, bold=True), fill="#137333")

    left, top, right = 95, 305, WIDTH - 95
    columns = [left, left + 105, left + 515, left + 665, right]
    draw.rectangle((left, top, right, top + 52), fill="#163B64")
    headers = ["ID", "Caso de prueba", "Estado", "Control automatizado"]
    for i, header in enumerate(headers):
        draw.text((columns[i] + 14, top + 15), header, font=font(16, bold=True), fill="white")

    row_h = 132
    for row_index, item in enumerate(data["results"]):
        y1 = top + 52 + row_index * row_h
        y2 = y1 + row_h
        fill = "#F8FAFC" if row_index % 2 else "white"
        draw.rectangle((left, y1, right, y2), fill=fill, outline="#D9E0E6", width=1)
        for x in columns[1:-1]:
            draw.line((x, y1, x, y2), fill="#D9E0E6", width=1)
        draw.text((columns[0] + 16, y1 + 20), item["id"], font=font(18, bold=True), fill="#17212B")
        wrapped(draw, (columns[1] + 14, y1 + 16), item["name"], columns[2] - columns[1] - 28, font(17, bold=True), "#17212B")
        draw.rounded_rectangle((columns[2] + 15, y1 + 16, columns[3] - 15, y1 + 54), radius=6, fill="#E6F4EA")
        draw.text((columns[2] + 35, y1 + 25), item["status"], font=font(16, bold=True), fill="#137333")
        draw.text((columns[2] + 22, y1 + 78), f"{item['duration_s']:.2f} s", font=font(15), fill="#52616B")
        wrapped(draw, (columns[3] + 14, y1 + 16), item["assertion"], right - columns[3] - 28, font(15, mono=True), "#273746")

    draw.text((95, 788), "Resultado consolidado generado desde suite_results.json. No corresponde a la interfaz de Selenium IDE.", font=font(14), fill="#52616B")
    image.save(EVIDENCE / "00_resumen_ejecucion.png", quality=95)


def make_assert_view() -> None:
    project = json.loads((ROOT / "Proyecto_VV_Cueva_Esteban.side").read_text(encoding="utf-8"))
    test = project["tests"][0]
    image = Image.new("RGB", (WIDTH, HEIGHT), "#EEF2F5")
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((45, 30, WIDTH - 45, HEIGHT - 30), radius=8, fill="white", outline="#CFD8DF", width=2)
    draw.rectangle((45, 30, WIDTH - 45, 92), fill="#202124")
    draw.text((74, 49), "Proyecto_VV_Cueva_Esteban.side", font=font(22, bold=True), fill="white")
    draw.text((76, 122), test["name"], font=font(27, bold=True), fill="#17212B")
    draw.text((76, 163), "Vista del contenido real del proyecto Selenium IDE .side", font=font(17), fill="#52616B")

    left, top, right = 76, 215, WIDTH - 76
    columns = [left, left + 62, left + 255, left + 610, left + 800, right]
    headers = ["#", "Command", "Target", "Value", "Comentario"]
    draw.rectangle((left, top, right, top + 48), fill="#163B64")
    for i, header in enumerate(headers):
        draw.text((columns[i] + 10, top + 14), header, font=font(15, bold=True), fill="white")

    row_h = 82
    for idx, command in enumerate(test["commands"], start=1):
        y1 = top + 48 + (idx - 1) * row_h
        y2 = y1 + row_h
        is_assert = command["command"].startswith("assert")
        fill = "#E6F4EA" if is_assert else ("#F8FAFC" if idx % 2 == 0 else "white")
        border = "#82C995" if is_assert else "#D9E0E6"
        draw.rectangle((left, y1, right, y2), fill=fill, outline=border, width=2 if is_assert else 1)
        for x in columns[1:-1]:
            draw.line((x, y1, x, y2), fill=border, width=1)
        draw.text((columns[0] + 20, y1 + 25), str(idx), font=font(15), fill="#17212B")
        cmd_fill = "#137333" if is_assert else "#17212B"
        draw.text((columns[1] + 10, y1 + 24), command["command"], font=font(15, bold=is_assert), fill=cmd_fill)
        wrapped(draw, (columns[2] + 10, y1 + 13), command["target"], columns[3] - columns[2] - 20, font(13, mono=True), "#273746")
        wrapped(draw, (columns[3] + 10, y1 + 13), command["value"], columns[4] - columns[3] - 20, font(13, mono=True), "#273746")
        wrapped(draw, (columns[4] + 10, y1 + 12), command["comment"], right - columns[4] - 20, font(14), "#273746")

    draw.text((76, 800), "La fila verde identifica el comando assertText configurado en CP01. Esta es una inspección del archivo .side, no una captura de la extensión.", font=font(14), fill="#52616B")
    image.save(EVIDENCE / "01_comando_assert_configurado.png", quality=95)


if __name__ == "__main__":
    make_summary()
    make_assert_view()
