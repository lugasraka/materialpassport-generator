#!/usr/bin/env python
# coding: utf-8

# # 03. Deep Learning with MLflow Tracking
# 
# **Objective:** Build deep learning models using PyTorch **with comprehensive MLflow experiment tracking**
# 
# **Models:**
# 1. Simple Feedforward Neural Network (Single-task)
# 2. Deeper Neural Network with Dropout & Batch Normalization
# 3. Multi-task Learning Network (Strength + Circularity)
# 
# **New in this version:**
# - MLflow experiment tracking for all neural networks
# - PyTorch model logging
# - Training curve tracking (per-epoch metrics)
# - Architecture and parameter logging
# - Model registry integration
# 
# **Contents:**
# 1. Setup & MLflow Configuration
# 2. Data Loading & Preprocessing
# 3. PyTorch Dataset & DataLoader
# 4. Neural Network Training with MLflow
# 5. Model Evaluation
# 6. Multi-task Learning
# 7. Model Comparison

# ## 1. Setup & MLflow Configuration

# In[ ]:


# Import libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
import sys
import time
import os
warnings.filterwarnings('ignore')

# PyTorch imports
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader, TensorDataset

# Sklearn utilities
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error

# MLflow imports
import mlflow
import mlflow.pytorch
import mlflow.sklearn

# Add src to path
sys.path.insert(0, 'src')

# Import MLflow utilities
from src.mlflow_config import (
    MLFLOW_TRACKING_URI,
    EXPERIMENTS,
    MODEL_NAMES,
    TAG_MODEL_FAMILY,
    TAG_MODEL_TYPE,
    TAG_TUNING_METHOD,
    TAG_FEATURE_SET,
    TAG_DATASET_VERSION
)
from src.utils.mlflow_utils import (
    setup_mlflow_experiment,
    log_model_artifacts,
    log_metrics_and_params,
    log_predictions_vs_actual,
    log_residual_plot,
    compare_runs
)

# Set plotting style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette('Set2')

# Random seed for reproducibility
RANDOM_STATE = 42
np.random.seed(RANDOM_STATE)
torch.manual_seed(RANDOM_STATE)

# Force CPU usage (set to False if you have compatible GPU)
FORCE_CPU = True

if FORCE_CPU:
    device = torch.device('cpu')
    print("[INFO] Using CPU (CUDA disabled)")
else:
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"[INFO] Using device: {device}")

print(f"Device: {device}")
print(f"PyTorch version: {torch.__version__}")
print("[PASS] Libraries imported successfully")
print("[PASS] MLflow utilities imported")


# In[ ]:


# Setup MLflow experiment
experiment_id = setup_mlflow_experiment('deep_learning')

print(f"\n[PASS] MLflow tracking configured:")
print(f"  Tracking URI: {MLFLOW_TRACKING_URI}")
print(f"  Experiment: {EXPERIMENTS['deep_learning']}")
print(f"  Experiment ID: {experiment_id}")
print(f"\nTo view results: mlflow ui --port 5000")
print(f"Then open: http://localhost:5000")


# ## 2. Data Loading & Preprocessing

# In[ ]:


# Load dataset
data_path = Path('data/processed/concrete_enriched.csv')

if not data_path.exists():
    raise FileNotFoundError("Dataset not found! Please run: python src/data/download_dataset.py")

df = pd.read_csv(data_path)
print(f"[PASS] Dataset loaded: {df.shape[0]} instances, {df.shape[1]} features")


# In[ ]:


# Define features and targets
feature_cols = [
    'cement', 'slag', 'fly_ash', 'water',
    'superplasticizer', 'coarse_aggregate',
    'fine_aggregate', 'age'
]

target_col = 'strength'
target_col_2 = 'circularity_score'

# Prepare data
X = df[feature_cols].values.astype(np.float32)
y_strength = df[target_col].values.astype(np.float32)
y_circularity = df[target_col_2].values.astype(np.float32)

