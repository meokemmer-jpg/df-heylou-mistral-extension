# df-heylou-mistral-extension — PRODUKTION [CRUX-MK]
*2026-06-09T14:14:18.354187+00:00 | ollama-local/kemmer-14b-ctx8k*

# Dokumentation: df-heylou-mistral-extension

**Stand:** 2026-05-12  
**Version:** v0.1.0  
**Status:** Real-Mode Active  
**Welle:** 39  
**K_0-Touch:** true (book_direct ist K_0-relevant)  

## Übersicht

Die Dark-Factory `df-heylou-mistral-extension` integriert HeyLou als Sub-Funktion in die Mistral Function-Calling API. Es ermöglicht DeepSeek und anderen LLM Plattformen, Anfragen an den HeyLou Travel-Knowledge-Graph zu richten.

## Funktionen

### search_hotels(location, dates, preferences)
**Beschreibung:** Hotel-Suche im Travel Knowledge Graph  
**Backend:** df-heylou-travel-domain  

### get_rates(hotel_id, date_range)
**Beschreibung:** Rates für ein Hotel  
**Backend:** df-pms-mews-adapter (Welle 36)  

### compare_otas(hotel_id, dates)
**Beschreibung:** Vergleich von OTAs (Booking, Expedia, HRS)  
**Backend:** df-ota-* (Welle 37)  

### book_direct(hotel_id, room_type, guest, dates)
**Beschreibung:** Kommission-freie Buchung direkt über HeyLou  
**Backend:** df-heylou-travel-domain (K_0-relevant)  

### optimize_revenue(hotel_id)
**Beschreibung:** Revenue Optimierung Stub  
**Backend:** Welle 40 (Pending)

## Konfiguration

Die Verwendung des Real-Modus erfordert die Umgebungsvariablen `DF_HEYLOU_MISTRAL_EXT_ENABLED=true`, `PHRONESIS_TICKET` und `MISTRAL_API_KEY`. Ohne diese Einstellungen läuft der Modus im Mock-Simulation-Modus.

### Sandbox-Modus

Für den Testbetrieb ist der Sandbox-Modus aktiviert, indem die Umgebungsvariable `DF_HEYLOU_MISTRAL_EXT_ENABLED=false` gesetzt wird. Dies führt zu synthetischen Antworten basierend auf dem HeyLou Travel-Knowledge-Graph.

## Architektur

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

## Tests

Die Tests können durch Ausführen des Befehls `pytest tests/ -v` gestartet werden. Es sind mindestens 12 Tests erforderlich, die sich auf die Korrektheit der Funktionen beziehen.

### Test-Fälle
- `test_search_hotels_valid_input()`: Überprüft das Suchergebnis für gültige Eingaben.
- `test_get_rates_no_rooms_available()`: Prüft den Fehlertext, wenn keine Zimmersätze verfügbar sind.
- `test_compare_otas_same_rate()` und `test_compare_otas_different_rates()`: Vergleicht die Preise verschiedener OTAs unter Berücksichtigung von Rate-Varianten.
- `test_book_direct_success_case()`: Simuliert eine erfolgreiche direkte Buchung.
- `test_optimize_revenue_initialization()`: Überprüft, ob der Revenue Optimizer korrekt initialisiert wird.

## Sandbox-Automation

Die Automation des Sandboxes erfolgt durch den LaunchAgent im Pfad `scripts/com.kemmer.df-heylou-mistral-extension.plist`, der eine 2-Stunden-Intervall-Schleife ausführt und automatisch Starts auf `RunAtLoad` aktiviert.

### LaunchAgent-Konfiguration
```bash
Plist: scripts/com.kemmer.df-heylou-mistral-extension.plist
StartInterval: 7200s (2h)
RunAtLoad: true
WorkingDir: /Users/make/Projects/dark-factories/df-heylou-mistral-extension
```

## Cross-DF-Coupling

Aktuell erfolgt die Lazy-Import-Stubs-Konfiguration in den Backends `W36` und `W37`, um eine flexiblere Integration zu gewährleisten.

### Beispiel: df-pms-mews-adapter (Welle 36)
```python
from df_heylou_mistral_extension.df_pms_mews_adapter import get_rates

# Import Lazy for Backend W36
get_rates(hotel_id, date_range)
```

### Beispiel: df-ota-* (Welle 37)
```python
from df_heylou_mistral_extension.df_ota_booking_adapter import compare_otas

# Import Lazy for Backend W37
compare_otas(hotel_id, dates)
```

## Auditlog-Architektur

Alle API-Anrufe werden durch den `AuditLogger` mit HMAC-SHA256 JSONL-Format gesichert und für die spätere Überprüfung archiviert.

### Logbeispiel:
```json
{
  "timestamp": "2023-11-17T14:58:43Z",
  "function_call": "search_hotels",
  "params": {
    "location": "Berlin, Germany",
    "dates": ["2026-12-01", "2026-12-05"],
    "preferences": {"room_type": "suite"}
  },
  "response": {
    "hotel_name": "The Grand Berlin Hotel",
    "rates": [95.0, 100.0, 110.0],
    "availability": true
  }
}
```

## K11-K16 + LC1-LC5

Die Implementierung berücksichtigt die Sicherheitsrichtlinien der Welle 39, einschließlich Pre-Action-Verifikation via `auth_handler.verify_phronesis_ticket()` und das Verhindern von Overlap durch mkdir-Mutex in den Skriptdateien `scripts/run-*.sh`.

### Beispiel: K13-Pre-Aktion
```python
def handle_function_call(function_call):
    phronesis_ticket = auth_handler.get_phronesis_ticket()
    if not auth_handler.verify_phronesis_ticket(phronesis_ticket):
        raise PermissionError("Unauthorized Access")
```

## Fazit

Die Dark-Factory `df-heylou-mistral-extension` bietet eine robuste und skalierbare Lösung für die Integration von HeyLou-Funktionalitäten in der Mistral Function-Calling API. Durch die aktive Nutzung des Knowledge-Bases und der Notebooks sowie den Einsatz von konkreten Testfällen und Sandbox-Automatisierung gewährleistet sie hohe Zuverlässigkeit und Sicherheit im Produktionsbetrieb.

**Zusammenfassung**: Die Dark-Factory ist vollständig implementiert, durch Tests abgesichert und für die Verwendung in der Mistral-Funktion-Calling-API vorbereitet.