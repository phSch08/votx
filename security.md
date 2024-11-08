# Sicherheitsbetrachtungen

Die Voting-Platform soll eine Wahl mit Berücksichtigung der 5 Wahlgrundsätze ermöglichen:
- Allgemein
- Unmittelbar
- Frei
- Gleich
- Geheim

Alle diese Grundsätze lassen sich durch eine Software nicht nachvollziehbar für eine breite Öffentlichkeit ohne spezifische Kenntnisse der Informationstechnologie gewährleisten. Der Einsatz einer Wahlsoftware muss daher immer mit Augenmaß erfolgen und muss unterlassen werden, wenn ein hinreichendes Bedürfnis der Wählerschaft auf Nachvollziehbarkeit der Wahl besteht.

## Implementierter Ablauf der Wahl

1. In Vorbereitung der Wahl wird eine beliebige Anzahl an Wahltoken generiert. Diese werden zum einen in der Datenbank hinterlegt, zum anderen in Form eines QR-Codes als PDF zur Verfügung gestellt.
1. Zu beginn der Wahl werden die QR-Codes zufällig an die wählenden Personen ausgeteilt. Durch diesen Schritt sollte keine Zuordnung eines Wahlergbnisses zu einer Person mehr möglich sein.
1. Die Wahlteilnehmer scannen den QR-Code, wodurch sie auf die Wähler-Website weitergeleitet werden. Der Server liefert die entsprechende Website zur Wahl aus. Auf dieser Website ist ein Skript hinterlegt, welches über Websockets eine Verbindung zum Server herstellt. Dabei prüft der Server die existenz des Wahltokens und gibt eine Liste aller laufenden und abgeschlossenen Wahlen zurück.
1. Der Wahlgang wird verlesen, und im Admin-Interface angelegt.
1. Der Wahlgang wird im Admin-Interface gestartet. Daraufhin erhalten alle registrieten Geräte die Information, dass ein neuer Wahlgang existiert. Die Geräte zeigen den Wahlgang für die Wähler an.
1. Die Wähler treffen Ihre Wahl. Das Wahlergebnis wird zusammen mit dem Wahltoken über den Websocket an den Server gesendet.
1. Der Server prüft, ob mit dem Wahltoken für den Wahlgang noch eine Wahl erfolgen darf und ob das Wahlergebnis legitim (Anzahl der Stimmen, Stimmhäufung, etc.) ist.
1. Der Server speichert das Wahlergebnis mit der Referenz zum entsprechenden Wahlgang in der Datenbank ab. Für das Wahltoken wird gespeichert, dass eine Wahl im entsprechenden Wahlgang stattgefunden hat. Beide Datenbankzugriffe werden in einem atomaren Schreibvorgang vorgenommen.
1. Der Server bestätigt den Wahlvorgang.
1. Der Server schickt eine Liste aller laufenden und abgeschlossenen Wahlen für das Wahltoken zurück.
1. Der Wähler kann so prüfen, dass eine Wahl mit seinem Wahltoken für den Wahlgang verbucht wurde.

## Annahmen

Für die Beurteilung der Umsetzung der Sicherheitsanforderungen ist von den folgenden Grundannahmen auszugehen:

- die Zustellung der Wahltoken erfolgt zufällig
- die Zustellung der Wahltoken ist Vertrauenswürdig
- der Wahlausschuss ist Vertrauenswürdig
- die Wahlsoftware inklusive der SLL-Verschlüsselung zwischen Mobilgerät und Server ist Vertrauenswürdig
- die Wahl findet in Präsenz statt


## Angriffsvektoren

### POLYAS