print(f"Features shape: {X.shape}")
print(f"Strength target shape: {y_strength.shape}")
print(f"Circularity target shape: {y_circularity.shape}")


# In[ ]:


# Train-val-test split
X_train, X_test, y_train_str, y_test_str, y_train_circ, y_test_circ = train_test_split(
    X, y_strength, y_circularity, test_size=0.2, random_state=RANDOM_STATE
)

X_train, X_val, y_train_str, y_val_str, y_train_circ, y_val_circ = train_test_split(
    X_train, y_train_str, y_train_circ, test_size=0.2, random_state=RANDOM_STATE
)

print(f"Training set: {X_train.shape[0]} samples")
print(f"Validation set: {X_val.shape[0]} samples")
print(f"Test set: {X_test.shape[0]} samples")
print(f"\nSplit: {X_train.shape[0]/len(X):.1%} train, {X_val.shape[0]/len(X):.1%} val, {X_test.shape[0]/len(X):.1%} test")


# In[ ]:


# Feature scaling
scaler_X = StandardScaler()
scaler_y_str = StandardScaler()
scaler_y_circ = StandardScaler()

X_train_scaled = scaler_X.fit_transform(X_train)
X_val_scaled = scaler_X.transform(X_val)
X_test_scaled = scaler_X.transform(X_test)

y_train_str_scaled = scaler_y_str.fit_transform(y_train_str.reshape(-1, 1)).ravel()
y_val_str_scaled = scaler_y_str.transform(y_val_str.reshape(-1, 1)).ravel()
y_test_str_scaled = scaler_y_str.transform(y_test_str.reshape(-1, 1)).ravel()

y_train_circ_scaled = scaler_y_circ.fit_transform(y_train_circ.reshape(-1, 1)).ravel()
y_val_circ_scaled = scaler_y_circ.transform(y_val_circ.reshape(-1, 1)).ravel()
y_test_circ_scaled = scaler_y_circ.transform(y_test_circ.reshape(-1, 1)).ravel()

print("[PASS] Data scaled successfully")


# ## 3. PyTorch DataLoaders

# In[ ]:


# Convert to tensors
X_train_tensor = torch.FloatTensor(X_train_scaled)
X_val_tensor = torch.FloatTensor(X_val_scaled)
X_test_tensor = torch.FloatTensor(X_test_scaled)

y_train_str_tensor = torch.FloatTensor(y_train_str_scaled)
y_val_str_tensor = torch.FloatTensor(y_val_str_scaled)
y_test_str_tensor = torch.FloatTensor(y_test_str_scaled)

y_train_circ_tensor = torch.FloatTensor(y_train_circ_scaled)
y_val_circ_tensor = torch.FloatTensor(y_val_circ_scaled)
y_test_circ_tensor = torch.FloatTensor(y_test_circ_scaled)

# Create datasets
train_dataset = TensorDataset(X_train_tensor, y_train_str_tensor)
val_dataset = TensorDataset(X_val_tensor, y_val_str_tensor)
test_dataset = TensorDataset(X_test_tensor, y_test_str_tensor)

train_dataset_mt = TensorDataset(X_train_tensor, y_train_str_tensor, y_train_circ_tensor)
val_dataset_mt = TensorDataset(X_val_tensor, y_val_str_tensor, y_val_circ_tensor)
test_dataset_mt = TensorDataset(X_test_tensor, y_test_str_tensor, y_test_circ_tensor)

# Create dataloaders
batch_size = 32
train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

train_loader_mt = DataLoader(train_dataset_mt, batch_size=batch_size, shuffle=True)
val_loader_mt = DataLoader(val_dataset_mt, batch_size=batch_size, shuffle=False)
test_loader_mt = DataLoader(test_dataset_mt, batch_size=batch_size, shuffle=False)

print(f"[PASS] DataLoaders created with batch size: {batch_size}")


