# FacturaRapida

Facturador de bolsillo para pymes españolas: genera facturas HTML listas para
imprimir en PDF con un solo comando. Sin instalaciones, sin suscripción,
sin conexión a internet.

## Qué hace

- Valida automáticamente el DNI/NIF o CIF del cliente (con letra/dígito de
  control): adiós a las facturas devueltas por letra mal escrita.
- Calcula el IVA (21%, 10%, 4% y 0%), la base imponible y los totales con
  formato español (121,00 €).
- Genera una factura A4 elegante que abres en el navegador y guardas en PDF
  con Ctrl+P.

## Requisitos

Python 3 (única dependencia: ninguna, usa solo la biblioteca estándar).
En Windows: <https://www.python.org/downloads/> (marca "Add to PATH").

## Uso

```
python factura.py --numero F-2026-001 --cliente-nif 12345678Z --cliente-nombre "Cliente SL" --lineas ejemplo.csv --output factura.html
```

O en Windows, doble clic en `lanzar.bat` con los mismos parámetros:

```
lanzar.bat --numero F-2026-001 --cliente-nif 12345678Z --cliente-nombre "Cliente SL" --lineas ejemplo.csv
```

### Parámetros

| Parámetro | Descripción |
|---|---|
| `--numero` | Número de factura (p.ej. `F-2026-001`) |
| `--cliente-nif` | DNI o CIF del cliente |
| `--cliente-nombre` | Nombre o razón social |
| `--lineas` | Archivo CSV con las líneas de la factura |
| `--output` | HTML de salida (por defecto `factura.html`) |
| `--fecha` | Fecha (por defecto, hoy) |
| `--test` | Ejecuta el autotest interno |

### Formato del CSV

Separador **punto y coma** (se abre directamente en Excel español),
sin cabecera:

```
descripcion;cantidad;precio;iva
```

Ejemplo (`ejemplo.csv`):

```
Producto A;2;50.00;21
Producto B;1;30.00;10
Servicio C;3;15.00;4
```

La columna `iva` es opcional: si falta se asume **21**. Valores: 21, 10, 4 o 0.

### Datos de tu empresa

Edita las constantes al inicio de `factura.py` (`EMPRESA_NOMBRE`,
`EMPRESA_CIF`, `EMPRESA_DIR`, `EMPRESA_BANCO`).

## Pregunta frecuentes

- **¿Cómo paso la factura a PDF?** Abre el `.html` en cualquier navegador y
  pulsa Ctrl+P → "Guardar como PDF". Ajustado a A4 por defecto.
- **¿Qué pasa si el NIF no es válido?** El programa avisa con un mensaje en
  español y no genera la factura.
- **¿Funciona sin internet?** Sí, al 100%.
- **¿Mis datos salen de mi ordenador?** No. No hay ni un solo envío de datos.

## Autotest

```
python factura.py --test
```

## Licencia

MIT — ver `LICENSE`.

## Comprar

FacturaRapida a **9 EUR** (una vez, tuyo para siempre, licencia de uso):

**<https://payhip.com/b/5JhQO>**
