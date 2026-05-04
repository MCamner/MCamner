# Docs

Den här katalogen är den statiska GitHub Pages-ytan för MCamner Client Tools.

Den innehåller webbsidor, profiler, exempeldata och metadata för klientvalidering,
endpoint readiness och supportnära felsökning.

## Publicerade sidor

- `index.html` - startsida för klientverktygen.
- `client-readiness-check.html` - första versionen av browser-baserad readiness
  check.
- `client-readiness-v2.html` - multi-profile diagnostics med live-, sparad- och
  exempeldata.

GitHub Pages publicerar normalt innehållet härifrån som:

```text
https://mcamner.github.io/MCamner/
```

## Viktiga filer

- `evaluator.js` - regelmotor för v2-sidan.
- `client-readiness-config.json` - konfiguration för v1-sidan.
- `client-readiness-config.v2.json` - konfiguration för v2-flöden.
- `sample-client-data.json` - fallback-data när ingen live-data finns.
- `live-client-data.json` - sparad live-data från helper-agenten.
- `profiles/index.json` - lista över valbara baseline-profiler.
- `profiles/*.json` - profiler för IGEL OS 12, eLux 7, macOS och kiosk-läge.
- `robots.txt` och `sitemap.xml` - sök- och indexeringsmetadata.
- `.nojekyll` - gör att GitHub Pages serverar filerna utan Jekyll-bearbetning.

## Dataflöde i v2

`client-readiness-v2.html` läser data i den här ordningen:

1. Lokal helper-agent på `http://127.0.0.1:38765/status`
2. Sparad data från `live-client-data.json`
3. Exempeldata från `sample-client-data.json`

Det gör att sidan fungerar både med en riktig klient, med senast sparade mätning
och som demo utan lokal helper.

## Uppdatera live-data

Kör helper-agenten från repo-roten och skriv v2-data till `docs`:

```bash
python3 helper/client_readiness_agent_v2.py \
  --profile igel-os12-citrix \
  --pretty \
  --out docs/live-client-data.json
```

Tillgängliga profiler finns i:

```text
docs/profiles/index.json
```

## Köra lokalt

Från repo-roten:

```bash
python3 -m http.server 8000 --directory docs
```

Öppna sedan:

```text
http://127.0.0.1:8000/
```

Vissa browser-säkerhetsregler gör att sidorna bör köras via en lokal HTTP-server
i stället för att öppnas direkt som filer.

## Ändringsriktlinjer

- Håll `index.html` enkel och länkfokuserad.
- Lägg nya profiler i `profiles/` och registrera dem i `profiles/index.json`.
- Uppdatera `sample-client-data.json` när nya regler kräver ny exempeldata.
- Undvik externa beroenden om sidan kan fortsätta vara statisk.
- Kontrollera att ändringar fungerar både med helper-data och fallback-data.