# ## 4. Model Architectures

# In[ ]:


class SimpleNN(nn.Module):
    """Simple feedforward neural network"""
    def __init__(self, input_dim, hidden_dims=[64, 32]):
        super(SimpleNN, self).__init__()
        self.fc1 = nn.Linear(input_dim, hidden_dims[0])
        self.fc2 = nn.Linear(hidden_dims[0], hidden_dims[1])
        self.fc3 = nn.Linear(hidden_dims[1], 1)
        self.relu = nn.ReLU()

    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.relu(self.fc2(x))
        x = self.fc3(x)
        return x

class DeepNN(nn.Module):
    """Deeper neural network with dropout and batch normalization"""
    def __init__(self, input_dim, hidden_dims=[128, 64, 32], dropout=0.2):
        super(DeepNN, self).__init__()
        self.fc1 = nn.Linear(input_dim, hidden_dims[0])
        self.bn1 = nn.BatchNorm1d(hidden_dims[0])
        self.dropout1 = nn.Dropout(dropout)

        self.fc2 = nn.Linear(hidden_dims[0], hidden_dims[1])
        self.bn2 = nn.BatchNorm1d(hidden_dims[1])
        self.dropout2 = nn.Dropout(dropout)

        self.fc3 = nn.Linear(hidden_dims[1], hidden_dims[2])
        self.bn3 = nn.BatchNorm1d(hidden_dims[2])
        self.dropout3 = nn.Dropout(dropout)

        self.fc4 = nn.Linear(hidden_dims[2], 1)
        self.relu = nn.ReLU()

    def forward(self, x):
        x = self.fc1(x)
        x = self.bn1(x)
        x = self.relu(x)
        x = self.dropout1(x)

        x = self.fc2(x)
        x = self.bn2(x)
        x = self.relu(x)
        x = self.dropout2(x)

        x = self.fc3(x)
        x = self.bn3(x)
        x = self.relu(x)
        x = self.dropout3(x)

        x = self.fc4(x)
        return x

class MultiTaskNN(nn.Module):
    """Multi-task neural network predicting both strength and circularity"""
    def __init__(self, input_dim, hidden_dims=[128, 64]):
        super(MultiTaskNN, self).__init__()
        self.shared_fc1 = nn.Linear(input_dim, hidden_dims[0])
        self.shared_fc2 = nn.Linear(hidden_dims[0], hidden_dims[1])

        self.strength_head = nn.Linear(hidden_dims[1], 1)
        self.circularity_head = nn.Linear(hidden_dims[1], 1)

        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.2)

    def forward(self, x):
        x = self.relu(self.shared_fc1(x))
        x = self.dropout(x)
        x = self.relu(self.shared_fc2(x))
        x = self.dropout(x)

        strength_out = self.strength_head(x)
        circularity_out = self.circularity_head(x)

        return strength_out, circularity_out

print("[PASS] Model architectures defined")


# ## 5. Training Functions with MLflow

# In[ ]:


def train_single_task_model_with_mlflow(model, train_loader, val_loader, model_name, 
                                        epochs=100, lr=0.001):
    """Train single-task model with MLflow tracking"""

    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)

    train_losses = []
    val_losses = []
    best_val_loss = float('inf')

    for epoch in range(epochs):
        # Training
        model.train()
        train_loss = 0.0

        for X_batch, y_batch in train_loader:
            X_batch, y_batch = X_batch.to(device), y_batch.to(device)
            outputs = model(X_batch).squeeze()
            loss = criterion(outputs, y_batch)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            train_loss += loss.item() * X_batch.size(0)

        train_loss /= len(train_loader.dataset)
        train_losses.append(train_loss)

        # Validation
        model.eval()
        val_loss = 0.0

        with torch.no_grad():
            for X_batch, y_batch in val_loader:
                X_batch, y_batch = X_batch.to(device), y_batch.to(device)
                outputs = model(X_batch).squeeze()
                loss = criterion(outputs, y_batch)
                val_loss += loss.item() * X_batch.size(0)

        val_loss /= len(val_loader.dataset)
        val_losses.append(val_loss)

        if val_loss < best_val_loss:
            best_val_loss = val_loss

        # Log to MLflow every 10 epochs
        if (epoch + 1) % 10 == 0:
            mlflow.log_metrics({
                "epoch_train_loss": train_loss,
                "epoch_val_loss": val_loss
            }, step=epoch)
            print(f"Epoch [{epoch+1}/{epochs}], Train Loss: {train_loss:.4f}, Val Loss: {val_loss:.4f}")

    print(f"\nBest validation loss: {best_val_loss:.4f}")

    return train_losses, val_losses, best_val_loss

