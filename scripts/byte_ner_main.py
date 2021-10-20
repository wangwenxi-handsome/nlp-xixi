import os
import sys
sys.path.append(os.getcwd())
import torch.optim as optim
import torch.nn as nn

from dataloader.preprocessor.byte_ner import BYTEPreProcessor
from model.BertLinerSoftmax import BertLinerSoftmax
from worker.worker import Worker
from utils.torch_related import setup_seed
from metric.ner_metric import NERMetric

# global args
model_name = "bert-base-chinese"
data_path = "./product/data/byte_ner1/con_unchecked1019.npy"
label_num = 63
lr = 0.001
momentum = 0.9
save_checkpoint_path = "product/data/byte_ner1/checkpoint"
load_checkpoint_path = None
batch_size = 12
num_workers = 0

if __name__ == "__main__":
    # train
    setup_seed(42)
    data_gen = BYTEPreProcessor(model_name=model_name)
    data_gen.init_data(data_path)
    dataloader = data_gen.get_dataloader(batch_size=batch_size, num_workers=num_workers)
    model = BertLinerSoftmax(model_name=model_name, loss_func="ce", label_num=label_num)
    optimizer = optim.SGD(model.parameters(), lr=lr, momentum=momentum)
    trainer = Worker(
        optimizer = optimizer, 
        model = model, 
        save_checkpoint_path = save_checkpoint_path,
        load_checkpoint_path = load_checkpoint_path,
    )
    trainer.train(dataloader["train"], dataloader["dev"])

    # test
    loss, outputs = trainer.rollout(dataloader["test"])
    entity_outputs, entity_labels = data_gen.decode(
        outputs, 
        data_gen.get_tokenize_length("test"), 
        data_gen.get_raw_data_y("test"),
    )
    metric = NERMetric(data_gen.get_raw_data_x("test"), entity_labels, entity_outputs)
    print(metric.get_score())
    print(metric.get_mean_score())