# Terms of Use

This archive contains the golden oracle implementations for RepoGenesis (Verified). It is
shared directly with the recipient for non-commercial academic research. It is **not** part
of the public benchmark release.

By using this archive you agree to the following.

## 1. Research use only

Use the implementations for academic research, such as structural or architectural analysis
of the reference code. Commercial use is not granted by this archive.

## 2. No training or fine-tuning

Do not use these implementations, in whole or in part, as training, fine-tuning, distillation,
alignment, or reinforcement-learning data for any model.

This is the condition we care about most. RepoGenesis measures whether a system can produce a
working repository from a README alone. A model that has seen the reference implementations
has effectively seen the answers, and any score it reports on the benchmark stops being
meaningful, both for that model and for every result it is compared against.

## 3. No public redistribution

Do not publish, upload, mirror, or otherwise make this archive or its contents publicly
available, including in a public code repository, dataset release, model artifact, or
appendix. Sharing within your immediate research group for the same research purpose is fine,
provided they are bound by these terms.

If you need to show specific code in a paper, quote the minimum necessary as a figure or
listing rather than releasing files.

## 4. Attribution

Cite the RepoGenesis paper in any publication that uses this archive. The BibTeX entry is in
`README.md`.

## 5. Third-party components

`NOTICE.md` lists components that carry their own licences. Those licences govern their
respective files and take precedence over these terms where they conflict. Note in particular
that `rock-paper-scissors-flask` is CC BY-NC 4.0 (non-commercial) and `synapse` is AGPL-3.0.

## 6. No warranty

The implementations are provided as is, without warranty of any kind. They are research
artifacts, not production software. Several contain deliberately simple storage layers,
placeholder configuration, and no hardening; do not deploy them.

## Questions

Contact the corresponding author, Pu Zhao (<puzhao@microsoft.com>), or the first author,
Zhiyuan Peng (<pzy2000@sjtu.edu.cn>).