def train_multitask_model_with_mlflow(model, train_loader_mt, val_loader_mt,
                                      epochs=100, lr=0.001, 
                                      strength_weight=1.0, circularity_weight=0.5):
    """Train multi-task model with MLflow tracking"""

    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)

    train_losses = []
    val_losses = []
    best_val_loss = float('inf')

    for epoch in range(epochs):
        # Training
        model.train()
        train_loss = 0.0

        for X_batch, y_str_batch, y_circ_batch in train_loader_mt:
            X_batch = X_batch.to(device)
            y_str_batch = y_str_batch.to(device)
            y_circ_batch = y_circ_batch.to(device)

            str_out, circ_out = model(X_batch)
            loss_str = criterion(str_out.squeeze(), y_str_batch)
            loss_circ = criterion(circ_out.squeeze(), y_circ_batch)
            loss = strength_weight * loss_str + circularity_weight * loss_circ

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            train_loss += loss.item() * X_batch.size(0)

        train_loss /= len(train_loader_mt.dataset)
        train_losses.append(train_loss)

        # Validation
        model.eval()
        val_loss = 0.0

        with torch.no_grad():
            for X_batch, y_str_batch, y_circ_batch in val_loader_mt:
                X_batch = X_batch.to(device)
                y_str_batch = y_str_batch.to(device)
                y_circ_batch = y_circ_batch.to(device)

                str_out, circ_out = model(X_batch)
                loss_str = criterion(str_out.squeeze(), y_str_batch)
                loss_circ = criterion(circ_out.squeeze(), y_circ_batch)
                loss = strength_weight * loss_str + circularity_weight * loss_circ

                val_loss += loss.item() * X_batch.size(0)

        val_loss /= len(val_loader_mt.dataset)
        val_losses.append(val_loss)

        if val_loss < best_val_loss:
            best_val_loss = val_loss

        if (epoch + 1) % 10 == 0:
            mlflow.log_metrics({
                "epoch_train_loss": train_loss,
                "epoch_val_loss": val_loss
            }, step=epoch)
            print(f"Epoch [{epoch+1}/{epochs}], Train Loss: {train_loss:.4f}, Val Loss: {val_loss:.4f}")

    print(f"\nBest validation loss: {best_val_loss:.4f}")

    return train_losses, val_losses, best_val_loss

def evaluate_model(model, X_test_tensor, y_test_str, scaler_y, is_multitask=False):
    """Evaluate model on test set"""
    model.eval()
    with torch.no_grad():
        X_test_device = X_test_tensor.to(device)

        if is_multitask:
            y_pred_scaled, _ = model(X_test_device)
        else:
            y_pred_scaled = model(X_test_device)

        y_pred_scaled = y_pred_scaled.cpu().numpy().ravel()

    y_pred = scaler_y.inverse_transform(y_pred_scaled.reshape(-1, 1)).ravel()

    r2 = r2_score(y_test_str, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test_str, y_pred))
    mae = mean_absolute_error(y_test_str, y_pred)

    return r2, rmse, mae, y_pred

print("[PASS] Training functions defined")


# ## 6. Model 1: Simple Neural Network

