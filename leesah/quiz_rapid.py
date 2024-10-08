import json
import uuid
import os
import yaml
import traceback

from datetime import datetime
from pathlib import Path
from yaml.loader import SafeLoader
from json import JSONDecodeError
from confluent_kafka import Consumer, Producer, KafkaError, KafkaException

from .kafka_config import consumer_config, producer_config
from .modeller import Svar, Spørsmål, TYPE_SVAR, TYPE_SPØRSMÅL


class QuizRapid:
    """Kvissformidler av spørsmål og svar.

    Til og fra stryket på vegne av deltakerne.
    """

    def __init__(self,
                 lagnavn: str,
                 ignorerte_kategorier: list = [],
                 topic: str = os.getenv("QUIZ_TOPIC"),
                 consumer_group_id: str = uuid.uuid4(),
                 path_to_certs: str = os.environ.get(
                     'QUIZ_CERTS', 'leesah-certs.yaml'),
                 auto_commit: bool = False,):
        """
        Konstruerer alle de nødvendige attributtene for et Kvissobjekt.

        Parametere
        ----------
            lagnavn : str
                lagnavn for å publisere meldinger med
            ignorerte_kategorier : list
                liste av kategorier som ikke skal logges (default er en tom liste)
            topic : str
                topic to produce and consume messages on (default is first topic in certs file)
            consumer_group_id : str
                the kafka consumer group id to commit offset on (default is random uuid)
            path_to_certs : str
                path to the certificate file (default is leesah-certs.yaml)
            auto_commit : bool, optional
                auto commit offset for the consumer (default is False)
        """
        print("🚀 Starter opp...")
        certs_path = Path(path_to_certs)
        if not certs_path.exists():
            if Path("certs/leesah-certs.yaml").exists():
                cert_path = Path("certs/leesah-certs.yaml")
            else:
                raise FileNotFoundError(
                    f"Kunne ikke finne sertifikater: {path_to_certs} eller {certs_path}")

        certs = yaml.load(certs_path.open(mode="r").read(),
                          Loader=SafeLoader)
        if not topic:
            self._topic = certs["topics"][0]
        else:
            self._topic = topic

        consumer = Consumer(consumer_config(certs,
                                            consumer_group_id,
                                            auto_commit))
        consumer.subscribe([self._topic])

        producer = Producer(producer_config(certs))

        self.running = True
        self._lagnavn = lagnavn
        self._producer: Producer = producer
        self._consumer: Consumer = consumer
        self._ignored_categories = ignorerte_kategorier

        print("🔍 Ser etter første spørsmål")

    def hent_spørsmål(self):
        """Henter neste spørsmål fra stryket."""
        while self.running:
            msg = self._consumer.poll(timeout=1)
            if msg is None:
                continue

            if msg.error():
                self._handle_error(msg)
            else:
                question = self._handle_message(msg)
                if question:
                    if question.kategori not in self._ignored_categories:
                        print(f"📥 Mottok spørsmål: {question}")
                    return question

    def _handle_error(self, msg):
        """Behandler feil fra forbrukeren."""
        if msg.error().code() == KafkaError._PARTITION_EOF:
            print("{} {} [{}] kom til enden av offset\n".
                  format(msg.topic(), msg.partition(), msg.offset()))
        elif msg.error():
            raise KafkaException(msg.error())

    def _handle_message(self, msg):
        """Behandler meldinger fra konsumenten."""
        try:
            msg = json.loads(msg.value().decode("utf-8"))
        except JSONDecodeError as e:
            print(f"feil: kunne ikke lese meldingen: {msg.value()}, feil: {e}")
            return

        try:
            if msg["@event_name"] == TYPE_SPØRSMÅL:
                self._last_message = msg
                return Spørsmål(kategori=msg['kategori'],
                                spørsmål=msg['spørsmål'],
                                svarformat=msg['svarformat'],
                                id=msg['spørsmålId'],
                                dokumentasjon=msg['dokumentasjon'])
        except KeyError as e:
            print(f"feil: ukjent melding: {msg}, mangler nøkkel: {e}")
            return

    def publiser_svar(self, svar: str):
        """Publiserer et svar til stryket."""
        try:
            if svar:
                msg = self._last_message
                answer = Svar(spørsmålId=msg['spørsmålId'],
                                kategori=msg['kategori'],
                                lagnavn=self._lagnavn,
                                svar=svar).model_dump()
                answer["@opprettet"] = datetime.now().isoformat()
                answer["@event_name"] = TYPE_SVAR

                if msg['kategori'] not in self._ignored_categories:
                    print(f"📤 Publisert svar: kategori='{msg['kategori']}' svar='{svar}' lagnavn='{self._lagnavn}'")

                value = json.dumps(answer).encode("utf-8")
                self._producer.produce(topic=self._topic,
                                       value=value)
                self._last_message = None
        except KeyError as e:
            print(f"feil: ukjent svar: {msg}, mangler nøkkel: {e}")
        except TypeError:
            stack = traceback.format_stack()
            print("DobbeltSvarException (prøver du å svare to ganger på rad?):")
            for line in stack:
                if "quiz_rapid.py" in line:
                    break
                print(line, end='')
            exit(1)

    def avslutt(self):
        """Avslutter kviss."""
        print("🛑 Stenger ned...")
        self.running = False
        self._producer.flush()
        self._consumer.close()
        self._consumer.close()
