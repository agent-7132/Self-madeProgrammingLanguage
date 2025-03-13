from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from datasets import load_dataset

class CodeFinetuner:
    def __init__(self, base_model="gpt-neo-2.7B"):
        self.tokenizer = AutoTokenizer.from_pretrained(base_model)
        self.model = AutoModelForCausalLM.from_pretrained(base_model)
        self.tokenizer.add_special_tokens({
            'pad_token': '[PAD]',
            'additional_special_tokens': ['<|zh-en|>', '<|sandbox|>']
        })
        self.model.resize_token_embeddings(len(self.tokenizer))
        
    def preprocess(self, examples):
        prompts = [
            f"<|zh-en|>{example['chinese']}\n// Equivalent English:\n{example['english']}\n<|sandbox|>"
            for example in examples
        ]
        return self.tokenizer(
            prompts,
            padding='max_length',
            truncation=True,
            max_length=512,
            return_tensors="pt"
        )
    
    def finetune(self, dataset_path, epochs=3):
        dataset = load_dataset('json', data_files=dataset_path, split='train')
        dataset = dataset.map(self.preprocess, batched=True)
        
        trainer = torch.optim.AdamW(self.model.parameters(), lr=5e-5)
        for epoch in range(epochs):
            for batch in dataset.iter(batch_size=8):
                outputs = self.model(
                    input_ids=batch['input_ids'],
                    attention_mask=batch['attention_mask'],
                    labels=batch['input_ids']
                )
                loss = outputs.loss
                loss.backward()
                trainer.step()
                trainer.zero_grad()
                
        self.model.save_pretrained("finetuned_code_model")
        self.tokenizer.save_pretrained("finetuned_code_tokenizer")