# In[ ]:


print("="*60)
print("MODEL 1: SIMPLE NEURAL NETWORK WITH MLFLOW")
print("="*60)

with mlflow.start_run(run_name="simple_nn_baseline") as run:
    start_time = time.time()

    # Create model
    input_dim = X_train.shape[1]
    model_simple = SimpleNN(input_dim, hidden_dims=[64, 32]).to(device)

    print(f"\nArchitecture: {model_simple}")
    total_params = sum(p.numel() for p in model_simple.parameters())
    print(f"Total parameters: {total_params:,}")

    # Log parameters
    params = {
        'model_type': 'simple_nn',
        'architecture': 'feedforward',
        'input_dim': input_dim,
        'hidden_dims': str([64, 32]),
        'total_parameters': total_params,
        'framework': 'pytorch',
        'device': str(device),
        'batch_size': batch_size,
        'epochs': 100,
        'learning_rate': 0.001,
        'optimizer': 'Adam',
        'loss_function': 'MSE',
        'feature_set': 'original_8_features',
        'scaling': 'StandardScaler'
    }

    # Train model
    print("\nTraining Simple NN...")
    train_losses, val_losses, best_val_loss = train_single_task_model_with_mlflow(
        model_simple, train_loader, val_loader, 'simple_nn', epochs=100, lr=0.001
    )

    training_time = time.time() - start_time

    # Evaluate
    r2_simple, rmse_simple, mae_simple, pred_simple = evaluate_model(
        model_simple, X_test_tensor, y_test_str, scaler_y_str
    )

    # Log metrics
    metrics = {
        'test_r2': r2_simple,
        'test_rmse': rmse_simple,
        'test_mae': mae_simple,
        'best_val_loss': best_val_loss,
        'final_train_loss': train_losses[-1],
        'final_val_loss': val_losses[-1],
        'training_time_seconds': training_time
    }

    # Tags
    tags = {
        TAG_MODEL_FAMILY: 'deep_learning',
        TAG_MODEL_TYPE: 'simple_nn',
        TAG_TUNING_METHOD: 'default',
        TAG_FEATURE_SET: 'original',
        TAG_DATASET_VERSION: 'v1.0'
    }

    log_metrics_and_params(params, metrics, tags)

    # Log model (PyTorch)
    mlflow.pytorch.log_model(
        model_simple,
        "model",
        registered_model_name=MODEL_NAMES['simple_nn']
    )

    # Log scalers
    mlflow.sklearn.log_model(scaler_X, "scaler_X")
    mlflow.sklearn.log_model(scaler_y_str, "scaler_y_strength")

    # Log visualizations
    fig = log_predictions_vs_actual(
        y_test_str, pred_simple,
        title="Simple NN: Predictions vs Actual"
    )
    plt.close(fig)

    fig = log_residual_plot(y_test_str, pred_simple)
    plt.close(fig)

    # Log training history plot
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(train_losses, label='Train Loss', linewidth=2)
    ax.plot(val_losses, label='Validation Loss', linewidth=2)
    ax.set_xlabel('Epoch')
    ax.set_ylabel('Loss (MSE)')
    ax.set_title('Simple NN: Training History')
    ax.legend()
    ax.grid(alpha=0.3)
    mlflow.log_figure(fig, "training_history.png")
    plt.close(fig)

    run_id = run.info.run_id

    print(f"\n[PASS] MLflow run completed: {run_id}")
    print(f"\nTest Performance:")
    print(f"  R² Score: {r2_simple:.4f}")
    print(f"  RMSE: {rmse_simple:.4f} MPa")
    print(f"  MAE: {mae_simple:.4f} MPa")


# ## 7. Model 2: Deep Neural Network

# In[ ]:


print("="*60)
print("MODEL 2: DEEP NEURAL NETWORK WITH MLFLOW")
print("="*60)

