# Model Code Architecture

The two consensus subprotocols are analyzed in a *model code architecture* which reifies each consensus subprotocol as a distinct code component: one for PoW and one for PoS. While implementations are not required to follow this code architecture, so long as they are equivalent by consensus, we also believe this code architecture will be a practical approach for implementations.

The network topology introduces a new network for TFL: the TFL subprotocol components of a fully validating node connect to other such components on other nodes using a TFL-specific networking protocol.

```dot process
{{#include ../diagrams/tf-starting-state.dot}}
```
