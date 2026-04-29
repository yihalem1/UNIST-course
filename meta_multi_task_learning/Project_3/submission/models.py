import torch
import torch.nn as nn
import torch.nn.functional as F


class CNN(nn.Module):
    def __init__(self, task):
        super(CNN, self).__init__()
        assert task in ['omniglot', 'miniimagenet']
        in_ch = 1 if task == 'omniglot' else 3
        self.encoder = nn.Sequential(
            self._conv_blk(in_ch, 64),
            self._conv_blk(64, 64),
            self._conv_blk(64, 64),
            self._conv_blk(64, 64),
        )

    def _conv_blk(self, in_channels, out_channels):
        bn = nn.BatchNorm2d(out_channels)
        nn.init.uniform_(bn.weight)
        return nn.Sequential(
            nn.Conv2d(in_channels, out_channels, 3, padding=1),
            bn,
            nn.ReLU(),
            nn.MaxPool2d(2),
        )

    def forward(self, x):
        return self.encoder(x).view(len(x), -1)


class DropBlock2D(nn.Module):
    """
    DropBlock: structured dropout for conv feature maps.
    """
    def __init__(self, drop_prob=0.0, block_size=5):
        super().__init__()
        self.drop_prob = float(drop_prob)
        self.block_size = int(block_size)

    def forward(self, x):
        if (not self.training) or self.drop_prob <= 0.0:
            return x

        b, c, h, w = x.shape
        bs = self.block_size
        if bs <= 1 or bs > min(h, w):
            return x

        denom = max(1, (h - bs + 1) * (w - bs + 1))
        gamma = self.drop_prob * (h * w) / (bs * bs) / denom
        gamma = min(gamma, 1.0)

        seed = (torch.rand((b, 1, h, w), device=x.device) < gamma).float()
        block_mask = F.max_pool2d(seed, kernel_size=bs, stride=1, padding=bs // 2)
        block_mask = block_mask[:, :, :h, :w]

        keep_mask = 1.0 - block_mask
        keep_sum = keep_mask.sum().clamp(min=1.0)
        return x * keep_mask * (keep_mask.numel() / keep_sum)


class ResNet12Block(nn.Module):
    def __init__(self, in_channels, out_channels, negative_slope=0.1,
                 drop_prob=0.0, block_size=5):
        super().__init__()
        self.conv1 = nn.Conv2d(in_channels, out_channels, 3, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(out_channels)

        self.conv2 = nn.Conv2d(out_channels, out_channels, 3, padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(out_channels)

        self.conv3 = nn.Conv2d(out_channels, out_channels, 3, padding=1, bias=False)
        self.bn3 = nn.BatchNorm2d(out_channels)

        self.relu = nn.LeakyReLU(negative_slope=negative_slope, inplace=True)
        self.pool = nn.MaxPool2d(2)

        self.downsample = None
        if in_channels != out_channels:
            self.downsample = nn.Sequential(
                nn.Conv2d(in_channels, out_channels, kernel_size=1, bias=False),
                nn.BatchNorm2d(out_channels),
            )

        self.dropblock = DropBlock2D(drop_prob=drop_prob, block_size=block_size)
        self._init_weights()

    def _init_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_normal_(m.weight, nonlinearity="leaky_relu")
            elif isinstance(m, nn.BatchNorm2d):
                nn.init.ones_(m.weight)
                nn.init.zeros_(m.bias)

    def forward(self, x):
        identity = x

        out = self.relu(self.bn1(self.conv1(x)))
        out = self.relu(self.bn2(self.conv2(out)))
        out = self.bn3(self.conv3(out))

        if self.downsample is not None:
            identity = self.downsample(identity)

        out = self.relu(out + identity)
        out = self.dropblock(out)
        out = self.pool(out)
        return out


class ResNet12(nn.Module):
    def __init__(self, task='miniimagenet', drop_prob=0.1, block_size=5):
        super().__init__()
        assert task in ['omniglot', 'miniimagenet']
        in_ch = 1 if task == 'omniglot' else 3

        self.block1 = ResNet12Block(in_ch, 64,  drop_prob=0.0,              block_size=block_size)
        self.block2 = ResNet12Block(64, 128,    drop_prob=drop_prob * 0.5,  block_size=block_size)
        self.block3 = ResNet12Block(128, 256,   drop_prob=drop_prob * 1.0,  block_size=block_size)
        self.block4 = ResNet12Block(256, 512,   drop_prob=drop_prob * 1.0,  block_size=block_size)

        self.gap = nn.AdaptiveAvgPool2d(1)
        self.out_dim = 512
        self.logit_scale = nn.Parameter(torch.tensor(2.0))

    def forward(self, x):
        x = self.block1(x)
        x = self.block2(x)
        x = self.block3(x)
        x = self.block4(x)
        x = self.gap(x)
        return x.view(x.size(0), -1)