with mlflow.start_run(run_name="deep_nn_baseline") as run:
    start_time = time.time()

    # Create model
    model_deep = DeepNN(input_dim, hidden_dims=[128, 64, 32], dropout=0.2).to(device)

    print(f"\nArchitecture: {model_deep}")
    total_params = sum(p.numel() for p in model_deep.parameters())
    print(f"Total parameters: {total_params:,}")

    params = {
        'model_type': 'deep_nn',
        'architecture': 'deep_feedforward_with_regularization',
        'input_dim': input_dim,
        'hidden_dims': str([128, 64, 32]),
        'dropout': 0.2,
        'batch_normalization': True,
        'total_parameters': total_params,
        'framework': 'pytorch',
        'device': str(device),
        'batch_size': batch_size,
        'epochs': 100,
        'learning_rate': 0.001,
        'optimizer': 'Adam',
        'loss_function': 'MSE',
        'feature_set': 'original_8_features',
        'scaling': 'StandardScaler'
    }

    print("\nTraining Deep NN...")
    train_losses, val_losses, best_val_loss = train_single_task_model_with_mlflow(
        model_deep, train_loader, val_loader, 'deep_nn', epochs=100, lr=0.001
    )

    training_time = time.time() - start_time

    r2_deep, rmse_deep, mae_deep, pred_deep = evaluate_model(
        model_deep, X_test_tensor, y_test_str, scaler_y_str
    )

    metrics = {
        'test_r2': r2_deep,
        'test_rmse': rmse_deep,
        'test_mae': mae_deep,
        'best_val_loss': best_val_loss,
        'final_train_loss': train_losses[-1],
        'final_val_loss': val_losses[-1],
        'training_time_seconds': training_time
    }

    tags = {
        TAG_MODEL_FAMILY: 'deep_learning',
        TAG_MODEL_TYPE: 'deep_nn',
        TAG_TUNING_METHOD: 'default',
        TAG_FEATURE_SET: 'original',
        TAG_DATASET_VERSION: 'v1.0'
    }

    log_metrics_and_params(params, metrics, tags)

    mlflow.pytorch.log_model(
        model_deep,
        "model",
        registered_model_name=MODEL_NAMES['deep_nn']
    )

    mlflow.sklearn.log_model(scaler_X, "scaler_X")
    mlflow.sklearn.log_model(scaler_y_str, "scaler_y_strength")

    fig = log_predictions_vs_actual(
        y_test_str, pred_deep,
        title="Deep NN: Predictions vs Actual"
    )
    plt.close(fig)

    fig = log_residual_plot(y_test_str, pred_deep)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(train_losses, label='Train Loss', linewidth=2)
    ax.plot(val_losses, label='Validation Loss', linewidth=2)
    ax.set_xlabel('Epoch')
    ax.set_ylabel('Loss (MSE)')
    ax.set_title('Deep NN: Training History')
    ax.legend()
    ax.grid(alpha=0.3)
    mlflow.log_figure(fig, "training_history.png")
    plt.close(fig)

    run_id = run.info.run_id

    print(f"\n[PASS] MLflow run completed: {run_id}")
    print(f"\nTest Performance:")
    print(f"  R² Score: {r2_deep:.4f}")
    print(f"  RMSE: {rmse_deep:.4f} MPa")
    print(f"  MAE: {mae_deep:.4f} MPa")


# ## 8. Model 3: Multi-Task Neural Network

# In[ ]:


print("="*60)
print("MODEL 3: MULTI-TASK NEURAL NETWORK WITH MLFLOW")
print("="*60)

