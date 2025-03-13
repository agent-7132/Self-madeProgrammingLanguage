import tensorflow as tf
from federated import FederatedClient

class ConflictDetectorTrainer:
    def __init__(self):
        self.model = tf.keras.Sequential([
            tf.keras.layers.TextVectorization(max_tokens=20000),
            tf.keras.layers.Embedding(20000, 128),
            tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(64)),
            tf.keras.layers.Dense(3, activation='softmax')
        ])
        
    def federated_update(self, client_data):
        client = FederatedClient(config='config.yaml')
        global_weights = client.get_global_model()
        self.model.set_weights(global_weights)
        
        self.model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])
        
        self.model.fit(client_data, epochs=5)
        return self.model.get_weights()

if __name__ == "__main__":
    trainer = ConflictDetectorTrainer()
    local_data = load_training_data()
    updated_weights = trainer.federated_update(local_data)
