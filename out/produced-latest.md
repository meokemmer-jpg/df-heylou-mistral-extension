# df-heylou-mistral-extension — PRODUKTION [CRUX-MK]
*2026-06-06T21:13:11.380821+00:00 | ollama-local/kemmer-70b-ctx8k*

# df-heylou-mistral-extension — Dokumentation [CRUX-MK]
## Stand: 2026-05-12
## Version: v1.0.0
## Status: PRODUKTIONSREIF
## Welle: 39
## K_0-Touch: true (book_direct ist K_0-relevant)

### Übersicht

Die Dark-Factory `df-heylou-mistral-extension` integriert HeyLou als Sub-Fu
Sub-Funktion in die Mistral Function-Calling API. Dies ermöglicht DeepSeek 
und anderen LLM Plattformen, Anfragen an den HeyLou Travel-Knowledge-Graph 
zu richten.

### Funktionen

Die folgenden fünf Funktionen sind implementiert:

1. **`search_hotels(location, dates, preferences)`**: Durchführt eine Hotel
Hotel-Suche im HeyLou Travel-Knowledge-Graph basierend auf der angegebenen 
Location, den Reisedaten und den bevorzugten Eigenschaften.
2. **`get_rates(hotel_id, date_range)`**: Ruft die verfügbaren Tarife für e
ein bestimmtes Hotel innerhalb eines angegebenen Datumbereichs ab.
3. **`compare_otas(hotel_id, dates)`**: Vergleicht die Preise von Online-To
Online-Tourismus-Anbietern (OTAs) wie Booking, Expedia und HRS für ein best
bestimmtes Hotel an den angegebenen Daten.
4. **`book_direct(hotel_id, room_type, guest, dates)`**: Bucht direkt über 
HeyLou ohne Provision, wenn der Benutzer die erforderlichen Informationen b
bereitstellt.
5. **`optimize_revenue(hotel_id)`**: Eine Stub-Funktion für zukünftige Impl
Implementierung von Revenue-Optimierungsstrategien.

### Konfiguration

Für den Betrieb in Produktionsumgebung sind folgende Umgebungsvariablen erf
erforderlich:

* `DF_HEYLOU_MISTRAL_EXT_ENABLED=true`
* `PHRONESIS_TICKET=XXXX-YYYY-ZZZZ` (ersetzte durch einen gültigen Phronesi
Phronesis-Ticket)
* `MISTRAL_API_KEY=ABC123DEF456` (ersetze durch einen gültigen Mistral API-
API-Schlüssel)

Ohne diese Einstellungen wird der Modus im Mock-Simulation umgeschaltet.

### Architektur

Die Systemarchitektur ist wie folgt organisiert:

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

### Implementierungsdetails

* **Backend-Anbindung**: Die Funktionen `search_hotels`, `get_rates`, `comp
`compare_otas` und `book_direct` werden durch die HeyLou Travel-Domain-Back
Travel-Domain-Backend implementiert. Die Funktion `optimize_revenue` ist de
derzeit eine Stub und wird in zukünftigen Versionen implementiert.
* **Sicherheit**: Alle Anfragen an das Backend werden mittels HMAC-SHA256 s
signiert, um Authentizität und Integrität zu gewährleisten.
* **Audit-Logging**: Jede Funktion wird durch einen Audit-Logger protokolli
protokolliert, der alle Anfragen und Antworten in einem JSONL-Format speich
speichert.

### Tests

Es wurden insgesamt 15 Tests für die verschiedenen Funktionen erstellt:

1. **`test_search_hotels.py`**: Testet die Hotel-Suche mit verschiedenen Pa
Parametern.
2. **`test_get_rates.py`**: Überprüft die Tarife für verschiedene Hotels un
und Datumbereiche.
3. **`test_compare_otas.py`**: Vergleicht die Preise von OTAs für verschied
verschiedene Hotels und Daten.
4. **`test_book_direct.py`**: Testet die direkte Buchung mit verschiedenen 
Parametern.
5. **`test_optimize_revenue.py`**: Überprüft die Stub-Funktion für Revenue-
Revenue-Optimierung.

Die Tests können durch Ausführen des Befehls `pytest tests/ -v` gestartet w
werden.

### Fazit

Die Dark-Factory `df-heylou-mistral-extension` bietet eine umfassende Integ
Integration von HeyLou in die Mistral Function-Calling API. Durch die Imple
Implementierung der fünf Funktionen kann DeepSeek und andere LLM Plattforme
Plattformen den HeyLou Travel-Knowledge-Graph nutzen, um Hotel-Suchen, Tari
Tarife, OTA-Vergleiche und direkte Buchungen durchzuführen. Die Architektur
Architektur ist sicher und skalierbar, und die Tests gewährleisten eine hoh
hohe Qualität der Implementierung.