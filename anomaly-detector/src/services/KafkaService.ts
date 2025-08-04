import { Consumer, EachMessagePayload } from 'kafkajs';
import { kafkaConsumer } from '../config/kafka.config.js';

type MessageHandler = (payload: EachMessagePayload) => Promise<void>;

export class KafkaService {
  private consumer: Consumer;

  constructor(private topic: string, private handler: MessageHandler) {
    this.consumer = kafkaConsumer;
  }

  async start(): Promise<void> {
    await this.consumer.connect();
    await this.consumer.subscribe({ topic: this.topic, fromBeginning: true });

    console.log(`[KafkaService] Subscribed to topic: ${this.topic}`);

    await this.consumer.run({
      eachMessage: async (payload) => {
        try {
          await this.handler(payload);
        } catch (error) {
          console.error('[KafkaService] Error handling message:', error);
        }
      },
    });
  }

  async stop(): Promise<void> {
    await this.consumer.disconnect();
    console.log('[KafkaService] Consumer disconnected.');
  }
}
