import torch
from transformers import ElectraTokenizer
from fastapi import FastAPI
from dataclasses import dataclass
from typing import Union
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from datetime import datetime

from gpt.model import GPT

app = FastAPI()

@dataclass 
class GPTConfig: 
    block_size:int 
    n_embd: int
    n_heads: int
    n_layer: int
    vocab_size: int
    dropout: float = 0.1
    
CONFIG = GPTConfig(block_size=32, n_embd=128, n_heads=8, n_layer=1, vocab_size=35000)


tokenizer = ElectraTokenizer.from_pretrained("monologg/koelectra-base-v3-discriminator")


model_state_dict = torch.load("./gpt/tmp/checkpoints/epoch-49.pt")
model = GPT(CONFIG)
model.load_state_dict(model_state_dict)
model.eval()

@torch.no_grad
def generate(prompt:str):
    tokens = tokenizer.tokenize(prompt)
    ids = tokenizer.convert_tokens_to_ids(tokens)

    context = torch.tensor(ids, dtype=torch.long, device=CONFIG.device)
    context = context.unsqueeze(0)

    result = model.generate(context, max_new_tokens=20)
    decoded_result = tokenizer.decode(result.tolist()[0])   
    return decoded_result

class Model(BaseModel):
    prompt: str


class Result(BaseModel):
    result: str
    timestamp: datetime


@app.post("/generate")
async def data(data : Model):
    output = await generate(data.prompt)
    result = Result(result=output, timestamp=datetime.now())
    return JSONResponse(content=result)


# @app.get("/analysis")
# async def 