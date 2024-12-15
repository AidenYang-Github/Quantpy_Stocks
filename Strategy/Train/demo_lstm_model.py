"""
Created on 2024年12月14日

@author: Aiden_yang
@website：https://gitee.com/aiden_yang/Stocks
"""
import itertools
import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
import numpy as np
import pandas as pd

from Module import MySQL_Database, mysql_data_processing as mdp
from config import STOCK_BASIC_NAME, USE_QFQ

# === 定义超参数 Hyper parameters
STOCK_TSCODE = '000001.SZ'  # 平安YH

# DATA parameters
TRAIN_SCALE = 0.8
WINDOW_SIZE = 1000

# DATALOADER parameters
SHUFFLE = False
DROP_LAST = True

# train patameters
EPOCHS = 1
LEARNING_RATE = 1e-2
MOMENTUM = 0.9

INPUT_SIZE = 1
HIDDEN_SIZE = 128
OUTPUT_SIZE = 1

BATCH1ST = True
BIDIRECT = False

# LSTM parameters
# OPTIM_NAME = ''  # 'SGD'
# BATCH_SIZE = 64
# NUM_LAYERS = 2
# DROPOUT = 0.2


def get_database_data(stn):
    """
    # 加载数据库中的个股数据
    :param stn:
    :return:
    """
    # 从数据库中获取所需回测的股票数据名称
    database = MySQL_Database.MySQLDatabaseOperations()
    all_stock_basic = database.read_data(stn)  # 获取数据表“all_stock_basic”中所有上市股票的代码
    stock_name = mdp.tscode_to_tbname(all_stock_basic.ts_code[0])  # 取数据库中第一只股票的代码名字
    # stock_name = 'sh603919'

    # 加载该个股OHLC及成交量等数据，并使用交易日期作为DataFrame的index
    df = database.read_data(stock_name)
    df.index = pd.to_datetime(df['trade_date'])

    # 重组df的列名称，让其符合backtrader要求的格式
    df.drop(['ts_code', 'trade_date', 'pre_close', 'change', 'pct_chg', 'amount'], axis=1, inplace=True)
    df.rename(columns={'vol': 'volume'}, inplace=True)
    return df


def create_dataset(stock_data, WINDOW_SIZE):
    X = []
    y = []
    scaler = MinMaxScaler()
    # 提取收盘价
    stock_data_close = stock_data.close
    stock_data_normalized = scaler.fit_transform(stock_data_close.values.reshape(-1, 1))
    sequence_length = len(stock_data_normalized)

    X_np = np.linspace(1, sequence_length, sequence_length)
    # y = stock_data_normalized
    for i in range(sequence_length - WINDOW_SIZE - 2):
        X.append(X_np[i: i + WINDOW_SIZE])
        y.append(stock_data_normalized[i: i + WINDOW_SIZE])

    X, y = np.array(X), np.array(y)
    X = torch.from_numpy(X)
    y = torch.from_numpy(y)
    return X.float(), y.float()


def train_test_split(X, y, TRAIN_SCALE):
    if len(X) == len(y):
        split_size = int(len(y) * TRAIN_SCALE)

        X_split, y_split = X.split(split_size), y.split(split_size)
        X_train, X_test = X_split[0], X_split[1]
        y_train, y_test = y_split[0], y_split[1]
        return X_train, X_test, y_train, y_test


