from dgl.nn.pytorch import GraphConv
import torch
import torch.nn as nn
import torch.nn.functional as F

from train import device

from sklearn.metrics import pairwise_distances
from sklearn.metrics.pairwise import pairwise_kernels

import pandas as pd


from dgl.nn import SAGEConv

# ----------- 2. create model -------------- #
# build a two-layer GraphSAGE model
# class GraphSAGE(nn.Module):
#     def __init__(self, in_feats, h_feats):
#         super(GraphSAGE, self).__init__()
#         self.conv1 = SAGEConv(in_feats, h_feats, 'mean')
#         self.conv2 = SAGEConv(h_feats, h_feats, 'mean')

#     def forward(self, g, in_feat):
#         h = self.conv1(g, in_feat)
#         h = F.relu(h)
#         h = self.conv2(g, h)
#         return h


class VGAEModel(nn.Module):
    def __init__(self, in_dim, hidden1_dim, hidden2_dim):
        super(VGAEModel, self).__init__()
        self.in_dim = in_dim
        self.hidden1_dim = hidden1_dim
        self.hidden2_dim = hidden2_dim

        layers = [SAGEConv(self.in_dim, self.hidden1_dim, activation=F.relu, aggregator_type='mean'),
                  SAGEConv(self.hidden1_dim, self.hidden2_dim, activation=lambda x: x, aggregator_type='mean'),
                  SAGEConv(self.hidden1_dim, self.hidden2_dim, activation=lambda x: x, aggregator_type='mean')]

        # layers = [GraphConv(self.in_dim, self.hidden1_dim, activation=F.relu, allow_zero_in_degree=True),
        #           GraphConv(self.hidden1_dim, self.hidden2_dim, activation=lambda x: x, allow_zero_in_degree=True),
        #           GraphConv(self.hidden1_dim, self.hidden2_dim, activation=lambda x: x, allow_zero_in_degree=True)]
        self.layers = nn.ModuleList(layers)

    def encoder(self, g, features):
        h = self.layers[0](g, features)
        self.mean = self.layers[1](g, h)
        self.log_std = self.layers[2](g, h)
        gaussian_noise = torch.randn(features.size(0), self.hidden2_dim).to(device)
        sampled_z = self.mean + gaussian_noise * torch.exp(self.log_std).to(device)
        return sampled_z

    # def decoder(self, z):
    #     adj_rec = torch.sigmoid(torch.matmul(z, z.t()))
    #     return adj_rec 

    # def forward(self, g, features):
    #     z = self.encoder(g, features)
    #     adj_rec = self.decoder(z)
    #     return adj_rec
