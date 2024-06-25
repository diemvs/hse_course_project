from torch.utils.data import Dataset
from torch.utils.data import TensorDataset
import os
import torch
import json
from PIL import Image
import numpy as np
from torchvision.transforms import functional as F

class CocoDataset(Dataset):
    
    def __init__(self, root_dir, transforms, train_set=True):
        super().__init__()
        self.transforms = transforms
        self.results_json = os.path.join(root_dir, 'result.json')
        self.root_dir = root_dir
        
        assert os.path.exists(self.results_json), f"{self.results_json} file not exists"
        
        results_file = open(self.results_json, 'r')
        self.coco_dict = json.load(results_file)
        self.bbox_image = {} 
        bbox_img = self.coco_dict['annotations']
        
        for temp in bbox_img:
            temp_append = []
            pic_id = temp['image_id']
            bbox = temp['bbox']
            class_id = temp['category_id']
            
            x = bbox[0]
            y = bbox[1]
            w = bbox[2]
            h = bbox[3]
            
            x_min = x
            y_min = y
            x_max = x_min + w
            y_max = y_min + h
            
            temp_append.append(class_id)                     
            temp_append.append([x_min, y_min, x_max, y_max]) 
            
            if self.bbox_image.__contains__(pic_id):
                self.bbox_image[pic_id].append(temp_append)
            else:
                self.bbox_image[pic_id] = []
                self.bbox_image[pic_id].append(temp_append)
                
    def __len__(self):
        return len(self.coco_dict["images"])    

    def __getitem__(self, idx):
        image_list = self.coco_dict['images']
        file_name = image_list[idx]['file_name']
        file_path = os.path.join(self.root_dir, file_name)
        image = Image.open(file_path)
        image = np.array(image)
        
        bboxes = []      
        labels = []
        target = {}
        
        if self.bbox_image.__contains__(idx):
            for annotations in self.bbox_image[idx]:
                bboxes.append(annotations[1])
                labels.append(annotations[0])
            bboxes = torch.as_tensor(bboxes, dtype=torch.float32)
            labels = torch.as_tensor(labels, dtype=torch.int64)
            target["boxes"] = bboxes
            target["labels"] = labels
        else:
            bboxes = torch.as_tensor(bboxes, dtype=torch.float32)
            labels = torch.as_tensor(labels, dtype=torch.int64)
            target["boxes"] = bboxes
            target["labels"] = labels

        if self.transforms is not None:
            image, target = self.transforms(image, target)

        return image, target
    
    def target_names(self):
        return self.coco_dict['categories']