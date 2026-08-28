/* Ziehbare Zonenbreiten des Leitstands (P1.7).
 *
 * Die Breiten von Bedienfeld und Telemetrie waren fest. Wer die Szene groesser
 * wollte oder die Telemetrie breiter, konnte nichts tun.
 *
 * **Warum clientseitig und nicht als Dash-Callback:** dieselbe Begruendung wie
 * beim Theme-Umschalter in P1.5. Ein Serverrundlauf je Mausbewegung macht das
 * Ziehen zaeh; der Server hat zu einer Spaltenbreite ausserdem nichts
 * beizutragen.
 *
 * **Warum die Breite auf `<html>` landet und nicht auf dem Shell-Element:**
 * `.af-shell` wird von Dash bei einem Neuaufbau ersetzt, `<html>` nie. Ein
 * Inline-Stil dort schlaegt die `:root`-Regel ohne Spezifitaetstricks, und
 * `.af-shell` erbt ihn. Dasselbe Skript im Kopf von `app.py` liest den
 * gespeicherten Wert vor dem ersten Zeichnen zurueck, damit die Spalte nicht
 * erst in der Standardbreite aufblitzt.
 *
 * **Warum Ereignisdelegation:** Die Griffe liegen im Dash-Layout und koennen
 * bei einem Neuaufbau ausgetauscht werden. Ein Zuhoerer am `document`
 * ueberlebt das, ein Zuhoerer am Griff nicht.
 */
(function () {
    "use strict";

    var SPEICHER = { left: "af-shell-left", right: "af-shell-right" };

    /* Grenzen in Pixeln. Untergrenze: schmaler wird das Bedienfeld unlesbar
       (die Stand-Zeilen brechen um). Obergrenze: Der Viewport ist die
       Hauptsache eines Leitstands und darf nicht zur Restflaeche werden --
       deshalb bekommt er mindestens die Haelfte des Fensters. */
    var MIN = 220;
    var MAX_ANTEIL = 0.32;

    var zug = null;

    function shell() {
        return document.getElementById("af-shell");
    }

    function grenze(wert) {
        var max = Math.max(MIN, window.innerWidth * MAX_ANTEIL);
        return Math.round(Math.min(Math.max(wert, MIN), max));
    }

    function setzen(seite, breite) {
        document.documentElement.style.setProperty("--shell-" + seite, breite + "px");
        try {
            window.localStorage.setItem(SPEICHER[seite], String(breite));
        } catch (e) {
            /* Privater Modus: Die Breite gilt dann nur fuer diese Sitzung. */
        }
    }

    function zuruecksetzen(seite) {
        document.documentElement.style.removeProperty("--shell-" + seite);
        try {
            window.localStorage.removeItem(SPEICHER[seite]);
        } catch (e) {}
    }

    document.addEventListener("pointerdown", function (ereignis) {
        var griff = ereignis.target.closest && ereignis.target.closest(".af-shell__gutter");
        if (!griff) {
            return;
        }
        var seite = griff.classList.contains("af-shell__gutter--left") ? "left" : "right";
        var zone = document.querySelector(".af-shell__" + seite);
        if (!zone) {
            return;
        }
        zug = {
            seite: seite,
            start: ereignis.clientX,
            breite: zone.getBoundingClientRect().width,
        };
        if (shell()) {
            shell().classList.add("af-shell--dragging");
        }
        /* Der Zeiger bleibt beim Griff, auch wenn er ihn verlaesst -- sonst
           reisst der Zug ab, sobald er ueber ein Plotly-Diagramm laeuft. */
        if (griff.setPointerCapture) {
            griff.setPointerCapture(ereignis.pointerId);
        }
        ereignis.preventDefault();
    });

    document.addEventListener("pointermove", function (ereignis) {
        if (!zug) {
            return;
        }
        var weg = ereignis.clientX - zug.start;
        /* Der rechte Griff waechst nach links: Was der Zeiger nach rechts geht,
           nimmt die rechte Zone ab. */
        var roh = zug.seite === "left" ? zug.breite + weg : zug.breite - weg;
        setzen(zug.seite, grenze(roh));
    });

    function beenden() {
        if (!zug) {
            return;
        }
        zug = null;
        if (shell()) {
            shell().classList.remove("af-shell--dragging");
        }
    }

    document.addEventListener("pointerup", beenden);
    document.addEventListener("pointercancel", beenden);

    /* Doppelklick stellt die Ausgangsbreite her -- die einzige Geste, die ohne
       Zielen funktioniert, wenn man sich verzogen hat. */
    document.addEventListener("dblclick", function (ereignis) {
        var griff = ereignis.target.closest && ereignis.target.closest(".af-shell__gutter");
        if (!griff) {
            return;
        }
        zuruecksetzen(griff.classList.contains("af-shell__gutter--left") ? "left" : "right");
    });

    /* Tastatur: Die Griffe sind fokussierbar, also muessen sie auch ohne Maus
       bedienbar sein. */
    document.addEventListener("keydown", function (ereignis) {
        var griff = ereignis.target.closest && ereignis.target.closest(".af-shell__gutter");
        if (!griff) {
            return;
        }
        var schritt = ereignis.key === "ArrowLeft" ? -16 : ereignis.key === "ArrowRight" ? 16 : 0;
        if (!schritt) {
            return;
        }
        var seite = griff.classList.contains("af-shell__gutter--left") ? "left" : "right";
        var zone = document.querySelector(".af-shell__" + seite);
        if (!zone) {
            return;
        }
        var breite = zone.getBoundingClientRect().width;
        setzen(seite, grenze(seite === "left" ? breite + schritt : breite - schritt));
        ereignis.preventDefault();
    });
})();
