import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import pandas as pd
from dataclasses import dataclass 
from transformers import ElectraTokenizer
import numpy as np
import tqdm
from pathlib import Path
import torch
import os
from torch.utils.tensorboard import SummaryWriter
writer = SummaryWriter('logs/')

from model import GPT


# Hyper Parameters
batch_size = 64
max_epoch = 1000
eval_interval = 10
save_interval = 50
learning_rate = 5e-5
device = 'cuda' if torch.cuda.is_available() else 'cpu'

# Basic Configs
TRAINING_OUTPUT_DIR="./tmp/checkpoints/" 

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


class ChatDataset(Dataset):
    def __init__(self, source_path:str, max_length:int):
        self.df = pd.read_csv(source_path, sep=",")
        self.max_length = max_length

    def __getitem__(self, index):
        row = self.df.iloc[index, :]
        Q = row["Q"]
        A = row["A"]

        query = f"[CLS] {Q} [SEP] {A} [CLS]"
        
        tokens = tokenizer.tokenize(query)
        ids = tokenizer.convert_tokens_to_ids(tokens)

        # print(tokenizer.convert_tokens_to_ids(tokenizer.tokenize("[PAD]")))

        if len(ids) > self.max_length:
            ids = ids[:self.max_length]

        x = torch.tensor(ids[:-1], device=device)
        y = torch.tensor(ids[1:], device=device)

        # Add Padding to the Sequence
        x = torch.nn.functional.pad(x ,pad=(0, self.max_length-x.shape[0]),value=0)
        y = torch.nn.functional.pad(y, pad=(0, self.max_length-y.shape[0]), value=0)
        
        return x, y

    def __len__(self): return len(self.df)


dataset = ChatDataset("./tmp/ChatbotData.csv", CONFIG.block_size)
train_dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
# x, y = dataset[0]/

os.makedirs(TRAINING_OUTPUT_DIR, exist_ok=True)
model = GPT(CONFIG).to(device)
optimizer = optim.AdamW(model.parameters(), lr=learning_rate, betas=(0.9, 0.95), weight_decay=1e-1)


scaler = torch.cuda.amp.GradScaler()
losses = np.zeros(max_epoch)

lr = learning_rate
for iter in range(0, max_epoch):
    if (iter+1) % 100 == 0:
        lr /= 2
        for param_group in optimizer.param_groups:
            param_group['lr'] = lr


    _losses = []

    pbar = tqdm.tqdm(train_dataloader, desc=f"Epoch {iter+1}/"+f"{max_epoch}")
    for step, (x, y) in enumerate(pbar):
        _, loss = model(x, y)
        _losses.append(loss.item())

        scaler.scale(loss).backward()

        max_norm = 5
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm)

        writer.add_scalar("Loss/train", loss, iter)

        scaler.step(optimizer)
        scaler.update()
        optimizer.zero_grad(set_to_none=True)

        with torch.no_grad():
            start_token = "[CLS] 나 너무 슬퍼 [SEP]"
            tokens = tokenizer.tokenize(start_token)
            ids = tokenizer.convert_tokens_to_ids(tokens)

            context = torch.tensor(ids, dtype=torch.long, device=device)
            context = context.unsqueeze(0)

            result = model.generate(context, max_new_tokens=20)
            decoded_result = tokenizer.decode(result.tolist()[0])
            
            writer.add_text('GPT', decoded_result, iter)

    print(f"Epoch: {iter+1} | Loss: {_losses[-1]}")

    # Save the every save interval
    if (iter+1) % save_interval == 0:
        save_dir = Path(TRAINING_OUTPUT_DIR) / f"epoch-{iter}.pt"
        torch.save(model.state_dict(), str(save_dir))

writer.close()