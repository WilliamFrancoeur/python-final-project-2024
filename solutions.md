# Issue: Stats not getting reset

## Problem Description
-When clicking on the "Reset Level" button the player stats would only reset after 2 clicks
-That clicking "Reset Level" once would reset all the player's stats to normal. 
-GAME_CONFIG was involved.

## Resolution
-The logic resetting the player stats was moved above the game.initialize_level method.
-Alternatively considered to create a player class to not have to change the GAME_CONFIG when
changing player stats.

## Prevention
-Carefully consider where code logic is being used.
-Understand execution order.
-Be careful changing GAME_CONFIG.



