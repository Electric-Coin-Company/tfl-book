# Visualizing Trailing Finality

In the [previous chapter](./motivating-finality.md) we visualized a block rollback diagram. Let's visualize a node's view of a protocol with trailing finality:

```dot process
{{#include ../diagrams/tf-single-branch.dot}}
```

This represents a sequence of blocks, similar to the first diagram in the [previous chapter](./motivating-finality.md), except now we distinguish between *finalized blocks* (which have corner markings) and *unfinalized PoW blocks*.

As previously, let's assume this is the node's view at time `T=0` and next visualize a valid PoW rollback at time `T=1`:

```dot process
{{#include ../diagrams/tf-with-pow-rollback.dot}}
```

The blocks `f` and `g` from `T=0` have been rolled back in favor of the sequence of `f' → g' → h'` at time `T=1`. Because no final blocks are rolled back, this is a valid transition, just as for vanilla PoW.
