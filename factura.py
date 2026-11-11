# -*- coding: utf-8 -*-
# FacturaRapida — facturador CLI en español para pymes.
# Solo Python 3 stdlib, sin dependencias.

import argparse
import csv
import sys
from datetime import date

# ---- Datos de tu empresa (EDITA esto) ------------------------------------
EMPRESA_NOMBRE = "Mi Empresa S.L."
EMPRESA_CIF = "B12345674H"
EMPRESA_DIR = "Calle Ejemplo 1, 28001 Madrid"
EMPRESA_BANCO = "ES91 2100 0418 4502 0005 1332"
# -------------------------------------------------------------------------

LETRAS_NIF = "TRWAGMYFPDXBNJZSQVHLCKE"
LETRAS_CIF = "JABCDEFGHI"
LETRAS_CIF_INICIO = "ABCDEFGHJNPQRSUVW"


def validar_nif_cif(nif: str) -> bool:
    """Valida NIF, CIF o NIE según el algoritmo oficial."""
    nif = nif.strip().upper()
    if len(nif) == 9 and nif[0] in "XYZ" and nif[1:8].isdigit():
        num = int("012"["XYZ".index(nif[0])] + nif[1:8])
        return LETRAS_NIF[num % 23] == nif[8]
    if len(nif) == 9 and nif[0] in LETRAS_CIF_INICIO and nif[1:8].isdigit():
        d = [int(c) for c in nif[1:8]]
        s = sum(d[0::2])
        for x in d[1::2]:
            x2 = x * 2
            s += (x2 - 9) if x2 >= 10 else x2
        control = (10 - s % 10) % 10
        ultimo = nif[8]
        if ultimo.isdigit():
            return ultimo == str(control)
        if control == 0:
            return False
        return ultimo == LETRAS_CIF[control - 1]
    if len(nif) == 9 and nif[:8].isdigit():
        return LETRAS_NIF[int(nif[:8]) % 23] == nif[8]
    return False


def leer_lineas(ruta_csv: str):
    """Lee CSV (separador ';', sin cabecera): descripcion;cantidad;precio;iva."""
    lineas = []
    try:
        with open(ruta_csv, newline="", encoding="utf-8-sig") as f:
            for i, fila in enumerate(csv.reader(f, delimiter=";"), start=1):
                if not fila or not any(c.strip() for c in fila):
                    continue
                if len(fila) < 3:
                    sys.exit(f"Error: la línea {i} del CSV tiene menos de 3 columnas.")
                desc = fila[0].strip() or "Línea"
                try:
                    cant = float(fila[1].replace(",", "."))
                    precio = float(fila[2].replace(",", "."))
                except ValueError:
                    sys.exit(f"Error: la línea {i} tiene cantidad o precio no numéricos.")
                iva = 21
                if len(fila) >= 4 and fila[3].strip():
                    try:
                        iva = int(float(fila[3].replace(",", ".")))
                    except ValueError:
                        sys.exit(f"Error: la línea {i} tiene un IVA no numérico.")
                    if iva not in (21, 10, 4, 0):
                        sys.exit(f"Error: la línea {i} tiene un IVA no válido ({iva}). Usa 21, 10, 4 o 0.")
                lineas.append({"desc": desc, "cant": cant, "precio": precio, "iva": iva})
    except FileNotFoundError:
        sys.exit(f"Error: no se encuentra el archivo {ruta_csv}.")
    if not lineas:
        sys.exit("Error: el CSV no contiene líneas válidas.")
    return lineas


def euros(x: float) -> str:
    s = f"{x:,.2f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".") + " €"


