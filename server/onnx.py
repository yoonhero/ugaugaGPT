import torch.onnx 
from dataclasses import dataclass
from gpt import GPT
from database import db
import onnxruntime
import numpy as np

@dataclass 
class GPTConfig: 
    block_size:int 
    n_embd: int
    n_heads: int
    n_layer: int
    vocab_size: int
    dropout: float = 0.1

CONFIG = GPTConfig(block_size=32, n_embd=128, n_heads=8, n_layer=5, vocab_size=35000)

model_state_dict = torch.load("./checkpoint/epoch-99.pt")
unwanted_prefix = '_orig_mod.'

for k,v in list(model_state_dict.items()):
    if k.startswith(unwanted_prefix):
        model_state_dict[k[len(unwanted_prefix):]] = model_state_dict.pop(k)

model = GPT(CONFIG)

model.load_state_dict(model_state_dict)
model.eval()


dummy_input = torch.zeros(1, 32, requires_grad=True).type(torch.LongTensor)  

# Export the model   
torch.onnx.export(model,         # model being run 
        dummy_input,       # model input (or a tuple for multiple inputs) 
        "./checkpoint/model.onnx",       # where to save the model  
        opset_version=13,    # the ONNX version to export the model to 
        do_constant_folding=True,  # whether to execute constant folding for optimization 
        input_names = ['modelInput'],   # the model's input names 
        output_names = ['modelOutput'], # the model's output names 
        dynamic_axes={"modelInput": {0: "batch", 1: "sequence"}},
        ) 
print(" ") 
print('Model has been converted to ONNX') 



model_path = 'model.onnx'
session = onnxruntime.InferenceSession("./checkpoint/model.onnx")

# Create a sample input
input_data = np.array([[1, 2, 5, 3]], dtype=np.int64)

def generate(idx, max_new_tokens, temperature=1.0, top_k=None):
    for _ in range(max_new_tokens):
        idx_cond = idx[:, -32:]
        idx_cond = np.pad(idx_cond[0], (32-idx_cond.shape[1], 0), constant_values=0)
        idx_cond = np.reshape(idx_cond, (1, -1))
        # print(idx_cond)

        output = session.run(None, {"modelInput": idx_cond})
        print(output)
        logits = output[0][-1, :] # becomes ( C)

        y = np.exp(logits - np.max(logits))
        probs = y / np.sum(np.exp(logits))
        probs = probs[-1]
        print(probs)
        idx_next = np.random.multinomial(100, probs, size=1) # (B, 1)
        idx_next = np.argmax(idx_next, axis=-1)
        idx_next = np.reshape(idx_next, (1, -1))
        
        if idx_next == 0:
            return idx
        
        idx = np.concatenate((idx, idx_next), axis=1)
    return idx

print(generate(input_data, 10))