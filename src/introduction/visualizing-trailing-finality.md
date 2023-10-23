# Visualizing Trailing Finality

In the [previous chapter](./motivating-finality.md) we visualized a node's view of consensus in PoW and a valid rollback transition. When we consider a protocol combining PoW with trailing finality, there are multiple possible transitions:

- PoW can make progress on discovering a new block,
- finality can make progress on finalizing a previously found block, and
- finality-constrained PoW rollbacks can occur.

However, unbounded PoW rollbacks may _not_ occur, although they are valid in pure PoW.

Let's visualize a node's view of consensus through each of these kinds of transition to gain an intuition of the intended protocol's behavior.

## Starting State

Let's begin at `T=0` with a known-valid starting state:

```dot process
{{#include ../diagrams/tf-starting-state.dot}}
```

This represents a sequence of blocks, similar to the first diagram in the [previous chapter](./motivating-finality.md), except now we distinguish between *finalized blocks* (which have corner markings) and *unfinalized PoW blocks*.

In the intended protocol design, both *PoW mining* and *finalization* processes are concurrently making progress, so from this starting state we can observe _either_ valid PoW mining progress _or_ valid finaliztion progress.

Let's examine PoW progress first:

## PoW Progress

At `T=1` a new valid PoW block `g` has arrived:

```dot process
{{#include ../diagrams/tf-pow-progress.dot}}
```

Again, from this state _either_ PoW or finality may make progress. For this example, let's assume finality makes progress next:

## Finality Progress

At `T=2` block `d` has become `final`:

```dot process
{{#include ../diagrams/tf-finality-progress.dot}}
```

## PoW Rollback

Just as in vanilla PoW, rollbacks are possible so long as they involve _no finalized blocks_. To illustrate, we envision at `T=3` the node discovers a new best PoW sequence endeing at `h'`:

```dot process
{{#include ../diagrams/tf-with-pow-rollback.dot}}
```

The blocks `f` and `g` from `T=2` have been rolled back in favor of the sequence of `f' → g' → h'`. Because no final blocks are rolled back, this is a valid transition, just as for vanilla PoW.

Now let's consider an invalid attempt to rollback a final block:

## An Invalid Finality Rollback

At `T=4` the node learns of a new sequence ending in `i''` where each header in the Proof-of-Work sequence is valid and demonstrates sufficient work according to pure PoW consensus:

```dot process
{{#include ../diagrams/tf-with-invalid-finality-rollback.dot}}
```

The sequence `d'' → e'' → f'' → g'' → h'' → i''` is invalid and rejected by the node because although it meets all PoW requirements, it does not extend from the most recent final block `d` and attempts to roll it back via `d''`.

# Summary

Visualizing these possible transitions of a PoW-with-Trailing-Finality protocol helps provide an intuition about the intended protocol's behavior.