with mlflow.start_run(run_name="multitask_nn_baseline") as run:
    start_time = time.time()

    # Create model
    model_mt = MultiTaskNN(input_dim, hidden_dims=[128, 64]).to(device)

    print(f"\nArchitecture: {model_mt}")
    total_params = sum(p.numel() for p in model_mt.parameters())
    print(f"Total parameters: {total_params:,}")

    strength_weight = 1.0
    circularity_weight = 0.5

    params = {
        'model_type': 'multitask_nn',
        'architecture': 'multi_task_shared_representation',
        'input_dim': input_dim,
        'hidden_dims': str([128, 64]),
        'dropout': 0.2,
        'tasks': 'strength+circularity',
        'strength_weight': strength_weight,
        'circularity_weight': circularity_weight,
        'total_parameters': total_params,
        'framework': 'pytorch',
        'device': str(device),
        'batch_size': batch_size,
        'epochs': 100,
        'learning_rate': 0.001,
        'optimizer': 'Adam',
        'loss_function': 'MSE',
        'feature_set': 'original_8_features',
        'scaling': 'StandardScaler'
    }

    print("\nTraining Multi-Task NN...")
    train_losses, val_losses, best_val_loss = train_multitask_model_with_mlflow(
        model_mt, train_loader_mt, val_loader_mt, epochs=100, lr=0.001,
        strength_weight=strength_weight, circularity_weight=circularity_weight
    )

    training_time = time.time() - start_time

    r2_mt, rmse_mt, mae_mt, pred_mt = evaluate_model(
        model_mt, X_test_tensor, y_test_str, scaler_y_str, is_multitask=True
    )

    metrics = {
        'test_r2': r2_mt,
        'test_rmse': rmse_mt,
        'test_mae': mae_mt,
        'best_val_loss': best_val_loss,
        'final_train_loss': train_losses[-1],
        'final_val_loss': val_losses[-1],
        'training_time_seconds': training_time
    }

    tags = {
        TAG_MODEL_FAMILY: 'deep_learning',
        TAG_MODEL_TYPE: 'multitask_nn',
        TAG_TUNING_METHOD: 'default',
        TAG_FEATURE_SET: 'original',
        TAG_DATASET_VERSION: 'v1.0'
    }

    log_metrics_and_params(params, metrics, tags)

    mlflow.pytorch.log_model(
        model_mt,
        "model",
        registered_model_name=MODEL_NAMES['multitask_nn']
    )

    mlflow.sklearn.log_model(scaler_X, "scaler_X")
    mlflow.sklearn.log_model(scaler_y_str, "scaler_y_strength")
    mlflow.sklearn.log_model(scaler_y_circ, "scaler_y_circularity")

    fig = log_predictions_vs_actual(
        y_test_str, pred_mt,
        title="Multi-Task NN: Predictions vs Actual"
    )
    plt.close(fig)

    fig = log_residual_plot(y_test_str, pred_mt)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(train_losses, label='Train Loss', linewidth=2)
    ax.plot(val_losses, label='Validation Loss', linewidth=2)
    ax.set_xlabel('Epoch')
    ax.set_ylabel('Combined Loss')
    ax.set_title('Multi-Task NN: Training History')
    ax.legend()
    ax.grid(alpha=0.3)
    mlflow.log_figure(fig, "training_history.png")
    plt.close(fig)

    run_id = run.info.run_id

    print(f"\n[PASS] MLflow run completed: {run_id}")
    print(f"\nTest Performance:")
    print(f"  R² Score: {r2_mt:.4f}")
    print(f"  RMSE: {rmse_mt:.4f} MPa")
    print(f"  MAE: {mae_mt:.4f} MPa")


# ## 9. Model Comparison

# In[ ]:


print("="*60)
print("COMPARING DEEP LEARNING RUNS FROM MLFLOW")
print("="*60)

comparison_df = compare_runs(
    experiment_names=[EXPERIMENTS['deep_learning']],
    metrics=['test_r2', 'test_rmse', 'test_mae', 'training_time_seconds'],
    max_results=10
)

baseline_runs = comparison_df[
    comparison_df['run_name'].str.contains('baseline')
].copy()

