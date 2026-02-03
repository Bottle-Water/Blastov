import torch
import torch.nn as nn
from config import Config

class HarmonicLSTM(nn.Module):
    def __init__(self):
        super(HarmonicLSTM, self).__init__()
        self.lstm = nn.LSTM(
            input_size=Config.INPUT_SIZE, 
            hidden_size=Config.HIDDEN_SIZE, 
            num_layers=1, 
            batch_first=True
        )
        self.fc = nn.Linear(Config.HIDDEN_SIZE, Config.OUTPUT_SIZE)
        
    def forward(self, x, hidden=None):
        out, hidden = self.lstm(x, hidden)
        out = self.fc(out[:, -1, :]) 
        return out, hidden