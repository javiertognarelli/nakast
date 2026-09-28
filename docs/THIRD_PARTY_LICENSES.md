<div class="cover" align="center">

# NAKAST

<p class="cover-subtitle">Compilado de Servicios y Licencias</p>

<p class="cover-institution">UNIVERSIDAD DE VALPARAÍSO</p>

<p class="cover-authors">Autores:<br>
JAVIER ALEJANDRO TOGNARELLI SANTIAGO<br>
DANIEL FERNANDO ESCOBAR ARAYA<br>
FERNANDO ANDRÉS AMAYA INZUNZA</p>

<p class="cover-date">SEPTIEMBRE 2026</p>

</div>

<div class="page-break"></div>

## 1. Introducción

El presente documento tiene como propósito declarar de forma transparente todos los servicios
externos, bibliotecas de código abierto y licencias de software utilizados en la plataforma
NAKAST.

NAKAST (*Nanopore Amplicon KMA Allele Sequence Typing*) es un pipeline de línea de comandos, desarrollado en Nextflow, que determina perfiles
MLST a partir de lecturas de secuenciación Oxford Nanopore. Se ejecuta en el equipo del
usuario y no cuenta con componentes de servidor, interfaz web ni base de datos propia.

Las versiones y licencias de las secciones 4.1 a 4.3 se obtuvieron de los metadatos
(`conda-meta`) de las compilaciones exactas que el pipeline fija en sus directivas `conda`, y
no de memoria ni de sitios web de terceros. Los términos de PubMLST de la sección 2.1 se
consultaron en el sitio oficial del proveedor en septiembre de 2026.

## 2. Servicios Externos

### 2.1 PubMLST — API REST

- **Proveedor:** PubMLST, Universidad de Oxford (Reino Unido).
- **Modelo/Versión:** API REST (`https://rest.pubmlst.org`), consultada con la clave de
  acceso a datos (*data access key*) de la cuenta de cada usuario, enviada en el encabezado
  `X-API-Key`. No tiene versión fija: se consulta en cada corrida.
- **Uso en la obra:** descarga del esquema MLST de cada especie analizada (secuencias de
  alelos, lista de loci y tabla de perfiles ST), que NAKAST indexa y usa como referencia para
  tipificar las muestras.
- **Tipo de licencia:** acceso mediante clave de acceso a datos personal, sujeto a los
  términos y condiciones del sitio, que distinguen dos tipos de datos:
  - *Depositados hasta el 31 de diciembre de 2024:* pueden descargarse, usarse y
    redistribuirse sin restricción, incluido el uso comercial, sujeto solo a la cita y el
    reconocimiento correspondientes.
  - *Depositados desde el 1 de enero de 2025:* solo pueden usarse para investigación
    académica no comercial o para vigilancia en salud pública, y no pueden redistribuirse
    ni incorporarse a bases de datos o servicios públicos o comerciales. Su uso comercial
    requiere una licencia de la Universidad de Oxford.

  La clave es personal y **no se distribuye con la obra**: cada usuario debe crear la suya en
  su propia cuenta y almacenarla en su equipo. NAKAST tampoco redistribuye datos de PubMLST;
  los descarga en cada corrida en el equipo del usuario. Sin clave, la obra puede operar en
  modo anónimo (`--pubmlst_anonymous`), limitado a los datos anteriores a 2025.
- **Modelo de cobro:** gratuito. La cuenta y la clave de acceso no tienen costo.
- **URL Oficial:** <https://pubmlst.org> · Términos: <https://pubmlst.org/terms-conditions>

Los términos exigen incluir el siguiente reconocimiento en toda publicación basada en datos
de PubMLST, además de citar a Jolley et al., *Wellcome Open Res* 2018, 3:124:

