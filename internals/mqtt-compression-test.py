#!/usr/bin/env python3

import argparse
import datetime
import logging
import lzma
import platform
import ssl
import zlib

import brotli
import cbor2 as cbor
import lz4.frame
import paho.mqtt.client as mqtt
import zstd
from influxdb import InfluxDBClient
from radiotracking import MatchingSignal, Signal
from radiotracking.consume import cborify, uncborify

parser = argparse.ArgumentParser(
    prog="mqtt-influx-bridge",
    description="Compress radiotracking signals",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
)
parser.add_argument("-v", "--verbose", help="increase output verbosity", action="count", default=0)

parser.add_argument("--mqtt-host", help="hostname for MQTT broker connection", default="localhost")
parser.add_argument("--mqtt-port", help="port for MQTT connection", default=1883, type=int)
parser.add_argument("--mqtt-keepalive", help="MQTT keepalive duration", default=60, type=int)
parser.add_argument("--mqtt-tls", help="use tls for broker connection", default=False, action="store_true")
parser.add_argument("--mqtt-username", help="MQTT username", type=str)
parser.add_argument("--mqtt-password", help="MQTT password", type=str)


def prec_round(number: float, ndigits: int, base: float):
    return round(base * round(float(number) / base), ndigits)


batch = []


def on_matched_cbor(client: mqtt.Client, userdata, message):
    signal = cbor.loads(message.payload, tag_hook=uncborify)
    batch.append(signal)
    logging.debug(signal)

    cbor_batch = cbor.dumps(
        batch,
        timezone=datetime.timezone.utc,
        datetime_as_timestamp=True,
        default=cborify,
    )
    batch_s = len(cbor_batch)
    lzma_s = len(lzma.compress(cbor_batch)) / batch_s
    zlib_s = len(zlib.compress(cbor_batch, 9)) / batch_s
    lz4_s = len(lz4.frame.compress(cbor_batch, compression_level=lz4.frame.COMPRESSIONLEVEL_MAX)) / batch_s
    zstd_s = len(zstd.compress(cbor_batch, 22)) / batch_s
    brotli_s = len(brotli.compress(cbor_batch, quality=11)) / batch_s

    if len(batch) < 10 or (len(batch) % 10) == 0:
        print(f"{len(batch)}, {batch_s}, {lzma_s}, {zlib_s}, {lz4_s}, {zstd_s}, {brotli_s}")


def on_connect(mqttc: mqtt.Client, inlfuxc, flags, rc):
    logging.info(f"MQTT connection established ({rc})")

    # subscribe to match signal cbor messages
    topic_matched_cbor = "jonas-rpi-00001/radiotracking/matched/cbor"
    mqttc.subscribe(topic_matched_cbor)
    mqttc.message_callback_add(topic_matched_cbor, on_matched_cbor)
    logging.info(f"Subscribed to {topic_matched_cbor}")


if __name__ == "__main__":
    args = parser.parse_args()
    logging_level = max(0, logging.WARN - (args.verbose * 10))
    logging.basicConfig(level=logging_level)

    # create client object and set callback methods
    mqttc = mqtt.Client(client_id=f"{platform.node()}-mqtt-influx-bridge", clean_session=False)
    mqttc.on_connect = on_connect

    # configure tls connection (skip tls certificate validation for now)
    if args.mqtt_tls:
        mqttc.tls_set(cert_reqs=ssl.CERT_NONE)

    if args.mqtt_username:
        mqttc.username_pw_set(args.mqtt_username, args.mqtt_password)

    ret = mqttc.connect(args.mqtt_host, args.mqtt_port, args.mqtt_keepalive)
    if ret == mqtt.MQTT_ERR_SUCCESS:
        print("batchsize,cbor,lzma,zlib,lz4,zstd,brotli")
        mqttc.loop_forever()
    else:
        logging.critical(f"MQTT connetion failed: {ret}")
        exit(ret)
