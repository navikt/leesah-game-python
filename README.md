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
python3 -m pip install leesah-game # import leesah
```

### Hent Kafkasertifikat

Sertifikater for å koble seg på Kafka ligger tilgjengelig på [leesah-certs.ekstern.dev.nav.no](https://leesah-certs.ekstern.dev.nav.no), brukernavn og passord skal du få utdelt.

Du kan også bruke kommandoen nedenfor:

```bash
wget --user <username> --password <password> -O leesah-certs.zip https://leesah-certs.ekstern.dev.nav.no && unzip leesah-certs.zip 
```

### Eksempelkode

Nedenfor finner du et nesten fungerende eksempel som svarer på spørsmålet om lagregistrering med et navn og en farge (hex-kode):

```python
"""The Leesah quiz game client.

# 1. Ensure credential files are in the certs directory
# 2. Set `TEAM_NAME` to your preferred team name
# 3. Set `HEX_CODE` to your preferred team color
# 4. Remove the `NotImplementedError` and return your hex code
"""
import leesah

TEAM_NAME = "CHANGE ME"
HEX_CODE = "CHANGE ME"

class Rapid(leesah.QuizRapid):
    """The Rapid class that answers questions."""

    def run(self):
        """Run the quiz game.

        We recommend you to use functions to answer questions.
        """
        while True:
            question = self.get_question()
            print(f"Received question: {question}")
            if question.kategorinavn == leesah.TEAM_REGISTRATION:
                self.handle_register_team()

    def handle_register_team(self):
        raise NotImplementedError("DU MÅ HÅNDTERE team-registration HER")
        # self.answer(HEX_CODE)


if __name__ == "__main__":
    rapid = Rapid(TEAM_NAME, ignored_categories=[
        # leesah.TEAM_REGISTRATION,
    ])
    rapid.run()
```

### Kjør koden

Kjør koden din med:

```shell
python3 main.py
```
