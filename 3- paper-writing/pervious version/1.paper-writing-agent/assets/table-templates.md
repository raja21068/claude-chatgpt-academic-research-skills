# Table Templates for Academic Papers

Ready-to-copy templates in both LaTeX and Markdown. Replace TODO placeholders with your data.

---

## 1. Main Results Comparison

Use this to compare your method against baselines on key metrics.

### LaTeX

```latex
\begin{table}[t]
\centering
\caption{Comparison with state-of-the-art methods on TODO:DATASET. Best results are in \textbf{bold}, second best are \underline{underlined}. $\uparrow$ means higher is better, $\downarrow$ means lower is better.}
\label{tab:main_results}
\begin{tabular}{l c c c c}
\toprule
\textbf{Method} & \textbf{Metric-1} $\uparrow$ & \textbf{Metric-2} $\uparrow$ & \textbf{Metric-3} $\downarrow$ & \textbf{Metric-4} $\uparrow$ \\
\midrule
Baseline-A~\cite{TODO} & 00.0 & 00.0 & 00.0 & 00.0 \\
Baseline-B~\cite{TODO} & 00.0 & 00.0 & 00.0 & 00.0 \\
Baseline-C~\cite{TODO} & 00.0 & 00.0 & 00.0 & 00.0 \\
Baseline-D~\cite{TODO} & 00.0 & 00.0 & 00.0 & 00.0 \\
\midrule
\textbf{Ours} & \textbf{00.0} & \textbf{00.0} & \textbf{00.0} & \textbf{00.0} \\
\bottomrule
\end{tabular}
\end{table}
```

### Markdown

```markdown
| Method | Metric-1 ↑ | Metric-2 ↑ | Metric-3 ↓ | Metric-4 ↑ |
|--------|-----------|-----------|-----------|-----------|
| Baseline-A [TODO] | 00.0 | 00.0 | 00.0 | 00.0 |
| Baseline-B [TODO] | 00.0 | 00.0 | 00.0 | 00.0 |
| Baseline-C [TODO] | 00.0 | 00.0 | 00.0 | 00.0 |
| **Ours** | **00.0** | **00.0** | **00.0** | **00.0** |
```

---

## 2. Ablation Study

Use this to show the impact of each component in your method.

### LaTeX

```latex
\begin{table}[t]
\centering
\caption{Ablation study on TODO:DATASET. Each row removes or modifies one component from the full model.}
\label{tab:ablation}
\begin{tabular}{l c c c c}
\toprule
\textbf{Variant} & \textbf{Component changed} & \textbf{Metric-1} $\uparrow$ & \textbf{Metric-2} $\uparrow$ & \textbf{$\Delta$} \\
\midrule
Full model & -- & 00.0 & 00.0 & -- \\
\midrule
w/o Module-A & Remove TODO & 00.0 & 00.0 & -0.0 \\
w/o Module-B & Remove TODO & 00.0 & 00.0 & -0.0 \\
w/o Module-C & Replace TODO with TODO & 00.0 & 00.0 & -0.0 \\
w/ Alternative-D & Swap TODO for TODO & 00.0 & 00.0 & -0.0 \\
\bottomrule
\end{tabular}
\end{table}
```

### Markdown

```markdown
| Variant | Component changed | Metric-1 ↑ | Metric-2 ↑ | Δ |
|---------|------------------|-----------|-----------|-----|
| Full model | -- | 00.0 | 00.0 | -- |
| w/o Module-A | Remove TODO | 00.0 | 00.0 | -0.0 |
| w/o Module-B | Remove TODO | 00.0 | 00.0 | -0.0 |
| w/o Module-C | Replace TODO | 00.0 | 00.0 | -0.0 |
```

---

## 3. Dataset Description

Use this to describe datasets used in experiments.

### LaTeX

```latex
\begin{table}[t]
\centering
\caption{Summary of datasets used in our experiments.}
\label{tab:datasets}
\begin{tabular}{l c c c c l}
\toprule
\textbf{Dataset} & \textbf{Train} & \textbf{Val} & \textbf{Test} & \textbf{Classes} & \textbf{Task} \\
\midrule
Dataset-A~\cite{TODO} & 00,000 & 0,000 & 0,000 & 00 & TODO \\
Dataset-B~\cite{TODO} & 00,000 & 0,000 & 0,000 & 00 & TODO \\
Dataset-C~\cite{TODO} & 00,000 & 0,000 & 0,000 & 00 & TODO \\
\bottomrule
\end{tabular}
\end{table}
```

### Markdown

```markdown
| Dataset | Train | Val | Test | Classes | Task |
|---------|-------|-----|------|---------|------|
| Dataset-A [TODO] | 00,000 | 0,000 | 0,000 | 00 | TODO |
| Dataset-B [TODO] | 00,000 | 0,000 | 0,000 | 00 | TODO |
| Dataset-C [TODO] | 00,000 | 0,000 | 0,000 | 00 | TODO |
```

---

## 4. Hyperparameter Settings

Use this to document training configuration for reproducibility.

### LaTeX

