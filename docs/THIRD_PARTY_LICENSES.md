# NAKAST — Third-Party Components and Licences

**Componentes de terceros y licencias** · Version 1.0 · Compiled 2026-09-24

This document inventories every third-party language, library and tool that NAKAST invokes,
together with its version and licence, for the purposes of software registration.

Este documento inventaría cada lenguaje, biblioteca y herramienta de terceros que NAKAST
utiliza, junto con su versión y licencia, para efectos del registro de la obra.

---

## 1. Method / Metodología

Licence information was read from the `conda-meta` metadata of the exact package builds that
the pipeline pins, not from memory or from upstream websites. Each entry can be reproduced
with:

La información de licencias fue leída desde los metadatos `conda-meta` de las compilaciones
exactas que el pipeline fija, no de memoria ni de sitios web. Cada entrada se puede
reproducir con:

```bash
conda search -c <channel> --override-channels <package>=<version> --info | grep -i license
```

Versions are those declared in the `conda` directives of `nakast.nf` and in
`nextflow.config`.

---

## 2. Runtime components / Componentes de ejecución

These are executed by the pipeline at run time. NAKAST invokes each one as a **separate
operating-system process**; it does not link against them, embed their source, or
redistribute their binaries.

Estos son ejecutados por el pipeline en tiempo de corrida. NAKAST invoca cada uno como un
**proceso independiente del sistema operativo**; no enlaza con ellos, no incorpora su código
fuente ni redistribuye sus binarios.

### 2.1 Workflow engine / Motor de flujo de trabajo

| Component | Version | Licence | Copyright holder | Source |
|---|---|---|---|---|
| Nextflow | 25.10.2 | Apache-2.0 | Seqera Labs | <https://github.com/nextflow-io/nextflow> |

### 2.2 Programming language / Lenguaje de programación

| Component | Version | Licence | Copyright holder | Source |
|---|---|---|---|---|
| Python | 3.13.11 | Python-2.0 (PSF) | Python Software Foundation | <https://www.python.org> |

The pipeline also uses the Python standard library only (`json`, `urllib`, `argparse`, `os`,
`glob`, `sys`, `time`, `re`, `concurrent.futures`), covered by the same licence.

El pipeline usa además únicamente la biblioteca estándar de Python (`json`, `urllib`,
`argparse`, `os`, `glob`, `sys`, `time`, `re`, `concurrent.futures`), cubierta por la misma
licencia.

### 2.3 Python libraries / Bibliotecas de Python

| Component | Version | Licence | Copyright holder | Source |
|---|---|---|---|---|
| pandas | 2.3.3 | BSD-3-Clause | AQR Capital Management, Lambda Foundry, PyData Development Team | <https://pandas.pydata.org> |
| NumPy | 2.4.0 | BSD-3-Clause | NumPy Developers | <https://numpy.org> |
| openpyxl | 3.1.5 | MIT | Eric Gazoni, Charlie Clark | <https://openpyxl.readthedocs.io> |

### 2.4 Bioinformatics tools / Herramientas bioinformáticas

| Component | Version | Licence | Copyright holder | Source |
|---|---|---|---|---|
| KMA | 1.6.8 | Apache-2.0 | Philip T.L.C. Clausen, DTU | <https://bitbucket.org/genomicepidemiology/kma> |
| Filtlong | 0.3.1 | GPL-3.0-or-later | Ryan Wick | <https://github.com/rrwick/Filtlong> |
| Chopper | 0.12.0 | MIT | Wouter De Coster | <https://github.com/wdecoster/chopper> |
| NanoPlot | 1.46.2 | MIT | Wouter De Coster | <https://github.com/wdecoster/NanoPlot> |
| MultiQC | 1.33 | GPL-3.0-or-later | Phil Ewels, Seqera | <https://multiqc.info> |

### 2.5 System utilities / Utilidades del sistema

| Component | Version | Licence | Copyright holder | Source |
|---|---|---|---|---|
| GNU coreutils | 9.5 | GPL-3.0-or-later | Free Software Foundation | <https://www.gnu.org/software/coreutils/> |
| gzip | 1.12 | GPL-3.0-or-later | Free Software Foundation | <https://www.gnu.org/software/gzip/> |

---

## 3. Build-time tooling / Herramientas de construcción

Used to create the execution environments. They are **not** part of the delivered software
and are not redistributed with it.

Se usan para crear los ambientes de ejecución. **No** forman parte del software entregado ni
se redistribuyen con él.

| Component | Version | Licence | Source |
|---|---|---|---|
| conda | 26.1.1 | BSD-3-Clause | <https://docs.conda.io> |
| mamba | 2.4.0 | BSD-3-Clause | <https://mamba.readthedocs.io> |

Packages are obtained from the **conda-forge** and **bioconda** community channels, which
act as distributors. The licence that governs each package is the upstream licence listed
above, not a channel licence.

Los paquetes se obtienen de los canales comunitarios **conda-forge** y **bioconda**, que
actúan como distribuidores. La licencia que rige cada paquete es la del proyecto original
listada arriba, no una licencia del canal.

---

## 4. Reference data / Datos de referencia

NAKAST is not distributed with biological reference data. It downloads it at run time.

NAKAST no se distribuye con datos biológicos de referencia. Los descarga en tiempo de
ejecución.

| Resource | Provider | Access | Terms |
|---|---|---|---|
| PubMLST allele sequences and ST profiles | PubMLST, University of Oxford | REST API, <https://rest.pubmlst.org> | See <https://pubmlst.org/about/terms> |

PubMLST data is publicly available for academic use. It is **not** redistributed as part of
this software: each run fetches it directly from the provider, and the copy saved among the
run outputs belongs to the user's own results.

