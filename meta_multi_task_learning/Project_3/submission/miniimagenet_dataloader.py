import torch
from torch.utils.data import Dataset
import os
import os.path as osp
from PIL import Image
from torchvision.transforms import v2 as T

ROOT_PATH = './'  # change as necessary.

AUGMENT_TRAIN = True


class miniImageNet(Dataset):
    def __init__(self, setname):
        csv_path = osp.join(ROOT_PATH, "splits", setname + '.csv')
        images_path = os.path.join(ROOT_PATH, "images")

        lines = [x.strip() for x in open(csv_path).readlines()[1:]]

        self.samples = []
        self.labels = []
        label_dict = {}
        label_index = 0
        self.label_index_2_name = []

        for e in lines:
            image_name, label_name = e.split(",")
            if label_name not in label_dict:
                label_dict[label_name] = label_index
                label_index += 1
                self.label_index_2_name.append(label_name)

            self.samples.append(os.path.join(images_path, image_name))
            self.labels.append(label_dict[label_name])

        mean = [0.485, 0.456, 0.406]
        std = [0.229, 0.224, 0.225]

        if setname == "train" and AUGMENT_TRAIN:
            self.transform = T.Compose([
                T.ToImage(),
                T.RandomResizedCrop((84, 84), scale=(0.6, 1.0)),
                T.RandomHorizontalFlip(p=0.5),
                T.RandAugment(num_ops=2, magnitude=9),
                T.ToDtype(torch.float32, scale=True),
                T.Normalize(mean=mean, std=std),
                T.RandomErasing(p=0.25, scale=(0.02, 0.2), ratio=(0.3, 3.3), value=0.0),
            ])
        else:
            self.transform = T.Compose([
                T.ToImage(),
                T.Resize((92, 92)),
                T.CenterCrop((84, 84)),
                T.ToDtype(torch.float32, scale=True),
                T.Normalize(mean=mean, std=std),
            ])

    def __len__(self):
        return len(self.labels)

    def get_label_num(self):
        return len(set(self.labels))

    def __getitem__(self, index):
        image_path, label = self.samples[index], self.labels[index]
        image = Image.open(image_path).convert('RGB')
        image = self.transform(image)
        return image, label