# === 定义网络结构
# Define model
class SimpleLSTM(nn.Module):
    def __init__(self, INPUT_SIZE, HIDDEN_SIZE, OUTPUT_SIZE, NUM_LAYERS):
        super(SimpleLSTM, self).__init__()
        self.D = 1
        if BIDIRECT:
            self.D = 2

        self.h_0 = torch.randn(self.D * NUM_LAYERS, BATCH_SIZE, HIDDEN_SIZE)
        self.c_0 = torch.randn(self.D * NUM_LAYERS, BATCH_SIZE, HIDDEN_SIZE)

        self.h_n = torch.zeros(self.D * NUM_LAYERS, BATCH_SIZE, HIDDEN_SIZE)
        self.c_n = torch.zeros(self.D * NUM_LAYERS, BATCH_SIZE, HIDDEN_SIZE)

        self.lstm = nn.LSTM(INPUT_SIZE, HIDDEN_SIZE, NUM_LAYERS,
                            batch_first=BATCH1ST, dropout=DROPOUT, bidirectional=BIDIRECT)
        self.fc = nn.Linear(HIDDEN_SIZE * self.D, OUTPUT_SIZE)
        self.bn = nn.BatchNorm1d(num_features=WINDOW_SIZE)

    def forward(self, input_, h_0, c_0):
        input_ = self.bn(input_)
        x, (h_n, c_n) = self.lstm(input_, (h_0, c_0))
        x = self.fc(x)
        return x, (h_n, c_n)


# === 定义训练循环
def train(dataloader, model, loss_fn, optimizer):
    train_loss = 0.0
    size = len(dataloader.dataset)

    # Network parameters settings
    h0, c0 = model.h_0, model.c_0
    hn, cn = model.h_n, model.c_n

    for i, (X, y) in enumerate(dataloader):
        optimizer.zero_grad()

        if i == 0:
            hn_clone, cn_clone = h0, c0
        else:
            hn_clone, cn_clone = hn.detach().clone(), cn.detach().clone()

        pred, (hn, cn) = model(y, hn_clone, cn_clone)
        loss = loss_fn(pred, y)

        loss.backward()
        optimizer.step()

        loss, current = loss.item(), i * len(X)
        train_loss += loss
        print(f"[step:{i}] loss: {loss:>7f}  [{current:>5d}/{size:>5d}]")

    return train_loss / size


# === 定义测试循环
def test(dataloader, model, loss_fn):
    size = len(dataloader.dataset)
    model.eval()
    test_loss, correct = 0, 0

    with torch.no_grad():
        # Network parameters settings
        h0, c0 = model.h_0, model.c_0
        hn, cn = model.h_n, model.c_n

        for i, (X, y) in enumerate(dataloader):
            if i == 0:
                hn_clone, cn_clone = h0, c0
            else:
                hn_clone, cn_clone = hn.detach().clone(), cn.detach().clone()

            pred, (hn, cn) = model(y, hn_clone, cn_clone)
            test_loss += loss_fn(pred, y).item()
    test_loss /= size
    print(f"Test Avg loss: {test_loss:>8f} \n")
    return test_loss


def main_train(train_dataloader, test_dataloader):
    # === 创建网络
    model = SimpleLSTM(INPUT_SIZE, HIDDEN_SIZE, OUTPUT_SIZE, NUM_LAYERS)
    model.train()
    print(f'\nmodel\n: {model}')
    print(f'\nmodel parameters\n: {model.parameters()}')

    # === 定义损失函数和优化器

    criterion = nn.MSELoss()

    optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)
    optim_name = OPTIM_NAME
    if optim_name == 'SGD':
        optimizer = torch.optim.SGD(model.parameters(), lr=LEARNING_RATE, momentum=MOMENTUM)
    else:
        optim_name = 'ADAM'

    # === 执行训练和测试
    train_test_avg_loss_dict = dict()
    for epoch in range(EPOCHS):
        print(f"Epoch {epoch + 1}\n-------------------------------")
        train_avg_loss = train(train_dataloader, model, criterion, optimizer)
        test_avg_loss = test(test_dataloader, model, criterion)

        train_test_avg_loss_dict.update({epoch + 1: [train_avg_loss, test_avg_loss]})
        print(f'Epoch [{epoch + 1}/{EPOCHS}], Train Avg Loss:{train_avg_loss:.8f}, Test Avg Loss:{test_avg_loss:.8f}')
    print("TrainDone!")

    # === 模型参数保存
    model_file_name = f"data/lstm_model_BS{BATCH_SIZE}_EP{EPOCHS}_NL{NUM_LAYERS}_DO{DROPOUT}_OP{optim_name}_DL{DROP_LAST}_BD{BIDIRECT}.pth"
    torch.save(model.state_dict(), model_file_name)
    print(model_file_name)
    return train_test_avg_loss_dict, model_file_name


