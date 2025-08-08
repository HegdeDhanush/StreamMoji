import pytest
from unittest.mock import Mock, patch
import json

class TestEmojiConsumer:
    def test_process_message(self):
        # Test message data
        test_message = Mock()
        test_message.value = {
            'user_id': 'test_user',
            'emoji_type': '😊',
            'timestamp': '2024-11-16T12:00:00'
        }
        
        # Create consumer instance with mocked Kafka
        with patch('kafka.KafkaConsumer'):
            consumer = EmojiConsumer('localhost:9092', 'test-topic')
            consumer.process_message(test_message)
            
    def test_connection_error(self):
        # Test handling of connection errors
        with patch('kafka.KafkaConsumer', side_effect=Exception('Connection failed')):
            with pytest.raises(Exception):
                consumer = EmojiConsumer('invalid:9092', 'test-topic')
                consumer.connect()

if __name__ == '__main__':
    pytest.main([__file__])
