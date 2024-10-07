# LEESAH Python

> Leesah-game er et hendelsedrevet applikasjonsutviklingspill som utfordrer spillerne til å bygge en hendelsedrevet applikasjon. 
> Applikasjonen håndterer forskjellige typer oppgaver som den mottar som hendelser på en Kafka-basert hendelsestrøm. 
> Oppgavene varierer fra veldig enkle til mer komplekse.

Python-bibliotek for å spille LEESAH!

## Kom i gang

Det finnes to versjoner av Leesah-game!
En hvor man lager en applikasjon som kjører på Nais, og en hvor man spiller lokalt direkte fra terminalen.
Dette biblioteket kan brukes i begge versjoner, men denne dokumentasjonen dekker **kun** lokal spilling.

### Sett opp lokalt miljø

Vi anbefaler at du bruker et virtuelt miljø for å kjøre koden din, som for eksempel [Venv](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/).

Start med å opprette en katalog `leesah-game`.

**For macOS/Linux**
```shell
cd leesah-game
python3 -m venv venv
source ./venv/bin/activate
```

**For Windows**
```shell
cd leesah-game
python3 -m venv venv
.\venv\Scripts\activate
```

### Installer biblioteket

Det er kun en avhengighet du trenger, og det er biblioteket [leesah-game](https://pypi.org/project/leesah-game/).

```shell
python3 -m pip install leesah-game
```

### Hent Kafkasertifikat

Sertifikater for å koble seg på Kafka ligger tilgjengelig på [leesah.io/certs](https://leesah.io/certs), passord får du utdelt.

Du kan også bruke kommandoen nedenfor:

```bash
curl -u leesah-game:<se presentasjon> -o leesah-certs.zip https://leesah.io/certs && unzip leesah-certs.zip
```

Du vil nå ende opp med filen `leesah-certs.yaml` i `leesah-game`-katalogen du lagde tidligere.

### Eksempelkode

For å gjøre det enklere å komme i gang har vi et fungerende eksempel som svarer på spørsmålet om lagregistrering med et navn og en farge (hexkode).
Opprett filen `main.py` og lim inn koden nedenfor.

```python
"""Spill Leesah-game

1. Hent ned sertifikater, og sikre deg at de ligger i filen leesah-certs.yaml
2. Sett 'LAGNAVN' til ditt valgte lagnavn
3. Sett 'HEXKODE' til din valgte farge
"""
import leesah

LAGNAVN = "BYTT MEG"
HEXKODE = "BYTT MEG"


class Rapid(leesah.QuizRapid):
    """Klassen som svarer på spørsmålene."""

    def kjør(self):
        """Start quizen!

        Vi anbefaler at du bruker funksjoner til å svare på spørsmålene.
        """
        while True:
            melding = self.hent_spørsmål()
            if melding.kategori == "team-registration":
                self.behandle_lagregistrering(melding.spørsmål)

    def behandle_lagregistrering(self, spørsmål):
        self.publiser_svar(HEXKODE)


if __name__ == "__main__":
    rapid = Rapid(LAGNAVN, ignorerte_kategorier=[
        # "team-registration",
    ])

    try:
        rapid.kjør()
    except (KeyboardInterrupt, SystemExit):
        rapid.avslutt()
```

### Kjør koden

Kjør koden din med:

```shell
python3 main.py
```
