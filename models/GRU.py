from lightning_modules import LitModel
import torch.nn.functional as F
import torch.optim as optim
import torch.nn as nn


class GRU(LitModel):
    def __init__(self,
            vocab_size: int,
            output_size: int = 1,
            hidden_size: int = 128,
            embedding_size: int = 400,
            n_layers: int = 2,
            dropout: float = 0.2,
            batch_first: bool = True,
            bidirectional: bool = False,
        ):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embedding_size)
        self.gru = nn.GRU(
            input_size = embedding_size,
            hidden_size = hidden_size,
            num_layers = n_layers,
            dropout = dropout,
            batch_first = batch_first,
            bidirectional = bidirectional
        )
        self.dropout = nn.Dropout(0.3)
        self.fc = nn.Linear(
            in_features = hidden_size*2 if bidirectional else hidden_size,
            out_features = output_size
        )
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        out = self.embedding(x)
        out, _ = self.gru(out)
        out = out[:, -1, :]
        out = self.dropout(out)
        out = self.fc(out)
        out = self.sigmoid(out)
        return out

    def save_hparams(self, config):
        self.hparams.update(config)
        self.save_hyperparameters()

    def criterion(self, y_hat, y):
        return F.binary_cross_entropy(y_hat, y)

    def configure_optimizers(self):
        return optim.Adam(self.parameters(), lr=self.hparams.trainer['learning_rate'])
