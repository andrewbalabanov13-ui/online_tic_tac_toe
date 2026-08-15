# Server API

The game server exposes a WebSocket endpoint on port `8000`.

```text
ws://<server-address>:8000
```

All application messages are WebSocket text messages. Fields are separated by a
pipe character (`|`). The protocol does not define escaping, so field values such
as player names must not contain `|`.

## Connection flow

1. Connect to the WebSocket endpoint.
2. Send `start_client|<name>` as the first message.
3. Wait for a second player to connect.
4. Receive `opponent|<name>`.
5. server rolls to see who goes first, if its the second then it would send a relay message witch the client
would relay the arguments to its own thread which would then start their turn.
6. Both players receive `update` messages after accepted moves.
7. Players alternate sending moves until the server sends `player_won`.

The server assigns the first player type `0` and the second player type `1`.
Board cells use the strings `"0"` and `"1"` for player marks and `"e"` for an
empty cell.

## Client-to-server messages

### Register a player

Must be the first message sent after connecting.

```text
start_client|<name>
```

| Field | Type | Description |
| --- | --- | --- |
| `start_client` | string | Command name. |
| `name` | string | Player name shown to the opponent. Must not contain `|`. |

Example:

```text
start_client|Alice
```

### Submit a move

Send this message when it is the client's turn.

```text
move|<x>|<y>
```

| Field | Type | Description |
| --- | --- | --- |
| `move` | string | Command name. The current server does not validate this field. |
| `x` | integer | Zero-based horizontal board coordinate. |
| `y` | integer | Zero-based vertical board coordinate. |

Example:

```text
move|4|3
```

The board is 10 by 10, so usable coordinates are `0` through `9` for both axes.

## Server-to-client messages

### Opponent selected

Sent after two players are connected.

```text
opponent|<name>
```

| Field | Type | Description |
| --- | --- | --- |
| `opponent` | string | Message type. |
| `name` | string | The other player's name. |

### Start game

Sent to the player selected to take the first turn.

```text
start_game
```

This message has no additional fields.

### Board update

Sent to both players after a move is accepted.

```text
update|<x>|<y>|<player_type>
```

| Field | Type | Description |
| --- | --- | --- |
| `update` | string | Message type. |
| `x` | integer | Zero-based horizontal coordinate. |
| `y` | integer | Zero-based vertical coordinate. |
| `player_type` | integer | Player mark: `0` or `1`. |

Example:

```text
update|4|3|0
```

### Retry move

Tells the active player that its move was rejected and another move is required.

```text
resend_message
```

This message has no additional fields.

### Player won

Sent to both players when the server detects five matching marks in a horizontal,
vertical, or diagonal line.

```text
player_won|<player_type>
```

| Field | Type | Description |
| --- | --- | --- |
| `player_won` | string | Message type. |
| `player_type` | integer | Winning player: `0` or `1`. |

## Current implementation caveats

This document describes the message contract visible in `server.py`. The current
implementation has several issues that affect the protocol at runtime:

- `random.randint(1-2)` is called with one argument, so player selection raises a
  `TypeError` before `start_game` is sent.
- Some calls to `connection.send(...)` are not awaited. Those messages may not be
  transmitted.
- Incoming messages are parsed into a list, but that list is compared directly to
  the string `"start_game"`; this condition can never be true.
- Move bounds allow values through `20`, while the board only has indices `0`
  through `9`.
- A move is written to the board before the server checks whether the cell was
  empty. Consequently, the occupied-cell check always rejects the move.
- Game state, turn state, and synchronization are global, so the server does not
  currently support multiple independent games.
