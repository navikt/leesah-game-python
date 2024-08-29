"""The Quiz Rapid class."""
import json
import uuid
import os
import yaml

from datetime import datetime
from pathlib import Path
from yaml.loader import SafeLoader
from json import JSONDecodeError
from confluent_kafka import Consumer, Producer, KafkaError, KafkaException

from .kafka_config import consumer_config, producer_config
from .models import Answer, Question, TYPE_QUESTION


class QuizRapid:
    """Mediates messages.

    To and from the quiz rapid on behalf of the quiz participant
    """

    def __init__(self,
                 team_name: str,
                 topic: str = os.getenv("QUIZ_TOPIC"),
                 ignored_categories: list = [],
                 consumer_group_id: str = uuid.uuid4(),
                 path_to_certs: str = os.environ.get(
                     'QUIZ_CERTS', 'leesah-certs.yaml'),
                 auto_commit: bool = False,):
        """
        Construct all the necessary attributes for the QuizRapid object.

        Parameters
        ----------
            team_name : str
                team name to filter messages on
            topic : str
                topic to produce and consume messages on (default is first topic in certs file)
            ignored_categories : list
                list of categories to ignore for handling (default is empty list)
            consumer_group_id : str
                the kafka consumer group id to commit offset on (default is random uuid)
            path_to_certs : str
                path to the certificate file (default is leesah-certs.yaml)
            auto_commit : bool, optional
                auto commit offset for the consumer (default is False)
        """
        certs_path = Path(path_to_certs)
        if not certs_path.exists():
            if Path("certs/leesah-certs.yaml").exists():
                cert_path = Path("certs/leesah-certs.yaml")
            else:
                raise FileNotFoundError(
                    f"Could not find certs file in: {path_to_certs} or {certs_path}")

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
        self._team_name = team_name
        self._producer: Producer = producer
        self._consumer: Consumer = consumer
        self._ignored_categories = ignored_categories

        print("🚀 Starting QuizRapid...")
        print("🔍 looking for first question")

    def get_question(self):
        """Get a question from the quiz rapid."""
        while self.running:
            msg = self._consumer.poll(timeout=1)
            if msg is None:
                continue

            if msg.error():
                self._handle_error(msg)
            else:
                question = self._handle_message(msg)
                if question:
                    if question.kategorinavn not in self._ignored_categories:
                        print(f"📥 Received question: {question}")
                    return question

    def _handle_error(self, msg):
        """Handle errors from the consumer."""
        if msg.error().code() == KafkaError._PARTITION_EOF:
            print("{} {} [{}] reached end at offset\n".
                  format(msg.topic(), msg.partition(), msg.offset()))
        elif msg.error():
            raise KafkaException(msg.error())

    def _handle_message(self, msg):
        """Handle messages from the consumer."""
        try:
            msg = json.loads(msg.value().decode("utf-8"))
        except JSONDecodeError as e:
            print(f"error: could not parse message: {msg.value()}, error: {e}")
            return

        try:
            if msg["@event_name"] == TYPE_QUESTION:
                self._last_message = msg
                return Question(id=msg['spørsmålId'],
                                kategorinavn=msg['kategorinavn'],
                                spørsmål=msg['spørsmål'],
                                svarformat=msg['svarformat'])
        except KeyError as e:
            print(f"error: unknown message: {msg}, missing key: {e}")
            return

    def answer(self, answer_string: str):
        try:
            if answer_string:
                msg = self._last_message
                answer = Answer(spørsmålId=msg['spørsmålId'],
                                kategorinavn=msg['kategorinavn'],
                                lagnavn=self._team_name,
                                svar=answer_string).model_dump()
                answer["@opprettet"] = datetime.now().isoformat()
                answer["@event_name"] = "SVAR"

                if msg['kategorinavn'] not in self._ignored_categories:
                    print(f"📤 Published answer: kategorinavn='{msg['kategorinavn']}' svar='{answer_string}' lagnavn='{self._team_name}'")

                value = json.dumps(answer).encode("utf-8")
                self._producer.produce(topic=self._topic,
                                       value=value)
                self._last_message = None
        except KeyError as e:
            print(f"error: unknown message: {msg}, missing key: {e}")

    def close(self):
        """Close the QuizRapid."""
        print("🛑 shutting down...")
        self.running = False
        self._producer.flush()
        self._consumer.close()
        self._consumer.close()
