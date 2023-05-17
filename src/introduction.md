# A Trailing Finality Layer for Zcash

This book introduces and specifies a `Trailing Finality Layer` for the Zcash network.

This design augments the existing Zcash Proof-of-Work (PoW) network with a new consensus layer which provides `trailing finality`. This layer enables blocks produced via PoW to become `final` which ensures they may never be rolled back. This enables benefits for wallets and other infrastructure as well as protocol improvements.

## Motivating Finality

In Zcash currently, consensus relies solely on PoW, which only provides `probabilistic finality`, rather than `guaranteed finality`.[^1] This style of consensus does not offer a guarantee that any given block may not be `rolled back` which may invalidate the transactions it contains. Instead, the probability that a block may be rolled back decreases as more blocks are mined subsquently on top of it.

Let's walk through an example of how Zcash's current PoW with `probabilistic finality` can impede important use cases. Consider a PoW node which sees this history at time `T=0`:

```dot process
{{#include diagrams/pow-single-branch.dot}}
```

Let's assume that a user, wallet, or other system chooses to act based on a transaction in block `f`. For example, a bridging system may have received a deposit for `ZEC` and issued a corresponding number of proxy tokens on a different network.

At a later time, `T=1`, this same node may see a longer PoW chain which invalidates some previously seen blocks:

```dot process
{{#include diagrams/pow-rollback.dot}}
```

The original block `f` at `T=0` has been replaced by a new block `f'` at `T=1` which no longer contains the deposit to the bridging system. Meanwhile, however, the associated proxy tokens may have already been used in a complex chain of Defi applications or deposited onto an exchange and sold.

This example demonstrates how a lack of `guaranteed finality` can impede many useful real-world scenarios. In practice, systems and services which need greater assurances wait for more block confirmations. This has two drawbacks: first, this introduces a delay which inhibits many useful applications, but second and perhaps worse, it _doesn't remove the vulnerability_, it only reduces the liklihood.

## Visualizing Trailing Finality

```dot process
{{#include diagrams/valid-local-view.dot}}
```

# Footnotes

[^1]: Throughout this book, when we say `finality` or `final` without other qualifiers, we specifically are referring to `guaranteed finality` or a `guaranteed final` block. Where we call out `probabalistic finality` we always use that qualifier.
