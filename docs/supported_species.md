# Species supported by NAKAST

Generated automatically by `bin/list_pubmlst_species.py` from the
PubMLST REST API (<https://rest.pubmlst.org>).

A species is supported when its `seqdef` database publishes an MLST
scheme with defined ST profiles, which is what NAKAST needs to assign
a Sequence Type.

## Summary

- **135 supported species**
- 102 define a Clonal Complex; the rest report `CC = -`
- 48 use a number of loci other than 7
- 7 use a `scheme_id` other than 1 (NAKAST detects it)

## Usage

The value in the `species` column below is what goes in the
`species` column of the samplesheet:

```
sample_id	fastq_dir	species
M1	data/M1	sagalactiae
```

To query the list live:

```bash
nextflow run nakast.nf --list_species
```

## Catalogue

| Organism | `species` | PubMLST database | Scheme | Loci | CC |
|---|---|---|---:|---:|:-:|
| Achromobacter spp. | `achromobacter` | `pubmlst_achromobacter_seqdef` | 1 | 7 | yes |
| Acinetobacter baumannii | `abaumannii` | `pubmlst_abaumannii_seqdef` | 1 | 7 | yes |
| Actinobacillus spp. | `actinobacillus` | `pubmlst_actinobacillus_seqdef` | 1 | 7 | no |
| Aeromonas spp. | `aeromonas` | `pubmlst_aeromonas_seqdef` | 1 | 6 | no |
| Aggregatibacter actinomycetemcomitans | `aactinomycetemcomitans` | `pubmlst_aactinomycetemcomitans_seqdef` | 1 | 7 | yes |
| Anaplasma phagocytophilum | `aphagocytophilum` | `pubmlst_aphagocytophilum_seqdef` | 1 | 7 | yes |
| Arcobacter spp. | `arcobacter` | `pubmlst_arcobacter_seqdef` | 1 | 7 | yes |
| Aspergillus fumigatus | `afumigatus` | `pubmlst_afumigatus_seqdef` | 1 | 7 | no |
| Avibacterium paragallinarum | `aparagallinarum` | `pubmlst_aparagallinarum_seqdef` | 1 | 7 | no |
| Bacillus cereus | `bcereus` | `pubmlst_bcereus_seqdef` | 1 | 7 | yes |
| Bacillus licheniformis | `blicheniformis` | `pubmlst_blicheniformis_seqdef` | 14 | 6 | yes |
| Bacillus subtilis | `bsubtilis` | `pubmlst_bsubtilis_seqdef` | 1 | 7 | no |
| Bacteroides fragilis | `bfragilis` | `pubmlst_bfragilis_seqdef` | 1 | 7 | no |
| Bartonella bacilliformis | `bbacilliformis` | `pubmlst_bbacilliformis_seqdef` | 1 | 7 | yes |
| Bartonella henselae | `bhenselae` | `pubmlst_bhenselae_seqdef` | 1 | 8 | yes |
| Bartonella washoensis | `bwashoensis` | `pubmlst_bwashoensis_seqdef` | 1 | 6 | yes |
| Borrelia spp. | `borrelia` | `pubmlst_borrelia_seqdef` | 1 | 8 | yes |
| Brucella spp. | `brucella` | `pubmlst_brucella_seqdef` | 1 | 9 | no |
| Burkholderia cepacia complex | `bcc` | `pubmlst_bcc_seqdef` | 1 | 7 | yes |
| Burkholderia pseudomallei | `bpseudomallei` | `pubmlst_bpseudomallei_seqdef` | 1 | 7 | yes |
| Campylobacter jejuni/coli | `campylobacter` | `pubmlst_campylobacter_seqdef` | 1 | 7 | yes |
| Candida albicans | `calbicans` | `pubmlst_calbicans_seqdef` | 1 | 7 | yes |
| Candida glabrata | `cglabrata` | `pubmlst_cglabrata_seqdef` | 1 | 6 | no |
| Candida krusei | `ckrusei` | `pubmlst_ckrusei_seqdef` | 1 | 6 | no |
| Candida tropicalis | `ctropicalis` | `pubmlst_ctropicalis_seqdef` | 1 | 6 | yes |
| Candidatus Liberibacter solanacearum | `liberibacter` | `pubmlst_liberibacter_seqdef` | 1 | 7 | no |
| Carnobacterium maltaromaticum | `cmaltaromaticum` | `pubmlst_cmaltaromaticum_seqdef` | 1 | 7 | yes |
| Chlamydiales spp. | `chlamydiales` | `pubmlst_chlamydiales_seqdef` | 1 | 7 | yes |
| Citrobacter spp. | `cfreundii` | `pubmlst_cfreundii_seqdef` | 1 | 7 | yes |
| Clonorchis sinensis | `csinensis` | `pubmlst_csinensis_seqdef` | 1 | 8 | yes |
| Clostridioides difficile | `cdifficile` | `pubmlst_cdifficile_seqdef` | 1 | 7 | no |
| Clostridium botulinum | `cbotulinum` | `pubmlst_cbotulinum_seqdef` | 1 | 7 | yes |
| Clostridium perfringens | `cperfringens` | `pubmlst_cperfringens_seqdef` | 1 | 8 | yes |
| Clostridium septicum | `csepticum` | `pubmlst_csepticum_seqdef` | 1 | 7 | yes |
| Cronobacter spp. | `cronobacter` | `pubmlst_cronobacter_seqdef` | 1 | 7 | yes |
| Cutibacterium acnes | `pacnes` | `pubmlst_pacnes_seqdef` | 3 | 8 | yes |
| Cutibacterium avidum | `cavidum` | `pubmlst_cavidum_seqdef` | 1 | 7 | no |
| Dichelobacter nodosus | `dnodosus` | `pubmlst_dnodosus_seqdef` | 1 | 7 | yes |
| Edwardsiella spp. | `edwardsiella` | `pubmlst_edwardsiella_seqdef` | 1 | 10 | yes |
| Enterobacter spp. | `ecloacae` | `pubmlst_ecloacae_seqdef` | 1 | 7 | yes |
| Enterococcus faecalis | `efaecalis` | `pubmlst_efaecalis_seqdef` | 1 | 7 | yes |
| Enterococcus faecium | `efaecium` | `pubmlst_efaecium_seqdef` | 1 | 7 | yes |
| Escherichia spp. | `escherichia` | `pubmlst_escherichia_seqdef` | 1 | 7 | yes |
| Flavobacterium psychrophilum | `fpsychrophilum` | `pubmlst_fpsychrophilum_seqdef` | 1 | 7 | yes |
| Gallibacterium anatis | `gallibacterium` | `pubmlst_gallibacterium_seqdef` | 1 | 8 | yes |
| Geotrichum spp. | `geotrichum` | `pubmlst_geotrichum_seqdef` | 1 | 5 | yes |
| Glaesserella parasuis | `hparasuis` | `pubmlst_hparasuis_seqdef` | 1 | 7 | yes |
| Haemophilus influenzae | `hinfluenzae` | `pubmlst_hinfluenzae_seqdef` | 1 | 7 | yes |
| Helicobacter cinaedi | `hcinaedi` | `pubmlst_hcinaedi_seqdef` | 1 | 7 | yes |
| Helicobacter pylori | `helicobacter` | `pubmlst_helicobacter_seqdef` | 1 | 7 | no |
| Helicobacter suis | `hsuis` | `pubmlst_hsuis_seqdef` | 1 | 7 | yes |
| Klebsiella aerogenes | `kaerogenes` | `pubmlst_kaerogenes_seqdef` | 1 | 7 | yes |
| Klebsiella oxytoca | `koxytoca` | `pubmlst_koxytoca_seqdef` | 1 | 7 | no |
| Kudoa septempunctata | `kseptempunctata` | `pubmlst_kseptempunctata_seqdef` | 1 | 2 | no |
| Lactobacillus salivarius | `lsalivarius` | `pubmlst_lsalivarius_seqdef` | 1 | 5 | yes |
| Lactococcus garvieae | `lgarvieae` | `pubmlst_lgarvieae_seqdef` | 1 | 7 | no |
| Lactococcus lactis 936-like bacteriophage | `llactis_phage` | `pubmlst_llactis_phage_seqdef` | 1 | 5 | yes |
| Leptospira spp. | `leptospira` | `pubmlst_leptospira_seqdef` | 1 | 7 | yes |
| Macrococcus canis | `mcanis` | `pubmlst_mcanis_seqdef` | 1 | 7 | yes |
| Macrococcus caseolyticus | `mcaseolyticus` | `pubmlst_mcaseolyticus_seqdef` | 1 | 7 | yes |
| Mammaliicoccus sciuri | `msciuri` | `pubmlst_msciuri_seqdef` | 1 | 7 | no |
| Mannheimia haemolytica | `mhaemolytica` | `pubmlst_mhaemolytica_seqdef` | 1 | 7 | yes |
| Melissococcus plutonius | `mplutonius` | `pubmlst_mplutonius_seqdef` | 1 | 4 | yes |
| Mycobacteria spp. | `mycobacteria` | `pubmlst_mycobacteria_seqdef` | 2 | 8 | no |
| Mycobacteroides abscessus complex | `mabscessus` | `pubmlst_mabscessus_seqdef` | 1 | 7 | yes |
| Mycoplasma agalactiae | `magalactiae` | `pubmlst_magalactiae_seqdef` | 1 | 5 | yes |
| Mycoplasma anserisalpingitidis | `manserisalpingitidis` | `pubmlst_manserisalpingitidis_seqdef` | 1 | 5 | no |
| Mycoplasma bovis | `mbovis` | `pubmlst_mbovis_seqdef` | 2 | 7 | yes |
| Mycoplasma flocculare | `mflocculare` | `pubmlst_mflocculare_seqdef` | 1 | 3 | no |
| Mycoplasma gallisepticum | `mgallisepticum` | `pubmlst_mgallisepticum_seqdef` | 1 | 7 | yes |
| Mycoplasma genitalium | `mgenitalium` | `pubmlst_mgenitalium_seqdef` | 2 | 6 | no |
| Mycoplasma hominis | `mhominis` | `pubmlst_mhominis_seqdef` | 1 | 5 | no |
| Mycoplasma hyopneumoniae | `mhyopneumoniae` | `pubmlst_mhyopneumoniae_seqdef` | 1 | 3 | yes |
| Mycoplasma hyorhinis | `mhyorhinis` | `pubmlst_mhyorhinis_seqdef` | 1 | 6 | yes |
| Mycoplasma hyosynoviae | `mhyosynoviae` | `pubmlst_mhyosynoviae_seqdef` | 1 | 7 | no |
| Mycoplasma iowae | `miowae` | `pubmlst_miowae_seqdef` | 1 | 6 | yes |
| Mycoplasma pneumoniae | `mpneumoniae` | `pubmlst_mpneumoniae_seqdef` | 1 | 8 | yes |
| Mycoplasma synoviae | `msynoviae` | `pubmlst_msynoviae_seqdef` | 1 | 7 | yes |
| Neisseria spp. | `neisseria` | `pubmlst_neisseria_seqdef` | 1 | 7 | yes |
| Orientia tsutsugamushi | `otsutsugamushi` | `pubmlst_otsutsugamushi_seqdef` | 1 | 7 | yes |
| Ornithobacterium rhinotracheale | `orhinotracheale` | `pubmlst_orhinotracheale_seqdef` | 1 | 7 | yes |
| Paenibacillus larvae | `plarvae` | `pubmlst_plarvae_seqdef` | 1 | 7 | yes |
| Pediococcus pentosaceus | `ppentosaceus` | `pubmlst_ppentosaceus_seqdef` | 1 | 7 | yes |
| Photobacterium damselae | `pdamselae` | `pubmlst_pdamselae_seqdef` | 1 | 6 | yes |
| Piscirickettsia salmonis | `psalmonis` | `pubmlst_psalmonis_seqdef` | 1 | 7 | yes |
| Porphyromonas gingivalis | `pgingivalis` | `pubmlst_pgingivalis_seqdef` | 1 | 7 | yes |
| Proteus spp. | `proteus` | `pubmlst_proteus_seqdef` | 1 | 6 | no |
| Providencia spp. | `providencia` | `pubmlst_providencia_seqdef` | 1 | 5 | no |
| Pseudomonas aeruginosa | `paeruginosa` | `pubmlst_paeruginosa_seqdef` | 1 | 7 | yes |
| Pseudomonas fluorescens | `pfluorescens` | `pubmlst_pfluorescens_seqdef` | 1 | 7 | yes |
| Pseudomonas putida | `pputida` | `pubmlst_pputida_seqdef` | 1 | 8 | yes |
| Rhodococcus spp. | `rhodococcus` | `pubmlst_rhodococcus_seqdef` | 1 | 7 | yes |
| Riemerella anatipestifer | `ranatipestifer` | `pubmlst_ranatipestifer_seqdef` | 1 | 7 | yes |
| Salmonella spp. | `salmonella` | `pubmlst_salmonella_seqdef` | 2 | 7 | yes |
| Saprolegnia parasitica | `sparasitica` | `pubmlst_sparasitica_seqdef` | 1 | 7 | yes |
| Serratia spp. | `serratia` | `pubmlst_serratia_seqdef` | 1 | 6 | no |
| Shewanella spp. | `shewanella` | `pubmlst_shewanella_seqdef` | 1 | 8 | no |
| Sinorhizobium spp. | `sinorhizobium` | `pubmlst_sinorhizobium_seqdef` | 1 | 10 | yes |
| Staphylococcus aureus | `saureus` | `pubmlst_saureus_seqdef` | 1 | 7 | no |
| Staphylococcus capitis | `scapitis` | `pubmlst_scapitis_seqdef` | 1 | 7 | no |
| Staphylococcus chromogenes | `schromogenes` | `pubmlst_schromogenes_seqdef` | 1 | 7 | no |
| Staphylococcus epidermidis | `sepidermidis` | `pubmlst_sepidermidis_seqdef` | 1 | 7 | yes |
| Staphylococcus haemolyticus | `shaemolyticus` | `pubmlst_shaemolyticus_seqdef` | 1 | 7 | yes |
| Staphylococcus hominis | `shominis` | `pubmlst_shominis_seqdef` | 1 | 6 | yes |
| Staphylococcus pseudintermedius | `spseudintermedius` | `pubmlst_spseudintermedius_seqdef` | 1 | 7 | yes |
| Stenotrophomonas maltophilia | `smaltophilia` | `pubmlst_smaltophilia_seqdef` | 1 | 7 | yes |
| Streptococcus agalactiae | `sagalactiae` | `pubmlst_sagalactiae_seqdef` | 1 | 7 | yes |
| Streptococcus bovis/equinus complex (SBSEC) | `sbsec` | `pubmlst_sbsec_seqdef` | 1 | 10 | yes |
| Streptococcus canis | `scanis` | `pubmlst_scanis_seqdef` | 1 | 7 | yes |
| Streptococcus dysgalactiae | `sdysgalactiae` | `pubmlst_sdysgalactiae_seqdef` | 1 | 7 | yes |
| Streptococcus gallolyticus | `sgallolyticus` | `pubmlst_sgallolyticus_seqdef` | 1 | 7 | yes |
| Streptococcus iniae | `siniae` | `pubmlst_siniae_seqdef` | 1 | 8 | yes |
| Streptococcus mitis | `smitis` | `pubmlst_smitis_seqdef` | 1 | 7 | yes |
| Streptococcus pneumoniae | `spneumoniae` | `pubmlst_spneumoniae_seqdef` | 1 | 7 | yes |
| Streptococcus pyogenes | `spyogenes` | `pubmlst_spyogenes_seqdef` | 1 | 7 | yes |
| Streptococcus suis | `ssuis` | `pubmlst_ssuis_seqdef` | 1 | 7 | yes |
| Streptococcus thermophilus | `sthermophilus` | `pubmlst_sthermophilus_seqdef` | 1 | 10 | no |
| Streptococcus uberis | `suberis` | `pubmlst_suberis_seqdef` | 1 | 7 | yes |
| Streptococcus zooepidemicus | `szooepidemicus` | `pubmlst_szooepidemicus_seqdef` | 1 | 7 | yes |
| Streptomyces spp | `streptomyces` | `pubmlst_streptomyces_seqdef` | 1 | 6 | yes |
| Taylorella spp. | `taylorella` | `pubmlst_taylorella_seqdef` | 1 | 7 | yes |
| Tenacibaculum spp. | `tenacibaculum` | `pubmlst_tenacibaculum_seqdef` | 1 | 7 | yes |
| Treponema pallidum | `tpallidum` | `pubmlst_tpallidum_seqdef` | 1 | 3 | yes |
| Tricohomas vaginalis | `tvaginalis` | `pubmlst_tvaginalis_seqdef` | 1 | 7 | yes |
| Trueperella pyogenes | `tpyogenes` | `pubmlst_tpyogenes_seqdef` | 1 | 7 | no |
| Ureaplasma spp. | `ureaplasma` | `pubmlst_ureaplasma_seqdef` | 1 | 4 | yes |
| Vibrio cholerae | `vcholerae` | `pubmlst_vcholerae_seqdef` | 1 | 7 | yes |
| Vibrio parahaemolyticus | `vparahaemolyticus` | `pubmlst_vparahaemolyticus_seqdef` | 1 | 7 | yes |
| Vibrio spp. | `vibrio` | `pubmlst_vibrio_seqdef` | 1 | 4 | no |
| Vibrio tapetis | `vtapetis` | `pubmlst_vtapetis_seqdef` | 1 | 10 | yes |
| Vibrio vulnificus | `vvulnificus` | `pubmlst_vvulnificus_seqdef` | 1 | 10 | yes |
| Wolbachia spp. | `wolbachia` | `pubmlst_wolbachia_seqdef` | 1 | 5 | yes |
| Xylella fastidiosa | `xfastidiosa` | `pubmlst_xfastidiosa_seqdef` | 1 | 7 | yes |
| Yersinia pseudotuberculosis | `ypseudotuberculosis_achtman` | `pubmlst_ypseudotuberculosis_achtman_seqdef` | 3 | 7 | yes |
| Yersinia ruckeri | `yruckeri` | `pubmlst_yruckeri_seqdef` | 1 | 6 | yes |

## Loci per scheme

- **`achromobacter`** (7): nusA, rpoB, eno, gltB, lepA, nuoL, nrdA
- **`abaumannii`** (7): Oxf_gltA, Oxf_gyrB, Oxf_gdhB, Oxf_recA, Oxf_cpn60, Oxf_gpi, Oxf_rpoD
- **`actinobacillus`** (7): adk, atpG, deoD, mdh, pgi, recA, zwf
- **`aeromonas`** (6): gyrB, groL, gltA, metG, ppsA, recA
- **`aactinomycetemcomitans`** (7): adk, atpG, frdB, mdh, pgi, recA, zwf
- **`aphagocytophilum`** (7): pheS, glyA, fumC, mdh, sucA, dnaN, atpA
- **`arcobacter`** (7): aspA, atpA, glnA, gltA, glyA, pgm, tkt
- **`afumigatus`** (7): ANX4, BGT1, CAT1, LIP, MAT1_2, SODB, ZRF2
- **`aparagallinarum`** (7): pmi, infB, mdh, adk, deoD, recA, zwf
- **`bcereus`** (7): glp, gmk, ilv, pta, pur, pyc, tpi
- **`blicheniformis`** (6): adk, ccpA, recF, rpoB, spo0A, sucC
- **`bsubtilis`** (7): glpF, ilvD, pta, purH, pycA, rpoD, tpiA
- **`bfragilis`** (7): dnaJ, fusA, groL, prfA, recA, rpoB, rprX
- **`bbacilliformis`** (7): ftsZ, flaA, ribC, rnpB, rpoB, bvrR, groEL
- **`bhenselae`** (8): 16S, batR, ftsZ, gltA, groEL, nlpD, ribC, rpoB
- **`bwashoensis`** (6): 16S, ftsZ, gltA, groEL, ribC, rpoB
- **`borrelia`** (8): clpA, clpX, nifS, pepX, pyrG, recG, rplB, uvrA
- **`brucella`** (9): gap, aroA, glk, dnaK, gyrB, trpE, cobQ, int_hyp, omp25
- **`bcc`** (7): atpD, gltB, gyrB, recA, lepA, phaC, trpB
- **`bpseudomallei`** (7): ace, gltB, gmhD, lepA, lipA, narK, ndh
- **`campylobacter`** (7): aspA, glnA, gltA, glyA, pgm, tkt, uncA
- **`calbicans`** (7): AAT1a, ACC1, ADP1, MPIb, SYA1, VPS13, ZWF1b
- **`cglabrata`** (6): FKS, LEU2, NMT1, TRP1, UGP1, URA3
- **`ckrusei`** (6): HIS3, LEU2, NMT1, TRP1, ADE2, LYS2D
- **`ctropicalis`** (6): ICL1, MDR1, SAPT2, SAPT4, XYR1, ZWF1a
- **`liberibacter`** (7): adk, atpA, fbpA, ftsZ, glyA, groEL, gyrB
- **`cmaltaromaticum`** (7): dapE, ddlA, glpQ, ilvE, leuS, pyc, pyrE
- **`chlamydiales`** (7): gatA, oppA, hflX, gidA, enoA, hemN, fumC
- **`cfreundii`** (7): aspC, clpX, fadD, mdh, arcA, dnaG, lysP
- **`csinensis`** (8): Actin, Cox1, Cox3, Ef_1a, Its1, Nad4, Nad5, Tubulin
- **`cdifficile`** (7): adk, atpA, dxr, glyA, recA, sodA, tpi
- **`cbotulinum`** (7): aroE, mdh, aceK, oppB, rpoB, recA, hsp
- **`cperfringens`** (8): colA, groEL, sodA, plc, gyrB, sigK, pgk, nadA
- **`csepticum`** (7): ddl, dnaK, glpK, groEL, gyrA, recA, tpi
- **`cronobacter`** (7): atpD, fusA, glnS, gltB, gyrB, infB, pps
- **`pacnes`** (8): aroE, atpD, gmk, guaA, lepA, sodA, tly, CAMP2
- **`cavidum`** (7): ab_hydrolase, aroE, atpD, gmk, guaA, lepA, sodA
- **`dnodosus`** (7): dcd, dtdA, folK, recR, rlmH, rplI, tsaE
- **`edwardsiella`** (10): adk, atpD, dnaJ, gapA, glnA, hsp60, phoR, pyrG, rpoA, tuf
- **`ecloacae`** (7): dnaA, fusA, gyrB, leuS, pyrG, rplB, rpoB
- **`efaecalis`** (7): gdh, gyd, pstS, gki, aroE, xpt, yqiL
- **`efaecium`** (7): atpA, ddl, gdh, purK, gyd, pstS, adk
- **`escherichia`** (7): adk, fumC, gyrB, icd, mdh, purA, recA
- **`fpsychrophilum`** (7): atpA, dnaK, fumC, gyrB, murG, trpB, tuf
- **`gallibacterium`** (8): adk, atpD, fumC, gyrB, infB, mdh, recN, thdF
- **`geotrichum`** (5): NUP116, URA1, URA3, SAPT4, PLB3
- **`hparasuis`** (7): atpD, infB, mdh, rpoB, 6pgd, g3pd, frdB
- **`hinfluenzae`** (7): adk, atpG, frdB, fucK, mdh, pgi, recA
- **`hcinaedi`** (7): 23S_rRNA, ppa, aspA, aroE, atpA, tkt, cdtB
- **`helicobacter`** (7): atpA, efp, mutY, ppa, trpC, ureI, yphC
- **`hsuis`** (7): atpA, efp, mutY, ppa, trpC, ureAB, yphC
- **`kaerogenes`** (7): dnaA, fusA, gyrB, leuS, pryG, rplB, rpoB
- **`koxytoca`** (7): gapA, infB, mdh, pgi, phoE, rpoB, tonB
- **`kseptempunctata`** (2): cox1, rnl
- **`lsalivarius`** (5): pstB, rpsB, nrdB, rpoA, parB
- **`lgarvieae`** (7): als, atpA, tuf, gapC, gyrB, rpoC, galP
- **`llactis_phage`** (5): terL, mcp, mtp, tmp, lys
- **`leptospira`** (7): glmU_1, pntA_1, sucA_1, tpiA_1, pfkB_1, mreA_1, caiB_1
- **`mcanis`** (7): ack, cpn60, fdh, pta, purA, sar, tuf
- **`mcaseolyticus`** (7): ack, cpn60, fdh, pta, purA, sar, tuf
- **`msciuri`** (7): ack, aroE, ftsZ, glpK, gmk, pta1, tpiA
- **`mhaemolytica`** (7): adk, aroE, deoD, gapDH, gnd, mdh, zwf
- **`mplutonius`** (4): argE, galK, gbpB, purR
- **`mycobacteria`** (8): S14Z, L35, S19, L19, S12, S8, L16, S7
- **`mabscessus`** (7): argH, cya, gnd, murC, pta, purH, rpoB
- **`magalactiae`** (5): dnaA, gltX, gyrB, metS, tufA
- **`manserisalpingitidis`** (5): atpG, fusA, pgiB, plsY, uvrA
- **`mbovis`** (7): dnaA, gltX, gpsA, gyrB, pta2, tdk, tkt
- **`mflocculare`** (3): adk, rpoB, tpiA
- **`mgallisepticum`** (7): atpG, dppC, DUF3196, lgT, mraW, plsC, ugpA
- **`mgenitalium`** (6): MLST_adk, MLST_atpA, MLST_gmk, MLST_gyrB, MLST_pgm, MLST_ppa
- **`mhominis`** (5): uvrA, gyrB, ftsY, tuf, gap
- **`mhyopneumoniae`** (3): adk, rpoB, tpiA
- **`mhyorhinis`** (6): dnaA, rpoB, gyrB, gltX, adk, gmk
- **`mhyosynoviae`** (7): dnaA, ftsY, fusA, gyrB, recA, rpoB, uvrA
- **`miowae`** (6): dppC, ulaA, valS, rpoC, leuS, kdpA
- **`mpneumoniae`** (8): ppa, pgm, gyrB, gmk, glyA, atpA, arcC, adk
- **`msynoviae`** (7): adk, atpG, efp, gmk, nagC, ppa, recA
- **`neisseria`** (7): abcZ, adk, aroE, fumC, gdh, pdhC, pgm
- **`otsutsugamushi`** (7): gpsA, mdh, nrdB, nuoF, ppdK, sucB, sucD
- **`orhinotracheale`** (7): adk, aroE, fumC, gdhA, mdh, pgi, pmi
- **`plarvae`** (7): glpF, sigF, glpT, Natrans, rpoB, ftsA, clpC
- **`ppentosaceus`** (7): gyrB, pyc, pgm, leuS, glnA, dalR, pgI
- **`pdamselae`** (6): glpF, gyrB, metG, pntA, pyrC, toxR
- **`psalmonis`** (7): dnaK, efp, fumC, glyA, murG, rpoD, trpB
- **`pgingivalis`** (7): ftsQ, gpdxJ, hagB, mcmA, pepO, pga, recA
- **`proteus`** (6): atpD, dnaJ, mdh, pyrC, recA, rpoD
- **`providencia`** (5): fusA, gyrB, ileS, lepA, leuS
- **`paeruginosa`** (7): acsA, aroE, guaA, mutL, nuoD, ppsA, trpE
- **`pfluorescens`** (7): glnS, gyrB, ileS, nuoD, recA, rpoB, rpoD
- **`pputida`** (8): argS, gyrB, ileS, nuoC, ppsA, recA, rpoB, rpoD
- **`rhodococcus`** (7): gapdh, tpi, mdh, icl, rpoB, recA, adk
- **`ranatipestifer`** (7): dnaB, groEL, gyrA, mdh, gluD, gpi, rpoB
- **`salmonella`** (7): aroC, dnaN, hemD, hisD, purE, sucA, thrA
- **`sparasitica`** (7): ALTS1, COX1, GLUT, NAD1, RPB2, SHMT, TUBB
- **`serratia`** (6): adk, fumC, gyrB, icd, mdh, recA
- **`shewanella`** (8): 16S_rRNA, adk, atpB, guaA, gyrB, mdh, recA, rpoS
- **`sinorhizobium`** (10): asd, edd, gap, glnD, gnd, nuoE1, ordL2, recA, sucA, zwf
- **`saureus`** (7): arcC, aroE, glpF, gmk, pta, tpi, yqiL
- **`scapitis`** (7): atpB2, carB, clpP, hisS, mntC, phoA, rluB
- **`schromogenes`** (7): arcC, hutU, fumC, dnaJ, glpF, menF, pta
- **`sepidermidis`** (7): arcC, aroE, gtr, mutS, pyrR, tpiA, yqiL
- **`shaemolyticus`** (7): arcC, SH_1200, hemH, leuB, SH1431, cfxE, Ribose_ABC
- **`shominis`** (6): arcC, glpK, gtr, pta, tpiA, tuf
- **`spseudintermedius`** (7): ack, cpn60, fdh, pta, purA, sar, tuf
- **`smaltophilia`** (7): atpD, gapA, guaA, mutM, nuoD, ppsA, recA
- **`sagalactiae`** (7): adhP, pheS, atr, glnA, sdhA, glcK, tkt
- **`sbsec`** (10): ddl, gki, glnA, mutS, mutS2, pheS, proS, pyrE, thrS, tpi
- **`scanis`** (7): gki, gtr, murI, mutS, recP, xpt, yqiZ
- **`sdysgalactiae`** (7): gki, gtr, murI, mutS, recP, xpt, atoB
- **`sgallolyticus`** (7): aroE, glgB, nifS, p20, tkt, trpD, uvrA
- **`siniae`** (8): dnaN, mutL, mutM, mutS, mutX, recD2, rnhC, yfhQ
- **`smitis`** (7): accA, gki, hom, oppC, patB, rlmN, tsf
- **`spneumoniae`** (7): aroE, gdh, gki, recP, spi, xpt, ddl
- **`spyogenes`** (7): gki, gtr, murI, mutS, recP, xpt, yqiL
- **`ssuis`** (7): aroA, cpn60, dpr, gki, mutS, recA, thrA
- **`sthermophilus`** (10): carB, clpX, dnaA, murC, murE, pepN, pepX, pyrG, recA, rpoB
- **`suberis`** (7): arcC, ddl, gki, recP, tdk, tpi, yqiL
- **`szooepidemicus`** (7): arcC, nrdE, proS, spi, tdk, tpi, yqiL
- **`streptomyces`** (6): 16S, atpD, gyrB, recA, rpoB, trpB
- **`taylorella`** (7): gltA, gyrB, fh, shmt, tyrB, adk, txn
- **`tenacibaculum`** (7): atpA, dnaK, glyA, gyrB, infB, rlmN, tgt
- **`tpallidum`** (3): TP0136, TP0548, TP0705
- **`tvaginalis`** (7): TRYP, GLUT, FT2A, ALTS, DMRP, SHMT, M6PI
- **`tpyogenes`** (7): adk, gyrB, leuA, metG, recA, tpi, tuf
- **`ureaplasma`** (4): ftsH, rpL22, thrS, valS
- **`vcholerae`** (7): adk, gyrB, mdh, metE, pntA, purM, pyrC
- **`vparahaemolyticus`** (7): dnaE, gyrB, recA, dtdS, pntA, pyrC, tnaA
- **`vibrio`** (4): gyrB, pyrH, recA, atpA
- **`vtapetis`** (10): atpA, fstZ, gapA, hsp60, pyrH, rctB, recA, rpoA, rpoD, topA
- **`vvulnificus`** (10): glp, gyrB, mdh, metG, purM, dtdS, lysA, pntA, pyrC, tnaA
- **`wolbachia`** (5): gatB, coxA, hcpA, ftsZ, fbpA
- **`xfastidiosa`** (7): leuA, petC, malF, cysG, holC, nuoL, gltT
- **`ypseudotuberculosis_achtman`** (7): adk, argA, aroA, glnA, thrA, tmk, trpE
- **`yruckeri`** (6): glnA, gyrB, dnaJ, thrA, hsp60, recA
