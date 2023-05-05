import torch 
import torch.nn as nn
import torch.nn.functional as F



class SentimentAnalysis(nn.Module):
    def __init__(self, vocab_size, embd_size, n_filters, filter_sizes, pool_size, dropout, hidden_size, num_classes):
        super().__init__()
        self.embd = nn.Embedding(vocab_size, embd_size)
        self.conv = nn.ModuleList([nn.Conv1d(in_channels=embd_size, out_channels=n_filters, kernel_size=fs) for fs in filter_sizes])

        self.max_pool = nn.ModuleList([nn.MaxPool1d(fs, stride=1) for fs in filter_sizes])

        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(dropout)

        self.fc1 = nn.Linear(690, hidden_size, bias=True)
        self.fc2 = nn.Linear(hidden_size, num_classes, bias=True)

    def forward(self, text):
        embedded = self.embd(text)
        embedded = embedded.transpose(1, 2)    
        convolution = [self.relu(pool(conv(embedded))) for conv, pool in zip(self.conv, self.max_pool)]
        x_concat = torch.cat(convolution, 2)
        x_concat = torch.flatten(x_concat, 1)

        x = self.fc1(x_concat)
        x = self.relu(x)
        x = self.dropout(x)
        x = self.fc2(x)
        x = torch.sigmoid(x)

        return x

    def total_parameters(self):
        return sum([p.nelement() for p in self.parameters()])


if __name__ == "__main__":
    model = SentimentAnalysis(500, 50, n_filters=5, filter_sizes=[2, 3, 4], pool_size=1, dropout=0.2, hidden_size=100, num_classes=10)

    print(model.total_parameters())

    test = torch.randint(0, 50, (1, 50))

    print(model(test))
        

    
