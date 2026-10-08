/* Der Fokus folgt einer Handlung, nicht dem Laden der Seite (P8-V12).
 *
 * Zwei Beobachter setzen den Fokus auf eine Ueberschrift: die Schrittfolge,
 * wenn ein neuer Schritt gezeichnet ist (P1.9-W5.3), und der Bereichswechsel
 * (P1.5). Beide liefen auch beim **ersten** Zeichnen -- die Schrittfolge, weil
 * ihr Inhalt dann zum ersten Mal kommt, der Bereichswechsel, weil
 * `dcc.Location` den Pfad nach dem Laden als Aenderung meldet. Dann hatte
 * niemand etwas getan, dem der Fokus folgen koennte, und der Sprunglink lag
 * hinter dem ersten Tabulator (Befund N2 der Gegenpruefung vom 2026-09-21,
 * WCAG 2.4.1).
 *
 * Gemerkt wird deshalb, **ob** jemand gehandelt hat: ein Zeiger, eine Taste
 * oder Vor/Zurueck im Browser. Erst danach nehmen die Beobachter den Fokus.
 * Am `document` und in der Einfangphase, damit kein Element die Meldung
 * verschluckt; die beiden Beobachter fragen `window.afHatGehandelt`.
 */
(function () {
    window.afHatGehandelt = false;
    var gehandelt = function () { window.afHatGehandelt = true; };
    document.addEventListener("pointerdown", gehandelt, true);
    document.addEventListener("keydown", gehandelt, true);
    window.addEventListener("popstate", gehandelt);
})();
