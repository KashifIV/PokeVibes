import torch 
import torch.nn as nn
from torch.nn import functional as F
class ConditionalCNN(nn.Module):
  def __init__(self, latent_size = 64):
    super(ConditionalCNN, self).__init__()

    # Encoding layers
    self.enc_conv1 = nn.Conv2d(in_channels = 1, out_channels = 64, kernel_size = (4, 4), stride = (4, 4))
    self.enc_conv2 = nn.Conv2d(in_channels = 64, out_channels = 128, kernel_size = (4, 4), stride = (4, 4))
    self.enc_conv3 = nn.Conv2d(in_channels = 128, out_channels = 256, kernel_size = (2, 8), stride = (2, 8))
    self.enc_lin1 = nn.Linear(512, 256)
    self.enc_lin2 = nn.Linear(256, latent_size)

    # Decoding layers
    self.dec_lin = nn.Linear(latent_size, 256)
    self.dec_conv1 = nn.ConvTranspose2d(in_channels = 256, out_channels = 128, kernel_size = (2, 8), stride = (2, 8))
    self.dec_conv2 = nn.ConvTranspose2d(in_channels = 128, out_channels = 64, kernel_size = (4, 4), stride = (4, 4))
    self.dec_conv3 = nn.ConvTranspose2d(in_channels = 64, out_channels = 1, kernel_size = (4, 4), stride = (4, 4))

    self.batch_norm_2d64 = nn.BatchNorm2d(64)
    self.batch_norm_2d128 = nn.BatchNorm2d(128)
    self.batch_norm_2d256 = nn.BatchNorm2d(256)

    self.dropout = nn.Dropout(0.4)

  def forward(self, prev_harmony, melody):
    # Input: batch_size x seq_length x n_pitches 
    prev_harmony = prev_harmony.unsqueeze(1)
    # batch_size x num_channels (1) x seq_length x n_pitches 
    prev_harmony = F.relu(self.batch_norm_2d64(self.enc_conv1(prev_harmony)))
    prev_harmony = self.dropout(prev_harmony)
    prev_harmony = F.relu(self.batch_norm_2d128(self.enc_conv2(prev_harmony)))
    prev_harmony = self.dropout(prev_harmony)
    prev_harmony = F.relu(self.batch_norm_2d256(self.enc_conv3(prev_harmony)))
    prev_harmony = prev_harmony.squeeze(3).squeeze(2)

    melody = melody.unsqueeze(1)
    # batch_size x num_channels (1) x seq_length x n_pitches 
    melody = F.relu(self.batch_norm_2d64(self.enc_conv1(melody)))
    melody = self.dropout(melody)
    melody = F.relu(self.batch_norm_2d128(self.enc_conv2(melody)))
    melody = self.dropout(melody)
    melody = F.relu(self.batch_norm_2d256(self.enc_conv3(melody)))
    melody = melody.squeeze(3).squeeze(2)
    
    # Concat melody and previous harmony together
    x = torch.cat((prev_harmony, melody), dim = 1)
    x = F.relu(self.enc_lin1(x))
    latent = self.enc_lin2(x)
    x = F.relu(self.dec_lin(latent))
    x = x.unsqueeze(2).unsqueeze(3)
    x = F.relu(self.batch_norm_2d128(self.dec_conv1(x)))
    x = F.relu(self.batch_norm_2d64(self.dec_conv2(x)))
    x = F.relu(self.dec_conv3(x))
    x = x.squeeze()
    return x, latent