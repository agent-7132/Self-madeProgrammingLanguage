import torch
from torch import nn
from quantum_integration import QuantumLayer

class HybridTypeModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.quantum_layer = QuantumLayer(4, 8)  # 4 qubits输入, 8维输出
        self.classifier = nn.Sequential(
            nn.Linear(8 + 768, 256),  # 量子特征 + BERT特征
            nn.ReLU(),
            nn.Linear(256, 3)         # 输出类型：dynamic/static/generic
        )
    
    def forward(self, quantum_input, bert_input):
        q_feat = self.quantum_layer(quantum_input)
        combined = torch.cat([q_feat, bert_input], dim=1)
        return self.classifier(combined)

# 导出为ONNX
model = HybridTypeModel()
dummy_quantum = torch.randn(1, 4)
dummy_bert = torch.randn(1, 768)

torch.onnx.export(
    model,
    (dummy_quantum, dummy_bert),
    "model.onnx",
    input_names=["quantum_input", "ast_input"],
    output_names=["output"],
    dynamic_axes={
        "quantum_input": {0: "batch_size"},
        "ast_input": {0: "batch_size"},
        "output": {0: "batch_size"}
    }
)