print(f"\nFound {len(baseline_runs)} deep learning baseline runs:\n")
print(baseline_runs[[
    'run_name', 'model_type', 'test_r2', 'test_rmse', 
    'test_mae', 'training_time_seconds'
]].to_string(index=False))

if len(baseline_runs) > 0:
    best_idx = baseline_runs['test_r2'].idxmax()
    best_model = baseline_runs.loc[best_idx, 'model_type']
    best_r2 = baseline_runs.loc[best_idx, 'test_r2']
    best_rmse = baseline_runs.loc[best_idx, 'test_rmse']

    print(f"\n{'='*60}")
    print(f"[PASS] Best Neural Network: {best_model}")
    print(f"  Test R²: {best_r2:.4f}")
    print(f"  Test RMSE: {best_rmse:.4f} MPa")
    print(f"{'='*60}")


# ## 10. Save Models (Traditional Method)

# In[ ]:


# Save models
import joblib

models_dir = Path('models')
models_dir.mkdir(parents=True, exist_ok=True)

torch.save(model_simple.state_dict(), models_dir / 'simple_nn.pth')
torch.save(model_deep.state_dict(), models_dir / 'deep_nn.pth')
torch.save(model_mt.state_dict(), models_dir / 'multitask_nn.pth')

joblib.dump(scaler_X, models_dir / 'scaler_X.pkl')
joblib.dump(scaler_y_str, models_dir / 'scaler_y_str.pkl')
joblib.dump(scaler_y_circ, models_dir / 'scaler_y_circ.pkl')

print("[PASS] PyTorch models saved to models/ directory:")
print("  - simple_nn.pth")
print("  - deep_nn.pth")
print("  - multitask_nn.pth")
print("\n[PASS] Scalers saved:")
print("  - scaler_X.pkl")
print("  - scaler_y_str.pkl")
print("  - scaler_y_circ.pkl")
print("\n[INFO] Models are also tracked in MLflow registry")


# ## 11. Summary & Next Steps

# In[ ]:


print("\n" + "="*60)
print("MLFLOW DEEP LEARNING MODELS COMPLETE")
print("="*60)

print("\n[PASS] MODEL PERFORMANCE:")
print(f"   • Simple NN: R² = {r2_simple:.4f}, RMSE = {rmse_simple:.2f} MPa")
print(f"   • Deep NN: R² = {r2_deep:.4f}, RMSE = {rmse_deep:.2f} MPa")
print(f"   • Multi-Task NN: R² = {r2_mt:.4f}, RMSE = {rmse_mt:.2f} MPa")

print("\n[PASS] MLFLOW TRACKING:")
print(f"   • Experiment: {EXPERIMENTS['deep_learning']}")
print(f"   • Runs logged: 3 (Simple NN, Deep NN, Multi-Task NN)")
print(f"   • Models registered: 3")
print(f"   • Artifacts: Parameters, metrics, models, plots, training curves")

print("\n[PASS] TOTAL MODELS TRACKED (Baseline + Deep Learning):")
print("   1. Linear Regression")
print("   2. Random Forest")
print("   3. XGBoost")
print("   4. Simple Neural Network")
print("   5. Deep Neural Network")
print("   6. Multi-Task Neural Network")

print("\n[INFO] VIEW RESULTS:")
print("   1. Open terminal in project directory")
print("   2. Run: mlflow ui --port 5000")
print("   3. Open: http://localhost:5000")
print(f"   4. Navigate to experiments: Baseline-Models & Deep-Learning")

print("\n[INFO] NEXT STEPS (From Plan):")
print("   • Phase 3: Hyperparameter optimization with Optuna + MLflow (200+ trials)")
print("   • Phase 4: Feature engineering experiments (7 feature sets)")
print("   • Phase 5: Ensemble models (stacking, weighted averaging)")
print("   • Phase 6: Model registry promotion workflow")

print("\n" + "="*60)
print("[PASS] All 6 models with MLflow tracking complete!")
print("="*60 + "\n")

