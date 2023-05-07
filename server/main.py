import torch
from transformers import ElectraTokenizer
from fastapi import FastAPI
from dataclasses import dataclass
from typing import Union
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware

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

model_state_dict = torch.load("./checkpoints/epoch-99.pt")
unwanted_prefix = '_orig_mod.'
for k,v in list(model_state_dict.items()):
    if k.startswith(unwanted_prefix):
        model_state_dict[k[len(unwanted_prefix):]] = model_state_dict.pop(k)

model = GPT(CONFIG)

model.load_state_dict(model_state_dict)
model.eval()

@torch.no_grad()
def sampling(prompt):
    tokens = tokenizer.tokenize(prompt)
    ids = tokenizer.convert_tokens_to_ids(tokens)

    context = torch.tensor(ids, dtype=torch.long, device="cpu")
    context = context.unsqueeze(0)

    result = model.generate(context, max_new_tokens=10)
    decoded_result = tokenizer.decode(result.tolist()[0])   
    decoded_result = decoded_result[len(prompt):].replace("[SEP] ", "").replace("[CLS] ", "")
    return decoded_result


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
    "http://localhost:3000"
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
    ugaed = text2uga(output)
    result = Result(result=ugaed, timestamp=datetime.now())
        
    db["archive"].update_one({"uid":"645752fbf0b1ae1b123ee633"}, {"$inc": {"count": 1}})

    return result

