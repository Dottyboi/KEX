import argparse
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torch.utils.data import random_split

# array shape: 25x79x3


# ~torch.is_nonzero


class SignSpottingModel(nn.Module):
    def __init__(self, input_size=237, hidden_size=32, num_layers=3, num_classes=120):
        super(SignSpottingModel, self).__init__()
        self.lstm = nn.LSTM(
            input_size, hidden_size, num_layers, batch_first=True, dropout=0.5
        )
        self.dropout = nn.Dropout(0.5)
        self.fc1 = nn.Linear(hidden_size, 64)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(64, num_classes)

    def forward(self, x):
        lstm_out, _ = self.lstm(x)

        x = lstm_out[:, -1, :]

        x = self.dropout(x)
        x = self.fc1(x)
        x = self.relu(x)
        x = self.fc2(x)

        return x


class SignDataset(torch.utils.data.Dataset):
    def __init__(self, filepaths, labels):
        self.filepaths = filepaths
        self.labels = labels

    def __len__(self):
        return len(self.filepaths)

    def __getitem__(self, idx):
        data = np.load(self.filepaths[idx])["pose"]
        data = data - data[:, 0:1]
        scale = np.linalg.norm(data, axis=1).max()
        if scale > 0:
            data = data / scale
        data = torch.tensor(data, dtype=torch.float32)
        label = torch.tensor(self.labels[idx], dtype=torch.long)
        return data, label


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cache_dir", default="Sign_cache", type=Path)
    args = parser.parse_args()

    cache_files: list[Path] = sorted(args.cache_dir.iterdir())

    data = []
    class_names = {file.name.split("_")[0] for file in cache_files}
    class_idx = {clas: i for i, clas in enumerate(list(class_names))}
    labels = []

    for file in cache_files:
        data.append(file)
        labels.append(class_idx[file.name.split("_")[0]])

    dataset = SignDataset(data, labels)

    train_size = int(0.8 * len(dataset))
    val_size = len(dataset) - train_size

    train_dataset, val_dataset = random_split(dataset, [train_size, val_size])

    train_loader = DataLoader(train_dataset, batch_size=250, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=50, shuffle=False)

    print("Done loading data")

    criterion = nn.CrossEntropyLoss()

    model = SignSpottingModel()

    optimizer = torch.optim.Adam(model.parameters(), lr=5e-4)

    epoch = 0

    best_val_loss = float("inf")

    patience = 100
    counter = 0

    plt.ion()  # turn on interactive mode
    fig, ax = plt.subplots()

    line, = ax.plot([], [])  # empty line
    ax.set_xlabel("Epoch")
    ax.set_ylabel("Validation Loss")
    ax.set_title("Training Progress")

    losses = []

    while True:
        # Training
        model.train()
        train_loss = 0

        for x, y in train_loader:
            outputs = model(x)
            loss = criterion(outputs, y)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            train_loss += loss.item()

        # Validation
        model.eval()
        val_loss = 0
        correct = 0
        total = 0

        with torch.no_grad():
            for x, y in val_loader:
                outputs = model(x)
                loss = criterion(outputs, y)

                val_loss += loss.item()

                _, predicted = torch.max(outputs, 1)

                total += y.size(0)
                correct += (predicted == y).sum().item()

        val_accuracy = correct / total

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            torch.save(model.state_dict(), "best_model.pth")
            counter = 0
        else:
            counter += 1

        print(f"Epoch {epoch}\t{counter}/{patience}")
        print(f"Train Loss: {train_loss:.4f}")
        print(f"Val Loss: {val_loss:.4f}")
        print(f"Val Accuracy: {val_accuracy:.4f}")

        line.set_xdata(range(len(losses)))
        line.set_ydata(losses)

        ax.relim()
        ax.autoscale_view()

        plt.draw()
        plt.pause(0.01)

        if counter >= patience:
            print("Early stopping")
            break

        epoch += 1

    print(best_val_loss)

    plt.ioff()
    plt.show()


if __name__ == "__main__":
    main()