Die folgenden Angriffsvektoren stammen aus dem [POLYAS Whitepaper](https://www.polyas.de/sites/default/files/POLYAS_Whitepaper_Status-Quo-Sicherheit_Online-Wahlen.pdf)

#### 3.2.1 Manipulation durch Wahlvorbereitende Personen
Der Wahlausschuss ist als Vertrauenswürdig anzusehen. Eine Zuordnung von Person zu Wahlergebnis wird dadurch unterbunden, dass die Wahlzettel mit dem Wahltoken zufällig verteilt werden müssen. Zusätzlich kann Verbesserungsansatz 1 implementiert werden.

#### 3.2.2 Daten-Leak von Wähler-ID und Passwort
Die nicht-autorisierte Nutzung eines Wahltokens würde durch den eigentlich autorisierten Wähler festgestellt werden, da dieser die Meldung erhält, dass er bereits gewählt hat. Weiterhin ist es nicht möglich vom Wahltoken auf die getroffene Wahl zu schließen.

#### 3.2.3 Brute-Force-Angriffe
Siehe Begründung aus 3.2.2

#### 4.2.1 Ballot-Stuffing
Stimmen können nur in Verbindung mit dem Wahltoken abgegeben werden. Bei der Stimmabgabe wird durch den Server in der Datenbank vermerkt, dass eine Stimme abgegeben wurde. Die Stimme wird ebenfalls in der Datenbank hinterlegt. Eine zuordnung zwischen Stimme und Token wird jedoch nicht gespeichert.

#### 4.2.2 Manipulierte Stimmzettel
Um dieses Problem zu beheben kann Verbesserungsansazt 2 implementiert werden.

#### 5.2.1 Verrat des Wahlergebnisses
Bei Ordnungsgemäßer zufälliger Verteilung der Wahltoken kann nachfolgend keine Identifikation des Wahlergebnisses mehr stattfinden. In der Datenbank selbst wird keine Verknüpfung von Wahltoken zu getroffener Wahl gespeichert.

#### 5.2.2 Manipulation des Wahlergebnisses
Könnte durch den Verbesserungsansatz 2 gelöst werden. Ansonsten muss die Annahme gelten, dass die Wahlsoftware Vertrauenswürdig ist.

#### 6.2.1 Manipulation des Beweises durch den Wahlanbieter
Kann durch Verbesserungsansatz 2 gelöst werden. Alle Stimmen können Zeitgleich eingesehen werden. Jeder Wahlteilnehmer kann seine Stimme identifizieren und das Gesamtergbnis somit verifizieren.

#### 6.2.2 Ausschluss von Stimmenkauf
Nicht Sinnvoll umsetzbar. Begründung in Polyas-Paper nicht Sinnvoll.

#### 8.2.1 Manipulation der Verifikation durch Wahlanbieter
Siehe 6.2.1

## Verbesserungsansätze

### 1. Mindest-Wahlbeteiligung
Um zu verhindern, dass die Stimme einer einzelnen Person aufgrund des Wahlzeitpunktes ermittelt werden kann wird eine Ausgabe des Ergebnisses Softwareseitig erst ermöglicht, sobald mindestens X Stimmen eingegangen sind.

### 2. Wahlstimmen-ID
Während des Wahlvorgangs wird auf dem Endgerät des Wählers eine Zeichenkette generiert, die ihm nach absenden des Wahlzettels angezeigt wird. Die Zeichenkette kann der Wähler entsprechend notieren. Die Zeichenkette wird zusammen mit der getroffenen Wahl in der Datenbank gespeichert. Zweifelt ein Wähler an der Integrität der Wahl, so können im Anschluss die Einträge der Datenbank zusammen mit den Zeichenketten veröffentlicht werden. Daraus lässt sich das Ergebnis nachvollziehen. Weiterhin kann jeder Wähler aufgrund der generierten Zeichenkette sein persönliches Wahlergbenis nachvollziehen.

## Weitere Ideen
- Zusätzliche Verschlüsselung des Datenverkehrs zwischen Client und Server
  - Wenn SSL Zertifikat nicht vertrauenswürdig - welchen Vorteil hat das dann?
  - Website mit Skript beim initialen Abruf könnte ja schon manipuliert sein