Los datos de PubMLST son de acceso público para uso académico. **No** se redistribuyen como
parte de este software: cada corrida los obtiene directamente del proveedor, y la copia que
queda entre las salidas pertenece a los resultados propios del usuario.

Attribution requested by the provider:

Atribución solicitada por el proveedor:

> Jolley KA, Bray JE, Maiden MCJ. Open-access bacterial population genomics: BIGSdb
> software, the PubMLST.org website and their applications. *Wellcome Open Res* 2018;3:124.

---

## 5. Licence compatibility analysis / Análisis de compatibilidad

### 5.1 Summary by licence family / Resumen por familia de licencia

| Licence | Components | Type |
|---|---|---|
| Apache-2.0 | Nextflow, KMA | Permissive |
| BSD-3-Clause | pandas, NumPy, conda, mamba | Permissive |
| MIT | openpyxl, Chopper, NanoPlot | Permissive |
| Python-2.0 (PSF) | Python | Permissive |
| GPL-3.0-or-later | Filtlong, MultiQC, coreutils, gzip | Copyleft |

### 5.2 Effect of the GPL components / Efecto de los componentes GPL

Four components are licensed under GPL-3.0-or-later. This matters for registration, so the
relationship is stated explicitly.

Cuatro componentes están bajo GPL-3.0-or-later. Esto importa para el registro, así que la
relación se explicita.

NAKAST is a **workflow orchestrator**. It invokes these tools as independent command-line
processes through Nextflow, communicating only through files and standard streams. It does
not:

NAKAST es un **orquestador de flujos de trabajo**. Invoca estas herramientas como procesos
independientes de línea de comandos a través de Nextflow, comunicándose únicamente mediante
archivos y flujos estándar. No:

- link against their libraries / enlaza con sus bibliotecas
- incorporate or derive from their source code / incorpora ni deriva de su código fuente
- distribute their binaries / distribuye sus binarios
- create a combined work in the sense of the GPL / crea una obra combinada en el sentido de
  la GPL

Under the Free Software Foundation's own reading, this is **mere aggregation**: separate
programs communicating at arm's length, each retaining its own licence. The copyleft
obligations of the GPL therefore do not extend to the NAKAST source code, and NAKAST may
carry a licence of the owner's choosing.

Según la lectura de la propia Free Software Foundation, esto constituye **mera agregación**:
programas separados que se comunican a distancia, cada uno conservando su propia licencia.
Las obligaciones de copyleft de la GPL, por lo tanto, no se extienden al código fuente de
NAKAST, y NAKAST puede llevar la licencia que su titular decida.

Reference / Referencia: <https://www.gnu.org/licenses/gpl-faq.html#MereAggregation>

### 5.3 Conditions to observe / Condiciones a observar

| Licence | Obligation when redistributing |
|---|---|
| Apache-2.0 | Retain copyright and licence notices; state modifications; includes a patent grant |
| BSD-3-Clause | Retain copyright notice and disclaimer; do not use contributors' names for endorsement |
| MIT | Retain copyright notice and permission notice |
| Python-2.0 | Retain PSF copyright notice |
| GPL-3.0-or-later | If the binaries are redistributed, provide the corresponding source. Not triggered here: NAKAST does not redistribute them |

None of these licences restricts commercial use, and none requires payment.

Ninguna de estas licencias restringe el uso comercial, y ninguna exige pago.

### 5.4 Conclusion / Conclusión

The third-party components used by NAKAST are all free and open-source software under
licences that are mutually compatible in this architecture. Their use is compatible with
registering NAKAST as a work and with its subsequent use, whether academic or commercial.

Los componentes de terceros que utiliza NAKAST son en su totalidad software libre y de código
abierto, bajo licencias mutuamente compatibles en esta arquitectura. Su uso es compatible con
el registro de NAKAST como obra y con su utilización posterior, sea académica o comercial.

---

## 6. Licence of NAKAST itself / Licencia de NAKAST

> **Pending decision.** This is a separate matter from the inventory above and must be
> resolved by the owner before deposit.
>
> **Decisión pendiente.** Es un asunto distinto del inventario anterior y debe resolverlo el
> titular antes del depósito.

The inventory above covers third-party components. It does not assign a licence to NAKAST's
own source code. A repository published without a licence file is, by default, **all rights
reserved**, which prevents others from legally using or citing the work.

El inventario anterior cubre componentes de terceros. No asigna licencia al código fuente
propio de NAKAST. Un repositorio publicado sin archivo de licencia queda, por defecto, con
**todos los derechos reservados**, lo que impide a terceros usar o citar la obra legalmente.

Options consistent with the components in use:

Opciones consistentes con los componentes utilizados:

| Licence | Effect |
|---|---|
| MIT | Maximum reuse; requires only attribution |
| Apache-2.0 | Like MIT plus an explicit patent grant; common for institutional software |
| GPL-3.0 | Requires derivative works to remain open source |

---

## 7. Provenance note / Nota de procedencia

All version and licence values in sections 2 and 3 were extracted programmatically from the
installed `conda-meta` package metadata on 2026-09-24 and cross-checked against the
`conda` directives declared in `nakast.nf`. Copyright holders and source URLs were taken from
each project's canonical repository.

Todos los valores de versión y licencia de las secciones 2 y 3 fueron extraídos
programáticamente de los metadatos `conda-meta` instalados el 2026-09-24 y contrastados con
las directivas `conda` declaradas en `nakast.nf`. Los titulares de copyright y las URL de
origen se tomaron del repositorio canónico de cada proyecto.

This document is informational and does not constitute legal advice.

Este documento es informativo y no constituye asesoría legal.
