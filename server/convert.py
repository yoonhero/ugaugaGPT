import bentoml
import torch
from dataclasses import dataclass
from gpt import model as Model
import torch.nn.functional as F

@dataclass 
class GPTConfig: 
    block_size:int 
    n_embd: int
    n_heads: int
    n_layer: int
    vocab_size: int
    dropout: float = 0.1
    
CONFIG = GPTConfig(block_size=32, n_embd=128, n_heads=8, n_layer=5, vocab_size=35000)

model_state_dict = torch.load("./checkpoint/epoch-99.pt", map_location=torch.device('cpu'))
unwanted_prefix = '_orig_mod.'
for k,v in list(model_state_dict.items()):
    if k.startswith(unwanted_prefix):
        model_state_dict[k[len(unwanted_prefix):]] = model_state_dict.pop(k)

model = Model.GPT(CONFIG)

model.load_state_dict(model_state_dict)
model.eval()

# print(type(model))

# bentoml.pytorch.save(
#     model,
#     "small-gpt",
#     signatures={"__call__": {"batchable": True, "batch_dim": 0}},
#     external_modules=[model]
# )

x_ft = torch.randint(0, 35000, (1, 32), dtype=torch.long)
sm = torch.jit.script(model, (x_ft))

@torch.no_grad()
def generate(idx, max_new_tokens, temperature=1.0, top_k=None):
    for _ in range(max_new_tokens):
        idx_cond = idx[:, -32:]

        logits = sm(idx_cond, None)
        logits = logits[:, -1, :] / temperature # becomes (B, C)

        if top_k is not None:
            v, _ = torch.topk(logits, min(top_k, logits.size(-1)))
            logits[logits < v[:, [-1]]] = -float('Inf')
        probs = F.softmax(logits, dim=-1)
        idx_next = torch.multinomial(probs, num_samples=1) # (B, 1)
        
        if idx_next == 0:
            return idx
        
        # append sample index to the running sequnce
        idx = torch.cat((idx, idx_next), dim=1) # (B, T+1)
    return idx

print(generate(x_ft, 100))

# path = "./checkpoint/model.pt"
# torch.jit.save(sm, path)

# bentoml.torchscript.save_model(
#     "model",
#     sm,
#     signatures={"__call__": {"batchable": True}},
# )
