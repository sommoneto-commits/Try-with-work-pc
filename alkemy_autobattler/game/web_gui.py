"""
Web GUI Module - Browser-based interface.

Uses Python's built-in http.server to serve a web interface.
No external dependencies required.
"""

import http.server
import json
import webbrowser
import threading
import urllib.parse
from typing import Optional
import os

from ..models.player import Player, AIPlayer
from ..models.shop import Shop
from ..models.card import Card
from ..systems.combat import CombatResolver, CombatOutcome


# Global game state (single player game)
game_state = {
    "player": None,
    "ai": None,
    "player_shop": None,
    "ai_shop": None,
    "combat_resolver": None,
    "round_number": 0,
    "game_over": False,
    "log": []
}


def init_game():
    """Initialize a new game."""
    game_state["player"] = Player("You")
    game_state["ai"] = AIPlayer("AI Opponent", difficulty="normal")
    game_state["player_shop"] = Shop(tier=1)
    game_state["ai_shop"] = Shop(tier=1)
    game_state["combat_resolver"] = CombatResolver()
    game_state["round_number"] = 0
    game_state["game_over"] = False
    game_state["log"] = ["Game initialized!"]
    start_new_round()


def start_new_round():
    """Start a new round."""
    game_state["round_number"] += 1
    player = game_state["player"]
    ai = game_state["ai"]
    player_shop = game_state["player_shop"]
    ai_shop = game_state["ai_shop"]

    player.start_round(game_state["round_number"])
    ai.start_round(game_state["round_number"])

    if not player_shop.frozen:
        player_shop.refresh(player.tier)
    else:
        player_shop.unfreeze()

    ai_shop.refresh(ai.tier)
    game_state["log"].append(f"=== Round {game_state['round_number']} ===")


def card_to_dict(card: Card) -> dict:
    """Convert card to JSON-serializable dict."""
    return {
        "instance_id": card.instance_id,
        "name": card.name,
        "tribe": card.tribe.name,
        "tier": card.tier,
        "attack": card.current_attack,
        "health": card.current_health,
        "cost": card.cost,
        "has_divine_shield": card.has_divine_shield,
        "has_taunt": card.has_taunt,
        "ability_id": card.ability_id
    }


def get_game_state_json() -> dict:
    """Get current game state as JSON."""
    player = game_state["player"]
    ai = game_state["ai"]
    shop = game_state["player_shop"]

    return {
        "round": game_state["round_number"],
        "game_over": game_state["game_over"],
        "player": {
            "health": player.health,
            "gold": player.gold,
            "tier": player.tier,
            "tier_up_cost": player.get_tier_up_cost(),
            "board": [card_to_dict(c) for c in player.board.units],
            "hand": [card_to_dict(c) for c in player.hand]
        },
        "ai": {
            "health": ai.health,
            "board_size": ai.board.size()
        },
        "shop": {
            "cards": [card_to_dict(c) for c in shop.available_cards],
            "frozen": shop.frozen
        },
        "log": game_state["log"][-20:]  # Last 20 messages
    }


