from typing import Union

from fastapi import FastAPI

app = FastAPI()

# import tiktoken
import torch
import argparse
from transformers import AutoTokenizer

import utils as utils
import nanoChatGPT.config as CONFIG
from nanoChatGPT.tokenizer import Tokenizer

# KoGPT Tokenizer
enc = AutoTokenizer.from_pretrained(
  'kakaobrain/kogpt', revision='KoGPT6B-ryan1.5b-float16',
  bos_token='[BOS]', eos_token='[EOS]', unk_token='[UNK]', pad_token='[PAD]', mask_token='[MASK]'
)
# enc = Tokenizer("./tokenizer/tokenizer.model")
encode = lambda x: enc.encode(x, bos=True)
decode = lambda x: enc.decode(x)

def main(args):
    model_path = args.path
    max_tokens = args.max_tokens
    start_tokens = args.start
    
    config = utils.getModelConfig(args.model_size)
    model, _, _ = utils.load_model(model_path, config, best=False)
    model.eval()

    if start_tokens == "":
        start_tokens = input(">> ")
    result = encode(start_tokens)
    
    @torch.no_grad()
    def generate(context):
        # generate from the model
        context = torch.tensor(context, dtype=torch.long, device=CONFIG.device)
        # unsqueeze for batched calculation
        context = context.unsqueeze(0)

        result = model.generate(context, max_new_tokens=max_tokens)
        decoded_result = decode(result[0])   
        return decoded_result

    result = generate(result)

    print(f"\n>> {result}\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Inference My Custom GPT 🚀!!!')

    parser.add_argument("--max_tokens", type=int, default=1000)
    parser.add_argument("--path", type=str, default=CONFIG.TRAINING_OUTPUT_DIR)
    parser.add_argument("--start", type=str, default="")
    parser.add_argument("--model_size", type=str, default="LLAMA")

    args = parser.parse_args()

    main(args)
 


# Generate the sample.
def sample(tokenizer: Tokenizer, model: torch.nn.Module) -> None:
    decode = lambda x: tokenizer.decode(x)
    start_tokens = "[BOS] 세상을 바꾸는 것은 누구일까?"
    result = tokenizer.encode(start_tokens)
    context = torch.tensor(result, device=CONFIG.device, dtype=torch.long)
    context = context.unsqueeze(0)
    result = model.generate(context, max_new_tokens=100)[0].tolist()
    result = decode(result)

    with open('result.txt', "w") as f:
        logger.info(result)
        f.writelines(result)
        f.close()

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}