```latex
\begin{table}[t]
\centering
\caption{Hyperparameter settings used in our experiments.}
\label{tab:hyperparams}
\begin{tabular}{l l}
\toprule
\textbf{Hyperparameter} & \textbf{Value} \\
\midrule
Optimizer & TODO (e.g., AdamW) \\
Learning rate & TODO (e.g., 1e-4) \\
LR scheduler & TODO (e.g., cosine annealing) \\
Weight decay & TODO (e.g., 0.01) \\
Batch size & TODO \\
Epochs & TODO \\
Warmup steps & TODO \\
Dropout & TODO \\
Input resolution & TODO \\
Random seed(s) & TODO \\
\midrule
\multicolumn{2}{l}{\textit{Hardware}} \\
\midrule
GPU(s) & TODO (e.g., 4$\times$ NVIDIA A100 40GB) \\
Training time & TODO (e.g., $\sim$12 hours) \\
Framework & TODO (e.g., PyTorch 2.1) \\
\bottomrule
\end{tabular}
\end{table}
```

### Markdown

```markdown
| Hyperparameter | Value |
|----------------|-------|
| Optimizer | TODO |
| Learning rate | TODO |
| LR scheduler | TODO |
| Weight decay | TODO |
| Batch size | TODO |
| Epochs | TODO |
| Warmup steps | TODO |
| Dropout | TODO |
| Input resolution | TODO |
| Random seed(s) | TODO |
| **Hardware** | |
| GPU(s) | TODO |
| Training time | TODO |
| Framework | TODO |
```

---

## 5. Computational Cost / Efficiency Comparison

Use this to compare model efficiency against baselines.

### LaTeX

```latex
\begin{table}[t]
\centering
\caption{Computational cost comparison. Params = total parameters (M = millions). FLOPs = floating-point operations for a single forward pass. Time = wall-clock training time. Memory = peak GPU memory during training.}
\label{tab:efficiency}
\begin{tabular}{l c c c c c}
\toprule
\textbf{Method} & \textbf{Params (M)} & \textbf{FLOPs (G)} & \textbf{Train time} & \textbf{Inference (ms)} & \textbf{GPU mem (GB)} \\
\midrule
Baseline-A & 00.0 & 00.0 & 00h & 00.0 & 00.0 \\
Baseline-B & 00.0 & 00.0 & 00h & 00.0 & 00.0 \\
Baseline-C & 00.0 & 00.0 & 00h & 00.0 & 00.0 \\
\midrule
\textbf{Ours} & 00.0 & 00.0 & 00h & 00.0 & 00.0 \\
\bottomrule
\end{tabular}
\end{table}
```

### Markdown

```markdown
| Method | Params (M) | FLOPs (G) | Train time | Inference (ms) | GPU mem (GB) |
|--------|-----------|----------|-----------|----------------|-------------|
| Baseline-A | 00.0 | 00.0 | 00h | 00.0 | 00.0 |
| Baseline-B | 00.0 | 00.0 | 00h | 00.0 | 00.0 |
| **Ours** | 00.0 | 00.0 | 00h | 00.0 | 00.0 |
```

---

## 6. Statistical Significance

Use this when reporting multiple runs or statistical tests.

### LaTeX

```latex
\begin{table}[t]
\centering
\caption{Results with statistical significance over TODO runs. We report mean $\pm$ standard deviation. $\dagger$ indicates statistically significant improvement over the best baseline (paired t-test, $p < 0.05$).}
\label{tab:significance}
\begin{tabular}{l c c c}
\toprule
\textbf{Method} & \textbf{Metric-1} $\uparrow$ & \textbf{Metric-2} $\uparrow$ & \textbf{$p$-value} \\
\midrule
Baseline-A & $00.0 \pm 0.0$ & $00.0 \pm 0.0$ & -- \\
Baseline-B & $00.0 \pm 0.0$ & $00.0 \pm 0.0$ & -- \\
Best baseline & $00.0 \pm 0.0$ & $00.0 \pm 0.0$ & -- \\
\midrule
\textbf{Ours} & $\mathbf{00.0 \pm 0.0}^{\dagger}$ & $\mathbf{00.0 \pm 0.0}^{\dagger}$ & $< 0.05$ \\
\bottomrule
\end{tabular}
\end{table}
```

### Markdown

```markdown
| Method | Metric-1 ↑ | Metric-2 ↑ | p-value |
|--------|-----------|-----------|---------|
| Baseline-A | 00.0 ± 0.0 | 00.0 ± 0.0 | -- |
| Baseline-B | 00.0 ± 0.0 | 00.0 ± 0.0 | -- |
| Best baseline | 00.0 ± 0.0 | 00.0 ± 0.0 | -- |
| **Ours** | **00.0 ± 0.0**† | **00.0 ± 0.0**† | < 0.05 |

† Statistically significant (paired t-test, p < 0.05) over TODO runs.
```

---

## Usage Notes

- Always mark best results in **bold** and second-best with underline
- Include metric direction arrows (↑ higher is better, ↓ lower is better)
- Never round numbers differently from source data
- Include citations for all baselines and datasets
- Report standard deviation when running multiple seeds
- Use TODO placeholders for any missing values — never fabricate