def handle_action(action: str, params: dict) -> dict:
    """Handle a game action."""
    player = game_state["player"]
    shop = game_state["player_shop"]

    if action == "buy":
        index = int(params.get("index", -1))
        if 0 <= index < len(shop.available_cards):
            card = shop.available_cards[index]
            if player.can_afford(card.cost):
                if len(player.hand) < Player.MAX_HAND_SIZE or not player.board.is_full():
                    if player.buy_card(card, shop):
                        game_state["log"].append(f"Bought {card.name}!")
                        # Auto-play
                        if card in player.hand and not player.board.is_full():
                            player.play_card(card)
                            game_state["log"].append(f"Played {card.name}")
                        return {"success": True}
            return {"success": False, "error": "Cannot buy"}

    elif action == "sell":
        location = params.get("location", "")
        index = int(params.get("index", -1))

        card = None
        if location == "board" and 0 <= index < len(player.board.units):
            card = player.board.units[index]
        elif location == "hand" and 0 <= index < len(player.hand):
            card = player.hand[index]

        if card:
            gold = player.sell_card(card)
            game_state["log"].append(f"Sold {card.name} for {gold}G")
            return {"success": True}
        return {"success": False, "error": "Invalid card"}

    elif action == "play":
        index = int(params.get("index", -1))
        if 0 <= index < len(player.hand):
            card = player.hand[index]
            if not player.board.is_full():
                if player.play_card(card):
                    game_state["log"].append(f"Played {card.name}")
                    return {"success": True}
        return {"success": False, "error": "Cannot play"}

    elif action == "reroll":
        if player.reroll_shop(shop):
            game_state["log"].append("Shop refreshed!")
            return {"success": True}
        return {"success": False, "error": "Not enough gold"}

    elif action == "tierup":
        if player.tier_up():
            shop.refresh(player.tier)
            game_state["log"].append(f"Upgraded to Tier {player.tier}!")
            return {"success": True}
        return {"success": False, "error": "Cannot tier up"}

    elif action == "freeze":
        frozen = shop.toggle_freeze()
        game_state["log"].append("Shop frozen!" if frozen else "Shop unfrozen!")
        return {"success": True}

    elif action == "fight":
        return do_combat()

    elif action == "newgame":
        init_game()
        return {"success": True}

    return {"success": False, "error": "Unknown action"}


def do_combat() -> dict:
    """Execute combat phase."""
    player = game_state["player"]
    ai = game_state["ai"]
    ai_shop = game_state["ai_shop"]
    resolver = game_state["combat_resolver"]

    game_state["log"].append("--- AI Shopping ---")
    ai_actions = ai.take_shop_actions(ai_shop)
    for a in ai_actions:
        game_state["log"].append(f"AI: {a}")

    game_state["log"].append("--- COMBAT ---")
    result = resolver.resolve_combat(
        player.board, ai.board,
        player.tier, ai.tier
    )

    for entry in result.log.get_all():
        game_state["log"].append(entry)

    if result.outcome == CombatOutcome.PLAYER_WIN:
        ai.take_damage(result.damage_to_enemy)
        game_state["log"].append(f"YOU WIN! Enemy takes {result.damage_to_enemy} damage.")
    elif result.outcome == CombatOutcome.ENEMY_WIN:
        player.take_damage(result.damage_to_player)
        game_state["log"].append(f"YOU LOSE! You take {result.damage_to_player} damage.")
    else:
        game_state["log"].append("DRAW!")

    if not player.is_alive:
        game_state["game_over"] = True
        game_state["log"].append("=== GAME OVER - DEFEAT ===")
    elif not ai.is_alive:
        game_state["game_over"] = True
        game_state["log"].append("=== GAME OVER - VICTORY! ===")
    else:
        start_new_round()

    return {"success": True}


