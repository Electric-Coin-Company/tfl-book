# A Trailing Finality Layer for Zcash

This site introduces and specifies a `Trailing Finality Layer` for the Zcash network.

This design augments the existing Zcash Proof-of-Work network with a new consensus layer which provides `trailing finality`. This layer enables blocks to become `final` which ensures they may never be rolled back. This enables all manner of clients to rely on this property for a variety of benefits.

```dot process
{{#include diagrams/valid-local-view.dot}}
```