def esc(s: str) -> str:
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def render_html(num: str, nif: str, nombre: str, fecha: str, lineas) -> str:
    filas = []
    base = total_iva = 0.0
    desgs = {}
    for l in lineas:
        b = l["cant"] * l["precio"]
        i = b * l["iva"] / 100
        base += b
        total_iva += i
        desgs.setdefault(l["iva"], [0.0, 0.0])
        desgs[l["iva"]][0] += b
        desgs[l["iva"]][1] += i
        filas.append(
            f"<tr><td>{esc(l['desc'])}</td><td class='num'>{l['cant']:g}</td>"
            f"<td class='num'>{euros(l['precio'])}</td><td class='num'>{l['iva']}%</td>"
            f"<td class='num'>{euros(b)}</td></tr>"
        )
    total = base + total_iva
    desgs_html = "".join(
        f"<tr><td>IVA {k}%</td><td class='num'>{euros(v[0])}</td>"
        f"<td class='num'>{euros(v[1])}</td></tr>"
        for k, v in sorted(desgs.items(), reverse=True)
    )
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>Factura {esc(num)}</title>
<style>
@page {{ size: A4; margin: 20mm; }}
body {{ font-family: 'Segoe UI', Arial, sans-serif; color: #222; font-size: 13px; }}
h1 {{ font-size: 22px; margin: 0; color: #1a3c5e; }}
table {{ border-collapse: collapse; width: 100%; }}
th, td {{ border-bottom: 1px solid #ddd; padding: 6px 8px; text-align: left; }}
th {{ background: #1a3c5e; color: #fff; }}
.num {{ text-align: right; }}
.caja {{ width: 100%; }}
.derecha {{ text-align: right; }}
.tot {{ width: 45%; margin-left: auto; }}
.tot td {{ border: none; padding: 3px 8px; }}
.grand {{ font-size: 16px; font-weight: bold; border-top: 2px solid #1a3c5e !important; }}
.gris {{ color: #666; font-size: 11px; }}
</style>
</head>
<body>
<div class="caja">
  <div class="derecha">
    <h1>FACTURA {esc(num)}</h1>
    <p class="gris">Fecha: {esc(fecha)}</p>
  </div>
  <p><strong>{esc(EMPRESA_NOMBRE)}</strong><br>
  {esc(EMPRESA_CIF)} · {esc(EMPRESA_DIR)}<br>
  Banco: {esc(EMPRESA_BANCO)}</p>
  <hr>
  <p><strong>Cliente</strong><br>{esc(nombre)} ({esc(nif)})</p>
</div>
<table>
<tr><th>Descripción</th><th>Cantidad</th><th>Precio</th><th>IVA</th><th>Importe</th></tr>
{''.join(filas)}
</table>
<table class="tot">
{desgs_html}
<tr><td><strong>Base imponible</strong></td><td class="num"><strong>{euros(base)}</strong></td><td></td></tr>
<tr><td><strong>Total IVA</strong></td><td class="num"><strong>{euros(total_iva)}</strong></td><td></td></tr>
<tr class="grand"><td>TOTAL</td><td class="num">{euros(total)}</td><td></td></tr>
</table>
<p class="gris">Gracias por su confianza. Formas de pago: transferencia al IBAN indicado.
Plazo de pago: 30 días desde la fecha de la factura.</p>
</body>
</html>
"""


def selftest() -> int:
    ok = True
    # 1) NIF, CIF y NIE válidos
    if (validar_nif_cif("12345678Z") and validar_nif_cif("B12345674H")
            and validar_nif_cif("F06107919") and validar_nif_cif("X1234567L")):
        print("PASS 1) NIF/CIF/NIE válidos aceptados")
    else:
        print("FAIL 1) NIF/CIF/NIE válidos no aceptados")
        ok = False
    # 2) NIF, CIF y NIE inválidos
    if not (validar_nif_cif("12345678A") or validar_nif_cif("B123456741")
            or validar_nif_cif("F06107910") or validar_nif_cif("X1234567K")):
        print("PASS 2) NIF/CIF/NIE inválidos rechazados")
    else:
        print("FAIL 2) NIF/CIF/NIE inválidos no rechazados")
        ok = False
    # 3) Totales: 2 x 50,00 con IVA 21% -> 121,00
    base = 2 * 50.0
    total = base + base * 21 / 100
    if euros(total) == "121,00 €":
        print("PASS 3) Total 2x50,00 + 21% = 121,00 €")
    else:
        print(f"FAIL 3) Total inesperado: {euros(total)}")
        ok = False
    if ok:
        print("SELFTEST OK")
        return 0
    return 1


def main() -> int:
    ap = argparse.ArgumentParser(description="FacturaRapida: factura HTML A4 en un comando.")
    ap.add_argument("--numero", help="Número de factura, p.ej. F-2026-001")
    ap.add_argument("--cliente-nif", help="NIF, CIF o NIE del cliente")
    ap.add_argument("--cliente-nombre", help="Nombre del cliente")
    ap.add_argument("--lineas", help="CSV: descripcion;cantidad;precio;iva (21|10|4|0)")
    ap.add_argument("--output", default="factura.html", help="Archivo HTML de salida")
    ap.add_argument("--fecha", default=date.today().isoformat())
    ap.add_argument("--test", action="store_true", help="Ejecuta el autotest y termina")
    args = ap.parse_args()

    if args.test:
        return selftest()

    for req in ("numero", "cliente_nif", "cliente_nombre", "lineas"):
        if not getattr(args, req):
            sys.exit(f"Falta el parámetro obligatorio --{req.replace('_', '-')}.")
    if not validar_nif_cif(args.cliente_nif):
        sys.exit(f"Error: NIF/CIF no válido: {args.cliente_nif}")

    lineas = leer_lineas(args.lineas)
    html = render_html(args.numero, args.cliente_nif, args.cliente_nombre, args.fecha, lineas)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Factura {args.numero} generada: {args.output}")
    print("Ábrela en el navegador y pulsa Ctrl+P para guardarla en PDF.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
