# Prefect Bambu Studio .6 – Workflow 4

Die eigene einfache Feldauswahl kann als zusammenhängende Liste angezeigt
werden. Ausgewählte, derzeit nicht anwendbare Felder bleiben auffindbar und
ausgegraut; dabei werden keine Druckparameter oder Objekt-Overrides geändert.
„Brücken nicht unterstützen“ erklärt seine Beziehung zu Baumstützen.

Die Druckerbox ist standardmäßig eingeklappt und bleibt manuell aufklappbar.
Die Rotationsvorgabe ist editierbar und merkt sich spätere Entscheidungen pro
Druckmodus. Jeder direkte Anordnungsklick startet über den normalen Jobpfad;
Hintergrundslicing blockiert ihn nicht, ein bereits laufender UI-Job weiterhin.
Das Optionspopup bleibt offen, Werkzeugwechsel lösen keinen weiteren Lauf aus.

Ein neuer Toolbarbutton leert mit einem Klick nur die aktuelle Platte über
den vorhandenen, rückgängig machbaren Löschweg. Kopien auf anderen Platten,
Filamente und Druckeinstellungen bleiben erhalten. Die Aktion hat eigene
Guards und einen separaten Workflow-Schalter.

Eine eigene Workflowoption verkürzt ausschließlich die erfolgreiche manuelle
Filamentsynchronisations-Einblendung auf eine Sekunde. Sie blendet Information
aus, ohne OK zu klicken, Entscheidungen zu bestätigen oder den Fokus auf das
Hauptfenster zurückzuziehen. Fehler und andere Hinweise bleiben unverändert.

Die bisherigen Workflowfunktionen, die getrennte Helio-Werbesteuerung und die
violette Prefect-Kennung bleiben erhalten. Druckerkommunikation und ausdrücklich
aktivierte Analysen erhalten ihre bisherigen Funktionspfade.

Basis ist Bambu Studio v02.08.02.61. Der eingefrorene neue Quellstand ist
727a703155237a94e4fcc31ebc4effef515d13f0 (Tree
16cbb874d6bef7ebbc3453e407451eb9af252b0e). Die Auslieferung bindet den tatsächlich
gebauten Quellstand, das vollständige Windows-Paket und die reproduzierbare
Patchserie; SHA256SUMS.txt enthält die beiden Archiv-Prüfsummen.

Prüfgrenzen: Policytests und Paketprüfungen ersetzen keine vollständige sichtbare
GUI-/Druckerabnahme. Dieser vorbereitete Releasetext behauptet keinen normalen
Profilneustart, keine neue Pinaktion und keine Wiederherstellung privater Projekte.