def main_eval(model_file_name, eval_dataloader):
    # === 模型参数加载
    model = SimpleLSTM(INPUT_SIZE, HIDDEN_SIZE, OUTPUT_SIZE, NUM_LAYERS)
    model.load_state_dict(torch.load(model_file_name))

    y_np = np.array(eval_dataloader.dataset.tensors[1][:, -1, -1])
    # === 模型验证
    model.eval()

    pred_tensor = torch.tensor(())
    with torch.no_grad():
        # Network parameters settings
        h0, c0 = model.h_0, model.c_0
        # hn, cn = model.h_n, model.c_n

        for i, (X, y) in enumerate(eval_dataloader):
            if i == 0:
                hn_clone, cn_clone = h0, c0
            else:
                hn_clone, cn_clone = hn.detach().clone(), cn.detach().clone()

            pred, (hn, cn) = model(y, hn_clone, cn_clone)
            pred_tensor = torch.cat((pred_tensor, pred))

    pred2_np = np.array(pred_tensor[:, -1, -1])

    print('Eval Done!')
    return y_np, pred2_np


def main():
    # 获取数据库中的个股数据
    if USE_QFQ:
        stock_df = mdp.adj_data_processing(STOCK_TSCODE)
    else:
        stock_df = get_database_data(STOCK_BASIC_NAME)

    # 将数据适配到pytorch框架的数据类型

    X, y = create_dataset(stock_df, WINDOW_SIZE)

    X_train, X_test, y_train, y_test = train_test_split(X, y, TRAIN_SCALE)

    train_tensor = TensorDataset(X_train, y_train)
    test_tensor = TensorDataset(X_test, y_test)

    train_dataloader = DataLoader(train_tensor, batch_size=BATCH_SIZE, shuffle=SHUFFLE, drop_last=DROP_LAST)
    test_dataloader = DataLoader(test_tensor, batch_size=BATCH_SIZE, shuffle=SHUFFLE, drop_last=DROP_LAST)

    model_file_name = None
    train_test_avg_loss_dict, model_file_name = main_train(train_dataloader, test_dataloader)
    if model_file_name is None:
        model_file_name = 'data/lstm_model_BS64_EP1_NL2_DO0.2_OPADAM_DLTrue_BDFalse.pth'
    close_data, pred_data = main_eval(model_file_name, test_dataloader)
    # main_eval(y_test)

    # plot
    fname = model_file_name.split('/')[1]
    fname = fname.strip('.pth')

    ep, tr, ts = 0, 0.0, 0.0
    for ep, t in zip(train_test_avg_loss_dict.keys(), train_test_avg_loss_dict.values()):
        tr = t[0]
        ts = t[1]

    plt.figure(figsize=(20.48, 11.52))
    plt.plot(close_data, '.')
    plt.plot(pred_data)
    plt.title(fname, fontsize=20)
    plt.legend(['close_data', 'predicted_data'])
    plt.text(250, 1, s=f'Epoch:{ep}, Train Avg Loss:{tr:.8f}, Test Avg Loss:{ts:.8f}', fontsize=15)
    # plt.show(block=True)

    # save figure
    fname += '.png'
    plt.savefig(fname=fname)

    pass


if __name__ == '__main__':
    # train patameters
    optim_name = ['ADAM', 'SGD']

    # LSTM parameters
    batch_size = [64, 320]
    num_layers = [1, 2]
    dropout = [0, 0.2, 0.4]

    combinations = list(itertools.product(num_layers, batch_size, dropout, optim_name))

    for i, (NUM_LAYERS, BATCH_SIZE, DROPOUT, OPTIM_NAME) in enumerate(combinations):
        print('===========================================')
        print(
            f'=== 执行第{i + 1}个超参组合，NUM_LAYERS={NUM_LAYERS}，BATCH_SIZE={BATCH_SIZE}，DROPOUT={DROPOUT}，OPTIM_NAME={OPTIM_NAME} ===')
        main()

    # main()
