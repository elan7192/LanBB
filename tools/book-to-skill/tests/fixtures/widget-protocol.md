# Widget Protocol Handbook
**Author**: Ada Example

## Chapter 1: Handshake

Use the three-way handshake when opening a stream. SYN means "I want to talk."
SYN-ACK means "I heard you and I want to talk." ACK means "we are open."

**When to use**: every new stream.
**Anti-pattern**: data-before-ACK; the peer will drop it.

```
client -> SYN
server -> SYN-ACK
client -> ACK
```

## Chapter 2: Backpressure

Prefer credit-based flow control over unbounded queues. Advertise remaining
buffer as credits. When credits hit zero, stop sending.

**When to use**: any producer that can outrun a consumer.
**Anti-pattern**: dropping on overflow without telling the sender.

## Chapter 3: Timeouts

Bound every wait. Idle timeout closes a quiet stream. Handshake timeout aborts
a stream that never opened. Use the same clock domain on both peers.
