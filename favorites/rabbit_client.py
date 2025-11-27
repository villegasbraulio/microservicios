import json
import threading
import time
import uuid

import pika
from django.conf import settings


class ArticleValidationError(Exception):
    """Error raised when an article cannot be validated."""


class ArticleValidator:
    """RabbitMQ RPC style client to validate articles before saving favorites."""

    def __init__(self):
        self._url = getattr(settings, "RABBIT_URL", "amqp://localhost")
        self._exchange = "article_exist"
        self._lock = threading.Lock()
        self._connection = None
        self._channel = None
        self._callback_queue = None
        self._response = None
        self._corr_id = None
        self._ensure_connection()

    def _ensure_connection(self):
        if self._connection and not self._connection.is_closed:
            return

        parameters = pika.URLParameters(self._url)
        self._connection = pika.BlockingConnection(parameters)
        self._channel = self._connection.channel()
        self._channel.exchange_declare(exchange=self._exchange, exchange_type="direct", durable=False)

        result = self._channel.queue_declare(queue="", exclusive=True)
        self._callback_queue = result.method.queue

        self._channel.queue_bind(
            exchange=self._exchange,
            queue=self._callback_queue,
            routing_key=self._callback_queue,
        )

        self._channel.basic_consume(
            queue=self._callback_queue,
            on_message_callback=self._on_response,
            auto_ack=True,
        )

    def _close_connection(self):
        try:
            if self._connection and self._connection.is_open:
                self._connection.close()
        except Exception:
            pass
        finally:
            self._connection = None
            self._channel = None
            self._callback_queue = None

    def _on_response(self, ch, method, props, body):
        try:
            payload = json.loads(body.decode("utf-8"))
        except json.JSONDecodeError:
            return

        incoming_corr = props.correlation_id or payload.get("correlation_id")
        if self._corr_id is None or incoming_corr == self._corr_id:
            self._response = payload

    def _call(self, article_id: str, reference_id: str, timeout: float = 5.0):
        self._response = None
        self._corr_id = str(uuid.uuid4())

        payload = {
            "correlation_id": self._corr_id,
            "exchange": self._exchange,
            "routing_key": self._callback_queue,
            "message": {
                "referenceId": reference_id,
                "articleId": article_id,
            },
        }

        self._channel.basic_publish(
            exchange=self._exchange,
            routing_key="article_exist",
            properties=pika.BasicProperties(
                correlation_id=self._corr_id,
                content_type="application/json",
                delivery_mode=1,
            ),
            body=json.dumps(payload),
        )

        deadline = time.time() + timeout
        while self._response is None and time.time() < deadline:
            self._connection.process_data_events(time_limit=0.1)

        if self._response is None:
            raise ArticleValidationError("Timeout validando artículo contra catálogo")

        return self._response

    def validate(self, article_id: str, reference_id: str) -> dict:
        with self._lock:
            for _ in range(2):
                try:
                    self._ensure_connection()
                    return self._call(article_id, reference_id)
                except (pika.exceptions.AMQPError, OSError):
                    self._close_connection()
            raise ArticleValidationError("No se pudo establecer conexión con RabbitMQ")


_validator = None


def _get_validator() -> ArticleValidator:
    global _validator
    if _validator is None:
        try:
            _validator = ArticleValidator()
        except (pika.exceptions.AMQPError, OSError) as exc:
            raise ArticleValidationError("No se pudo conectar a RabbitMQ") from exc
    return _validator


def validate_article(article_id: str, reference_id: str) -> dict:
    """Validates an article through RabbitMQ and returns the payload."""
    response = _get_validator().validate(article_id, reference_id)
    message = response.get("message") or response
    if not message.get("valid"):
        raise ArticleValidationError("El artículo no existe o está deshabilitado")
    return message

