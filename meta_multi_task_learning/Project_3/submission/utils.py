import torch
import torch.nn as nn
import numpy as np
import random
import matplotlib
import matplotlib.pyplot as plt
import os
from data_sampling import *



def cycle(dataloader):
    while True:
        for x in dataloader:
            yield x
            
            
def load_datasets(args, N, K, Q, batch_size):
    data_sampling = DataSampling(args, N, K, Q, batch_size)
    
    trainloader = cycle(data_sampling.m_dataloader['train'])
    validloader = data_sampling.m_dataloader['val']
    
    return trainloader, validloader


def split_support_query(x, ways, shots, query):
    """
    x: n_sample * shape
    :param x:
    :param n_support:
    :return:
    """
    x_reshaped = x.contiguous().view(ways, shots + query, *x.shape[1:])
    x_support = x_reshaped[:, :shots].contiguous().view(ways * shots, *x.shape[1:])
    x_query = x_reshaped[:, shots:].contiguous().view(ways * query, *x.shape[1:])
    return x_support.cuda(), x_query.cuda()

class SineWaveTask:
    def __init__(self):
        amplitude = torch.rand(1) * 4.9 + 0.1
        phase = torch.rand(1) * torch.tensor(np.pi)
        self.f = lambda x: amplitude * torch.sin(x + phase)

    def sample_data(self, K=10):
        x = torch.rand(K) * 10.0 - 5.0
        y = self.f(x)
        return (x, y)

def set_seed(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        # torch.backends.cudnn.deterministic = True
        # torch.backends.cudnn.benchmark = False

def draw_plot(model, adapted_model, sine_f, support_x, support_y):
    """
    model: model that has not been adapted to the support set.
    adapted_model: model that has been adapted to the support set. (1-step SGD)
    sine_f: sine function of the task.
    support_x, support_y: support set of the task.
    """
    K = len(support_x)
    assert(K == len(support_y) and (K == 5 or K == 10))

    # Generate dense x values
    dense_x = torch.linspace(-5, 5, 200).view(-1, 1)

    # Evaluate model, adapted_model and sine function for each x
    with torch.no_grad():
        model_preds = model(dense_x).squeeze().numpy()
        adapted_preds = adapted_model(dense_x).squeeze().numpy()
    true_values = sine_f(dense_x).squeeze().numpy()

    # Plot
    plt.figure(figsize=(8, 6))
    plt.plot(dense_x, model_preds, label='Pre-update Model', color='green', linestyle='--', alpha=0.2)
    plt.plot(dense_x, adapted_preds, label='Adapted Model', color='green', linestyle='--')
    plt.plot(dense_x, true_values, label='True Sine Function', color='red')
    plt.scatter(support_x, support_y, color='blue', marker='^', label='Samples (K=%d)' % (K))

    plt.legend()
    plt.xlabel('x')
    plt.ylabel('y')
    plt.title('MAML, K=%d' % (K))
    plt.xlim([-6.0, 6.0])
    plt.ylim([-5.0, 5.0])
    plt.show()
    plt.savefig('MAML_K_%d.png' % (K))


