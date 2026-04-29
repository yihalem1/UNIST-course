import time
import random
import argparse
import numpy as np

import torch
import torch.nn.functional as F
import torch.optim as optim

from itertools import islice

from utils import DataSampling, load_datasets, split_support_query
import miniimagenet_dataloader as midl

from models import ResNet12, CNN


# ----------------------------
# Repro
# ----------------------------
def seed_everything(seed: int = 0):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def _get_device(model: torch.nn.Module) -> torch.device:
    return next(model.parameters()).device


# ----------------------------
# ProtoNet helpers
# ----------------------------
def _prepare_episode(batch, ways: int, K: int, Q: int, device: torch.device):
    # batch is (x, y) from DataLoade
    x = batch[0] if isinstance(batch, (list, tuple)) else batch

    # utils.split_support_query already .cuda()'s x_support/x_query
    x_support, x_query = split_support_query(x, ways=ways, shots=K, query=Q)

    y_support = torch.arange(ways, device=device).unsqueeze(1).expand(ways, K).reshape(-1)
    y_query = torch.arange(ways, device=device).unsqueeze(1).expand(ways, Q).reshape(-1)
    return x_support, x_query, y_support, y_query


def _compute_logits(model, z_query, prototypes, metric: str):
    """
    metric:
      - 'euclidean': logits = -||q - p||^2
      - 'cosine'   : logits = scale * cos(q, p)
    """
    if metric == "euclidean":
        dists = torch.cdist(z_query, prototypes, p=2) ** 2
        return -dists

    if metric == "cosine":
        zq = F.normalize(z_query, dim=-1)
        zp = F.normalize(prototypes, dim=-1)
        scale = F.softplus(model.logit_scale).clamp(min=1.0, max=50.0)
        return scale * (zq @ zp.t())

    raise ValueError(f"Unknown metric: {metric}")


# ----------------------------
# Train / Eval
# ----------------------------
def proto_train(args, model, N, K, Q=15, num_epochs=20000):
    train_ways = args.train_ways if args.train_ways is not None else (30 if (N == 5 and K == 1) else N)
    trainloader, _ = load_datasets(args, train_ways, K, Q, batch_size=1)

    device = _get_device(model)
    model.train()

    if args.optim == "sgd":
        optimizer = optim.SGD(model.parameters(), lr=args.lr, momentum=0.9, weight_decay=args.wd, nesterov=True)
        scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=num_epochs)
    else:
        optimizer = optim.Adam(model.parameters(), lr=args.lr, weight_decay=args.wd)
        scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=max(1, num_epochs // 10), gamma=0.5)

    for episode in range(num_epochs):
        batch = next(trainloader)

        x_support, x_query, y_support, y_query = _prepare_episode(
            batch, ways=train_ways, K=K, Q=Q, device=device
        )

        z_support = model(x_support)
        z_query = model(x_query)

        prototypes = []
        for c in range(train_ways):
            prototypes.append(z_support[y_support == c].mean(dim=0))
        prototypes = torch.stack(prototypes, dim=0)

        logits = _compute_logits(model, z_query, prototypes, metric=args.metric)

        loss = F.cross_entropy(logits, y_query, label_smoothing=args.label_smoothing)

        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), args.clip_grad)
        optimizer.step()
        scheduler.step()

        if episode % 50 == 0:
            print(
                f"ProtoTrain ({train_ways}-way {K}-shot): "
                f"{episode}/{num_epochs} loss={float(loss.item()):.4f} lr={float(optimizer.param_groups[0]['lr']):.6g}"
            )

    return model


def proto_eval(args, model, dataloader, N, K, Q, max_episodes=None):
    model.eval()
    device = _get_device(model)

    total_loss = 0.0
    total_correct = 0
    total_examples = 0
    num_episodes = 0

    iterator = dataloader
    if max_episodes is not None:
        iterator = islice(dataloader, max_episodes)

    with torch.no_grad():
        for batch in iterator:
            x_support, x_query, y_support, y_query = _prepare_episode(batch, ways=N, K=K, Q=Q, device=device)

            z_support = model(x_support)
            z_query = model(x_query)

            prototypes = []
            for c in range(N):
                prototypes.append(z_support[y_support == c].mean(dim=0))
            prototypes = torch.stack(prototypes, dim=0)

            logits = _compute_logits(model, z_query, prototypes, metric=args.metric)

            loss = F.cross_entropy(logits, y_query)
            preds = logits.argmax(dim=1)

            total_loss += float(loss.item())
            total_correct += int((preds == y_query).sum().item())
            total_examples += int(y_query.size(0))
            num_episodes += 1

            if num_episodes % 500 == 0:
                acc_so_far = 100.0 * total_correct / max(1, total_examples)
                print(f"ProtoEval ({N}-way {K}-shot): {num_episodes} episodes, acc={acc_so_far:.2f}%")

    return total_loss / max(1, num_episodes), total_correct / max(1, total_examples)


def train(args, model_list, N, K, Q, **kwargs):
    model = model_list[0]
    num_epochs = getattr(args, "epoch", 20000)
    model = proto_train(args, model, N=N, K=K, Q=Q, num_epochs=num_epochs)
    model_list = list(model_list)
    model_list[0] = model
    return model_list


def evaluate(args, model_list, dataloader, N, K, Q, **kwargs):
    model = model_list[0]
    max_episodes = getattr(args, "max_test_task", 5000)
    return proto_eval(args, model, dataloader, N=N, K=K, Q=Q, max_episodes=max_episodes)


