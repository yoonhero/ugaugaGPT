import torch
from transformers import ElectraTokenizer
from fastapi import FastAPI
from dataclasses import dataclass
from pydantic import BaseModel
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
# import onnxruntime
import numpy as np

from gpt import GPT
from database import db

@dataclass 
class GPTConfig: 
    block_size:int 
    n_embd: int
    n_heads: int
    n_layer: int
    vocab_size: int
    dropout: float = 0.1
    
CONFIG = GPTConfig(block_size=32, n_embd=128, n_heads=8, n_layer=5, vocab_size=35000)

tokenizer = ElectraTokenizer.from_pretrained("monologg/koelectra-base-v3-discriminator")

model_state_dict = torch.load("./checkpoint/epoch-99.pt", map_location=torch.device('cpu'))
unwanted_prefix = '_orig_mod.'
for k,v in list(model_state_dict.items()):
    if k.startswith(unwanted_prefix):
        model_state_dict[k[len(unwanted_prefix):]] = model_state_dict.pop(k)

model = GPT(CONFIG)

model.load_state_dict(model_state_dict)
model.eval()

model = torch.jit.script(model)

@torch.no_grad()
def sampling(prompt):
    tokens = tokenizer.tokenize(prompt)
    ids = tokenizer.convert_tokens_to_ids(tokens)

    context = torch.tensor(ids, dtype=torch.long, device="cpu")
    context = context.unsqueeze(0)

    @torch.no_grad()
    def generate(idx, max_new_tokens, temperature=1.0, top_k=None):
        for _ in range(max_new_tokens):
            idx_cond = idx[:, -32:]

            logits = model(idx_cond, None)
            logits = logits[:, -1, :] / temperature # becomes (B, C)

            if top_k is not None:
                v, _ = torch.topk(logits, min(top_k, logits.size(-1)))
                logits[logits < v[:, [-1]]] = -float('Inf')
            probs = torch.nn.functional.softmax(logits, dim=-1)
            idx_next = torch.multinomial(probs, num_samples=1) # (B, 1)
            
            if idx_next == 2:
                return idx
        
            idx = torch.cat((idx, idx_next), dim=1) # (B, T+1)
        return idx

    result = generate(context, max_new_tokens=30)
    decoded_result = tokenizer.decode(result.tolist()[0])   
    decoded_result = decoded_result[len(prompt):].replace("[SEP]", "").replace("[CLS]", "")

    return decoded_result

# session = onnxruntime.InferenceSession("./checkpoint/model.onnx")

# def sampling(prompt):
#     tokens = tokenizer.tokenize(prompt)
#     ids = tokenizer.convert_tokens_to_ids(tokens)
#     idx = np.array(ids, dtype=np.int64)
#     idx = np.reshape(idx, (1, -1))
#     max_new_tokens = 10

#     for _ in range(max_new_tokens):
#         idx_cond = idx[:, -32:]
#         idx_cond = np.pad(idx_cond[0], (32-idx_cond.shape[1], 0), constant_values=0)
#         idx_cond = np.reshape(idx_cond, (1, -1))

#         output = session.run(None, {"modelInput": idx_cond})
#         # print(output)
#         logits = output[0][-1, :] # becomes ( C)

#         y = np.exp(logits - np.max(logits))
#         probs = y / np.sum(np.exp(logits))
#         probs = probs[-1]
#         # print(probs)
#         idx_next = np.random.multinomial(100, probs, size=1) # (B, 1)
#         idx_next = np.argmax(idx_next, axis=-1)
#         idx_next = np.reshape(idx_next, (1, -1))
        
#         if idx_next == 0:
#             return idx
        
#         idx = np.concatenate((idx, idx_next), axis=1)

#     decoded_result = tokenizer.decode(idx.tolist()[0])   
#     decoded_result = decoded_result[len(prompt):].replace("[SEP] ", "").replace("[CLS] ", "")
#     return decoded_result


# 0: 우 1: 가
def text2uga(text):
    toBinary = lambda text: ' '.join(format(ord(x), 'b') for x in text)
    binaried_text = toBinary(text)
    result = binaried_text.replace("0", "우").replace("1", "가")
    return result

# 우: 0, 가: 1
def uga2text(uga):
    binaried_text = uga.replace("우", "0").replace("가", "1")
    input_string = [int(binary, 2) for binary in binaried_text.split(" ")]

    toChar = lambda text: "".join(chr(x) for x in text)
    result = toChar(input_string)

    return result


class Model(BaseModel):
    prompt: str


class Result(BaseModel):
    result: str
    timestamp: datetime

class HomeResult(BaseModel):
    visit: int

class TotalResult(BaseModel):
    count: int


app = FastAPI()

origins = [
    "http://localhost:3000",
    "https://ugagpt.vercel.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/visit")
def home():
    db["archive"].update_one({"uid":"645752fbf0b1ae1b123ee633"}, {"$inc": {"visit": 1}})

    visit = db["archive"].find_one({"uid":"645752fbf0b1ae1b123ee633"})["visit"]

    result = HomeResult(visit=visit)

    return result


@app.get("/total")
def total_turn():
    count = db["archive"].find_one({"uid":"645752fbf0b1ae1b123ee633"})["count"]

    result = TotalResult(count=count)

    return result


@app.post("/generate")
def generate(data : Model):
    output = sampling(data.prompt)
    splitted_output = output.split(" ")
    if splitted_output[0] == " ":
        splitted_output = splitted_output[1:]
    ugaed = text2uga(" ".join(splitted_output[:2]))
    re = ugaed + " " + " ".join(splitted_output[2:])
    # print(re)
    result = Result(result=re, timestamp=datetime.now())
        
    db["archive"].update_one({"uid":"645752fbf0b1ae1b123ee633"}, {"$inc": {"count": 1}})

    return result

