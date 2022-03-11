# Team Network Tactics (MVP)
### *Mandatory Assignment in INF142 (Spring 2022)*
*This is only an <u><b>MVP</b></u> which means that you are only able to run game trough <u>localhost</u> ports are automatically set*

Developer: 
* **André Bjørgum** (*Group 1*)

On MittUIB: ***Mandatory assignment 97***

TAs from Team 1: 
* Fredrik (*Github:* Nestvold)
* Tobias (*Github:* bigmantobs)

# *How to play* 
**Clone this repository into your machine**
### 1. Start servers
Run `server_database.py` and `server.py`
* `server_database` creates a socket and connects to MariaDB database
* `server` runs the game server for clients, talks with both `client` and `server_database`

### 2. Create two clients
Run `client.py` two times, one for each player and ***Follow steps***

### 3. Play
* Follow steps in both clients

### 4. See match history on MongoDB
* Not yet implemented using Flask

## Extra champions
*Feel free to add champions on MongoDB*

| **Name** | **Rock** | **Paper** | **Scissors** |
|:---------|:---------|:----------|:-------------|
| Andre    | 0.33     | 0.33      | 0.33         |
| Wuqeen   | 0.3      | 0.5       | 0.2          |
| Jax      | 0.9      | 0.05      | 0.05         |