# ----------------------------
# 95% CI helper (across seeds)
# ----------------------------
def _t_critical_975(df: int) -> float:
    table = {
        1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571,
        6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228,
        11: 2.201, 12: 2.179, 13: 2.160, 14: 2.145, 15: 2.131,
        16: 2.120, 17: 2.110, 18: 2.101, 19: 2.093, 20: 2.086,
        25: 2.060, 30: 2.042
    }
    if df in table:
        return table[df]
    if df > 30:
        return 1.96
    return 2.228


def mean_ci95(values):
    values = np.array(values, dtype=np.float64)
    n = len(values)
    m = float(values.mean())
    if n < 2:
        return m, 0.0
    s = float(values.std(ddof=1))
    t = _t_critical_975(n - 1)
    half = t * s / np.sqrt(n)
    return m, half


def run_once(args) -> dict:
    assert torch.cuda.is_available(), "No GPU available."

    seed_everything(args.seed)
    torch.backends.cudnn.benchmark = True

    midl.AUGMENT_TRAIN = (not args.no_aug)

    # Backbone selection (for ablation)
    if args.backbone == "resnet12":
        model = ResNet12('miniimagenet', drop_prob=args.drop_prob, block_size=args.block_size).cuda()
    else:
        model = CNN('miniimagenet').cuda()

    start_time = time.time()
    print("[Hard Cutoffs] Accuracy: 50.00%, Training Time: 9.0 hours")

    model_list = train(args, [model], N=5, K=1, Q=15)

    training_time = (time.time() - start_time) / 3600.0
    time_score = 0.5 * np.tanh(-training_time + 7) + 0.6 if (training_time < 9.0) else 0.0

    num_params = sum([sum(p.numel() for p in m.parameters()) for m in model_list])
    param_score = 0.5 * np.tanh(-num_params / 10_000_000 + 3) + 0.55

    testloader = DataSampling(args, 5, 1, 15, batch_size=1).m_dataloader['test']
    _, acc_5_1 = evaluate(args, model_list, testloader, 5, 1, 15)

    acc_score = max(1.2 * (0.5 * (acc_5_1 * 100.0 - 50.0) / (1.0 + abs(0.5 * (acc_5_1 * 100.0 - 50.0)))), 0.0)
    final_score = 70.0 * acc_score * time_score * param_score

    print("======================================")
    print("Final Performance Score: %.1f / 70.0" % final_score)
    print("======================================")
    print("Accuracy Score\t: %.2f (%.2f%%)" % (acc_score, acc_5_1 * 100.0))
    print("Time Score\t: %.2f (%.1f hours)" % (time_score, training_time))
    print("Parameter Score\t: %.2f (%.2fM)" % (param_score, num_params / 1_000_000))

    return {
        "acc": float(acc_5_1),
        "acc_pct": float(acc_5_1 * 100.0),
        "final_score": float(final_score),
        "training_hours": float(training_time),
        "params_m": float(num_params / 1_000_000.0),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--epoch', '--epochs', type=int, default=20000)
    parser.add_argument('--max_test_task', type=int, default=5000)
    parser.add_argument('--seed', type=int, default=0)

    # Core knobs
    parser.add_argument('--metric', type=str, default='cosine', choices=['euclidean', 'cosine'])
    parser.add_argument('--train_ways', type=int, default=20)
    parser.add_argument('--label_smoothing', type=float, default=0.1)
    parser.add_argument('--clip_grad', type=float, default=5.0)

    parser.add_argument('--optim', type=str, default='sgd', choices=['sgd', 'adam'])
    parser.add_argument('--lr', type=float, default=0.05)
    parser.add_argument('--wd', type=float, default=5e-4)

    # Backbone + regularization
    parser.add_argument('--backbone', type=str, default='resnet12', choices=['resnet12', 'cnn'])
    parser.add_argument('--drop_prob', type=float, default=0.1)
    parser.add_argument('--block_size', type=int, default=5)

    # Augmentation ablation
    parser.add_argument('--no_aug', action='store_true', help='Disable train-time augmentation in miniimagenet_dataloader.')

    # 95% CI across seeds (>=3 runs). Example: --ci_seeds 0,1,2
    parser.add_argument('--ci_seeds', type=str, default=None,
                        help='Comma-separated seeds for IID runs to compute 95% CI (e.g., 0,1,2).')

    args = parser.parse_args()

    # Multi-run CI mode
    if args.ci_seeds is not None:
        seeds = [int(s.strip()) for s in args.ci_seeds.split(",") if s.strip() != ""]
        assert len(seeds) >= 3, "For 95% CI bonus, use >= 3 IID runs (e.g., --ci_seeds 0,1,2)."

        accs = []
        scores = []
        print(f"\n=== CI mode: running seeds {seeds} ===\n")
        for s in seeds:
            run_args = argparse.Namespace(**vars(args))
            run_args.seed = s
            out = run_once(run_args)
            accs.append(out["acc_pct"])
            scores.append(out["final_score"])
            print(f"[Seed {s}] acc={out['acc_pct']:.2f}% score={out['final_score']:.1f}\n")

        mean_acc, ci_acc = mean_ci95(accs)
        mean_score, ci_score = mean_ci95(scores)

        print("======================================")
        print("95% CI Summary (across seeds)")
        print("======================================")
        print(f"Accuracy: {mean_acc:.2f}% ± {ci_acc:.2f}% (95% CI, n={len(seeds)})")
        print(f"Score   : {mean_score:.1f} ± {ci_score:.1f} (95% CI, n={len(seeds)})")
        return

    # Normal single-run mode
    _ = run_once(args)


if __name__ == '__main__':
    main()
