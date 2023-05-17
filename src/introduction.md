# A Trailing Finality Layer for Zcash

This book introduces and specifies a *Trailing Finality Layer* for the Zcash network.

This design augments the existing Zcash Proof-of-Work (PoW) network with a new consensus layer which provides *trailing finality*. This layer enables blocks produced via PoW to become *final* which ensures they may never be rolled back. This enables benefits for wallets and other infrastructure as well as protocol improvements.

## Motivating Finality

In Zcash currently, consensus relies solely on PoW, which only provides *probabilistic finality*, rather than *guaranteed finality*.[^finality-qualifiers] This style of consensus does not offer a guarantee that any given block may not be *rolled back* which may invalidate the transactions it contains. Instead, the probability that a block may be rolled back decreases as more blocks are mined subsquently on top of it.

Let's walk through an example of how Zcash's current PoW with *probabilistic finality* can impede important use cases. Consider a PoW node which sees this block sequence at time `T=0`:

```dot process
{{#include diagrams/pow-single-branch.dot}}
```

When should a user, wallet, or other system choose to act based on a transaction in a block?

For this example, let's assume a bridging system may have received a deposit for `ZEC` in block `f` and issued a corresponding number of proxy tokens on a different network.

At a later time, `T=1`, this same node may see a longer PoW chain which invalidates some previously seen blocks:

```dot process
{{#include diagrams/pow-rollback.dot}}
```

The node has observed a longer chain ending at block `h'`, so PoW consensus calls for that new sequence to be treated as consensus. The previously seen blocks `f` and `g` are no longer part of the consensus history, and have been *rolled back*.

In our example, the bridging system acted in response to a transaction in the original block `f` at `T=0`. If the new sequence ending at `h'` no longer contains the deposit to the bridging system, the integrity of the bridge has been violated[^txn-rollback]; the associated proxy tokens may have already been used in a complex chain of Defi applications or deposited onto an exchange and sold, which would make any recovery impossible. The proxy tokens on the other network no longer correspond to the correct amount of `ZEC` on the Zcash network.

This example demonstrates how a lack of *guaranteed finality* can impede many useful real-world scenarios. In practice, systems and services which need greater assurances wait for more block confirmations.

This has several drawbacks:

- it _doesn't remove the vulnerability_, it only reduces the likelihood,
- different applications may require different block depths making it difficult to compose or chain together different applications and potentially confusing users, and
- it introduces a delay which inhibits many useful applications.

*Trailing finality* extends the existing PoW consensus so that older blocks become *final*, ensuring they _cannot_ be rolled back, and by extension neither can any of the transactions they containt. This directly addresses the first two flaws above.

 As for delay, *tailing finality* also introduces delay since *final* blocks "trail behind" the most recent PoW blocks. This can be an improvement for some applications, but not others. For example, if the delay to finality averages around 10 minutes, then this would enable an improvement for an exchange which requires 60 minutes of PoW blocks for a deposit. On the other hand, it would not be an improvement for an application that needs finality faster than 10 minutes.

## Visualizing Trailing Finality

```dot process
{{#include diagrams/valid-local-view.dot}}
```

# Footnotes

[^finality-qualifiers]: Throughout this book, when we say *finality* or *final* without other qualifiers, we specifically are referring to *guaranteed finality* or a *guaranteed final* block. Where we call out *probabalistic finality* we always use that qualifier.

[^txn-rollback]: This discussion simplifies consideration of *transaction rollback* vs *block rollback*. When a block is rolled back, it is possible for some of the transactions contained in it to appear in new canonical blocks. The conditions when this can occur vs when it cannot are multifaceted and also subject to malicious influence, so for simplicity we assume all transactions within a rolled-back block are also rolled back.
