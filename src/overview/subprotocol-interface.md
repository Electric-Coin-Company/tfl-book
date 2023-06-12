# Subprotocol Interface

The interaction between the two subprotocols is modeled as a message-passing interface with each subprotocol notifying the other of state changes. The sending subprotocol of a notification is authoritative so each notification enables the recipient to update necessary local state with the assumption that it is already validated according to the peer subprotocol's consensus rules.

## Message Ordering

The ordering of notifications is strict in the sender-perspective only: if one subprotocol sends notifications `A` then `B`, then the recipient subprotocol must see `A` then `B` in that order.

However, the notifications have arbitrary ordering across subprotocols. For example if one subprotocol sends `A` then `B` and the other subprotocol sends `X` then `Y`, the first subprotocol may observe the ordering `A`, `X`, `B`, `Y`, while the other subprotocol may observe the ordering `A`, `B`, `X`, `Y`.

## PoW → TFL: `new_pow_block(blockhash, pos_actions)`

Here PoW notifies TFL of a newly discovered PoW block, along with *PoS Actions* initiated by transactions within that block.

Caution: the block identified by `blockhash` may be known to _NOT_ be a descendent of the *Most Recent Final Block* (MRFB) due to a race condition. While the TFL may have sent a notice of a new MRFB, the PoW may send a `new_pow_block` prior to receiving that notification. This is a consequence of [Message Ordering](#message-ordering) above.

If TFL receives a `blockhash` which does not descend from the TFL's local view of MRFB, then TFL must ignore the notification. OTOH, if it _does_ descend from TFL's local MRFB, it must store `(blockhash, pos_actions)`.

## TFL → PoW: `new_final_block(blockhash, pos_results)`

This notifies PoW that a previously discovered PoW block is now final. `blockhash` is guaranteed by TFL to meet these conditions:

- It was previously transmitted to TFL via a `new_pow_block` message.
- It is a direct descendent of the previous Most Recent Final Block.

When PoW receives this message, it must replace its previous MRFB with this new MRFB (which is a direct descendent).
