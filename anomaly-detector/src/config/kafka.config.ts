import { Kafka, Consumer, Producer } from 'kafkajs';
import dotenv from 'dotenv';
dotenv.config();

const kafka = new Kafka({
  clientId: process.env.KAFKA_CLIENT_ID ?? "default-client-id",
  brokers: (process.env.KAFKA_BROKERS || '').split(','),
});

export const kafkaConsumer: Consumer = kafka.consumer({
  groupId: process.env.KAFKA_GROUP_ID!,
});

export const kafkaProducer: Producer = kafka.producer();
