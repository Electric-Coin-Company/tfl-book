# A Trailing Finality Layer for Zcash

This book introduces and specifies a `Trailing Finality Layer` for the Zcash network.

This design augments the existing Zcash Proof-of-Work (PoW) network with a new consensus layer which provides `trailing finality`. This layer enables blocks produced via PoW to become `final` which ensures they may never be rolled back. This enables benefits for wallets and other infrastructure as well as protocol improvements.

## Visualizing Trailing Finality

In Zcash currently, consensus relies solely on PoW, which only provides `probabilistic finality`, rather than `guaranteed finality`.[^1] This style of consensus does not offer a guarantee that any given block may not be `rolled back` which may invalidate the transactions it contains. Instead, the probability that a block may be rolled back decreases as more blocks are mined subsquently on top of it.

Consider a PoW node which sees this history at time `T=0`:

```dot process
{{#include diagrams/pow-single-branch.dot}}
```

Let's assume that a user, wallet, or other system chooses to act based on a transaction in block `f`. For example, a barista may have received a payment for coffee, then performed the labor to prepare the coffee and then given it to the customer, who enjoys drinking it, then departs.

At a later time, `T=1`, this same node may see a longer PoW chain which invalidates some previously seen blocks:

```dot process
{{#include diagrams/pow-rollback.dot}}
```

The original block `f` at `T=0` has been replaced by a new block `f'` at `T=1` which no longer contains the payment to our barista.


[^1]: Throughout this book, when we say `finality` or `final` without other qualifiers, we specifically are referring to `guaranteed finality` or a `guaranteed final` block. Where we call out `probabalistic finality` we always use that qualifier.

```dot process
{{#include diagrams/valid-local-view.dot}}
```
