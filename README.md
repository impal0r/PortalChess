# PortalChess
Chess, but in Python and with portals!

Requirements

- Windows
- Python 3
- pygame

settings.json

- Customise colours and layout parameters
- Change the max framerate from 60fps
- Change the path for saved games

big_chess.pyw

- All the code is contained in this file
- Board size and starting position can be changed by modifying constants in this file

Gameplay

- There is no game engine in the current version: the app works like a physical chessboard in that you can move any piece anywhere, except onto a piece of the same colour. You can even take pieces off the board and/or resurrect them.
- The "Edit pieces" menu allows extra pieces to be added to the board midgame. Unfortunately, this is the only way to promote pawns, and it's a bit fiddly. Pieces can also be completely removed from play.
- The "Edit black holes" menu lets you place or remove "black holes" by left-clicking on any square on the board. What these do is up to you, I added them for a specific chess variation.
- The "Edit portals" menu lets you place or remove portals by left-clicking any square on the board. There are several portal colours available, and all the portals of the same colour form a group. Since a portal links different squares together, these squares are considered to be the 'same' square in this game, so that a piece on a portal square is on all portals of the same colour simultaneously. Portals cannot be placed where there is already a piece. 
- The "Undo" and "Redo" buttons (you can use Ctrl-Z and Ctrl-Y) undo all interactions in the app, not just piece moves
- The "Reset" button (restores the original set of pieces and) moves all the pieces back to their starting positions
- The "Save Game" button saves the current game state to a file. You can close the app, re-open it, and reload the saved state with the "Open Game" button. Saving multiple games concurrently is not currently supported (unless you manually modify the file path in the settings.json file)
- Whenever the app is closed, it stashes the current game state to the `saved_games/stashed_game.json` file. This means that you can reload the game state from when the app last closed (useful if it crashed). To do this, you have to modify the `open_path` parameter in `settings.json` to change the file that the "Open Game" button looks for.

Keyboard shortcuts

<table>
  <tr>
    <th>K</th>
    <td>'Kill' a piece (move it to the captured rank)</td>
  </tr>
  <tr>
    <th>B</th>
    <td>Edit black holes</td>
  </tr>
  <tr>
    <th>P</th>
    <td>Edit portals</td>
  </tr>
  <tr>
    <th>I</th>
    <td>Edit pieces</td>
  </tr>
  <tr>
    <th>ESC</th>
    <td>Exit any editing modes</td>
  </tr>
  <tr>
    <th>Ctrl+Z</th>
    <td>Undo</td>
  </tr>
  <tr>
    <th>Ctrl+Y</th>
    <td>Redo</td>
  </tr>
  <tr>
    <th>Ctrl+S</th>
    <td>Save Game</td>
  </tr>
  <tr>
    <th>Ctrl+O</th>
    <td>Open Game</td>
  </tr>
</table>
