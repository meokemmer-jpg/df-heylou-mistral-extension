# df-heylou-mistral-extension — Output [CRUX-MK]
*Autonom aktiviert 2026-06-05T10:01:57.580427+00:00 | ollama-local/qwen2.5:14b-instruct*

# Dokumentation: df-heylou-mistral-extension

**Stand:** 2026-05-12  
**Version:** v0.1.0-SKELETON  
**Status:** SKELETON-CONDITIONAL  
**Welle:** 39  
**K_0-Touch:** true (book_direct ist K_0-relevant)  

## Übersicht

Die Dark-Factory `df-heylou-mistral-extension` integriert HeyLou als Sub-Fu
Sub-Funktion in die Mistral Function-Calling API. Es ermöglicht DeepSeek un
und anderen LLM Plattformen, Anfragen an den HeyLou Travel-Knowledge-Graph 
zu richten.

### Funktionen

| Funktion               | Beschreibung                                    
       | Backend                           |
|------------------------|-------------------------------------------------|------------------------|---------------------------------------------------------|-----------------------------------|
| `search_hotels`        | Hotel-Suche im Travel Knowledge Graph           
       | df-heylou-travel-domain          |
| `get_rates`            | Rates für ein Hotel                             
       | df-pms-mews-adapter (Welle 36)   |
| `compare_otas`         | Vergleich von OTAs (Booking, Expedia, HRS)      
       | df-ota-* (Welle 37)              |
| `book_direct`          | Kommission-freie Buchung direkt über HeyLou     
       | df-heylou-travel-domain (K_0)    |
| `optimize_revenue`     | Revenue Optimierung Stub                        
       | Welle 40 (Pending)               |

### Konfiguration

Die Verwendung des Real-Modus erfordert die Umgebungsvariablen `DF_HEYLOU_M
`DF_HEYLOU_MISTRAL_EXT_ENABLED=true`, `PHRONESIS_TICKET`, und `MISTRAL_API_
`MISTRAL_API_KEY`. Ohne diese Einstellungen läuft der Modus im Mock-Simulat
Mock-Simulation.

### Architektur

Die Struktur des Systems ist wie folgt organisiert:

```mermaid
graph LR
    A[Mistral-LLM] --> B[functionCall]
    B --> C[MistralExtension.handle_function_call()]
    C --> D{mock | real-backend}
    D --> E[df-heylou-travel-domain(mock/real)]
    D --> F[df-pms-mews-adapter(mock/real)]
    D --> G[df-ota-*(mock/real)]
    D --> H[df-heylou-travel-domain(K_0)]
    D --> I[W40-stub]
    C --> J[AuditLogger(HMAC-SHA256 JSONL)]
```

### Tests

Die Tests können durch Ausführen des Befehls `pytest tests/ -v` gestartet w
werden. Es sind mindestens 12 Tests erforderlich.

## Sandbox-Modus

Für die Entwicklung und den Testbetrieb ist der Sandbox-Modus aktiviert:

```bash
DF_HEYLOU_MISTRAL_EXT_ENABLED=false
```

Dies führt zu synthetischen Mock-Antworten, um die Integration in einem sic
sicheren Umfeld zu ermöglichen.

## Schaltplan

Der LaunchAgent für diese Dark-Factory ist konfiguriert mit den folgenden E
Einstellungen:

- `Plist`: `scripts/com.kemmer.df-heylou-mistral-extension.plist`
- `StartInterval`: 7200s (2h)
- `WorkingDir`: `/Users/make/Projects/dark-factories/df-heylou-mistral-exte
`/Users/make/Projects/dark-factories/df-heylou-mistral-extension`

Durch den Startinterval-Befehl wird sichergestellt, dass die Dark-Factory r
regelmäßig neu gestartet wird, um sicherzustellen, dass sie immer aktuell u
und bereit ist.

## Kompabilität

Diese Dark-Factory arbeitet mit den Backends aus Wellen 36 und 37. Es sind 
Lazy-Import-Stubs vorhanden, die während des Betriebs dynamisch importiert 
werden.

Diese Dokumentation bietet eine detaillierte Anleitung zur Konfiguration, N
Nutzung und Integration der `df-heylou-mistral-extension` in das HeyLou Eco
Ecosystem.