> This publication made use of the PubMLST website (https://pubmlst.org/) sited at the
> University of Oxford. The development of that website was funded by the Wellcome Trust.

### 2.2 Canales de paquetes conda-forge y Bioconda

- **Proveedor:** comunidad conda-forge y proyecto Bioconda, con los paquetes alojados en
  anaconda.org.
- **Modelo/Versión:** canales `conda-forge` y `bioconda`. Las versiones de cada paquete están
  fijadas en la obra (sección 4).
- **Uso en la obra:** distribución e instalación automática de las herramientas que ejecuta
  cada proceso del pipeline.
- **Tipo de licencia:** canales comunitarios de libre acceso. Cada paquete conserva la
  licencia de su proyecto original, detallada en la sección 4. Todos los paquetes se declaran
  desde estos dos canales y no desde el canal `defaults` de Anaconda, cuyo uso institucional
  puede estar sujeto a pago.
- **Modelo de cobro:** gratuito.
- **URL Oficial:** <https://conda-forge.org> · <https://bioconda.github.io>

## 3. Infraestructura de Despliegue

NAKAST no tiene componentes de servidor (*backend*) ni de interfaz web (*frontend*): se
ejecuta desde la línea de comandos en el equipo del usuario. La tabla adapta la plantilla a
esa arquitectura.

| Componente | Plataforma | Plan | Modelo de Costo |
|------|-----------|-----|-------|
| Ejecución del pipeline | Equipo del usuario, sistema operativo Linux | No aplica | Sin costo de licencia; hardware propio del usuario |
| Motor de flujo de trabajo | Nextflow, ejecutor local | Código abierto | Gratuito |
| Gestión de ambientes | Conda / Mamba, canales conda-forge y Bioconda | Código abierto | Gratuito |
| Distribución del código | GitHub (`github.com/javiertognarelli/nakast`) | Repositorio público | Gratuito |
| Base de Datos | No aplica: no hay base propia; los esquemas se obtienen de PubMLST en cada corrida | No aplica | Gratuito |

## 4. Bibliotecas de Código Abierto (Open Source)

NAKAST invoca cada herramienta como un proceso independiente del sistema operativo. No enlaza
con sus bibliotecas, no incorpora su código fuente y no redistribuye sus binarios: los
ambientes se construyen en el equipo del usuario a partir de los canales de la sección 2.2.

### 4.1 Herramientas de ejecución y bioinformáticas

| Paquete | Versión | Licencia | Uso |
|------|----|------|--------------|
| Nextflow | 25.10.2 | Apache-2.0 | Motor que orquesta y ejecuta el flujo de trabajo |
| KMA | 1.6.8 | Apache-2.0 | Indexación de la base de alelos y alineamiento de lecturas |
| Filtlong | 0.3.1 | GPL-3.0-or-later | Filtrado de lecturas por longitud y calidad |
| Chopper | 0.12.0 | MIT | Filtrado de lecturas por calidad Phred |
| NanoPlot | 1.46.2 | MIT | Control de calidad de lecturas por muestra |
| MultiQC | 1.33 | GPL-3.0-or-later | Reporte agregado de control de calidad |
| GNU coreutils | 9.5 | GPL-3.0-or-later | Concatenación de archivos FASTQ |
| gzip | 1.12 | GPL-3.0-or-later | Compresión y descompresión de lecturas |

### 4.2 Lenguaje y bibliotecas de Python

| Paquete | Versión | Licencia | Uso |
|------|----|------|--------------|
| Python | 3.13.11 | Python-2.0 (PSF) | Lenguaje de los scripts de validación, descarga y reporte |
| pandas | 2.3.3 | BSD-3-Clause | Lectura de tablas, llamado de alelos y asignación de ST |
| NumPy | 2.4.0 | BSD-3-Clause | Cálculo del puntaje de confianza de cada alelo |
| openpyxl | 3.1.5 | MIT | Escritura del reporte final en formato Excel |

Los scripts usan además solo módulos de la biblioteca estándar de Python (`json`, `urllib`,
`argparse`, `os`, `glob`, `sys`, `time`, `re`, `concurrent.futures`), cubiertos por la misma
licencia de Python.

### 4.3 Herramientas de instalación

Se usan solo para construir los ambientes de ejecución. No forman parte de la obra ni se
distribuyen con ella.

| Paquete | Versión | Licencia | Uso |
|------|----|------|--------------|
| conda | 26.1.1 | BSD-3-Clause | Creación de los ambientes de cada proceso |
| mamba | 2.4.0 | BSD-3-Clause | Resolución rápida de dependencias al crear los ambientes |

### 4.4 Nota sobre los componentes con licencia GPL

Cuatro componentes (Filtlong, MultiQC, GNU coreutils y gzip) tienen licencia
GPL-3.0-or-later, de tipo *copyleft*. Como NAKAST solo los invoca como programas separados,
comunicándose con ellos mediante archivos y flujos estándar, la relación constituye una
**mera agregación** según la interpretación de la propia Free Software Foundation
(<https://www.gnu.org/licenses/gpl-faq.html#MereAggregation>). Las obligaciones de *copyleft*
no se extienden, por lo tanto, al código fuente de NAKAST.

## 5. Resumen Ejecutivo

NAKAST **no requiere licencias pagadas fijas**. Todos los componentes de terceros son
software libre y de código abierto bajo licencias Apache-2.0, BSD-3-Clause, MIT, PSF o
GPL-3.0, compatibles entre sí en esta arquitectura, y ninguno restringe el uso comercial ni
exige pago.

El único servicio externo de datos, PubMLST, es gratuito. NAKAST lo consulta con la clave
de acceso personal de cada usuario, que no se distribuye con la obra. Los datos depositados
desde 2025 que se obtienen de esta forma están restringidos a uso académico no comercial y
de vigilancia en salud pública; su uso comercial requiere una licencia de la Universidad de
Oxford. Esta restricción recae sobre los datos y sobre quien los descarga, no sobre el código
de NAKAST, que no incorpora ni redistribuye datos de PubMLST.

La obra **no tiene costos operativos recurrentes** asociados a licencias ni servicios. Su
operación requiere únicamente el equipo de cómputo del usuario, con sistema operativo Linux,
una cuenta gratuita en PubMLST y conexión a internet para consultar PubMLST y, en la primera
ejecución, descargar los paquetes de software.

*Este documento es informativo y no constituye asesoría legal.*
