import torch
import torch.optim as optim
import tqdm

def train(model,train_data):
    model.train()

    optimizer = optim.AdamW(model.parameters(),lr = 0.0001)
    loss_fn = torch.nn.CrossEntropyLoss()
   
    epochs = 10

    for epoch in range(epochs):
        t_loss = 0
        for batch_idx, (x, y) in tqdm(train_data):        
            out = model(x)
            loss = loss_fn(out,y)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            t_loss += loss.detach().item()

        print(f"Epoch : {epoch + 1} / {epochs} \t Train  Loss : {t_loss/len(train_data) : .3f}")

    torch.save(model.state_dict(), "model.pt")