HTML_TEMPLATE = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Alkemy Autobattler</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: white;
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 1400px; margin: 0 auto; }

        /* Header */
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: rgba(0,0,0,0.3);
            padding: 15px 25px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .round { font-size: 24px; color: #e94560; font-weight: bold; }
        .stats { font-size: 18px; }
        .stats span { margin: 0 15px; }
        .gold { color: #f1c40f; }
        .health { color: #e74c3c; }
        .tier { color: #9b59b6; }

        /* Main layout */
        .main {
            display: grid;
            grid-template-columns: 300px 1fr;
            gap: 20px;
        }

        /* Shop */
        .shop {
            background: rgba(0,0,0,0.3);
            border-radius: 10px;
            padding: 15px;
        }
        .shop h2 {
            text-align: center;
            margin-bottom: 15px;
            color: #3498db;
        }
        .shop-buttons {
            display: flex;
            flex-wrap: wrap;
            gap: 5px;
            margin-bottom: 15px;
        }
        .shop-buttons button {
            flex: 1;
            min-width: 80px;
            padding: 8px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-weight: bold;
            transition: transform 0.1s;
        }
        .shop-buttons button:hover { transform: scale(1.05); }
        .btn-reroll { background: #3498db; color: white; }
        .btn-tierup { background: #9b59b6; color: white; }
        .btn-freeze { background: #1abc9c; color: white; }
        .btn-freeze.frozen { background: #e74c3c; }

        /* Game area */
        .game-area {
            display: flex;
            flex-direction: column;
            gap: 15px;
        }

        /* Boards */
        .board-section {
            background: rgba(0,0,0,0.3);
            border-radius: 10px;
            padding: 15px;
        }
        .board-section h3 {
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .board-section.enemy h3 { color: #e74c3c; }
        .board-section.player h3 { color: #3498db; }
        .board {
            display: flex;
            gap: 10px;
            min-height: 130px;
            flex-wrap: wrap;
            justify-content: center;
            align-items: center;
        }

        /* Cards */
        .card {
            width: 100px;
            height: 130px;
            border-radius: 8px;
            padding: 8px;
            display: flex;
            flex-direction: column;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
            position: relative;
        }
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 5px 20px rgba(0,0,0,0.5);
        }
        .card.shop-card:hover { transform: scale(1.05); }
        .card-name {
            font-size: 11px;
            font-weight: bold;
            text-align: center;
            margin-bottom: 3px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }
        .card-tribe {
            font-size: 9px;
            text-align: center;
            opacity: 0.8;
            margin-bottom: 5px;
        }
        .card-stats {
            display: flex;
            justify-content: center;
            gap: 10px;
            font-size: 16px;
            font-weight: bold;
            flex-grow: 1;
            align-items: center;
        }
        .card-stats .atk { color: #c0392b; }
        .card-stats .hp { color: #27ae60; }
        .card-cost {
            text-align: center;
            font-size: 12px;
            color: #f1c40f;
            font-weight: bold;
        }
        .card-badges {
            position: absolute;
            top: 5px;
            right: 5px;
            font-size: 12px;
        }
        .empty-slot {
            width: 100px;
            height: 130px;
            border: 2px dashed #444;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #666;
        }

        /* Tribe colors */
        .tribe-MANAGEMENT { background: linear-gradient(145deg, #9b59b6, #8e44ad); }
        .tribe-STAFF { background: linear-gradient(145deg, #27ae60, #1e8449); }
        .tribe-CONSULTING { background: linear-gradient(145deg, #3498db, #2980b9); }
        .tribe-DATA_ANALYTICS { background: linear-gradient(145deg, #f1c40f, #d4ac0d); color: #000; }
        .tribe-MARKETING_MEDIA { background: linear-gradient(145deg, #e67e22, #d35400); }
        .tribe-BRAND_EXPERIENCE { background: linear-gradient(145deg, #e74c3c, #c0392b); }
        .tribe-TECH { background: linear-gradient(145deg, #ecf0f1, #bdc3c7); color: #000; }
        .tribe-NEUTRAL { background: linear-gradient(145deg, #95a5a6, #7f8c8d); }

        /* Hand */
        .hand-section {
            background: rgba(52, 73, 94, 0.5);
            border-radius: 10px;
            padding: 15px;
        }
        .hand-section h3 { color: #95a5a6; margin-bottom: 10px; }
        .hand-hint { font-size: 11px; color: #666; margin-bottom: 10px; }

        /* Fight button */
        .fight-section {
            display: flex;
            justify-content: center;
            gap: 20px;
            padding: 15px;
        }
        .btn-fight {
            background: linear-gradient(145deg, #e74c3c, #c0392b);
            color: white;
            border: none;
            padding: 15px 50px;
            font-size: 20px;
            font-weight: bold;
            border-radius: 10px;
            cursor: pointer;
            transition: transform 0.2s;
        }
        .btn-fight:hover { transform: scale(1.05); }
        .btn-newgame {
            background: #27ae60;
            color: white;
            border: none;
            padding: 15px 30px;
            font-size: 16px;
            border-radius: 10px;
            cursor: pointer;
        }

        /* Combat log */
        .log-section {
            background: rgba(0,0,0,0.5);
            border-radius: 10px;
            padding: 15px;
            margin-top: 20px;
        }
        .log-section h3 { margin-bottom: 10px; color: #f39c12; }
        .log {
            height: 150px;
            overflow-y: auto;
            font-family: monospace;
            font-size: 12px;
            color: #0f0;
            background: #0a0a0a;
            padding: 10px;
            border-radius: 5px;
        }
        .log div { margin-bottom: 2px; }

        /* Game over overlay */
        .game-over {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0.8);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 1000;
        }
        .game-over-content {
            text-align: center;
            padding: 40px;
            background: #16213e;
            border-radius: 20px;
        }
        .game-over h1 { font-size: 48px; margin-bottom: 20px; }
        .game-over.victory h1 { color: #f1c40f; }
        .game-over.defeat h1 { color: #e74c3c; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="round">Round <span id="round">1</span></div>
            <div class="stats">
                <span class="health">HP: <span id="player-hp">30</span></span>
                <span class="gold">Gold: <span id="player-gold">3</span></span>
                <span class="tier">Tier: <span id="player-tier">1</span></span>
            </div>
            <div class="stats">
                <span class="health">Enemy HP: <span id="ai-hp">30</span></span>
            </div>
        </div>

        <div class="main">
            <div class="shop">
                <h2>Shop</h2>
                <div class="shop-buttons">
                    <button class="btn-reroll" onclick="doAction('reroll')">Reroll (1G)</button>
                    <button class="btn-tierup" id="btn-tierup" onclick="doAction('tierup')">Tier Up</button>
                    <button class="btn-freeze" id="btn-freeze" onclick="doAction('freeze')">Freeze</button>
                </div>
                <div id="shop-cards" class="board"></div>
            </div>

            <div class="game-area">
                <div class="board-section enemy">
                    <h3>Enemy Board (<span id="enemy-count">0</span>/7)</h3>
                    <div id="enemy-board" class="board"></div>
                </div>

                <div class="fight-section">
                    <button class="btn-fight" onclick="doAction('fight')">FIGHT!</button>
                    <button class="btn-newgame" onclick="doAction('newgame')">New Game</button>
                </div>

                <div class="board-section player">
                    <h3>Your Board (<span id="player-board-count">0</span>/7)</h3>
                    <div id="player-board" class="board"></div>
                </div>

                <div class="hand-section">
                    <h3>Your Hand</h3>
                    <div class="hand-hint">Click to play | Right-click to sell</div>
                    <div id="player-hand" class="board"></div>
                </div>
            </div>
        </div>

        <div class="log-section">
            <h3>Combat Log</h3>
            <div id="log" class="log"></div>
        </div>
    </div>

    <div id="game-over" class="game-over" style="display: none;">
        <div class="game-over-content">
            <h1 id="game-over-text"></h1>
            <button class="btn-newgame" onclick="doAction('newgame'); hideGameOver();">Play Again</button>
        </div>
    </div>

    <script>
        function createCard(card, onClick, onRightClick, showCost) {
            const div = document.createElement('div');
            div.className = `card tribe-${card.tribe}`;
            if (showCost) div.classList.add('shop-card');

            let badges = '';
            if (card.has_divine_shield) badges += '🛡️';
            if (card.has_taunt) badges += '⚔️';

            div.innerHTML = `
                <div class="card-badges">${badges}</div>
                <div class="card-name">${card.name}</div>
                <div class="card-tribe">${card.tribe.replace('_', ' ')}</div>
                <div class="card-stats">
                    <span class="atk">⚔${card.attack}</span>
                    <span class="hp">♥${card.health}</span>
                </div>
                ${showCost ? `<div class="card-cost">💰 ${card.cost}G</div>` : ''}
            `;

            if (onClick) div.onclick = onClick;
            if (onRightClick) div.oncontextmenu = (e) => { e.preventDefault(); onRightClick(); };

            return div;
        }

        function updateUI(state) {
            document.getElementById('round').textContent = state.round;
            document.getElementById('player-hp').textContent = state.player.health;
            document.getElementById('player-gold').textContent = state.player.gold;
            document.getElementById('player-tier').textContent = state.player.tier;
            document.getElementById('ai-hp').textContent = state.ai.health;

            document.getElementById('btn-tierup').textContent =
                state.player.tier >= 6 ? 'MAX' : `Tier Up (${state.player.tier_up_cost}G)`;

            const freezeBtn = document.getElementById('btn-freeze');
            freezeBtn.textContent = state.shop.frozen ? 'Unfreeze' : 'Freeze';
            freezeBtn.classList.toggle('frozen', state.shop.frozen);

            // Shop
            const shopDiv = document.getElementById('shop-cards');
            shopDiv.innerHTML = '';
            state.shop.cards.forEach((card, i) => {
                shopDiv.appendChild(createCard(card, () => doAction('buy', {index: i}), null, true));
            });
            if (state.shop.cards.length === 0) {
                shopDiv.innerHTML = '<div class="empty-slot">Empty</div>';
            }

            // Enemy board
            document.getElementById('enemy-count').textContent = state.ai.board_size;
            const enemyDiv = document.getElementById('enemy-board');
            enemyDiv.innerHTML = '';
            for (let i = 0; i < state.ai.board_size; i++) {
                const placeholder = document.createElement('div');
                placeholder.className = 'empty-slot';
                placeholder.textContent = '?';
                placeholder.style.background = '#e74c3c33';
                enemyDiv.appendChild(placeholder);
            }
            if (state.ai.board_size === 0) {
                enemyDiv.innerHTML = '<div class="empty-slot">Empty</div>';
            }

            // Player board
            document.getElementById('player-board-count').textContent = state.player.board.length;
            const boardDiv = document.getElementById('player-board');
            boardDiv.innerHTML = '';
            state.player.board.forEach((card, i) => {
                boardDiv.appendChild(createCard(card, null,
                    () => doAction('sell', {location: 'board', index: i}), false));
            });
            if (state.player.board.length === 0) {
                boardDiv.innerHTML = '<div class="empty-slot">Empty</div>';
            }

            // Hand
            const handDiv = document.getElementById('player-hand');
            handDiv.innerHTML = '';
            state.player.hand.forEach((card, i) => {
                handDiv.appendChild(createCard(card,
                    () => doAction('play', {index: i}),
                    () => doAction('sell', {location: 'hand', index: i}), false));
            });
            if (state.player.hand.length === 0) {
                handDiv.innerHTML = '<div class="empty-slot">Empty</div>';
            }

            // Log
            const logDiv = document.getElementById('log');
            logDiv.innerHTML = state.log.map(l => `<div>${l}</div>`).join('');
            logDiv.scrollTop = logDiv.scrollHeight;

            // Game over
            if (state.game_over) {
                const isVictory = state.ai.health <= 0;
                const overlay = document.getElementById('game-over');
                overlay.style.display = 'flex';
                overlay.className = 'game-over ' + (isVictory ? 'victory' : 'defeat');
                document.getElementById('game-over-text').textContent =
                    isVictory ? 'VICTORY!' : 'DEFEAT';
            }
        }

        function hideGameOver() {
            document.getElementById('game-over').style.display = 'none';
        }

        async function doAction(action, params = {}) {
            const url = '/action?action=' + action + '&' +
                Object.entries(params).map(([k,v]) => `${k}=${v}`).join('&');
            await fetch(url);
            fetchState();
        }

        async function fetchState() {
            const res = await fetch('/state');
            const state = await res.json();
            updateUI(state);
        }

        // Initial load
        fetchState();
    </script>
</body>
</html>
'''


class GameHandler(http.server.BaseHTTPRequestHandler):
    """HTTP request handler for the game."""

    def log_message(self, format, *args):
        pass  # Suppress logging

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        if path == "/" or path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(HTML_TEMPLATE.encode())

        elif path == "/state":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            state = get_game_state_json()
            self.wfile.write(json.dumps(state).encode())

        elif path == "/action":
            action = query.get("action", [""])[0]
            params = {k: v[0] for k, v in query.items() if k != "action"}
            result = handle_action(action, params)

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())

        else:
            self.send_response(404)
            self.end_headers()


def main():
    """Start the web GUI."""
    port = 8080
    init_game()

    server = http.server.HTTPServer(("localhost", port), GameHandler)
    print(f"\n{'='*50}")
    print("  ALKEMY AUTOBATTLER - Web GUI")
    print(f"{'='*50}")
    print(f"\n  Opening browser at: http://localhost:{port}")
    print("  Press Ctrl+C to quit\n")

    # Open browser
    webbrowser.open(f"http://localhost:{port}")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.shutdown()


if __name__ == "__main__":
    main()
