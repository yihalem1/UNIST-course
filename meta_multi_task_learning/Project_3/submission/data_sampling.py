
import torch 
import numpy as np
from torch.utils.data import DataLoader
from torch.utils.data import Dataset
from miniimagenet_dataloader import miniImageNet
DS_INFO_INDEX = 1
SAMPLE_START_INDEX = 2
SAMPLE_END_INDEX = 3
LABEL_START_INDEX = 4
LABEL_END_INDEX = 5

class DatasetsInfo(Dataset):
    def __init__(self, split):
        self.cluster_info = []
        self.labels = None
        self.total_label_num = 0
        self.total_sample_num = 0
        # for ds_name, ds_info in dataset_dict:
        
        ds_name = 'mini'
        ds_info = miniImageNet(split)
        
        self.total_label_num = ds_info.get_label_num()
        self.total_sample_num = len(ds_info)
        if self.labels is None:
            self.labels = np.array(ds_info.labels)
        else:
            self.labels = np.append(self.labels, self.total_label_num + np.array(ds_info.labels))
        self.cluster_info = (ds_name, ds_info, self.total_sample_num, self.total_label_num)
    

    def __getitem__(self, index):
        # find cluster
        x, _ = self.cluster_info[1][index]
        return x, torch.LongTensor([self.labels[index]])

    def __len__(self):
        return self.total_sample_num

    def get_label_num(self):
        return self.total_label_num

class DatasetSampler(object):
    def __init__(self, args, datasets, total_steps=10000, n_way=5, k_shot=1, batch_size=2, start_fraction=0, end_fraction=1, is_train=True, is_random_classes=False):

        self.total_steps = total_steps
        self.n_way = n_way
        self.k_shot = k_shot
        self.datasets = datasets
        self.args = args
        self.batch_size = batch_size
        self.is_train = is_train
        self.cluster_num = len(datasets.cluster_info)
        
        self.cluster_samples = np.array([], dtype=np.int8)
        if is_train:
            self.cluster_samples = []
            for num in np.random.choice(self.cluster_num, self.total_steps):
                self.cluster_samples.extend([num]*self.batch_size)
            self.cluster_samples = np.array(self.cluster_samples, dtype=np.int8)
        else:
            sort_list = np.repeat(int(0), args.max_test_task)
            self.cluster_samples = np.hstack((self.cluster_samples, sort_list))

        print("{} num_task:{}".format("miniImageNet", self.cluster_samples.shape[0]))

        self.label_2_instance_ids = []

        labels = datasets.labels

        for i in range(max(labels) + 1):
            ids = np.argwhere(labels == i).reshape(-1)
            ids = torch.from_numpy(ids)
            num_instance = len(ids)
            start_id = max(0, int(np.floor(start_fraction * num_instance)))
            end_id = min(num_instance, int(np.floor(end_fraction * num_instance)))
            self.label_2_instance_ids.append(ids[start_id: end_id])

        self.labels_num = len(self.label_2_instance_ids)
        self.labels = labels
        self.is_random_classes = is_random_classes

    def __len__(self):
        if self.is_train:
            return self.total_steps*self.self.batch_size
        else:
            return self.total_steps#*self.args.batch_size

    def __iter__(self):
        if self.is_train:
            for i_batch in range(self.total_steps*self.batch_size):
                batch = []
                class_ids = np.random.choice(np.arange(0, self.datasets.cluster_info[3]), self.n_way, replace=False)
                for class_id in class_ids:
                    instances_ids = self.label_2_instance_ids[class_id]
                    instances_ids_selected = torch.randperm(len(instances_ids))[0:self.k_shot]
                    batch.append(instances_ids[instances_ids_selected])
                batch = torch.stack(batch).reshape(-1)
                yield batch
        else:
            for i_batch in range(self.total_steps):
                batch = []
                np.arange(0, self.datasets.cluster_info[3])
                class_ids = np.random.choice(np.arange(0, self.datasets.cluster_info[3]), self.n_way, replace=False)
                for class_id in class_ids:
                    instances_ids = self.label_2_instance_ids[class_id]
                    instances_ids_selected = torch.randperm(len(instances_ids))[0:self.k_shot]
                    batch.append(instances_ids[instances_ids_selected])
                batch = torch.stack(batch).reshape(-1)
                yield batch
                
                
class DataSampling():
    def __init__(self, args, N, K, Q, batch_size):

        self.stages = {'train':'train', 'val':'val', 'test':'test'}

        # self.ds_name = args.datasets
        
        self.m_dataset = {stage: DatasetsInfo(split=stage) for stage in self.stages}
        self.n_cluster = len(self.m_dataset[self.stages['train']].cluster_info)
        max_steps = {'train' : args.epoch, 'val': args.max_test_task, 'test': args.max_test_task} #*self.n_cluster*args.batch_size
        shuffling = {'train': True, 'val': False, 'test': False}
        
      
        self.m_sampler = {
            stage: DatasetSampler(args,
                                  self.m_dataset[stage],
                                  total_steps=max_steps[stage],
                                  batch_size=batch_size,
                                  n_way= N, k_shot=K + Q,
                                  is_train = shuffling[stage],
                                  is_random_classes=False) for stage in self.stages
            }
        
        self.m_dataloader = {
            stage: DataLoader(self.m_dataset[stage], 
                              batch_sampler=self.m_sampler[stage], 
                              num_workers=8, 
                              pin_memory=True) for stage in self.stages
        }

        
       
